from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from datetime import datetime
from graph import check_for_interruption, graph


def get_conversation_history(thread_id: str = "1", max_messages: int = 10) -> List[Dict[str, Any]]:
    """Extract conversation history from the graph state."""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = graph.get_state(config)
        
        if not state.values or 'messages' not in state.values:
            return []
        
        messages = state.values['messages'][-max_messages:]
        history = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({
                    "type": "human",
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                })
            elif isinstance(msg, AIMessage):
                history.append({
                    "type": "assistant", 
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                })
            elif isinstance(msg, SystemMessage):
                history.append({
                    "type": "system",
                    "content": "[System message]",
                    "timestamp": datetime.now().isoformat()
                })
            elif isinstance(msg, ToolMessage):
                history.append({
                    "type": "tool",
                    "content": f"Tool ({msg.name}) executed",
                    "timestamp": datetime.now().isoformat()
                })
        
        return history
    except Exception as e:
        print(f"Error getting conversation history: {e}")
        return []

def process_chat_message(message: str, thread_id: str = "1") -> tuple[str, str]:
    """Process a chat message and return the final response and status."""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        user_message = HumanMessage(content=message)
        
        events = list(graph.stream(
            {"messages": [user_message]}, 
            config=config,
            stream_mode="values"
        ))
        
        if check_for_interruption(thread_id):
            return "I need some additional information. Please provide more details.", "waiting_for_input"
        
        final_state = graph.get_state(config)
        if final_state.values and 'messages' in final_state.values:
            final_message = final_state.values['messages'][-1]
            if hasattr(final_message, 'content') and final_message.__class__.__name__ == 'AIMessage':
                return final_message.content, "completed"
        
        return "I'm sorry, I couldn't process your request. Please try again.", "error"
        
    except Exception as e:
        print(f"Error processing chat message: {e}")
        return f"An error occurred: {str(e)}", "error"