from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime

# Import your existing app logic
from ai.app import stream_graph_updates, check_for_interruption, resume_from_interrupt, graph
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

app = FastAPI(title="Party Planning Chatbot API", version="1.0.0")

# Add CORS middleware to allow Streamlit to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "1"

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    status: str
    conversation_history: List[Dict[str, Any]]

class ResumeRequest(BaseModel):
    response_data: str
    thread_id: Optional[str] = "1"

# Helper function to extract messages from graph state
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

# Helper function to process chat and get final response
def process_chat_message(message: str, thread_id: str = "1") -> tuple[str, str]:
    """Process a chat message and return the final response and status."""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        user_message = HumanMessage(content=message)
        
        # Stream the response and collect events
        events = list(graph.stream(
            {"messages": [user_message]}, 
            config=config,
            stream_mode="values"
        ))
        
        # Check if we're waiting for human input (interruption)
        if check_for_interruption(thread_id):
            return "I need some additional information. Please provide more details.", "waiting_for_input"
        
        # Get the final state
        final_state = graph.get_state(config)
        if final_state.values and 'messages' in final_state.values:
            final_message = final_state.values['messages'][-1]
            if hasattr(final_message, 'content') and final_message.__class__.__name__ == 'AIMessage':
                return final_message.content, "completed"
        
        return "I'm sorry, I couldn't process your request. Please try again.", "error"
        
    except Exception as e:
        print(f"Error processing chat message: {e}")
        return f"An error occurred: {str(e)}", "error"

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Party Planning Chatbot API is running!", "status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for processing user messages.
    
    Args:
        request: ChatRequest containing message and optional thread_id
        
    Returns:
        ChatResponse with the assistant's response and conversation history
    """
    try:
        # Process the chat message
        response_text, status = process_chat_message(request.message, request.thread_id)
        
        # Get conversation history
        history = get_conversation_history(request.thread_id)
        
        return ChatResponse(
            response=response_text,
            thread_id=request.thread_id,
            status=status,
            conversation_history=history
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/resume")
async def resume_endpoint(request: ResumeRequest):
    """
    Resume conversation after human-in-the-loop interruption.
    
    Args:
        request: ResumeRequest containing response_data and thread_id
        
    Returns:
        ChatResponse with the continued conversation
    """
    try:
        # Check if there's actually an interruption to resume
        if not check_for_interruption(request.thread_id):
            raise HTTPException(status_code=400, detail="No interruption to resume")
        
        # Resume the conversation
        config = {"configurable": {"thread_id": request.thread_id}}
        from langgraph.types import Command
        
        human_command = Command(resume={"data": request.response_data})
        events = list(graph.stream(human_command, config, stream_mode="values"))
        
        # Get the final response
        final_state = graph.get_state(config)
        response_text = "Conversation resumed successfully."
        
        if final_state.values and 'messages' in final_state.values:
            final_message = final_state.values['messages'][-1]
            if hasattr(final_message, 'content') and final_message.__class__.__name__ == 'AIMessage':
                response_text = final_message.content
        
        # Get updated conversation history
        history = get_conversation_history(request.thread_id)
        
        return ChatResponse(
            response=response_text,
            thread_id=request.thread_id,
            status="completed",
            conversation_history=history
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resuming conversation: {str(e)}")

@app.get("/conversation/{thread_id}")
async def get_conversation(thread_id: str, max_messages: int = 10):
    """
    Get conversation history for a specific thread.
    
    Args:
        thread_id: Thread ID to retrieve
        max_messages: Maximum number of messages to return
        
    Returns:
        Conversation history
    """
    try:
        history = get_conversation_history(thread_id, max_messages)
        return {
            "thread_id": thread_id,
            "conversation_history": history,
            "message_count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {str(e)}")

@app.get("/status/{thread_id}")
async def get_thread_status(thread_id: str):
    """
    Check if a thread is waiting for human input.
    
    Args:
        thread_id: Thread ID to check
        
    Returns:
        Status information
    """
    try:
        is_waiting = check_for_interruption(thread_id)
        return {
            "thread_id": thread_id,
            "waiting_for_input": is_waiting,
            "status": "waiting_for_input" if is_waiting else "ready"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking thread status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
