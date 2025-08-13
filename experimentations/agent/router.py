from models.llm import open_ai_llm
from exception.exceptions import format_exception
import json
from langchain_core.messages import HumanMessage
from prompt_library.router_sys_msg import router_system_message

def router_llm(human_message)->json: 
    try: 
        human_msg = human_message
        response = open_ai_llm.invoke([router_system_message]+human_msg)
        response_json = json.loads(response.content)
        print(response_json)
        return response_json
    except Exception as e:
        error_details = format_exception(e)
        return error_details
