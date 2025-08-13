from models.llm import open_ai_llm
from exception.exceptions import format_exception
import json
from langchain_core.messages import HumanMessage
from prompt_library.request_sys_msg import request_system_message
from typing import TypedDict
from pydantic import Field

class requestState(TypedDict):
    application_no : str = Field(description = "application_no should be exactly the alphanumeric code the user provides (drop any “appl” prefix).")
    process_name : str = Field(description = "by default the value will be : 'document_download' ")
    requested_document : str = Field(description = "requested_document should be a concise, lowercase description (e.g., “loan agreement”).")

def request_llm(human_message) -> dict:
    try:
        print('starting reuest chain')
        human_msg = [human_message]
        # print("before lm")
        response = open_ai_llm.with_structured_output(requestState).invoke([request_system_message] + human_msg)
        
        print(f"appln no : {response.get("application_no")}, process name : {response.get("process_name")}, doc : {response.get("requested_document")}")
        # response_json = json.loads(response.content)
        if response.get("application_no") is not None and response.get("process_name") is not None and response.get("requested_document") is not None:
            return {
                "application_no":response.get("application_no"),
                "process_name": response.get("process_name"),
                "requested_document":response.get("requested_document")
                }
        
        else:
            return {"message": "Please provide the application number to proceed with the document request."}
    except Exception as e:
        error_details = format_exception(e)
        return error_details
    


# from models.llm import open_ai_llm
# from exception.exceptions import format_exception
# import json
# from langchain_core.messages import HumanMessage
# from prompt_library.request_sys_msg import request_system_message

# def request_llm(human_message) -> dict:
#     try:
#         # human_msg = HumanMessage(content=human_message)
#         human_msg = human_message
#         response = open_ai_llm.invoke([request_system_message] + human_msg)
#         # print(f'after llm invocation data recieved :{response.content}')
#         response_json = json.loads(response.content)
#         return response_json
#     except Exception as e:
#         error_details = format_exception(e)
#         return error_details