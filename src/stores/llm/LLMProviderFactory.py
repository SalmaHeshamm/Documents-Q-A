from .LLMEnums import LLMEnums
from .providers import OpenAIProvider, CohereProvider, GroqProvider

class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                   api_key= self.config.OPENAI_API_KEY,
                   api_url= self.config.OPENAI_API_URL,
                   default_input_max_characters=self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                   default_generation_temperature=self.config.GENERATION_DEFAULT_MAX_TEMPRATURE,
                   default_generation_max_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,           
            )

        if provider == LLMEnums.COHERE.value:
            return CohereProvider(
                api_key= self.config.COHERE_API_KEY,
                default_input_max_characters=self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_MAX_TEMPRATURE,
                default_generation_max_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,     
            )

        if provider == LLMEnums.GROQ.value:
            return GroqProvider(
                api_key= self.config.GROQ_API_KEY,
                default_input_max_characters=self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_MAX_TEMPRATURE,
                default_generation_max_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,                              
            )

        return None

