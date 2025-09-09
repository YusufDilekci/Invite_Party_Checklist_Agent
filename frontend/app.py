import streamlit as st
import time
from components.sidebar import render_sidebar
from components.chat_box import render_chat_box
from components.interrupt import render_interrupt_box
from components.feature_highlights import render_feature_highlights
from components.example_prompts import render_example_prompts
from components.footer import render_footer

# Configure the Streamlit page
st.set_page_config(
    page_title="🎉 Party Planning Assistant",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS styles
with open("styles/theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with open("styles/chat.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

# Render components
render_sidebar()

# Main content
st.markdown('<h1 class="main-header">🎉 Party Planning Assistant</h1>', unsafe_allow_html=True)
render_feature_highlights()
render_interrupt_box()
render_chat_box()
render_example_prompts()
render_footer()