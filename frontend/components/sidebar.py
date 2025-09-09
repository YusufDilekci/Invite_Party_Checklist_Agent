import streamlit as st
import requests
from datetime import datetime
from config import AI_SERVICE_URL
import time

def check_fastapi_connection():
    """Check if FastAPI backend is running."""
    try:
        response = requests.get(f"{AI_SERVICE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def render_sidebar():
    """Render the sidebar with controls and thread management."""
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
                response = requests.get(f"{AI_SERVICE_URL}/conversation/{st.session_state.current_thread}")
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