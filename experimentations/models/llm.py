from config.configuration import Config
from langchain_openai import ChatOpenAI
from exception.exceptions import format_exception
try:
    open_ai_llm = ChatOpenAI(
        model_name = Config.MODEL,
        temperature = Config.TEMPERATURE,
        openai_api_key = Config.OPENAI_API_KEY
    )
except Exception as e:
    error_details = format_exception(e)
    print(f"Error initializing OpenAI LLM: {error_details}")
    open_ai_llm = None