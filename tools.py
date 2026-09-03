import math
from dotenv import load_dotenv
from httpx2 import query
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from database import save_memory, search_memory
from rag import retrieve_from_rag


load_dotenv()

CURRENT_THREAD_ID="default_thread"

def set_current_thread_id(thread_id:str):
    """
    Set the current thread ID for the session.
    """
    global CURRENT_THREAD_ID
    CURRENT_THREAD_ID = thread_id

web_search=TavilySearch(
    max_results=5,
    topic="general",
    search_depth="advanced"
)

@tool
def calculator(expression: str) -> str:
    """
    A simple calculator tool that evaluates mathematical expressions.
    """
    try:
        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": None}, {"math": math})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


@tool
def search_uploaded_documents(query:str)->str:
    """
    A tool to search uploaded documents using RAG (Retrieval-Augmented Generation).
    """
    return retrieve_from_rag(
        query=query,
        thread_id=CURRENT_THREAD_ID
    )

@tool
def remember_this(memory:str)->str:
    """
    A tool to remember important user information.
    """
    return save_memory(
        thread_id=CURRENT_THREAD_ID,
        memory=memory
    )


@tool
def recall_memory(query:str)->str:
    """
    A tool to recall previously remembered information.
    """
    return search_memory(
        thread_id=CURRENT_THREAD_ID,
        query=query
    )


tools=[
    web_search,
    calculator,
    search_uploaded_documents,
    remember_this,
    recall_memory
]