import os
from dotenv import load_dotenv

load_dotenv()


class EmbeddingFactory:
    def __init__(self):
        self.embedding_type = os.getenv('EMBEDDING_TYPE')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_embedding_model = os.getenv('EMBEDDING_MODEL')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL')
        self.ollama_embedding_model = os.getenv('OLLAMA_EMBEDDING_MODEL')
        self.embedding_models = {}
    
    def create_embedding(self, embedding_type: str = ""):
        embedding_type = embedding_type.lower() or self.embedding_type.lower()
        
        if embedding_type in self.embedding_models:
            return self.embedding_models[embedding_type]

        if embedding_type == 'openai':
            from langchain_openai import OpenAIEmbeddings
            embedding_model = OpenAIEmbeddings(
                model=self.openai_embedding_model,
                api_key=self.openai_api_key
            )
        elif embedding_type == 'ollama':
            from langchain_ollama import OllamaEmbeddings
            embedding_model = OllamaEmbeddings(
                model=self.ollama_embedding_model,
                base_url=self.ollama_base_url
            )
        else:
            raise ValueError(f"Unsupported embedding type: {embedding_type}")
        
        self.embedding_models[embedding_type] = embedding_model
        return embedding_model