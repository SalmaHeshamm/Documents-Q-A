from llm import LLMIntrface, CohereEnums, DocumentTypeEnum
import cohere
import logging

class CohereProvider(LLMIntrface):

    def __init__(self, api_key: str,
                 default_input_max_characters: int = 1000,
                 default_generation_max_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):
        
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_tokens = default_generation_max_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_name = None

        self.embedding_model_name = None
        self.embedding_size = None

        self.client = cohere.Client(api_key = self.api_key)

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_name: str):
        self.generation_model_name = model_name


    def set_embedding_model(self, model_name: str, embedding_size: int):
        self.embedding_model_name = model_name
        self.embedding_size = embedding_size


    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()
    

    def embed_text(self, text: str, document_type: str = None):

        if not self.client:
            self.logger.error("CoHere client wasn't set")
            return None
        
        if not self.embedding_model_name:
            self.logger.error("CoHere model for OpenAI wasn't set")
            return None

        input_type = CohereEnums.DOCUMENT

        if document_type == DocumentTypeEnum.QUERY:
            input_type = CohereEnums.QUERY

        response = self.client.embed(
            model= self.embedding_model_name,
            texts= [self.process_text(text)], 
            input_type= input_type,
            embedding_types= ['float']
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None

        return response.embeddings.float[0]


    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int = None,
                       temperature: float = None ):
        
        if not self.client.chat:
            self.logger.error("Cohere client wasn't set")
            return None
        
        if not self.generation_model_name:
            self.logger.error("Generation model for Cohere wasn't set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        response = self.client.chat(
            model = self.generation_model_name,
            chat_history = chat_history,
            message = self.process_text(prompt),
            temperature= temperature,
            max_tokens= max_output_tokens
        )

        if not response or not response.text:
            self.logger.error("Error while generating txt with CoHere")
            return None

        return response.text


    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.process_text(prompt)
        }


