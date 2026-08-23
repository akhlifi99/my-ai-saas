```python
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
BOT_WIDGET_SCRIPT_URL = "https://omnitoolspro.example/widget.js"

BASE_PAGES = [
    "📊 Dashboard",
    "🤖 My Chatbots",
    "📚 Knowledge Base",
    "💬 Widget Settings",
]
ADMIN_PAGE = "⚙️ Admin"
ALL_PAGES = BASE_PAGES + [ADMIN_PAGE]


# =============================================================================
# 2) THEME: OMNITOOLSPRO (DEEP NAVY-PURPLE)
# =============================================================================
st.markdown(
    """
<style>
    :root {
        --bg: #0f172a;
        --panel: #1a233a;
        --panel-2: #162033;
        --border: #1e293b;
        --border-2: #334155;
        --text: #ffffff;
        --muted: #94a3b8;
        --blue: #1d4ed8;
        --blue-2: #3b82f6;
        --success: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    .main {
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid var(--border) !important;
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    html, body, [class*="css"] {
        color: var(--text) !important;
    }

    a {
        color: #60a5fa !important;
    }

    hr {
        border-color: var(--border) !important;
    }

    .sidebar-brand {
        font-size: 20px;
        font-weight: 800;
        color: #ffffff;
        padding: 22px 0 18px 0;
        text-align: center;
        border-bottom: 1px solid var(--border);
        margin-bottom: 18px;
        letter-spacing: 1px;
    }

    .sidebar-user {
        background: var(--panel);
        border: 1px solid var(--border-2);
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 14px;
    }

    .main-header {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 8px;
        line-height: 1.15;
    }

    .main-subtitle {
        color: var(--muted);
        margin-bottom: 22px;
        font-size: 15px;
    }

    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 10px 0;
    }

    .metric-card,
    .bot-card,
    .section-card {
        background: linear-gradient(180deg, #1a233a 0%, #152036 100%);
        border: 1px solid var(--border-2);
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 16px;
        color: #ffffff;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18);
        transition: all 0.25s ease;
    }

    .metric-card:hover,
    .bot-card:hover,
    .section-card:hover {
        border-color: var(--blue-2);
        transform: translateY(-1px);
    }

    .metric-card h3 {
        margin: 0;
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
    }

    .metric-card p,
    .bot-card p,
    .section-card p {
        margin: 0;
        color: #cbd5e1;
    }

    .bot-id {
        display: inline-block;
        margin-top: 10px;
        padding: 4px 10px;
        border-radius: 999px;
        background: #0f172a;
        border: 1px solid var(--border-2);
        color: #cbd5e1;
        font-size: 12px;
        word-break: break-all;
    }

    .status-dot {
        color: var(--success);
        font-weight: 800;
        margin-right: 6px;
    }

    .pill {
        display: inline-block;
        margin-left: 8px;
        padding: 4px 10px;
        border-radius: 999px;
        background: #0f172a;
        border: 1px solid var(--border-2);
        color: #cbd5e1;
        font-size: 12px;
    }

    .stButton > button {
        background-color: var(--blue) !important;
        color: #ffffff !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.62rem 1.1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }

    .stButton > button:hover {
        background-color: var(--blue-2) !important;
        border-color: var(--blue-2) !important;
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.28) !important;
    }

    .stButton > button:focus {
        outline: none !important;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div,
    .stMultiselect div {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid var(--border-2) !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #64748b !important;
    }

    button[data-baseweb="tab"] {
        color: #cbd5e1 !important;
        background: transparent !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 2px solid var(--blue-2) !important;
    }

    [data-testid="stChatMessage"] {
        background-color: #1a233a !important;
        border: 1px solid var(--border-2) !important;
        border-radius: 12px !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(180deg, #1a233a 0%, #152036 100%) !important;
        border: 1px solid var(--border-2) !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18) !important;
        padding: 18px !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: var(--blue-2) !important;
    }

    [data-testid="stAlert"] {
        border-radius: 12px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# 3) CONFIG HELPERS
# =============================================================================
def get_config_value(key: str, default: str = "") -> str:
    try:
        value = st.secrets.get(key)  # type: ignore[attr-defined]
        if value not in (None, ""):
            return str(value)
    except Exception:
        pass

    env_value = os.getenv(key, default)
    return env_value if env_value not in (None, "") else default


APP_ENCRYPTION_SECRET = get_config_value("OMNITOOLSPRO_SECRET", "change-me-in-production")
GLOBAL_OPENAI_API_KEY = get_config_value("OPENAI_API_KEY", "")


# =============================================================================
# 4) DATABASE
# =============================================================================
def db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(APP_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
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
                role TEXT NOT NULL CHECK(role IN ('admin', 'member')),
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chatbots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                prompt TEXT NOT NULL,
                model TEXT NOT NULL DEFAULT 'gpt-4o-mini',
                welcome_message TEXT NOT NULL DEFAULT 'Hi! How can I help you today?',
                api_key_enc TEXT NOT NULL DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(owner_user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS kb_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL,
                bot_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                content_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(owner_user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(bot_id) REFERENCES chatbots(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL,
                bot_id INTEGER NOT NULL,
                title TEXT NOT NULL DEFAULT 'Live Demo',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(owner_user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(bot_id) REFERENCES chatbots(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('system', 'user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_bots_owner ON chatbots(owner_user_id);
            CREATE INDEX IF NOT EXISTS idx_docs_bot ON kb_documents(bot_id);
            CREATE INDEX IF NOT EXISTS idx_conversations_bot ON conversations(bot_id);
            CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
            """
        )


def fetch_one(query: str, params: Sequence[Any] = ()) -> Optional[Dict[str, Any]]:
    with db_connect() as conn:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else None


def fetch_all(query: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
    with db_connect() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def execute(query: str, params: Sequence[Any] = ()) -> int:
    with db_connect() as conn:
        cur = conn.execute(query, params)
        conn.commit()
        return cur.lastrowid


def scalar(query: str, params: Sequence[Any] = ()) -> Any:
    row = fetch_one(query, params)
    if not row:
        return None
    return next(iter(row.values()))


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def bootstrap_first_admin_if_needed() -> bool:
    return int(scalar("SELECT COUNT(*) AS c FROM users") or 0) == 0


# =============================================================================
# 5) SECURITY / AUTH HELPERS
# =============================================================================
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


def derive_fernet_key(secret: str) -> bytes:
    key_material = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(key_material)


def xor_bytes(data: bytes, key: bytes) -> bytes:
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ key[i % len(key)])
    return bytes(out)


def encrypt_secret(plain_text: str) -> str:
    if not plain_text:
        return ""

    if Fernet is not None:
        try:
            f = Fernet(derive_fernet_key(APP_ENCRYPTION_SECRET))
            return f.encrypt(plain_text.encode("utf-8")).decode("utf-8")
        except Exception:
            pass

    key = hashlib.sha256(APP_ENCRYPTION_SECRET.encode("utf-8")).digest()
    encrypted = xor_bytes(plain_text.encode("utf-8"), key)
    return "xor:" + base64.urlsafe_b64encode(encrypted).decode("utf-8")


def decrypt_secret(cipher_text: str) -> str:
    if not cipher_text:
        return ""

    if cipher_text.startswith("xor:"):
        try:
            payload = base64.urlsafe_b64decode(cipher_text[4:].encode("utf-8"))
            key = hashlib.sha256(APP_ENCRYPTION_SECRET.encode("utf-8")).digest()
            return xor_bytes(payload, key).decode("utf-8")
        except Exception:
            return ""

    if Fernet is not None:
        try:
            f = Fernet(derive_fernet_key(APP_ENCRYPTION_SECRET))
            return f.decrypt(cipher_text.encode("utf-8")).decode("utf-8")
        except Exception:
            return ""

    return ""


# =============================================================================
# 6) SESSION STATE
# =============================================================================
def init_session_state() -> None:
    defaults = {
        "auth_user_id": None,
        "nav_page": DEFAULT_PAGE,
        "active_bot_id": None,
        "pending_delete_bot_id": None,
        "pending_delete_bot_name": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_auth_state() -> None:
    for key in [
        "auth_user_id",
        "nav_page",
        "active_bot_id",
        "pending_delete_bot_id",
        "pending_delete_bot_name",
    ]:
        st.session_state.pop(key, None)
    st.session_state.nav_page = DEFAULT_PAGE


def rerun_app() -> None:
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()


def get_current_user() -> Optional[Dict[str, Any]]:
    user_id = st.session_state.get("auth_user_id")
    if not user_id:
        return None

    user = fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
    if not user or int(user.get("is_active", 0)) != 1:
        clear_auth_state()
        return None

    return user


def available_pages_for_user(user: Dict[str, Any]) -> List[str]:
    if user["role"] == "admin":
        return ALL_PAGES
    return BASE_PAGES


def enforce_page_access(user: Dict[str, Any]) -> None:
    allowed_pages = available_pages_for_user(user)
    if st.session_state.nav_page not in allowed_pages:
        st.session_state.nav_page = DEFAULT_PAGE

    active_bot = get_bot_by_id(st.session_state.get("active_bot_id"))
    if active_bot and not can_access_bot(user, active_bot):
        st.session_state.active_bot_id = None


# =============================================================================
# 7) USER / BOT ACCESS HELPERS
# =============================================================================
def can_access_bot(user: Dict[str, Any], bot: Dict[str, Any]) -> bool:
    return user["role"] == "admin" or int(bot["owner_user_id"]) == int(user["id"])


def get_bot_by_id(bot_id: Optional[int]) -> Optional[Dict[str, Any]]:
    if not bot_id:
        return None
    return fetch_one(
        """
        SELECT b.*, u.name AS owner_name, u.email AS owner_email
        FROM chatbots b
        JOIN users u ON u.id = b.owner_user_id
        WHERE b.id = ?
        """,
        (bot_id,),
    )


def get_accessible_bots(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    if user["role"] == "admin":
        return fetch_all(
            """
            SELECT b.*, u.name AS owner_name, u.email AS owner_email
            FROM chatbots b
            JOIN users u ON u.id = b.owner_user_id
            ORDER BY b.updated_at DESC, b.id DESC
            """
        )
    return fetch_all(
        """
        SELECT b.*, u.name AS owner_name, u.email AS owner_email
        FROM chatbots b
        JOIN users u ON u.id = b.owner_user_id
        WHERE b.owner_user_id = ?
        ORDER BY b.updated_at DESC, b.id DESC
        """,
        (user["id"],),
    )


def get_active_bot() -> Optional[Dict[str, Any]]:
    return get_bot_by_id(st.session_state.get("active_bot_id"))


def set_active_bot_and_open_editor(bot_id: int) -> None:
    st.session_state.active_bot_id = bot_id
    st.session_state.nav_page = "💬 Widget Settings"
    rerun_app()


def navigate_to(page: str) -> None:
    st.session_state.nav_page = page
    rerun_app()


def get_bot_api_key(bot: Dict[str, Any]) -> str:
    stored = bot.get("api_key_enc", "") or ""
    if stored:
        secret = decrypt_secret(stored)
        if secret:
            return secret
    return GLOBAL_OPENAI_API_KEY


def get_bot_knowledge_context(bot_id: int, max_chars: int = 4500) -> str:
    docs = fetch_all(
        """
        SELECT filename, content_text, created_at
        FROM kb_documents
        WHERE bot_id = ?
        ORDER BY id DESC
        """,
        (bot_id,),
    )
    if not docs:
        return ""

    combined_parts = []
    for doc in docs:
        part = f"[Document: {doc['filename']} | Created: {doc['created_at']}]\n{doc['content_text']}"
        combined_parts.append(part)

    combined = "\n\n---\n\n".join(combined_parts)
    if len(combined) > max_chars:
        combined = combined[:max_chars] + "\n\n[Truncated KB context]"
    return combined


# =============================================================================
# 8) AUTH / USERS
# =============================================================================
def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    return fetch_one("SELECT * FROM users WHERE lower(email) = lower(?)", (email.strip(),))


def create_user(name: str, email: str, password: str, role: str = "member") -> int:
    user_id = execute(
        """
        INSERT INTO users (name, email, password_hash, role, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, 1, ?, ?)
        """,
        (name.strip(), email.strip().lower(), hash_password(password), role, now_iso(), now_iso()),
    )
    return user_id


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    user = get_user_by_email(email)
    if not user or int(user.get("is_active", 0)) != 1:
        return None
    if verify_password(password, user["password_hash"]):
        return user
    return None


def create_first_admin_screen() -> None:
    st.markdown('<div class="main-header">First-Time Setup</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">No users found. Create the first administrator account to begin.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown('<div class="section-title">Create Admin Account</div>', unsafe_allow_html=True)

        with st.form("first_admin_form"):
            name = st.text_input("Full Name", placeholder="Admin Name")
            email = st.text_input("Email", placeholder="admin@company.com")
            password = st.text_input("Password", type="password", placeholder="Create a strong password")
            confirm = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Create Admin Account", use_container_width=True)

        if submit:
            if not name.strip() or not email.strip() or not password:
                st.error("Please complete all fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif get_user_by_email(email):
                st.error("A user with this email already exists.")
            else:
                user_id = create_user(name=name, email=email, password=password, role="admin")
                st.session_state.auth_user_id = user_id
                st.session_state.nav_page = DEFAULT_PAGE
                st.success("Admin account created successfully.")
                rerun_app()


def login_screen() -> None:
    st.markdown('<div class="main-header">Welcome back</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Sign in to manage your chatbot SaaS workspace.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown('<div class="section-title">Login</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@company.com")
            password = st.text_input("Password", type="password", placeholder="Your password")
            submit = st.form_submit_button("Sign In", use_container_width=True)

        if submit:
            user = authenticate_user(email, password)
            if user:
                st.session_state.auth_user_id = user["id"]
                st.session_state.nav_page = DEFAULT_PAGE
                st.success("Signed in successfully.")
                rerun_app()
            else:
                st.error("Invalid credentials or account is inactive.")

    st.caption(
        "If this is a fresh installation, the app will guide you to create the first admin account."
    )


def logout() -> None:
    clear_auth_state()
    rerun_app()


# =============================================================================
# 9) BOT CRUD
# =============================================================================
def create_bot(owner_user_id: int) -> int:
    bot_id = execute(
        """
        INSERT INTO chatbots
            (owner_user_id, name, prompt, model, welcome_message, api_key_enc, is_active, created_at, updated_at)
        VALUES
            (?, ?, ?, ?, ?, ?, 1, ?, ?)
        """,
        (
            owner_user_id,
            "New Assistant",
            "You are a helpful, professional AI assistant.",
            DEFAULT_MODEL,
            "Hi! How can I help you today?",
            "",
            now_iso(),
            now_iso(),
        ),
    )
    return bot_id


def update_bot(
    bot_id: int,
    name: str,
    prompt: str,
    model: str,
    welcome_message: str,
    api_key_plain: Optional[str] = None,
    clear_api_key: bool = False,
) -> None:
    bot = get_bot_by_id(bot_id)
    if not bot:
        raise ValueError("Bot not found.")

    if clear_api_key:
        api_key_enc = ""
    elif api_key_plain is None:
        api_key_enc = bot.get("api_key_enc", "")
    else:
        api_key_enc = encrypt_secret(api_key_plain.strip()) if api_key_plain.strip() else bot.get("api_key_enc", "")

    execute(
        """
        UPDATE chatbots
        SET name = ?, prompt = ?, model = ?, welcome_message = ?, api_key_enc = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            name.strip(),
            prompt.strip(),
            model.strip() or DEFAULT_MODEL,
            welcome_message.strip() or "Hi! How can I help you today?",
            api_key_enc,
            now_iso(),
            bot_id,
        ),
    )


def duplicate_bot(source_bot_id: int, owner_user_id: int) -> int:
    source = get_bot_by_id(source_bot_id)
    if not source:
        raise ValueError("Source bot not found.")

    new_name = f"{source['name']} Copy"
    new_id = execute(
        """
        INSERT INTO chatbots
            (owner_user_id, name, prompt, model, welcome_message, api_key_enc, is_active, created_at, updated_at)
        VALUES
            (?, ?, ?, ?, ?, ?, 1, ?, ?)
        """,
        (
            owner_user_id,
            new_name,
            source["prompt"],
            source["model"],
            source["welcome_message"],
            source.get("api_key_enc", ""),
            now_iso(),
            now_iso(),
        ),
    )

    docs = fetch_all(
        """
        SELECT filename, content_text
        FROM kb_documents
        WHERE bot_id = ?
        ORDER BY id ASC
        """,
        (source_bot_id,),
    )
    for doc in docs:
        execute(
            """
            INSERT INTO kb_documents (owner_user_id, bot_id, filename, content_text, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                owner_user_id,
                new_id,
                f"Copy of {doc['filename']}",
                doc["content_text"],
                now_iso(),
            ),
        )

    return new_id


def delete_bot(bot_id: int) -> None:
    execute("DELETE FROM chatbots WHERE id = ?", (bot_id,))


# =============================================================================
# 10) KNOWLEDGE BASE
# =============================================================================
def extract_text_from_uploaded_file(uploaded_file: Any) -> str:
    filename = uploaded_file.name
    lower = filename.lower()
    raw = uploaded_file.getvalue()

    if lower.endswith((".txt", ".md", ".csv", ".json", ".html", ".htm", ".log", ".py", ".yaml", ".yml")):
        return raw.decode("utf-8", errors="ignore")

    if lower.endswith(".pdf"):
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception:
            try:
                from PyPDF2 import PdfReader  # type: ignore
            except Exception as exc:
                raise ValueError("PDF support requires pypdf or PyPDF2 installed.") from exc

        reader = PdfReader(uploaded_file)
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages).strip()

    raise ValueError(f"Unsupported file type: {filename}")


def save_kb_document(owner_user_id: int, bot_id: int, filename: str, content_text: str) -> int:
    return execute(
        """
        INSERT INTO kb_documents (owner_user_id, bot_id, filename, content_text, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (owner_user_id, bot_id, filename, content_text, now_iso()),
    )


def delete_kb_document(doc_id: int) -> None:
    execute("DELETE FROM kb_documents WHERE id = ?", (doc_id,))


# =============================================================================
# 11) CONVERSATIONS / MESSAGES
# =============================================================================
def get_or_create_conversation(bot_id: int, user_id: int) -> int:
    active_key = f"conversation_{bot_id}"

    conversation_id = st.session_state.get(active_key)
    if conversation_id:
        existing = fetch_one("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
        if existing:
            return conversation_id

    latest = fetch_one(
        """
        SELECT id
        FROM conversations
        WHERE bot_id = ? AND owner_user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (bot_id, user_id),
    )
    if latest:
        st.session_state[active_key] = latest["id"]
        return latest["id"]

    new_id = execute(
        """
        INSERT INTO conversations (owner_user_id, bot_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, bot_id, "Live Demo", now_iso(), now_iso()),
    )
    st.session_state[active_key] = new_id
    return new_id


def create_new_conversation(bot_id: int, user_id: int) -> int:
    new_id = execute(
        """
        INSERT INTO conversations (owner_user_id, bot_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, bot_id, "Live Demo", now_iso(), now_iso()),
    )
    st.session_state[f"conversation_{bot_id}"] = new_id
    return new_id


def get_conversation_messages(conversation_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    return fetch_all(
        """
        SELECT role, content, created_at
        FROM (
            SELECT *
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
        )
        ORDER BY id ASC
        """,
        (conversation_id, limit),
    )


def append_message(conversation_id: int, role: str, content: str) -> None:
    execute(
        """
        INSERT INTO messages (conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (conversation_id, role, content, now_iso()),
    )
    execute(
        "UPDATE conversations SET updated_at = ? WHERE id = ?",
        (now_iso(), conversation_id),
    )


# =============================================================================
# 12) AI REPLY GENERATION
# =============================================================================
def generate_assistant_reply(bot: Dict[str, Any], history: List[Dict[str, str]], api_key: str) -> str:
    if OpenAI is None:
        raise RuntimeError("The OpenAI Python SDK is not installed. Run: pip install openai")

    client = OpenAI(api_key=api_key.strip())
    model = bot.get("model") or DEFAULT_MODEL

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": bot["prompt"]},
    ]

    kb_context = get_bot_knowledge_context(int(bot["id"]))
    if kb_context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Knowledge base context for this assistant:\n\n"
                    f"{kb_context}"
                ),
            }
        )

    trimmed_history = history[-30:]
    messages.extend(trimmed_history)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    content = response.choices[0].message.content if response.choices else None
    return content or "No response content returned by the model."


# =============================================================================
# 13) RENDER HELPERS
# =============================================================================
def render_page_heading(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="main-header">{html_escape(title)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-subtitle">{html_escape(subtitle)}</div>', unsafe_allow_html=True)


def render_metric_card(title: str, value: str, subtitle: str = "") -> None:
    subtitle_html = f"<p style='margin-top:8px;'>{html_escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <h3>{html_escape(value)}</h3>
            <p style="margin-top: 6px; font-size: 14px; color: #cbd5e1; font-weight: 700;">
                {html_escape(title)}
            </p>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_bot_card(bot: Dict[str, Any]) -> None:
    owner_text = f"Owner: {bot.get('owner_name', 'Unknown')}"
    updated_at = bot.get("updated_at", "")
    model = bot.get("model", DEFAULT_MODEL)
    name = html_escape(str(bot.get("name", "Unnamed Bot")))
    bot_id = html_escape(str(bot.get("id", "")))
    owner_text = html_escape(owner_text)
    model = html_escape(model)
    updated_at = html_escape(updated_at)

    st.markdown(
        f"""
        <div class="bot-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
                <div style="width:100%;">
                    <div style="margin-bottom:8px;">
                        <span class="status-dot">●</span>
                        <span style="color:#10b981; font-weight:800;">Active</span>
                        <span class="pill">{model}</span>
                    </div>
                    <h3 style="margin:0; color:#ffffff; font-size:20px; font-weight:800;">{name}</h3>
                    <p style="margin-top:6px; color:#cbd5e1;">{owner_text}</p>
                    <p style="margin-top:6px; color:#94a3b8; font-size:13px;">Updated: {updated_at}</p>
                    <div class="bot-id">ID: {bot_id}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(message: str, hint: str) -> None:
    st.markdown(
        f"""
        <div class="bot-card" style="text-align:center; padding: 62px 28px; border-style: dashed;">
            <h3 style="color:#ffffff; margin-bottom:10px;">{html_escape(message)}</h3>
            <p style="color:#94a3b8; margin:0;">{html_escape(hint)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_widget_preview_html(bot: Dict[str, Any]) -> str:
    bot_name = html_escape(str(bot.get("name", "Assistant")))
    welcome = html_escape(str(bot.get("welcome_message", "Hi! How can I help you today?")))
    prompt_snippet = html_escape(textwrap.shorten(str(bot.get("prompt", "")), width=180, placeholder="..."))
    bot_id = html_escape(str(bot.get("id", "")))

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <style>
        html, body {{
          margin: 0;
          background: #0f172a;
          font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color: #fff;
        }}
        .wrap {{
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 22px;
          box-sizing: border-box;
        }}
        .widget {{
          width: 100%;
          max-width: 420px;
          background: linear-gradient(180deg, #1a233a 0%, #152036 100%);
          border: 1px solid #334155;
          border-radius: 18px;
          box-shadow: 0 18px 44px rgba(0,0,0,.35);
          overflow: hidden;
        }}
        .top {{
          padding: 16px 18px;
          background: rgba(15, 23, 42, 0.55);
          border-bottom: 1px solid #334155;
        }}
        .name {{
          font-size: 18px;
          font-weight: 800;
          margin: 0;
        }}
        .sub {{
          color: #94a3b8;
          font-size: 13px;
          margin-top: 6px;
        }}
        .chat {{
          padding: 18px;
          display: grid;
          gap: 12px;
        }}
        .bubble {{
          padding: 12px 14px;
          border-radius: 14px;
          line-height: 1.45;
          font-size: 14px;
        }}
        .assistant {{
          background: #0f172a;
          border: 1px solid #334155;
        }}
        .user {{
          background: #1d4ed8;
          border: 1px solid #3b82f6;
          margin-left: 46px;
        }}
        .footer {{
          padding: 14px 18px 18px 18px;
          color: #94a3b8;
          font-size: 12px;
          border-top: 1px solid #334155;
        }}
        .input {{
          margin-top: 4px;
          border: 1px solid #334155;
          border-radius: 12px;
          padding: 11px 12px;
          color: #94a3b8;
          background: #0f172a;
        }}
        .meta {{
          margin-top: 8px;
          color: #64748b;
          font-size: 11px;
        }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="widget">
          <div class="top">
            <p class="name">🤖 {bot_name}</p>
            <div class="sub">OmniToolsPro Embed Preview</div>
          </div>
          <div class="chat">
            <div class="bubble assistant">{welcome}</div>
            <div class="bubble user">Show me what this widget looks like in my product.</div>
            <div class="bubble assistant">
              I can answer using your system prompt and knowledge base.
              <div class="meta">Prompt: {prompt_snippet}</div>
            </div>
            <div class="input">Type a message...</div>
          </div>
          <div class="footer">
            Bot ID: {bot_id} • Secure embedded assistant UI
          </div>
        </div>
      </div>
    </body>
    </html>
    """


def render_sidebar(user: Dict[str, Any]) -> None:
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">🤖 OMNITOOLSPRO</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="sidebar-user">
                <div style="font-size:12px; color:#94a3b8;">Signed in as</div>
                <div style="font-size:16px; font-weight:800; color:#ffffff; margin-top:4px;">
                    {html_escape(user["name"])}
                </div>
                <div style="font-size:13px; color:#cbd5e1; margin-top:4px;">
                    {html_escape(user["email"])}
                </div>
                <div class="bot-id" style="margin-top:10px;">Role: {html_escape(user["role"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        allowed_pages = available_pages_for_user(user)
        st.radio(
            "Navigation",
            allowed_pages,
            label_visibility="collapsed",
            key="nav_page",
        )

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        active_bot = get_active_bot()
        if active_bot:
            st.markdown(
                f"""
                <div class="section-card">
                    <div style="font-size:12px; color:#94a3b8; margin-bottom:6px;">Current Editor</div>
                    <div style="font-size:16px; font-weight:800; color:#ffffff;">{html_escape(active_bot["name"])}</div>
                    <div class="bot-id" style="margin-top:10px;">{html_escape(str(active_bot["id"]))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("⬅ Exit Editor", use_container_width=True):
                st.session_state.active_bot_id = None
                st.session_state.nav_page = "🤖 My Chatbots"
                rerun_app()
        else:
            st.markdown(
                """
                <div class="section-card">
                    <div style="font-size:12px; color:#94a3b8; margin-bottom:6px;">Current Editor</div>
                    <div style="font-size:16px; font-weight:700; color:#cbd5e1;">No bot selected</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            logout()


# =============================================================================
# 14) PAGE RENDERERS
# =============================================================================
def render_dashboard(user: Dict[str, Any]) -> None:
    render_page_heading(
        "System Analytics",
        "Unified performance view across your AI agents and deployment surface.",
    )

    if user["role"] == "admin":
        total_users = int(scalar("SELECT COUNT(*) AS c FROM users") or 0)
    else:
        total_users = 1

    if user["role"] == "admin":
        bots_count = int(scalar("SELECT COUNT(*) AS c FROM chatbots") or 0)
        docs_count = int(scalar("SELECT COUNT(*) AS c FROM kb_documents") or 0)
        msg_count = int(scalar("SELECT COUNT(*) AS c FROM messages") or 0)
    else:
        bots_count = int(scalar("SELECT COUNT(*) AS c FROM chatbots WHERE owner_user_id = ?", (user["id"],)) or 0)
        docs_count = int(
            scalar(
                """
                SELECT COUNT(*) AS c
                FROM kb_documents d
                JOIN chatbots b ON b.id = d.bot_id
                WHERE b.owner_user_id = ?
                """,
                (user["id"],),
            )
            or 0
        )
        msg_count = int(
            scalar(
                """
                SELECT COUNT(*) AS c
                FROM messages m
                JOIN conversations c ON c.id = m.conversation_id
                JOIN chatbots b ON b.id = c.bot_id
                WHERE b.owner_user_id = ?
                """,
                (user["id"],),
            )
            or 0
        )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Bots", str(bots_count), "Active chatbot projects")
    with c2:
        render_metric_card("Knowledge Docs", str(docs_count), "Uploaded or pasted content")
    with c3:
        render_metric_card("Messages", str(msg_count), "Persisted conversation history")
    with c4:
        render_metric_card("Users", str(total_users), "Workspace accounts")

    today = datetime.utcnow().date()
    start = today - timedelta(days=6)
    counts: List[int] = []

    for i in range(7):
        d = start + timedelta(days=i)
        if user["role"] == "admin":
            cnt = int(
                scalar(
                    """
                    SELECT COUNT(*) AS c
                    FROM messages
                    WHERE substr(created_at, 1, 10) = ?
                    """,
                    (d.isoformat(),),
                )
                or 0
            )
        else:
            cnt = int(
                scalar(
                    """
                    SELECT COUNT(*) AS c
                    FROM messages m
                    JOIN conversations c ON c.id = m.conversation_id
                    JOIN chatbots b ON b.id = c.bot_id
                    WHERE substr(m.created_at, 1, 10) = ? AND b.owner_user_id = ?
                    """,
                    (d.isoformat(), user["id"]),
                )
                or 0
            )
        counts.append(cnt)

    with st.container(border=True):
        st.markdown('<div class="section-title">7-Day Message Trend</div>', unsafe_allow_html=True)
        st.caption("Persisted usage data from the database.")
        st.line_chart({"Messages": counts}, use_container_width=True)

    with st.container(border=True):
        st.markdown('<div class="section-title">Workspace Summary</div>', unsafe_allow_html=True)
        st.write("• Persistent SQLite storage for users, bots, documents, conversations, and messages.")
        st.write("• Role-based access with admin controls.")
        st.write("• Per-bot API keys securely stored in the database.")
        st.write("• Knowledge base content injected into assistant context at runtime.")


def render_my_chatbots(user: Dict[str, Any]) -> None:
    header_col, action_col = st.columns([4.5, 1.2], vertical_alignment="center")
    with header_col:
        render_page_heading("My Chatbots", "Create, manage, duplicate, and deploy your AI agents.")
    with action_col:
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        if st.button("+ New Bot", use_container_width=True):
            new_bot_id = create_bot(user["id"])
            st.session_state.active_bot_id = new_bot_id
            st.session_state.nav_page = "💬 Widget Settings"
            rerun_app()

    accessible_bots = get_accessible_bots(user)

    if st.session_state.pending_delete_bot_id:
        pending_bot = get_bot_by_id(st.session_state.pending_delete_bot_id)
        if pending_bot and can_access_bot(user, pending_bot):
            st.warning(
                f"Delete confirmation: **{pending_bot['name']}** will be permanently removed, including KB docs and conversation history."
            )
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("Confirm Delete", use_container_width=True):
                    delete_bot(int(pending_bot["id"]))
                    if st.session_state.active_bot_id == int(pending_bot["id"]):
                        st.session_state.active_bot_id = None
                        st.session_state.nav_page = "🤖 My Chatbots"
                    st.session_state.pending_delete_bot_id = None
                    st.session_state.pending_delete_bot_name = None
                    st.success("Chatbot deleted successfully.")
                    rerun_app()
            with c2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.pending_delete_bot_id = None
                    st.session_state.pending_delete_bot_name = None
                    rerun_app()
        else:
            st.session_state.pending_delete_bot_id = None
            st.session_state.pending_delete_bot_name = None

    if not accessible_bots:
        render_empty_state("No bots found", "Click + New Bot to create your first chatbot.")
        return

    for bot in accessible_bots:
        with st.container(border=True):
            left, right = st.columns([4.7, 1.6], vertical_alignment="center")
            with left:
                render_bot_card(bot)
            with right:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                if st.button("Manage ->", key=f"manage_{bot['id']}", use_container_width=True):
                    set_active_bot_and_open_editor(int(bot["id"]))
                if st.button("Duplicate", key=f"duplicate_{bot['id']}", use_container_width=True):
                    new_id = duplicate_bot(int(bot["id"]), user["id"])
                    st.session_state.active_bot_id = new_id
                    st.session_state.nav_page = "💬 Widget Settings"
                    st.success("Bot duplicated successfully.")
                    rerun_app()
                if st.button("Delete", key=f"delete_{bot['id']}", use_container_width=True):
                    st.session_state.pending_delete_bot_id = int(bot["id"])
                    st.session_state.pending_delete_bot_name = bot["name"]
                    rerun_app()


def render_knowledge_base(user: Dict[str, Any]) -> None:
    render_page_heading(
        "Knowledge Base",
        "Upload files or paste content to give your bots persistent contextual knowledge.",
    )

    bots = get_accessible_bots(user)
    if not bots:
        render_empty_state("No bots available", "Create a chatbot before uploading knowledge base content.")
        return

    bot_labels = [f"{bot['name']} (ID: {bot['id']})" for bot in bots]
    default_index = 0
    active_bot = get_active_bot()
    if active_bot:
        for idx, bot in enumerate(bots):
            if int(bot["id"]) == int(active_bot["id"]):
                default_index = idx
                break

    selected_label = st.selectbox("Select Chatbot", bot_labels, index=default_index)
    selected_bot = bots[bot_labels.index(selected_label)]
    st.session_state.active_bot_id = int(selected_bot["id"])

    docs = fetch_all(
        """
        SELECT id, filename, content_text, created_at
        FROM kb_documents
        WHERE bot_id = ?
        ORDER BY id DESC
        """,
        (selected_bot["id"],),
    )
    total_chars = sum(len(d["content_text"]) for d in docs)

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Documents", str(len(docs)), "Indexed source files")
    with c2:
        render_metric_card("Characters", str(total_chars), "Total KB content stored")
    with c3:
        render_metric_card("Selected Bot", selected_bot["name"], "Target workspace assistant")

    with st.container(border=True):
        st.markdown('<div class="section-title">Upload Files / Paste Text</div>', unsafe_allow_html=True)
        st.caption(
            "Supported text files: txt, md, csv, json, html, log, py, yaml, yml, pdf (if optional PDF library is installed)."
        )

        with st.form(f"kb_upload_form_{selected_bot['id']}"):
            uploaded_files = st.file_uploader(
                "Upload knowledge files",
                type=["txt", "md", "csv", "json", "html", "htm", "log", "py", "yaml", "yml", "pdf"],
                accept_multiple_files=True,
            )
            pasted_text = st.text_area(
                "Or paste text directly",
                placeholder="Paste documentation, FAQs, policies, onboarding docs, internal SOPs...",
                height=220,
            )
            submit = st.form_submit_button("Save to Knowledge Base", use_container_width=True)

        if submit:
            saved_docs = 0

            if uploaded_files:
                for file in uploaded_files:
                    try:
                        content = extract_text_from_uploaded_file(file)
                        if content.strip():
                            save_kb_document(
                                owner_user_id=user["id"],
                                bot_id=int(selected_bot["id"]),
                                filename=file.name,
                                content_text=content.strip(),
                            )
                            saved_docs += 1
                    except Exception as exc:
                        st.error(f"{file.name}: {exc}")

            if pasted_text.strip():
                save_kb_document(
                    owner_user_id=user["id"],
                    bot_id=int(selected_bot["id"]),
                    filename="pasted_content.txt",
                    content_text=pasted_text.strip(),
                )
                saved_docs += 1

            if saved_docs:
                st.success(f"Saved {saved_docs} knowledge base item(s) successfully.")
                rerun_app()
            else:
                st.warning("No content was saved. Please upload a supported file or paste text.")

    with st.container(border=True):
        st.markdown('<div class="section-title">Current Knowledge Base Documents</div>', unsafe_allow_html=True)
        if not docs:
            st.info("No knowledge base documents yet. Add your first file or pasted content above.")
        else:
            for doc in docs:
                doc_id = int(doc["id"])
                with st.container(border=True):
                    c1, c2 = st.columns([4.8, 1.2], vertical_alignment="center")
                    with c1:
                        st.markdown(
                            f"""
                            <div style="font-weight:800; color:#ffffff;">{html_escape(doc['filename'])}</div>
                            <div style="font-size:12px; color:#94a3b8; margin-top:4px;">
                                Created: {html_escape(doc['created_at'])}
                            </div>
                            <div style="font-size:13px; color:#cbd5e1; margin-top:8px;">
                                {html_escape(textwrap.shorten(doc['content_text'], width=220, placeholder='...'))}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with c2:
                        if st.button("Delete", key=f"delete_doc_{doc_id}", use_container_width=True):
                            delete_kb_document(doc_id)
                            st.success("Document deleted.")
                            rerun_app()


def render_widget_settings(user: Dict[str, Any]) -> None:
    bots = get_accessible_bots(user)
    if not bots:
        render_page_heading("Widget Settings", "No chatbot selected.")
        st.warning("Create a chatbot in My Chatbots first.")
        return

    active_bot = get_active_bot()
    if active_bot is None or not can_access_bot(user, active_bot):
        render_page_heading(
            "Widget Settings",
            "Select a chatbot to configure its system prompt, demo chat, and embed code.",
        )
        bot_labels = [f"{bot['name']} (ID: {bot['id']})" for bot in bots]
        selected_label = st.selectbox("Select Chatbot", bot_labels)
        chosen_bot = bots[bot_labels.index(selected_label)]
        if st.button("Open Configuration", use_container_width=True):
            st.session_state.active_bot_id = int(chosen_bot["id"])
            rerun_app()
        return

    bot = active_bot
    render_page_heading(
        f"Configuring: {bot['name']}",
        f"Bot ID: {bot['id']} — update the system prompt, test the live demo, copy the embed code, or preview the widget.",
    )

    tab1, tab2, tab3, tab4 = st.tabs(["System Prompt", "Live Demo", "Embed Code", "Embed Preview"])

    with tab1:
        with st.container(border=True):
            st.markdown('<div class="section-title">Bot Configuration</div>', unsafe_allow_html=True)
            st.caption("Changes are saved to the database.")

            stored_key_present = bool(bot.get("api_key_enc"))
            st.info(
                "Stored API key: "
                + ("present" if stored_key_present else "not set")
                + ". Leave the key field blank to keep the current value."
            )

            with st.form(f"bot_settings_form_{bot['id']}"):
                bot_name = st.text_input("Bot Label", value=bot["name"])
                bot_model = st.text_input("Model", value=bot.get("model", DEFAULT_MODEL))
                welcome_message = st.text_area(
                    "Welcome Message",
                    value=bot.get("welcome_message", "Hi! How can I help you today?"),
                    height=100,
                )
                bot_prompt = st.text_area(
                    "System Prompt",
                    value=bot["prompt"],
                    height=220,
                    placeholder="Define the assistant's behavior, tone, constraints, and knowledge boundaries.",
                )
                api_key_input = st.text_input(
                    "Per-Bot OpenAI API Key",
                    value="",
                    type="password",
                    placeholder="sk-...",
                )
                clear_key = st.checkbox("Clear stored API key for this bot")
                save = st.form_submit_button("Save Bot Settings", use_container_width=True)

            if save:
                try:
                    api_key_plain: Optional[str]
                    if clear_key:
                        api_key_plain = ""
                    elif api_key_input.strip():
                        api_key_plain = api_key_input.strip()
                    else:
                        api_key_plain = None

                    update_bot(
                        bot_id=int(bot["id"]),
                        name=bot_name,
                        prompt=bot_prompt,
                        model=bot_model,
                        welcome_message=welcome_message,
                        api_key_plain=api_key_plain,
                        clear_api_key=clear_key,
                    )
                    st.success("Bot settings saved successfully.")
                    rerun_app()
                except Exception as exc:
                    st.error(f"Could not save bot settings: {exc}")

    with tab2:
        with st.container(border=True):
            st.markdown(
                f'<div class="section-title">Sandbox Chat for {html_escape(bot["name"])}</div>',
                unsafe_allow_html=True,
            )
            st.caption("This demo uses the current system prompt, selected model, and knowledge base context.")

            conversation_id = get_or_create_conversation(int(bot["id"]), int(user["id"]))

            top_left, top_right = st.columns([1.2, 1.6], vertical_alignment="center")
            with top_left:
                if st.button("New Conversation", key=f"new_conv_{bot['id']}", use_container_width=True):
                    create_new_conversation(int(bot["id"]), int(user["id"]))
                    rerun_app()

            with top_right:
                if st.button("Clear Conversation Messages", key=f"clear_conv_{bot['id']}", use_container_width=True):
                    execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
                    rerun_app()

            history_rows = get_conversation_messages(conversation_id, limit=50)
            history = [{"role": row["role"], "content": row["content"]} for row in history_rows if row["role"] in ("user", "assistant")]

            if not history:
                st.info("Start chatting to test the bot live.")
            else:
                for message in history_rows:
                    role = message["role"]
                    if role in ("user", "assistant"):
                        with st.chat_message(role):
                            st.markdown(message["content"])

            user_prompt = st.chat_input(f"Ask {bot['name']} something...")
            if user_prompt:
                append_message(conversation_id, "user", user_prompt)
                with st.chat_message("user"):
                    st.markdown(user_prompt)

                api_key = get_bot_api_key(bot)
                if not api_key:
                    assistant_error = (
                        "Missing OpenAI API Key. Add a per-bot key in System Prompt, or set OPENAI_API_KEY in environment/secrets."
                    )
                    with st.chat_message("assistant"):
                        st.error(assistant_error)
                    append_message(conversation_id, "assistant", assistant_error)
                    rerun_app()
                else:
                    try:
                        reply = generate_assistant_reply(
                            bot=bot,
                            history=history + [{"role": "user", "content": user_prompt}],
                            api_key=api_key,
                        )
                        with st.chat_message("assistant"):
                            st.markdown(reply)
                        append_message(conversation_id, "assistant", reply)
                        rerun_app()
                    except Exception as exc:
                        error_message = f"API Error: {exc}"
                        with st.chat_message("assistant"):
                            st.error(error_message)
                        append_message(conversation_id, "assistant", error_message)
                        rerun_app()

    with tab3:
        with st.container(border=True):
            st.markdown('<div class="section-title">Production Deployment</div>', unsafe_allow_html=True)
            st.caption("Copy this snippet into your website.")
            embed_code = (
                f'<script src="{BOT_WIDGET_SCRIPT_URL}" '
                f'data-bot-id="{bot["id"]}" '
                f'data-theme="dark" defer></script>'
            )
            st.code(embed_code, language="html")
            st.info("This embed snippet should load your public chatbot widget in production.")

            st.markdown("**Recommended attributes**")
            st.write(f"- `data-bot-id=\"{bot['id']}\"`")
            st.write("- `data-theme=\"dark\"`")
            st.write("- Add any additional custom widget attributes your front-end loader supports.")

    with tab4:
        with st.container(border=True):
            st.markdown('<div class="section-title">Widget Preview</div>', unsafe_allow_html=True)
            st.caption("Visual preview of the embedded widget layout.")
            components.html(build_widget_preview_html(bot), height=560, scrolling=False)


def render_admin(user: Dict[str, Any]) -> None:
    if user["role"] != "admin":
        st.warning("You do not have permission to access Admin.")
        return

    render_page_heading("Administration", "Manage users, roles, access, and workspace operations.")

    user_count = int(scalar("SELECT COUNT(*) AS c FROM users") or 0)
    admin_count = int(scalar("SELECT COUNT(*) AS c FROM users WHERE role = 'admin'") or 0)
    bot_count = int(scalar("SELECT COUNT(*) AS c FROM chatbots") or 0)
    doc_count = int(scalar("SELECT COUNT(*) AS c FROM kb_documents") or 0)
    msg_count = int(scalar("SELECT COUNT(*) AS c FROM messages") or 0)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card("Users", str(user_count), "Workspace accounts")
    with c2:
        render_metric_card("Admins", str(admin_count), "Privileged accounts")
    with c3:
        render_metric_card("Bots", str(bot_count), "All chatbot projects")
    with c4:
        render_metric_card("Docs", str(doc_count), "Knowledge base items")
    with c5:
        render_metric_card("Messages", str(msg_count), "Persisted chat history")

    with st.container(border=True):
        st.markdown('<div class="section-title">Create User</div>', unsafe_allow_html=True)

        with st.form("create_user_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name")
                email = st.text_input("Email")
            with c2:
                role = st.selectbox("Role", ["member", "admin"], index=0)
                password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Create User", use_container_width=True)

        if submit:
            if not name.strip() or not email.strip() or not password:
                st.error("Please complete all fields.")
            elif get_user_by_email(email):
                st.error("A user with this email already exists.")
            else:
                create_user(name=name, email=email, password=password, role=role)
                st.success("User created successfully.")
                rerun_app()

    with st.container(border=True):
        st.markdown('<div class="section-title">Users & Access Control</div>', unsafe_allow_html=True)
        users = fetch_all("SELECT * FROM users ORDER BY id ASC")
        for u in users:
            user_id = int(u["id"])
            with st.container(border=True):
                header_cols = st.columns([2.3, 1.1, 1.1, 1.2], vertical_alignment="center")
                with header_cols[0]:
                    st.markdown(
                        f"""
                        <div style="font-weight:800; color:#ffffff;">{html_escape(u['name'])}</div>
                        <div style="color:#cbd5e1; font-size:13px;">{html_escape(u['email'])}</div>
                        <div style="color:#94a3b8; font-size:12px; margin-top:4px;">
                            Created: {html_escape(u['created_at'])}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with header_cols[1]:
                    st.markdown(f"**Role**: {html_escape(u['role'])}")
                with header_cols[2]:
                    st.markdown(f"**Status**: {'Active' if int(u['is_active']) == 1 else 'Inactive'}")
                with header_cols[3]:
                    st.markdown(f"**ID**: {user_id}")

                if user_id == int(user["id"]):
                    st.info("This is your current account. For safety, self-role/active changes are disabled.")
                    continue

                with st.form(f"user_manage_form_{user_id}"):
                    c1, c2, c3 = st.columns([1.2, 1.2, 1.6])
                    with c1:
                        role_value = st.selectbox(
                            "Role",
                            ["member", "admin"],
                            index=0 if u["role"] == "member" else 1,
                            key=f"role_{user_id}",
                        )
                    with c2:
                        active_value = st.checkbox(
                            "Active",
                            value=bool(int(u["is_active"])),
                            key=f"active_{user_id}",
                        )
                    with c3:
                        new_password = st.text_input(
                            "Reset Password (optional)",
                            type="password",
                            key=f"resetpw_{user_id}",
                            placeholder="Leave blank to keep existing password",
                        )

                    save_user = st.form_submit_button("Save Changes", use_container_width=True)

                if save_user:
                    updates = []
                    params: List[Any] = []

                    updates.append("role = ?")
                    params.append(role_value)

                    updates.append("is_active = ?")
                    params.append(1 if active_value else 0)

                    if new_password.strip():
                        updates.append("password_hash = ?")
                        params.append(hash_password(new_password.strip()))

                    updates.append("updated_at = ?")
                    params.append(now_iso())

                    params.append(user_id)

                    execute(
                        f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                        tuple(params),
                    )
                    st.success("User updated successfully.")
                    rerun_app()


# =============================================================================
# 15) MAIN APP FLOW
# =============================================================================
db_init()
init_session_state()

current_user = get_current_user()

if current_user is None:
    if bootstrap_first_admin_if_needed():
        create_first_admin_screen()
    else:
        login_screen()
    st.stop()

enforce_page_access(current_user)
render_sidebar(current_user)

menu = st.session_state.nav_page

if menu == "📊 Dashboard":
    render_dashboard(current_user)
elif menu == "🤖 My Chatbots":
    render_my_chatbots(current_user)
elif menu == "📚 Knowledge Base":
    render_knowledge_base(current_user)
elif menu == "💬 Widget Settings":
    render_widget_settings(current_user)
elif menu == "⚙️ Admin":
    render_admin(current_user)
else:
    st.session_state.nav_page = DEFAULT_PAGE
    rerun_app()


# =============================================================================
# 16) FOOTER
# =============================================================================
st.markdown(
    """
    <br>
    <hr>
    <center>
        <small style="color: #94a3b8;">
            OmniToolsPro SaaS Architecture | Chatbot Builder v4.0
        </small>
    </center>
    """,
    unsafe_allow_html=True,
)
```
