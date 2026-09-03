import math
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch


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
    # Placeholder implementation for searching uploaded documents
    # In a real implementation, this would interface with a document retrieval system
    return f"Searching uploaded documents for: {query}"


@tool
def remember_this(memory:str)->str:
    """
    A tool to remember important user information.
    """
    # Placeholder implementation for remembering information
    # In a real implementation, this would store the memory in a database or memory system
    return f"Remembered: {memory}"


@tool
def recall_memory(query:str)->str:
    """
    A tool to recall previously remembered information.
    """
    # Placeholder implementation for recalling memory
    # In a real implementation, this would retrieve the memory from a database or memory system
    return f"Recalling memory for: {query}"


tools=[
    web_search,
    calculator,
    search_uploaded_documents,
    remember_this,
    recall_memory
]