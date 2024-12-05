import os
import logging
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

# Load environment variables
load_dotenv()

class LLMConfig:
    def __init__(self):
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama2')
        self.use_local_model = os.getenv('DEFAULT_LLM_MODEL', 'openai') == 'ollama'
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def get_chat_model(self) -> BaseChatModel:
        try:
            if self.use_local_model:
                self.logger.info("Using local Ollama model")
                return ChatOllama(model=self.ollama_model, temperature=0.2)
            else:
                self.logger.info("Using OpenAI model")
                return ChatOpenAI(
                    model=self.openai_model, 
                    temperature=0.2,
                    max_retries=1
                )
        except Exception as e:
            self.logger.error(f"Error initializing chat model: {e}")
            # Fallback to local model if remote fails
            self.use_local_model = True
            return ChatOllama(model=self.ollama_model, temperature=0.2)

    def toggle_model(self):
        self.use_local_model = not self.use_local_model
        self.logger.info(f"Switched to {'local Ollama' if self.use_local_model else 'OpenAI'} model")

# Global LLM Configuration
llm_config = LLMConfig()
