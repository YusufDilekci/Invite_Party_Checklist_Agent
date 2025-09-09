from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from helper import get_conversation_history, process_chat_message
from models import ChatRequest, ChatResponse, ResumeRequest
from graph import check_for_interruption, graph



app = FastAPI(title="Party Planning Chatbot API", version="1.0.0")

# Add CORS middleware to allow Streamlit to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
