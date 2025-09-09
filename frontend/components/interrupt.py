import streamlit as st
import requests
import time
from config import AI_SERVICE_URL

def resume_conversation(response_data: str, thread_id: str):
    """Resume conversation after interruption."""
    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/resume",
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
        response = requests.get(f"{AI_SERVICE_URL}/status/{thread_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"waiting_for_input": False}
    except:
        return {"waiting_for_input": False}

def render_interrupt_box():
    """Render the human-in-the-loop interface."""
    # Check for interruption status
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