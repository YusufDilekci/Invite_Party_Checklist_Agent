import streamlit as st

def render_footer():
    """Render footer and API information."""
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