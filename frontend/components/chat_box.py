import streamlit as st
import requests
from datetime import datetime
from config import AI_SERVICE_URL


def send_chat_message(message: str, thread_id: str):
    """Send a message to the FastAPI backend."""
    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/chat",
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

def render_chat_box():
    """Render the chat interface."""
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

    # Handle example processing
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