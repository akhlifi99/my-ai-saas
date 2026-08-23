import streamlit as st
import openai
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Chatbot Builder | Pro Edition",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DEEP NAVY-PURPLE OMNI-THEME CSS ---
st.markdown("""
    <style>
    /* 1. Global App & Background Styling */
    [data-testid="stAppViewContainer"], .main, .stApp {
        background-color: #0f172a !important;
        color: #ffffff !important;
    }

    /* 2. Seamless Sidebar Styling */
    [data-testid="stSidebar"], [data-testid="stSidebarContent"], [data-testid="stSidebarNav"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }

    /* Target specific markdown inside sidebar */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1 {
        color: #ffffff !important;
    }

    /* Sidebar Brand Header */
    .sidebar-brand {
        font-size: 20px;
        font-weight: 800;
        color: #3b82f6;
        padding: 25px 0px;
        text-align: center;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 20px;
        letter-spacing: 1px;
    }

    /* 3. Navigation Radio Styling */
    div[role="radiogroup"] > label {
        background-color: transparent !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
        color: #94a3b8 !important;
        border: none !important;
    }

    div[role="radiogroup"] > label:hover {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }

    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    /* 4. Card & Container Styling (Lighter Tint) */
    .metric-card, .bot-card {
        background-color: #1a233a;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: 0.3s ease;
    }
    
    .bot-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }

    /* 5. Typography & Headers */
    .main-header {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
    }
    .main-subtitle {
        color: #94a3b8;
        margin-bottom: 30px;
    }

    /* 6. Buttons Styling */
    .stButton > bu
