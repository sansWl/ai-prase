import os
from dotenv import load_dotenv

load_dotenv()


class LLMsFactory:
    def __init__(self):
        self.llm_type = os.getenv('LLM_TYPE')
        self.openai_model = os.getenv('OPENAI_MODEL')
        self.openai_temperature = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_base_url = os.getenv('OPENAI_BASE_URL')
        self.ollama_model = os.getenv('OLLAMA_MODEL')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL')
        self.ollama_system_prompt = os.getenv('OLLAMA_SYSTEM_PROMPT', '你是一个专业的助手')
        self._llms = {}


    def create_llm(self, llm_type: str="" ):
        llm_type = llm_type.strip().lower() or self.llm_type.strip().lower()
        
        if llm_type in self._llms:
            return self._llms[llm_type]

        if llm_type == 'openai':
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=self.openai_model,
                temperature=self.openai_temperature,
                base_url=self.openai_base_url,
                api_key=self.openai_api_key
            )
        elif llm_type == 'ollama':
            from langchain_ollama import ChatOllama
            llm = ChatOllama(
                model=self.ollama_model,
                base_url=self.ollama_base_url,
                system=self.ollama_system_prompt
            )
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
        
        self._llms[llm_type] = llm
        return llm