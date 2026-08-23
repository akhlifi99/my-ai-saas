from __future__ import annotations

import base64
import hashlib
import hmac
import os
import sqlite3
import textwrap
from datetime import datetime, timedelta
from html import escape as html_escape
from typing import Any, Dict, List, Optional, Sequence

import streamlit as st
import streamlit.components.v1 as components

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    from cryptography.fernet import Fernet
except Exception:
    Fernet = None

# =============================================================================
# 1) PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="OmniToolsPro | Chatbot SaaS",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "OmniToolsPro"
APP_DB_PATH = "omnitoolspro.sqlite3"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_PAGE = "📊 Dashboard"

BASE_PAGES = [
    "📊 Dashboard",
    "🤖 My Chatbots",
    "📚 Knowledge Base",
    "💬 Widget Settings",
]
ADMIN_PAGE = "⚙️ Admin"
ALL_PAGES = BASE_PAGES + [ADMIN_PAGE]

# =============================================================================
# 2) THEME & HIGH-CONTRAST CSS
# =============================================================================
st.markdown(
    """
<style>
    :root {
        --bg: #0f172a;
        --panel: #1a233a;
        --border: #334155;
        --text: #ffffff;
        --muted: #94a3b8;
        --blue: #1d4ed8;
        --blue-2: #3b82f6;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stSidebar"],
    .main {
        background-color: var(--bg) !important;
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid var(--border) !important;
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    p, span, label, div, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid var(--border) !important;
    }

    [data-testid="stChatMessage"] {
        background-color: #1a233a !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }

    [data-testid="stChatMessage"] p {
        color: #ffffff !important;
    }

    .stButton > button {
        background-color: var(--blue) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }

    .stButton > button:hover {
        background-color: var(--blue-2) !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# =============================================================================
# 3) DB & AUTH HELPERS
# =============================================================================
def db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(APP_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def db_init() -> None:
    with db_connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT, updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS chatbots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                prompt TEXT NOT NULL,
                model TEXT DEFAULT 'gpt-4o-mini',
                welcome_message TEXT DEFAULT 'Hi! How can I help you today?',
                api_key_enc TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                created_at TEXT, updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS kb_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL,
                bot_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                content_text TEXT NOT NULL,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL,
                bot_id INTEGER NOT NULL,
                title TEXT DEFAULT 'Live Demo',
                created_at TEXT, updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT
            );
            """
        )

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"{salt.hex()}${digest.hex()}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
        return hmac.compare_digest(candidate, expected)
    except Exception:
        return False

# =============================================================================
# 4) INITIALIZATION
# =============================================================================
db_init()

if "auth_user_id" not in st.session_state:
    st.session_state.auth_user_id = None
if "nav_page" not in st.session_state:
    st.session_state.nav_page = DEFAULT_PAGE

# =============================================================================
# 5) LOGIN / SETUP
# =============================================================================
with db_connect() as conn:
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

if user_count == 0:
    st.title("First-Time Setup")
    with st.form("admin_setup"):
        name = st.text_input("Admin Name")
        email = st.text_input("Admin Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Create Admin Account")
        if submit and name and email and password:
            now = datetime.utcnow().isoformat()
            with db_connect() as conn:
                conn.execute(
                    "INSERT INTO users (name, email, password_hash, role, created_at, updated_at) VALUES (?, ?, ?, 'admin', ?, ?)",
                    (name, email.lower(), hash_password(password), now, now)
                )
            st.success("Admin created! Please refresh.")
            st.rerun()
elif st.session_state.auth_user_id is None:
    st.title("Login to OmniToolsPro")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In")
        if submit:
            with db_connect() as conn:
                user = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
            if user and verify_password(password, user["password_hash"]):
                st.session_state.auth_user_id = user["id"]
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid email or password.")
else:
    # Sidebar Navigation without state conflicts
    st.sidebar.title("🤖 OmniToolsPro")
    
    # Safe navigation option selection
    selected_page = st.sidebar.radio("Menu", ALL_PAGES, index=ALL_PAGES.index(st.session_state.nav_page) if st.session_state.nav_page in ALL_PAGES else 0)
    st.session_state.nav_page = selected_page

    if st.sidebar.button("Logout"):
        st.session_state.auth_user_id = None
        st.rerun()

    # Main views
    if st.session_state.nav_page == "📊 Dashboard":
        st.title("📊 System Analytics")
        st.write("Welcome to your AI Chatbot SaaS platform.")

    elif st.session_state.nav_page == "🤖 My Chatbots":
        st.title("🤖 My Chatbots")
        if st.button("+ New Bot"):
            now = datetime.utcnow().isoformat()
            with db_connect() as conn:
                conn.execute(
                    "INSERT INTO chatbots (owner_user_id, name, prompt, created_at, updated_at) VALUES (?, 'New Assistant', 'You are a helpful assistant.', ?, ?)",
                    (st.session_state.auth_user_id, now, now)
                )
            st.success("Created new bot!")
            st.rerun()

    elif st.session_state.nav_page == "📚 Knowledge Base":
        st.title("📚 Knowledge Base")
        st.write("Upload documents to train your bots.")

    elif st.session_state.nav_page == "💬 Widget Settings":
        st.title("💬 Widget & Chat Test")
        st.write("Test your assistant live with OpenAI.")

    elif st.session_state.nav_page == "⚙️ Admin":
        st.title("⚙️ Admin Settings")
        st.write("User management panel.")
        
