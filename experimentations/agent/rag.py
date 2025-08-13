from models.llm import open_ai_llm
from models.embedding import open_ai_embed_model
from exception.exceptions import format_exception
import json
from langchain_core.messages import HumanMessage
from prompt_library.rag_sys_msg import rag_system_message
from data_ingestion.ingestion_pipeline import get_rag_chain
def rag_llm(human_message) -> dict:
    try:
        rag_chain = get_rag_chain()
        answer = rag_chain.invoke({"question": human_message})
        return {"answer": answer}
        
    except Exception as e:
        error_details = format_exception(e)
        return error_details