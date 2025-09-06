from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from tools import tools
from prompts import get_system_prompt
from langgraph.types import Command, interrupt
from dotenv import load_dotenv
import json
load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


checkpointer = InMemorySaver()
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    messages = state["messages"]
    
    if not messages or not any(isinstance(msg, SystemMessage) for msg in messages):
        system_message = SystemMessage(content=get_system_prompt())
        messages = [system_message] + messages
    
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}

def should_continue(state: State):
    """Determine the next step based on the last message."""
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"

    return END

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    should_continue,
    {"tools": "tools", END: END}
)

graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile(checkpointer=checkpointer)


def print_event_info(event, event_type="Event"):
    """Helper function to print event information in a structured way."""
    if "messages" in event:
        messages = event["messages"]
        if messages:
            last_message = messages[-1]
            
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                print(f"\n🔧 Tool Calls Requested:")
                for tool_call in last_message.tool_calls:
                    print(f"  • {tool_call['name']} (ID: {tool_call['id']})")
                    print(f"    Args: {tool_call['args']}")
            
            elif isinstance(last_message, ToolMessage):
                print(f"\n⚙️ Tool Response:")
                print(f"  Tool: {last_message.name}")
                # Truncate long responses for readability
                content = last_message.content
                if len(content) > 200:
                    content = content[:200] + "..."
                print(f"  Content: {content}")
            
            elif hasattr(last_message, 'content') and last_message.content:
                # Only print AI responses, not human messages
                if last_message.__class__.__name__ == 'AIMessage':
                    print(f"\n🤖 Assistant: {last_message.content}")


def stream_graph_updates(user_input: str, thread_id: str = "1"):
    """
    Stream graph updates for a given user input with enhanced formatting.
    
    Args:
        user_input: The user's message
        thread_id: Thread ID for conversation persistence
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n💭 Processing your request...")
    
    user_message = HumanMessage(content=user_input)
    
    try:
        # Stream the response
        events = list(graph.stream(
            {"messages": [user_message]}, 
            config=config,
            stream_mode="values"
        ))
        
        # Process events and show progress
        for i, event in enumerate(events):
            print_event_info(event, f"Step {i+1}")
        
        # Get the final state to display the complete conversation
        final_state = graph.get_state(config)
        if final_state.values and 'messages' in final_state.values:
            final_message = final_state.values['messages'][-1]
            if hasattr(final_message, 'content') and final_message.__class__.__name__ == 'AIMessage':
                print(f"\n✨ Final Response:")
                print(f"{final_message.content}")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print("Please try again or contact support if the issue persists.")


def resume_from_interrupt(response_data: str, thread_id: str = "1"):
    """
    Resume execution after a human-in-the-loop interruption.
    
    Args:
        response_data: The human's response to the query
        thread_id: Thread ID for conversation persistence
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n🔄 Resuming execution with your input...")
    

    human_command = Command(resume={"data": response_data})
    
    try:
        events = list(graph.stream(human_command, config, stream_mode="values"))
        
        for i, event in enumerate(events):
            print_event_info(event, f"Resume Step {i+1}")
        

        final_state = graph.get_state(config)
        if final_state.values and 'messages' in final_state.values:
            final_message = final_state.values['messages'][-1]
            if hasattr(final_message, 'content') and final_message.__class__.__name__ == 'AIMessage':
                print(f"\n✨ Final Response:")
                print(f"{final_message.content}")
                
    except Exception as e:
        print(f"\n❌ Error during resume: {str(e)}")


def check_for_interruption(thread_id: str = "1"):
    """
    Check if the graph is waiting for human input.
    
    Args:
        thread_id: Thread ID to check
        
    Returns:
        bool: True if waiting for human input, False otherwise
    """
    config = {"configurable": {"thread_id": thread_id}}
    try:
        state = graph.get_state(config)
        return state.next == ('tools',) and state.tasks
    except:
        return False


def show_conversation_history(thread_id: str = "1", max_messages: int = 10):
    """
    Display recent conversation history.
    
    Args:
        thread_id: Thread ID to check
        max_messages: Maximum number of messages to show
    """
    config = {"configurable": {"thread_id": thread_id}}
    try:
        state = graph.get_state(config)
        if state.values and 'messages' in state.values:
            messages = state.values['messages'][-max_messages:]
            
            print(f"\n📜 Recent Conversation History (Thread: {thread_id}):")
            print("=" * 60)
            
            for i, msg in enumerate(messages, 1):
                if isinstance(msg, HumanMessage):
                    print(f"{i}. 👤 You: {msg.content}")
                elif isinstance(msg, SystemMessage):
                    print(f"{i}. 🎯 System: [System prompt configured]")
                elif hasattr(msg, 'content') and msg.__class__.__name__ == 'AIMessage':
                    content = msg.content if len(msg.content) <= 100 else msg.content[:100] + "..."
                    print(f"{i}. 🤖 Assistant: {content}")
                elif isinstance(msg, ToolMessage):
                    print(f"{i}. ⚙️ Tool ({msg.name}): [Tool execution completed]")
            print("=" * 60)
        else:
            print(f"\n📜 No conversation history found for thread {thread_id}")
    except Exception as e:
        print(f"\n❌ Error retrieving history: {str(e)}")

