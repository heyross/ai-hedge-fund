import asyncio
from datetime import datetime
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict
from src.logging_config import setup_logging
from src.message_bus import message_bus
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from src.llm_config import llm_config

# Load environment variables
load_dotenv()

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, agent_type: str):
        self.name = name
        self.agent_type = agent_type
        self._running = False
        self.state: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # LLM Configuration
        self.llm = llm_config.get_chat_model()

    async def start(self):
        """Start the agent"""
        self._running = True
        # Subscribe to messages
        await message_bus.subscribe(self.agent_type, self._handle_message)
        # Start agent's main loop
        self._task = asyncio.create_task(self._run())
        logger.info(f"Agent {self.name} started")
        await self._broadcast_status("Running")

    async def stop(self):
        """Stop the agent"""
        self._running = False
        logger.info(f"Agent {self.name} stopped")
        await self._broadcast_status("Stopped")

    async def _run(self):
        """Enhanced main agent loop with more robust error handling"""
        consecutive_errors = 0
        max_consecutive_errors = 3

        while self._running:
            try:
                await self.process()
                await asyncio.sleep(1)  # Prevent busy waiting
                consecutive_errors = 0  # Reset error count on successful run
            except Exception as e:
                consecutive_errors += 1
                error_message = f"Error in agent {self.name}: {e}"
                logger.error(error_message, exc_info=True)
                
                # Broadcast error thoughts with increasing urgency
                if consecutive_errors == 1:
                    await self.broadcast_thought(f"Encountered an issue: {error_message}")
                elif consecutive_errors == 2:
                    await self.broadcast_thought(f"Persistent issue detected. Attempting recovery: {error_message}")
                elif consecutive_errors >= max_consecutive_errors:
                    await self.broadcast_thought(f"CRITICAL: Multiple consecutive errors. Agent may need manual intervention.")
                    await self.stop()  # Stop the agent if too many errors occur
                
                # Exponential backoff for error recovery
                await asyncio.sleep(min(2 ** consecutive_errors, 60))  # Max 1 minute wait

    @abstractmethod
    async def process(self):
        """Main processing logic - must be implemented by subclasses"""
        pass

    async def _handle_message(self, message: dict):
        """Handle incoming messages"""
        try:
            logger.debug(f"Agent {self.name} received message: {message}")
            
            # Handle chat messages specifically
            if message.get("type") == "chat":
                await self.handle_chat(message)
                return
                
            # Handle other messages if they're public or from this agent
            if not message.get("private", False) or message.get("sender") == self.agent_type:
                await self.handle_message(message)
        except Exception as e:
            logger.error(f"Error handling message in {self.name}: {e}", exc_info=True)

    async def handle_chat(self, message: dict):
        """Enhanced chat handling with more interactive responses"""
        try:
            # Extract message content and sender
            content = message.get("content", "")
            sender = message.get("sender", "Unknown")

            # Generate a contextual response using the LLM
            try:
                llm_response = await self.llm.generate(
                    messages=[
                        {"role": "system", "content": f"You are {self.name}. Respond naturally and concisely."},
                        {"role": "user", "content": content}
                    ]
                )
                response_text = llm_response.generations[0].text.strip()
            except Exception as e:
                # Fallback to a default response if LLM fails
                response_text = f"I heard you, {sender}. As the {self.name}, I'm processing your message: {content}"
                logger.warning(f"LLM chat generation failed: {e}")

            # Broadcast the response
            await message_bus.publish(
                sender=self.agent_type,
                message_type="chat",
                content={
                    "text": response_text,
                    "in_response_to": content,
                    "original_sender": sender
                },
                private=False
            )

            # Also broadcast a thought to add more context
            await self.broadcast_thought(f"Responding to message from {sender}")

        except Exception as e:
            logger.error(f"Error in chat handling for {self.name}: {e}")
            await self.broadcast_thought(f"Error processing chat: {str(e)}")

    @abstractmethod
    async def handle_message(self, message: dict):
        """Handle a specific message - must be implemented by subclasses"""
        pass

    async def _broadcast_status(self, status: str):
        """Broadcast agent status"""
        await message_bus.publish(
            sender=self.agent_type,
            message_type="agent_status",
            content={
                "agent": self.name,
                "status": status
            },
            private=False
        )
        
        # Also publish a thought to make it more interactive
        await message_bus.publish(
            sender=self.agent_type,
            message_type="agent_thought",
            content=f"{self.name} is currently {status.lower()}.",
            private=False
        )

    async def generate_contextual_thought(self, context: str = None) -> str:
        """
        Generate a more nuanced, context-aware thought using the LLM
        
        Args:
            context (str, optional): Additional context for thought generation
        
        Returns:
            str: A generated thought
        """
        try:
            # Prepare system prompt with agent's role and current state
            system_prompt = f"""
            You are {self.name}. Generate a brief, introspective thought that reflects 
            your current state of mind and ongoing tasks. Be professional, concise, 
            and provide insight into your current cognitive process.
            """
            
            # Add optional context to the prompt
            user_prompt = f"Current context: {context}" if context else "Reflect on your current state."
            
            # Generate thought using LLM
            thought_response = await self.llm.generate(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract and clean the generated thought
            generated_thought = thought_response.generations[0].text.strip()
            
            # Fallback if generation fails
            return generated_thought or f"Processing tasks as {self.name}."
        
        except Exception as e:
            logger.warning(f"Thought generation failed for {self.name}: {e}")
            return f"Continuing my work as {self.name}."

    async def broadcast_thought(self, thought: str = None, context: str = None):
        """
        Enhanced thought broadcasting with optional LLM-generated content
        
        Args:
            thought (str, optional): Predefined thought to broadcast
            context (str, optional): Additional context for thought generation
        """
        # If no predefined thought, try to generate one
        if not thought:
            thought = await self.generate_contextual_thought(context)
        
        # Broadcast the thought
        await message_bus.publish(
            sender=self.agent_type,
            message_type="agent_thought",
            content=thought,
            private=False
        )

    async def broadcast_message(self, content: Any, message_type: str = "info"):
        """Broadcast a message to all agents"""
        await message_bus.publish(
            sender=self.agent_type,
            message_type=message_type,
            content=content,
            private=False
        )

    def handle_api_error(self, error):
        """
        Handle API errors with intelligent fallback
        """
        self.logger.error(f"API Error encountered: {error}")
        
        # Toggle to local model if remote API fails
        if not llm_config.use_local_model:
            llm_config.toggle_model()
            self.llm = llm_config.get_chat_model()
            self.logger.warning("Switched to local Ollama model due to API error")
        
        return None

    def get_current_model(self):
        """
        Return the current active model
        """
        return "Ollama" if llm_config.use_local_model else "OpenAI"
