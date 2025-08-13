#IMPORTS

from typing import Annotated, Sequence, List, Literal, TypedDict
from pydantic import BaseModel, Field 
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from langgraph.types import Command 
from langgraph.graph import StateGraph, START, END, MessagesState
import uuid

from langgraph.graph.message import add_messages
import asyncio 
from dotenv import load_dotenv
import os 
from agent.request import request_llm
from agent.knowledgebase import data_fetcher
from prompt_library.merger_sys_msg import merger_system_message
load_dotenv()

import time
from langchain_openai import ChatOpenAI
from typing import Optional
from data_ingestion.ingestion_pipeline import get_rag_chain
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

route_system_message = """You are a customer service routing agent for Tata Capital. Your role is to analyze incoming customer messages and classify them into exactly one of four categories: QUERY, REQUEST, COMPLAINT or KNOWLEDGEBASE.
                                      
Category Definitions
                                      
QUERY
Messages seeking information about Tata Capital, the company, its services, policies, or general inquiries that can be answered using company documentation.
Characteristics:
Questions about company background, history, financial performance
Inquiries about services offered, eligibility criteria, interest rates
General information requests about policies, procedures, or terms
Educational questions about financial products
"What is...", "How does...", "Can you explain...", "Tell me about..."
Examples:
"What is Tata Capital's revenue for this year?"
"How does your personal loan process work?"
"What are the eligibility criteria for home loans?"
"Tell me about Tata Capital's business segments"
"What is the company's market position?"
                                    
REQUEST
Messages asking for specific documents, services, or actions to be performed on behalf of the customer.
Characteristics:
Explicit requests for documents (PAN, Aadhar, CIBIL score, statements, certificates)
Service requests (account opening, loan applications, updates)
Action items that require processing or delivery
"I need...", "Please send...", "Can you provide...", "I want to..."
Examples:
"I need my CIBIL score report"
"Please send me my PAN card copy"
"Can you provide my Aadhar document?"
"I want to request my loan statement"
"Please send the NOC certificate to my email"
"I need my account balance certificate"
                                     
COMPLAINT
Messages providing a ticket number for complaint processing and resolution. The system requires a valid ticket number to scrape complaint details and process sentiment analysis, categorization, and routing.
Characteristics:
Contains a ticket number (various formats: alphanumeric, numeric, with prefixes/suffixes)
References existing complaint or issue tracking
Requests status update or processing of logged complaint
May include phrases like "ticket number", "complaint ID", "reference number"
Customer wants to process or check status of previously logged complaint
Examples:
"Please process my complaint ticket number TC123456"
"My ticket ID is COMP2024001, please update"
"I have complaint reference number 789012, can you check status?"
"Ticket: TC-2024-0456 needs processing"
"My complaint number is 123456789"
"Reference ID: REF789 - please resolve this issue"
                                      
KNOWLEDGEBASE
Messages requesting analytics, insights, reports, or data analysis from the customer support ticket database (QRCKnowledgeBase). These involve querying historical ticket data for business intelligence, performance metrics, trends, and operational insights.
Characteristics:
Requests for analytics, reports, or data insights from ticket database
Questions about ticket volumes, trends, patterns, or statistics
Month-to-Date (MTD), Year-to-Date (YTD), or period-based analysis requests
Sentiment analysis across tickets or time periods
Performance metrics for support teams or processes
Queries about ticket resolution times, escalation patterns, or customer satisfaction
Database analysis for business intelligence purposes
"Show me...", "Analyze...", "What are the trends...", "Generate report...", "MTD analysis..."
Examples:
"Show me MTD ticket volume analysis"
"What are the sentiment trends for this month?"
"Analyze complaint patterns by product category"
"Generate a report of open tickets by escalation level"
"What's the YTD resolution time for technical issues?"
"Show me customer satisfaction trends over the last quarter"
"Analyze ticket distribution by communication mode"
"What are the top 5 complaint categories this month?"
"Generate MTD analysis of negative sentiment tickets"
"Show me escalation patterns for Digital Banking vertical"
'**IMPORTANT** : Always check if current userquery can reslve previous pending query and accordingly frame the intent-message pairs,'
"""

#DECLARATIONS

api_key = os.getenv('OPENAI_API_KEY')
open_ai_llm = ChatOpenAI(model = 'gpt-4o-mini', api_key=api_key)

# ALL INTENTS

class IntentSchema(TypedDict):
    intent: Literal["Query", "Request", "Complaint", "knowledgebase"] = Field(
        default= "",
        description="One or more labels that define the nature of the user's input. "
                    "**Query** - for information-seeking questions about tatacapital, "
                    "**Request** - for demands or tasks processing " #actionable
                    "**Complaint** -  for expressions of dissatisfaction or issues, "
                    "and **knowledgebase** - if any question related to database or data retrieveal then use this intent."
    ) 
    message: str = Field(
        default= "",
        description="Extract message corresponding to the intent"
    )
    tone: Optional[Literal["Neutral", "Angry"]] = Field(
        default=None,
        description="REQUIRED for Complaint intent: Must be either 'Neutral' or 'Angry'. "
                    "This field indicates the emotional tone of complaints only. "
                    "Should not be provided for Query, Request, or Other intents."
    )


class IntentSchemas(TypedDict):
    intent_schema_list: List[IntentSchema] = Field(
        default=[],
        description="List of intent-message pairs, including complaints with tone where applicable"
    )

# Custom reducer for dictionaries - allows accumulation like add_messages but for dicts
def add_dicts(left: list[dict], right: list[dict]) -> list[dict]:
    """Custom reducer to accumulate dictionaries like add_messages does for messages"""
    if not left:
        return right
    if not right:
        return left
    return left + right

# for outer graph 
class MainIntent(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]
    active_intents : list[dict]
    completed_intents : Annotated[list[dict], add_dicts]  # Custom reducer for persistence
    incompleted_intents : Annotated[list[dict], add_dicts]  # Custom reducer for persistence
    sub_response : list[str]
    active_state : str


class subIntent(TypedDict):
    uid : str
    intent : str
    message : str
    tone : str
    output : str
    active_state : str
    completed : bool = False

# dummy definations

async def query_processor(state : subIntent)-> subIntent:
        print('fetching....RAG')
        qa =await get_rag_chain()
        print('fetched....RAG')
        response =await qa.ainvoke(state['message'])

        return {'output' : response['result'], 'completed' : True,  'message' : state['message']}

async def request_processor(state : subIntent)-> subIntent:
        human_msg = state['message']

        response =request_llm(human_msg)

        if "message" in response:
            
            result = response["message"]
            return {'output' : result,'completed' : False, 'message' : state['message']}
        
        else:
            
            application_no = response["application_no"]
            process_name = response["process_name"]
            requested_document =    response["requested_document"]
            result = {"Webtop_Id": application_no, 
                    "Process_Name": "NA", 
                    "DocNames": requested_document,
                    "Task_Name": process_name,
                    "Work_Id": 123}
            result = f"SR-1320099902 has been raised for the Ops Team in the CRM. The {requested_document} for loan application {application_no} will be sent to the customer's registered email address. Overall Sentiment seems to be 'Neutral'"
            return {'output' : result,'completed' : True,  'message' : state['message']}


async def complaint_processor(state : subIntent)-> subIntent:
        message = state['message']
        tone = state['tone']

        print(f'complaint : {message} , tone : {tone}')
        

        return {'output' : 'ticket against your complaint has been raised your issue will be resolved at priority','completed' : True, 'message' : state['message']}

async def knowledge_fetcher(state : subIntent)-> subIntent:

        print('fetching data.....')

        result =await data_fetcher(state['message'])

        return {'output' : result,'completed' : True, 'message' : state['message']}

def divertor(state : subIntent)-> subIntent:
    state['active_state'] = 'divertor'
    
    if state['intent'].lower() == 'query':
           
        return Command(
                update = {'active_state' : 'query_processor'},
                goto = 'query_processor'
        )

    elif state['intent'].lower() == 'request':
           
        return Command(
                update = {'active_state' : 'request_processor'},
                goto = 'request_processor'
        )
    
    elif state['intent'].lower() == 'complaint':
           
        return Command(
                update = {'active_state' : 'complaint_processor'},
                goto = 'complaint_processor'
        )
    
    elif state['intent'].lower() == 'knowledgebase':
           
        return Command(
                update = {'active_state' : 'knowledge_fetcher'},
                goto = 'knowledge_fetcher'
        )


#inner graph

SubGraph = StateGraph(subIntent)

SubGraph.add_node('divertor',divertor)
SubGraph.add_node('query_processor',query_processor)
SubGraph.add_node('request_processor',request_processor)
SubGraph.add_node('complaint_processor',complaint_processor)
SubGraph.add_node('knowledge_fetcher',knowledge_fetcher)

SubGraph.add_edge(START,'divertor')

ready_subgraph = SubGraph.compile()

#DEFINATIONS

async def handle_request(message: dict):
    print(f"Starting main node...for : {message.get('intent')}")

    input = {'uid': message.get('uid'),'intent': message.get('intent') ,'message': message.get('message'), 'tone' : message.get('tone')}

    sub_graph_retrieved_state = await ready_subgraph.ainvoke(input)
    return {'uid':sub_graph_retrieved_state['uid'], 'message' : sub_graph_retrieved_state['message'],
            'output':sub_graph_retrieved_state['output'],'completed' : sub_graph_retrieved_state['completed']}


def intent_classifier(state : MainIntent) -> MainIntent:
    print("Current incompleted intents:", state.get('incompleted_intents', []))
    print('fresh talk')
    
    # Build context for the LLM including previous incomplete intents
    context_messages = ['system message : ' + route_system_message]
    
    # Add previous pending queries if they exist
    if state.get('incompleted_intents'):
        context_messages.extend([
            f"previous pending queries : {data.get('message')}" 
            for data in state['incompleted_intents']
        ])
    
    # Add current user query
    context_messages.append('current user query : ' + state["messages"][-1].content)
    
    print("Context messages:", context_messages)
    
    response = open_ai_llm.with_structured_output(IntentSchemas).invoke(context_messages)
        
    active_intent_lists = response.get('intent_schema_list')

    for item in active_intent_lists:
        item['uid'] = str(uuid.uuid4())

    print("New active intents:", active_intent_lists)
    
    return Command(
        update = {
            'active_intents': active_intent_lists,
            'active_state' : 'intent_invoker'
        },
        goto = 'intent_invoker'
    )
    

async def intent_invoker(state : MainIntent)-> MainIntent:

    final_states = await asyncio.gather(*(handle_request(msg) for msg in state['active_intents']))

    print(f'final states : {final_states}') 

    # Separate completed and incompleted intents
    completed_intents = []
    incompleted_intents = []
    
    for data in final_states:
        if data['completed'] is True:
            completed_intents.append(data)
        else:
            incompleted_intents.append(data)

    goto = 'intent_merger'
    
    return Command(
        update = {
                'sub_response' : [data['output'] for data in final_states],
                'completed_intents': completed_intents,  # Will be added to existing list via add_dicts
                'incompleted_intents': incompleted_intents,  # Will be added to existing list via add_dicts
                'active_intents': [],  # Clear active intents after processing
                'active_state' : goto
        },
        goto = goto
    )

def intent_merger(state : MainIntent)-> MainIntent:

    output = f"""
        question: {state['messages'][-1].content}
        outputs generated:
        {chr(10).join(f"- {resp}" for resp in state['sub_response'])}
        """

    print(output)
    response = open_ai_llm.invoke([merger_system_message,output])

    # FIXED: Return the update in Command format
    return Command(
        update = {'messages': [AIMessage(response.content)]},
        goto = END
    )

#outer graph

graph = StateGraph(MainIntent)

graph.add_node('intent_classifier',intent_classifier)
graph.add_node('intent_invoker',intent_invoker)
graph.add_node('intent_merger',intent_merger)

graph.add_edge(START,'intent_classifier')

ready_graph = graph.compile(checkpointer = checkpointer)

# Test with multiple messages to demonstrate persistence
async def main():
    config = {'configurable':{'thread_id':'2'}}
    
    # First message
    print("=== FIRST MESSAGE ===")
    user_msg1 = 'i want to know about count open cases in database and send me loan agreement for appli'
    input1 = {
        'messages': [HumanMessage(content=user_msg1)], 
        'active_intents': [],
        'completed_intents': [],
        'incompleted_intents': []
    }

    try:
        graph_retrieved_state1 = await ready_graph.ainvoke(input1, config)
        print("First response completed")
        print("Incomplete intents after first message:", graph_retrieved_state1.get('incompleted_intents', []))
    except Exception as e:
        print(f"Error in first message: {e}")
        return

    # Second message - should have context of previous incomplete intents
    print("\n=== SECOND MESSAGE ===")
    user_msg2 = 'application number is ABC123456'
    input2 = {
        'messages': [HumanMessage(content=user_msg2)]
    }

    try:
        graph_retrieved_state2 = await ready_graph.ainvoke(input2, config)
        print("Second response completed")
        print("Final state messages:", [msg.content for msg in graph_retrieved_state2['messages']])
    except Exception as e:
        print(f"Error in second message: {e}")

# Uncomment to run
# await main()