import streamlit as st

PAGE_CONFIG = {
    "page_title": "Legal Chatbot",
    "page_icon": "⚖️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

CUSTOM_CSS = """
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        width: 100%;
        display: block;
        margin-left: auto;
        margin-right: auto;
        padding: 0;
    }
    
    /* Đảm bảo container chứa header được căn giữa */
    .header-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin: 0 auto;
        padding: 0;
    }
    
    /* Điều chỉnh padding của main container */
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left-color: #4caf50;
    }
    .source-info {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    .sidebar-section {
        margin-bottom: 1.5rem;
    }
</style>
"""

DEFAULT_CONFIG = {
    'api_key': " ",
    'base_url': " ",
    'app_code': " "
}

def initialize_session_state():
    """Khởi tạo session state"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'retriever' not in st.session_state:
        st.session_state.retriever = None
    if 'config' not in st.session_state:
        st.session_state.config = DEFAULT_CONFIG