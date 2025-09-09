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
from langgraph.prebuilt import create_react_agent
import os
load_dotenv()



class State(TypedDict):
    messages: Annotated[list, add_messages]


checkpointer = InMemorySaver()


llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

max_iterations = 3
recursion_limit = 2 * max_iterations + 1
agent = create_react_agent(
    model=llm,  
    tools=tools,  
    prompt=get_system_prompt(),
    
)

def chatbot(state: State):
    messages = state["messages"]
    response = agent.invoke({"messages": messages},{"recursion_limit": recursion_limit})

    return response


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile(checkpointer=checkpointer)


def stream_graph_updates(user_input: str, thread_id: str = "1"):
    """
    Stream graph updates for a given user input with enhanced formatting.
    
    Args:
        user_input: The user's message
        thread_id: Thread ID for conversation persistence
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n💭 Processing your request...")

    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
        


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
        
        events = graph.stream(
            human_command,
            config,
            stream_mode="values",
        )
        for event in events:
            if "messages" in event:
                event["messages"][-1].pretty_print()

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

def main():
    """Enhanced main function with better user experience."""
    print("🎉 Party Planning Assistant - Enhanced with Memory & Human-in-the-Loop!")
    print("=" * 70)
    print("Features:")
    print("• 💾 Remembers entire conversation history")
    print("• 🔧 Can search party invites and web information")
    print("• 🤝 Can request human assistance for complex decisions")
    print("• 📜 View conversation history with 'history'")
    print("• 🔄 Resume interrupted conversations")
    print("• 🆔 Use different thread IDs for separate conversations")
    print("• 📊 LLM calls are being traced with Langfuse")
    print("\nCommands:")
    print("• 'quit', 'exit', 'q' - Stop the assistant")
    print("• 'history' - Show recent conversation")
    print("• 'thread:ID' - Switch to thread ID (e.g., 'thread:party1')")
    print("• 'resume:your response' - Resume after human assistance request")
    print("=" * 70)
    
    current_thread = "1"
    
    while True:
        try:
            user_input = input(f"\n👤 You (Thread {current_thread}): ").strip()
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n👋 Thanks for using Party Planning Assistant! Goodbye!")
                break
            
            elif user_input.lower() == "history":
                show_conversation_history(current_thread)
                continue
            
            elif user_input.lower().startswith("thread:"):
                new_thread = user_input[7:].strip()
                if new_thread:
                    current_thread = new_thread
                    print(f"\n🔄 Switched to thread: {current_thread}")
                else:
                    print("\n❌ Please provide a thread ID (e.g., 'thread:party1')")
                continue
            
            elif user_input.lower().startswith("resume:"):
                response_data = user_input[7:].strip()
                if response_data and check_for_interruption(current_thread):
                    resume_from_interrupt(response_data, current_thread)
                elif not response_data:
                    print("\n❌ Please provide your response (e.g., 'resume:I think we should invite John')")
                else:
                    print("\n💡 No interruption detected. Please continue with normal conversation.")
                continue
            
            elif not user_input:
                print("\n💡 Please enter a message or command.")
                continue
            
            if check_for_interruption(current_thread):
                print(f"\n⏸️ This conversation is waiting for human input.")
                print(f"Use 'resume:your response' to continue, or start a new thread.")
                continue
            
            stream_graph_updates(user_input, current_thread)
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("💡 Try continuing the conversation or restart if issues persist.")


if __name__ == "__main__":
    main()