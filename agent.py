
import os 
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from tools import tools

Path("data").mkdir(exist_ok=True)



# Update default and allowed models to use Gemini 2.5
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

ALLOWED_MODELS = {
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite", # Included the lite version if needed
    "gemini-3.5-flash-image", # Included the lite version if needed
    "gemini-2.5-flash",      # Kept for fallback compatibility 
    "gemini-3.7-flash"
}



SYSTEM_PROMPT = """
You are a helpful Agentic AI assistant named ChatsGPT similar to ChatGPT.

You can:
1. Answer normal questions.
2. Use tools when needed.
3. Search uploaded documents using the RAG tool.
4. Search the web for latest/current information using Tavily Search.
5. Remember important user information using the memory tool.
6. Recall memory when useful.
7. Use calculator for math.

Rules:
- If the user asks about latest news, current events, recent updates, today's information, current prices, current people, current versions, new releases, or anything time-sensitive, use Tavily Search.
- If the user asks about an uploaded document, use search_uploaded_documents.
- If the user asks you to remember something, use remember_this.
- If the user asks about previous preferences or saved facts, use recall_memory.
- Use calculator for math questions.
- When using web search, summarize clearly and mention that the answer is based on web search results.
- Be clear, helpful, and concise.
"""

def normalize_model_name(model_name:str)->str:
    """
    Normalize the model name to match the allowed models.
    If the model name is not in the allowed list, return the default model.
    """
    if not model_name:
        return DEFAULT_MODEL
    
    if model_name in ALLOWED_MODELS:
        return model_name
    else:
        return DEFAULT_MODEL


def build_agent(model_name:str):
    """
    Build one Langgraph agent for a selected Gemini model
    """

    selected_model = normalize_model_name(model_name)

    llm=ChatGoogleGenerativeAI(model=selected_model, temperature=0.2, max_output_tokens=1024,streaming=True)

    llm_with_tools=llm.bind_tools(tools)

    def chatbot_node(state:MessagesState):
        messages =[SystemMessage(content=SYSTEM_PROMPT)]+state['messages']
        response = llm_with_tools.invoke(messages)
        return {
            "messages":[response]
        }

    tool_node=ToolNode(tools)

    workflow=StateGraph(MessagesState)

    workflow.add_node("chatbot",chatbot_node)
    workflow.add_node("tools",tool_node)

    workflow.add_edge(START,"chatbot")
    workflow.add_conditional_edges("chatbot",tools_condition)
    workflow.add_edge("tools","chatbot")


    conn=sqlite3.connect("data/agent_checkpoint.sqlite3",check_same_thread=False)
    checkpointer=SqliteSaver(conn)

    return workflow.compile(checkpointer=checkpointer)


_AGENT_CACHE={}



def get_agent(model_name: str | None = None):
    """
    Return cached LangGraph agent for selected model.
    If not created yet, create it once and reuse it.
    """

    selected_model = normalize_model_name(model_name)

    if selected_model not in _AGENT_CACHE:
        _AGENT_CACHE[selected_model] = build_agent(selected_model)

    return _AGENT_CACHE[selected_model]