from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
load_dotenv()


checkpointer = InMemorySaver()

model = init_chat_model(
    "openai:gpt-4o-mini",
    temperature=0,
)

agent = create_react_agent(
    model=model,
    tools=[],
    checkpointer=checkpointer

)

config = {"configurable": {"thread_id": "1"}}
response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather today?"}]},
    config
    )
print(response['messages'][1].content)
