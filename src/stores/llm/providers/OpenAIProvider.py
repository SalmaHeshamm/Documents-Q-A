from llm import LLMIntrface, OpenAIEnums
from openai import OpenAI
import logging

class OpenAIProvider(LLMIntrface):

    def __init__(self, api_key: str, api_url: str = None,
                 default_input_max_characters: int = 1000,
                 default_generation_max_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):
        
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_tokens = default_generation_max_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_name = None

        self.embedding_model_name = None
        self.embedding_size = None

        self.client = OpenAI(api_key = self.api_key,
                             api_url = self.api_url)

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_name: str):
        self.generation_model_name = model_name


    def set_embedding_model(self, model_name: str, embedding_size: int):
        self.embedding_model_name = model_name
        self.embedding_size = embedding_size


    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()


    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                       temperature: float = None ):
        
        if not self.client:
            self.logger.error("OpenAI client wasn't set")
            return None
        
        if not self.generation_model_name:
            self.logger.error("Generation model for OpenAI wasn't set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value)
        )

        response = self.client.chat.completions.create(
            model = self.generation_model_name,
            messages= chat_history,
            max_tokens= max_output_tokens,
            temperature= temperature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generation text with OpenAI")

        return response.choices[0].message["content"]


    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }
 

    def embed_text(self, text: str, document_type: str = None):

        if not self.client:
            self.logger.error("OpenAI client wasn't set")
            return None
        
        if not self.embedding_model_name:
            self.logger.error("Embedding model for OpenAI wasn't set")
            return None

        response = self.client.embeddings.create(
            model = self.embedding_model_name,
            input = text
        )

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            return None

        return response.data[0].embedding
