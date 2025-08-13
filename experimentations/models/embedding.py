from config.configuration import Config
from langchain_openai import OpenAIEmbeddings
from exception.exceptions import format_exception
try:
    open_ai_embed_model = OpenAIEmbeddings(model=Config.EMBEDDING_MODEL,
                         openai_api_key = Config.OPENAI_API_KEY)
    print('embedding model')
except Exception as e:
    error_details = format_exception(e)
    print(f"Error initializing OpenAI LLM: {error_details}")
    open_ai_llm = None