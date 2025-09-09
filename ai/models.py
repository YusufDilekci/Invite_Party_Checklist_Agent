from typing import Optional, List, Dict, Any
from pydantic import BaseModel


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