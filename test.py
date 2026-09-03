from agent import get_agent
from langchain_core.messages import SystemMessage,HumanMessage
from database import init_db



init_db()

agent=get_agent("gemini-3.5-flash-lite")

config={
    "configurable":{
        "thread_id":"test_thread_1"
    }
}


for message_chunk , metadata in agent.stream(
    {'messages':[HumanMessage(content="Do you remember my name?")]},
    config=config,
    stream_mode='messages'
):
    if message_chunk.content:
        print(message_chunk.content,end='',flush=True)