import streamlit as st

def render_feature_highlights():
    """Render feature highlights section."""
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