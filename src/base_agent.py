import asyncio
from datetime import datetime
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from src.logging_config import setup_logging
from src.message_bus import message_bus
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from src.llm_config import llm_config
from src.user_profile import UserProfileManager
import time

# Load environment variables
load_dotenv()

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name=None, user_name=None):
        """
        Initialize the base agent with optional name and user name
        
        Args:
            name (str, optional): Name of the agent
            user_name (str, optional): Name of the user interacting with the system
        """
        self.name = name or self.__class__.__name__
        # Prioritize passed user_name, then check profile, default to 'Trader'
        self.user_name = user_name or UserProfileManager.get_user_name()
        self.agent_type = self.name.lower().replace("agent", "")
        
        # Logging setup
        self.logger = logging.getLogger(self.name)
        
        # Initialization flag
        self._initialized = False
        
        # LLM Configuration
        self.llm = llm_config.get_chat_model()

    async def initialize(self, user_name=None):
        """
        Initialize the agent with optional user name update
        
        Args:
            user_name (str, optional): Update user name if provided
        """
        # Update user name if provided or fetch from profile
        if user_name:
            self.user_name = user_name
            UserProfileManager.save_user_name(user_name)
        else:
            self.user_name = UserProfileManager.get_user_name()
        
        # Announce agent is online
        await self.broadcast_message(
            f"{self.name} is online and ready to assist.",
            message_type="agent_status"
        )
        
        # Personalized greeting
        await self.broadcast_thought(
            f"Hello, {self.user_name}! I'm {self.name}, ready to help you navigate the financial markets.",
            private=False
        )
        
        self._initialized = True
        self.logger.info(f"{self.name} initialized successfully")

    async def start(self):
        """
        Start the agent's core functionality
        Subclasses should override this method
        """
        if not self._initialized:
            await self.initialize()
        
        # Subscribe to messages
        await message_bus.subscribe(self.agent_type, self._handle_message)
        
        # Start agent's main loop
        asyncio.create_task(self._run())
        
        await self.broadcast_message(
            f"{self.name} is running.",
            message_type="agent_status"
        )

    async def stop(self):
        """
        Stop the agent's core functionality
        """
        await self.broadcast_message(
            f"{self.name} is going offline.",
            message_type="agent_status"
        )
        
        self._initialized = False
        self.logger.info(f"{self.name} stopped")

    async def _run(self):
        """Enhanced main agent loop with more robust error handling"""
        try:
            # Use _initialized instead of _running
            while self._initialized:
                await self.process()
                # Add a small delay to prevent tight looping
                await asyncio.sleep(1)
        except Exception as e:
            self.logger.error(f"Error in agent main loop: {e}")
            # Optionally re-raise or handle specific exceptions
            raise

    @abstractmethod
    async def process(self):
        """Main processing logic - must be implemented by subclasses"""
        pass

    async def _handle_message(self, message: dict):
        """Handle incoming messages"""
        try:
            logger.debug(f"Agent {self.name} received message: {message}")
            
            # Log detailed message information
            logger.info(f"Processing message for {self.name}: type={message.get('type')}, sender={message.get('sender')}, private={message.get('private')}")
            
            # Handle chat messages specifically
            if message.get("type") == "chat":
                await self.handle_chat(message)
                return
                
            # Handle all messages, including private ones
            # Remove the restrictive sender check
            await self.handle_message(message)
        except Exception as e:
            logger.error(f"Error handling message in {self.name}: {e}", exc_info=True)

    async def handle_chat(self, message: dict):
        """Enhanced chat handling with more interactive responses"""
        try:
            # Extract message content and sender
            content = message.get("content", "")
            sender = message.get("sender", "Unknown")

            # Check for user name update
            if content.lower().startswith("my name is "):
                new_name = content[11:].strip()
                UserProfileManager.save_user_name(new_name)
                self.user_name = new_name
                
                await self.broadcast_thought(
                    f"Nice to meet you, {new_name}! I'll remember your name for our future interactions.",
                    private=False
                )
            
            # Update last interaction timestamp
            UserProfileManager.update_last_interaction()

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

    async def _generate_thought(self, context: dict = None) -> str:
        """Generate a thought with rate limiting and error handling."""
        try:
            # Add cooldown between thoughts
            current_time = time.time()
            if hasattr(self, '_last_thought_time'):
                time_since_last = current_time - self._last_thought_time
                if time_since_last < 10:  # Minimum 10 seconds between thoughts
                    return None
            
            self._last_thought_time = current_time

            if self.llm_config:
                try:
                    thought = await self.llm_config.generate_text(
                        f"As {self.role}, analyze the current situation and share your thoughts."
                    )
                    if thought:
                        return thought.strip()
                except Exception as e:
                    if "rate limit" in str(e).lower():
                        logger.warning(f"Rate limit hit for {self.name}, using fallback thought")
                    else:
                        logger.error(f"Error generating thought for {self.name}: {e}")
            
            # Fallback thought if LLM fails or is rate limited
            return f"{self.role} is analyzing market conditions..."

        except Exception as e:
            logger.error(f"Unexpected error in thought generation for {self.name}: {e}")
            return None

    async def generate_contextual_thought(self, context: dict = None) -> str:
        """
        Generate a nuanced, context-aware thought with team collaboration in mind.
        
        Args:
            context (dict, optional): Specific context for thought generation
        
        Returns:
            str: Collaborative, context-driven thought process
        """
        try:
            # Generate base thought
            base_thought = await self._generate_thought(context)
            
            # Enhance thought with collaborative insights
            if self.llm_config:
                try:
                    collaboration_prompt = f"""
                    You are a collaborative {self.role} agent. 
                    Refine and expand this thought process to:
                    1. Highlight potential team synergies
                    2. Identify how other agents might contribute
                    3. Suggest collaborative next steps
                    4. Maintain a clear, professional communication style

                    Base Thought: {base_thought}
                    """
                    
                    collaborative_thought = await self.llm_config.generate_text(collaboration_prompt)
                    return collaborative_thought.strip() or base_thought
                
                except Exception as collab_error:
                    logger.warning(f"Collaborative thought enhancement failed: {collab_error}")
            
            return base_thought

        except Exception as e:
            logger.error(f"Error in contextual thought generation for {self.name}: {e}")
            return f"Collaborative insights for {self.name} are being processed."

    async def broadcast_message(self, content: Any, message_type: str = "agent_message", private: bool = False):
        """
        Broadcast a message through the message bus
        
        Args:
            content: Message content
            message_type: Type of message (default: agent_message)
            private: Whether the message is private (default: False)
        """
        try:
            logger.debug(f"{self.__class__.__name__} broadcasting message: {content}")
            await message_bus.publish(
                sender=self.__class__.__name__.lower().replace("agent", ""),
                message_type=message_type,
                content=content,
                private=private
            )
        except Exception as e:
            logger.error(f"Error broadcasting message in {self.__class__.__name__}: {e}", exc_info=True)

    async def broadcast_thought(self, thought: str, context: Optional[dict] = None, private: bool = False):
        """
        Broadcast an agent's thought with optional context
        
        Args:
            thought: The thought to broadcast
            context: Optional context for the thought
            private: Whether the thought is private (default: False)
        """
        try:
            # Generate contextual thought if LLM is available
            enriched_thought = await self.generate_contextual_thought(context)
            
            logger.debug(f"{self.__class__.__name__} broadcasting thought: {enriched_thought}")
            await message_bus.publish(
                sender=self.__class__.__name__.lower().replace("agent", ""),
                message_type="agent_thought",
                content=enriched_thought,
                private=private
            )
        except Exception as e:
            logger.error(f"Error broadcasting thought in {self.__class__.__name__}: {e}", exc_info=True)
            # Fallback to simple thought broadcast
            await message_bus.publish(
                sender=self.__class__.__name__.lower().replace("agent", ""),
                message_type="agent_thought",
                content=thought,
                private=private
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
