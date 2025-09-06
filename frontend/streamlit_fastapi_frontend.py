import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configure the Streamlit page
st.set_page_config(
    page_title="🎉 Party Planning Assistant",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
FASTAPI_URL = "http://localhost:8000"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .feature-box {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B6B;
        margin: 0.5rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background-color: #F3E5F5;
        border-left: 4px solid #9C27B0;
    }
    .tool-message {
        background-color: #E8F5E8;
        border-left: 4px solid #4CAF50;
        font-size: 0.9rem;
    }
    .error-message {
        background-color: #FFEBEE;
        border-left: 4px solid #F44336;
        color: #C62828;
    }
    .success-message {
        background-color: #E8F5E8;
        border-left: 4px solid #4CAF50;
        color: #2E7D32;
    }
    .interrupt-box {
        background-color: #FFF3E0;
        border: 2px solid #FF9800;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_thread" not in st.session_state:
    st.session_state.current_thread = f"session_{int(time.time())}"
if "waiting_for_human" not in st.session_state:
    st.session_state.waiting_for_human = False
if "interrupt_query" not in st.session_state:
    st.session_state.interrupt_query = ""
if "processing" not in st.session_state:
    st.session_state.processing = False
if "pending_input" not in st.session_state:
    st.session_state.pending_input = None

def check_fastapi_connection():
    """Check if FastAPI backend is running."""
    try:
        response = requests.get(f"{FASTAPI_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_chat_message(message: str, thread_id: str):
    """Send a message to the FastAPI backend."""
    try:
        response = requests.post(
            f"{FASTAPI_URL}/chat",
            json={"message": message, "thread_id": thread_id},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

def resume_conversation(response_data: str, thread_id: str):
    """Resume conversation after interruption."""
    try:
        response = requests.post(
            f"{FASTAPI_URL}/resume",
            json={"response_data": response_data, "thread_id": thread_id},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Resume error: {str(e)}"}

def check_thread_status(thread_id: str):
    """Check if thread is waiting for human input."""
    try:
        response = requests.get(f"{FASTAPI_URL}/status/{thread_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"waiting_for_input": False}
    except:
        return {"waiting_for_input": False}

# Sidebar for thread management and controls
with st.sidebar:
    st.markdown("## 🎛️ Control Panel")
    
    # Connection status
    if check_fastapi_connection():
        st.success("✅ FastAPI Backend Connected")
    else:
        st.error("❌ FastAPI Backend Disconnected")
        st.info("Run: `uvicorn fastapi_backend:app --reload` to start the backend")
    
    # Thread management
    st.markdown("### 🧵 Thread Management")
    new_thread = st.text_input("Thread ID", value=st.session_state.current_thread)
    if st.button("Switch Thread") and new_thread:
        st.session_state.current_thread = new_thread
        st.session_state.messages = []
        st.rerun()
    
    st.markdown(f"**Current Thread:** `{st.session_state.current_thread}`")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    if st.button("🗂️ Show History"):
        try:
            response = requests.get(f"{FASTAPI_URL}/conversation/{st.session_state.current_thread}")
            if response.status_code == 200:
                data = response.json()
                history = data.get("conversation_history", [])
                st.session_state.messages = []
                for msg in history[-10:]:  # Last 10 messages
                    if msg["type"] in ["human", "assistant"]:
                        role = "user" if msg["type"] == "human" else "assistant"
                        st.session_state.messages.append({
                            "role": role,
                            "content": msg["content"],
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        })
                st.rerun()
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("🔄 New Session"):
        st.session_state.current_thread = f"session_{int(time.time())}"
        st.session_state.messages = []
        st.session_state.waiting_for_human = False
        st.rerun()
    
    # Features info
    st.markdown("### ✨ Features")
    st.markdown("""
    - 💾 **Persistent Memory**
    - 🔍 **Party Guest Search**
    - 🌐 **Web Search**
    - 🤝 **Human Assistance**
    - 📧 **Contact Management**
    """)

# Main content area
st.markdown('<h1 class="main-header">🎉 Party Planning Assistant</h1>', unsafe_allow_html=True)

# Feature highlights
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="feature-box">
        <h4>🧠 Smart Memory</h4>
        <p>Remembers all conversations and can reference previous discussions</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h4>🔧 Powerful Tools</h4>
        <p>Search party databases, web information, and get human assistance</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-box">
        <h4>🎯 Party Focus</h4>
        <p>Specialized for guest lists, invitations, and party organization</p>
    </div>
    """, unsafe_allow_html=True)

# Check for interruption status - API call to check thread status
try:
    thread_status = check_thread_status(st.session_state.current_thread)
    is_interrupted = thread_status.get("waiting_for_input", False)
    if is_interrupted and not st.session_state.waiting_for_human:
        st.session_state.waiting_for_human = True
        st.session_state.interrupt_query = "Human assistance requested for complex decision"
except Exception:
    is_interrupted = False

# Human-in-the-loop interface
if st.session_state.waiting_for_human:
    st.markdown("""
    <div class="interrupt-box">
        <h3>🤝 Human Assistance Needed</h3>
        <p>The assistant is requesting your input for a complex decision.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Query:** {st.session_state.interrupt_query}")
    
    human_response = st.text_area(
        "Your Response:", 
        placeholder="Please provide your guidance or decision...",
        key="human_input"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Submit Response") and human_response:
            with st.spinner("Processing your response..."):
                try:
                    # Resume the conversation via API
                    result = resume_conversation(human_response, st.session_state.current_thread)
                    if "error" not in result:
                        st.session_state.waiting_for_human = False
                        st.session_state.interrupt_query = ""
                        st.success("Response submitted successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error: {result['error']}")
                except Exception as e:
                    st.error(f"Error submitting response: {str(e)}")
    
    with col2:
        if st.button("❌ Cancel"):
            st.session_state.waiting_for_human = False
            st.session_state.interrupt_query = ""
            st.rerun()

def add_user_message(user_input):
    """Add user message without triggering rerun."""
    st.session_state.messages.append({
        "role": "user", 
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

def process_ai_response(user_input):
    """Process AI response after user message is shown."""
    try:
        # Send message to FastAPI backend
        result = send_chat_message(user_input, st.session_state.current_thread)
        
        if "error" in result:
            assistant_response = f"I encountered an error: {result['error']}. Please try again."
        else:
            assistant_response = result.get("response", "No response received")
            
            # Check if we're now waiting for human input
            if result.get("status") == "waiting_for_input":
                st.session_state.waiting_for_human = True
                st.session_state.interrupt_query = "Human assistance requested"
        
        # Add assistant response to chat
        if assistant_response:
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_response,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
        
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"I'm sorry, I encountered an error: {str(e)}. Please try again.",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    
    # Clear processing state
    st.session_state.processing = False
    if "pending_input" in st.session_state:
        st.session_state.pending_input = None

# Chat interface
st.markdown("## 💬 Chat with Your Party Assistant")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        timestamp = message.get("timestamp", "")
        
        if role == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 You ({timestamp}):</strong><br>
                {content}
            </div>
            """, unsafe_allow_html=True)
        elif role == "assistant":
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistant ({timestamp}):</strong><br>
                {content}
            </div>
            """, unsafe_allow_html=True)
        elif role == "tool":
            st.markdown(f"""
            <div class="chat-message tool-message">
                <strong>🔧 Tool: {message.get('tool_name', 'Unknown')} ({timestamp}):</strong><br>
                {content[:200]}{"..." if len(content) > 200 else ""}
            </div>
            """, unsafe_allow_html=True)

# Chat input
if not st.session_state.waiting_for_human:
    user_input = st.chat_input("Ask about party planning, guest lists, or anything else...")
    
    if user_input:
        # Add user message immediately
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # Show the user message immediately
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You ({datetime.now().strftime("%H:%M:%S")}):</strong><br>
            {user_input}
        </div>
        """, unsafe_allow_html=True)
        
        # Process AI response with spinner
        with st.spinner("🤔 Thinking..."):
            try:
                result = send_chat_message(user_input, st.session_state.current_thread)
                
                if "error" in result:
                    assistant_response = f"I encountered an error: {result['error']}. Please try again."
                else:
                    assistant_response = result.get("response", "No response received")
                    
                    if result.get("status") == "waiting_for_input":
                        st.session_state.waiting_for_human = True
                        st.session_state.interrupt_query = "Human assistance requested"
                
                # Add assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"I'm sorry, I encountered an error: {str(e)}. Please try again.",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
        
        # Refresh to show complete conversation
        st.rerun()

# Check if we need to process AI response for example buttons
if "example_processing" in st.session_state and st.session_state.example_processing:
    user_input = st.session_state.example_processing
    st.session_state.example_processing = None
    
    with st.spinner("🤔 Thinking..."):
        try:
            result = send_chat_message(user_input, st.session_state.current_thread)
            
            if "error" in result:
                assistant_response = f"I encountered an error: {result['error']}. Please try again."
            else:
                assistant_response = result.get("response", "No response received")
                
                if result.get("status") == "waiting_for_input":
                    st.session_state.waiting_for_human = True
                    st.session_state.interrupt_query = "Human assistance requested"
            
            # Add assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_response,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"I'm sorry, I encountered an error: {str(e)}. Please try again.",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
    
    st.rerun()

# Example prompts
st.markdown("## 💡 Example Prompts")
col1, col2 = st.columns(2)

with col1:
    if st.button("🎯 Who can come to my party?", disabled=st.session_state.waiting_for_human):
        user_input = "Who can come to my party?"
        # Add user message immediately
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        st.session_state.example_processing = user_input
        st.rerun()
    
    if st.button("📧 Give me email addresses", disabled=st.session_state.waiting_for_human):
        user_input = "Give me email addresses of potential guests"
        # Add user message immediately
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        st.session_state.example_processing = user_input
        st.rerun()

with col2:
    if st.button("👥 Search for family members", disabled=st.session_state.waiting_for_human):
        user_input = "Search for family members in my guest list"
        # Add user message immediately
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        st.session_state.example_processing = user_input
        st.rerun()
    
    if st.button("🌐 Current party planning trends", disabled=st.session_state.waiting_for_human):
        user_input = "What are the current party planning trends?"
        # Add user message immediately
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        st.session_state.example_processing = user_input
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    🎉 Party Planning Assistant v2.0 | Powered by LangGraph & FastAPI + Streamlit | 
    <a href="https://github.com/YusufDilekci/Invite_Party_Checklist_Agent" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)

# API Information section
st.markdown("---")
st.markdown("### 🚀 How to Use:")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Getting Started:**
    1. Start the FastAPI backend: `uvicorn fastapi_backend:app --reload`
    2. Ask questions about party planning
    3. Use example buttons for quick starts
    4. The assistant remembers our conversation context
    """)

with col2:
    st.markdown("""
    **API Endpoints:**
    - `POST /chat`: Send messages to chatbot
    - `POST /resume`: Resume interrupted conversations  
    - `GET /conversation/{thread_id}`: Get conversation history
    - `GET /status/{thread_id}`: Check thread status
    """)
