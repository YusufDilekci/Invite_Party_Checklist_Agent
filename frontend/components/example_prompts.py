import streamlit as st
from datetime import datetime

def render_example_prompts():
    """Render example prompts section."""
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