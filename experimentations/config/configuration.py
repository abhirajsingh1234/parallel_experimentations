import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
    DB_CONN_STR=os.getenv("DB_CONN_STR")
    FILE_PATH=os.getenv("FILE_PATH")
    MODEL="gpt-4o-mini"
    TEMPERATURE=0.0
    EMBEDDING_MODEL="text-embedding-3-large"
    

