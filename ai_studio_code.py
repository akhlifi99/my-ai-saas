from __future__ import annotations

import uuid
from html import escape as html_escape
from typing import Dict, List, Optional

import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# =============================================================================
# 1) PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Chatbot Builder | Enterprise",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# 2) THEME: OMNITOOLSPRO (DEEP NAVY-PURPLE)
# =============================================================================
st.markdown(
    """
<style>
    /* App shell */
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    .main {
        background-color: #0f172a !important;
        color: #ffffff !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        border-right: 1px solid #1e293b !important;
    }

    /* Hide default header/footer */
    #MainMenu, footer, header {
        visibility: hidden;
    }

    /* Global typography */
    html, body, [class*="css"] {
        color: #ffffff !important;
    }

    /* Sidebar branding */
    .sidebar-brand {
        font-size: 20px;
        font-weight: 800;
        color: #ffffff;
        padding: 24px 0 18px 0;
        text-align: center;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 18px;
        letter-spacing: 1px;
    }

    /* Headers */
    .main-header {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 8px;
        line-height: 1.15;
    }

    .main-subtitle {
        color: #94a3b8;
        margin-bottom: 22px;
        font-size: 15px;
    }

    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 10px 0;
    }

    .muted-text {
        color: #94a3b8;
    }

    /* Cards / containers */
    .metric-card,
    .bot-card {
        background: #1a233a;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 16px;
        color: #ffffff;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18);
        transition: all 0.25s ease;
    }

    .metric-card:hover,
    .bot-card:hover {
        border-color: #3b82f6;
        transform: translateY(-1px);
    }

    .metric-card h3 {
        margin: 0;
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
    }

    .metric-card p,
    .bot-card p {
        margin: 0;
        color: #cbd5e1;
    }

    .bot-id {
        display: inline-block;
        margin-top: 10px;
        padding: 4px 10px;
        border-radius: 999px;
        background: #0f172a;
        border: 1px solid #334155;
        color: #cbd5e1;
        font-size: 12px;
        word-break: break-all;
    }

    .status-dot {
        color: #10b981;
        font-weight: 800;
        margin-right: 6px;
    }

    /* Better native container styling */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #1a233a !important;
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18) !important;
        padding: 18px !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #3b82f6 !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.62rem 1.1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }

    .stButton > button:hover {
        background-color: #2563eb !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.28) !important;
    }

    .stButton > button:focus {
        outline: none !important;
    }

    /* Primary buttons */
    button[kind="primary"] {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
    }

    /* Inputs */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div,
    .stMultiselect div {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #64748b !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        color: #cbd5e1 !important;
        background: transparent !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 2px solid #3b82f6 !important;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: #1a233a !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }

    /* Horizontal rule */
    hr {
        border-color: #1e293b !important;
    }

    /* Streamlit links */
    a {
        color: #60a5fa !important;
    }

    /* Sidebar radio labels */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        color: #e2e8f0 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# 3) CONSTANTS
# =============================================================================
PAGES = [
    "📊 Dashboard",
    "🤖 My Chatbots",
    "📚 Knowledge Base",
    "💬 Widget Settings",
    "⚙️ Admin",
]

DEFAULT_PAGE = "📊 Dashboard"
DEFAULT_MODEL = "gpt-4o-mini"


# =============================================================================
# 4) SESSION STATE INITIALIZATION
# =============================================================================
def init_session_state() -> None:
    defaults = {
        "chatbots": [],
        "active_bot_id": None,
        "nav_page": DEFAULT_PAGE,
        "api_key": "",
        "knowledge_base_text": "",
        "knowledge_base_indexed": False,
        "knowledge_base_word_count": 0,
        "chat_histories": {},  # {bot_id: [messages]}
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state.nav_page not in PAGES:
        st.session_state.nav_page = DEFAULT_PAGE

    if not isinstance(st.session_state.chatbots, list):
        st.session_state.chatbots = []

    if not isinstance(st.session_state.chat_histories, dict):
        st.session_state.chat_histories = {}

    if st.session_state.active_bot_id is not None:
        if get_bot_by_id(st.session_state.active_bot_id) is None:
            st.session_state.active_bot_id = None


# =============================================================================
# 5) HELPERS
# =============================================================================
def request_rerun() -> None:
    """Compatibility-safe rerun helper."""
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()


def get_bot_by_id(bot_id: Optional[str]):
    if not bot_id:
        return None
    return next((bot for bot in st.session_state.chatbots if bot["id"] == bot_id), None)


def get_active_bot():
    return get_bot_by_id(st.session_state.active_bot_id)


def navigate_to(page: str) -> None:
    if page in PAGES:
        st.session_state.nav_page = page
        request_rerun()


def select_bot_and_open_editor(bot_id: str) -> None:
    bot = get_bot_by_id(bot_id)
    if bot is None:
        st.warning("The selected chatbot no longer exists.")
        return

    st.session_state.active_bot_id = bot_id
    st.session_state.nav_page = "💬 Widget Settings"
    request_rerun()


def create_new_bot() -> dict:
    new_id = str(uuid.uuid4())[:8]
    bot = {
        "id": new_id,
        "name": f"Assistant {new_id}",
        "prompt": "You are a professional support agent.",
    }
    st.session_state.chatbots.append(bot)
    st.session_state.chat_histories[new_id] = []
    st.session_state.active_bot_id = new_id
    st.session_state.nav_page = "💬 Widget Settings"
    return bot


def get_chat_history(bot_id: str) -> List[dict]:
    if bot_id not in st.session_state.chat_histories:
        st.session_state.chat_histories[bot_id] = []
    return st.session_state.chat_histories[bot_id]


def reset_chat_history(bot_id: str) -> None:
    st.session_state.chat_histories[bot_id] = []


def generate_assistant_reply(api_key: str, bot: dict, history: List[dict]) -> str:
    if OpenAI is None:
        raise RuntimeError(
            "The OpenAI Python SDK is not installed. Install it with: pip install openai"
        )

    client = OpenAI(api_key=api_key.strip())

    messages = [{"role": "system", "content": bot.get("prompt", "")}] + history

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
    )

    content = response.choices[0].message.content
    return content or "No response content returned by the model."


def render_metric_card(title: str, value: str, subtitle: str = "") -> None:
    title_safe = html_escape(title)
    value_safe = html_escape(value)
    subtitle_html = f"<p style='margin-top:8px;'>{html_escape(subtitle)}</p>" if subtitle else ""

    st.markdown(
        f"""
        <div class="metric-card">
            <h3>{value_safe}</h3>
            <p style="margin-top: 6px; font-size: 14px; color: #cbd5e1; font-weight: 700;">{title_safe}</p>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_bot_card(bot: dict) -> None:
    bot_name = html_escape(str(bot.get("name", "Unnamed Bot")))
    bot_id = html_escape(str(bot.get("id", "")))

    st.markdown(
        f"""
        <div class="bot-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
                <div style="width:100%;">
                    <div style="margin-bottom:8px;">
                        <span class="status-dot">●</span>
                        <span style="color:#10b981; font-weight:800;">Active</span>
                    </div>
                    <h3 style="margin:0; color:#ffffff; font-size:20px; font-weight:800;">{bot_name}</h3>
                    <div class="bot-id">ID: {bot_id}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_heading(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="main-header">{html_escape(title)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-subtitle">{html_escape(subtitle)}</div>', unsafe_allow_html=True)


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


# =============================================================================
# 6) INIT STATE
# =============================================================================
init_session_state()


# =============================================================================
# 7) SIDEBAR NAVIGATION
# =============================================================================
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">🤖 OMNITOOLSPRO</div>',
        unsafe_allow_html=True,
    )

    menu = st.radio(
        "Navigation",
        PAGES,
        label_visibility="collapsed",
        key="nav_page",
    )

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    active_bot = get_active_bot()
    if active_bot:
        st.markdown(
            f"""
            <div class="bot-card">
                <div style="font-size:12px; color:#94a3b8; margin-bottom:6px;">Current Editor</div>
                <div style="font-size:16px; font-weight:800; color:#ffffff;">{html_escape(active_bot["name"])}</div>
                <div class="bot-id" style="margin-top:10px;">{html_escape(active_bot["id"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("⬅ Exit Editor", use_container_width=True):
            st.session_state.active_bot_id = None
            st.session_state.nav_page = "🤖 My Chatbots"
            request_rerun()
    else:
        st.markdown(
            """
            <div class="bot-card">
                <div style="font-size:12px; color:#94a3b8; margin-bottom:6px;">Current Editor</div>
                <div style="font-size:16px; font-weight:700; color:#cbd5e1;">No bot selected</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# 8) MAIN VIEW ROUTING
# =============================================================================
if menu == "📊 Dashboard":
    render_page_heading(
        "System Analytics",
        "Unified performance view across your AI agents and deployment surface.",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card(
            "Total Bots",
            str(len(st.session_state.chatbots)),
            "All active chatbot projects",
        )
    with c2:
        render_metric_card(
            "Conversations",
            "2,410",
            "Simulated monthly usage",
        )
    with c3:
        render_metric_card(
            "Success Rate",
            "97.8%",
            "Average task completion",
        )

    with st.container(border=True):
        st.markdown('<div class="section-title">Traffic Trend</div>', unsafe_allow_html=True)
        st.caption("Illustrative usage trend for the current workspace.")
        st.area_chart(
            {"Inbound": [20, 35, 30, 50, 75, 60, 100]},
            use_container_width=True,
        )

elif menu == "🤖 My Chatbots":
    header_col, action_col = st.columns([4, 1.2], vertical_alignment="center")

    with header_col:
        render_page_heading(
            "My Chatbots",
            "Create, manage, and deploy your AI agents.",
        )

    with action_col:
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        if st.button("+ New Bot", use_container_width=True):
            create_new_bot()
            request_rerun()

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    if not st.session_state.chatbots:
        render_empty_state(
            "No bots found",
            "Click + New Bot to get started.",
        )
    else:
        for bot in st.session_state.chatbots:
            with st.container(border=True):
                left, right = st.columns([4.5, 1.2], vertical_alignment="center")
                with left:
                    render_bot_card(bot)
                with right:
                    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
                    if st.button(
                        "Manage ->",
                        key=f"manage_{bot['id']}",
                        use_container_width=True,
                    ):
                        select_bot_and_open_editor(bot["id"])

elif menu == "📚 Knowledge Base":
    render_page_heading(
        "Knowledge Base",
        "Paste documentation, FAQs, or website content to use as training source material.",
    )

    with st.container(border=True):
        st.markdown('<div class="section-title">Training Data</div>', unsafe_allow_html=True)
        st.caption("This field is stored locally in session state for the current app session.")

        kb_text = st.text_area(
            "Knowledge Base Text",
            key="knowledge_base_text",
            placeholder="Paste website content, support docs, onboarding guides, policy text, etc.",
            height=300,
            label_visibility="collapsed",
        )

        btn_col, status_col = st.columns([1.4, 4.6], vertical_alignment="center")
        with btn_col:
            train_clicked = st.button("Train Knowledge Engine", use_container_width=True)

        with status_col:
            if st.session_state.knowledge_base_indexed:
                st.success(
                    f"Knowledge base indexed successfully: {st.session_state.knowledge_base_word_count} words loaded."
                )

        if train_clicked:
            if kb_text.strip():
                word_count = len(kb_text.split())
                st.session_state.knowledge_base_indexed = True
                st.session_state.knowledge_base_word_count = word_count
                st.success(f"Successfully indexed the knowledge base ({word_count} words).")
            else:
                st.warning("Please provide some text to train the engine.")

elif menu == "💬 Widget Settings":
    bot = get_active_bot()

    if not bot:
        st.warning("⚠️ No active bot selected. Go to 'My Chatbots' and click 'Manage ->'.")
    else:
        render_page_heading(
            f"Configuring: {bot['name']}",
            f"Bot ID: {bot['id']} — update the system prompt, test the live demo, or copy the embed snippet.",
        )

        tab1, tab2, tab3 = st.tabs(["System Prompt", "Live Demo", "Embed Code"])

        # ---------------------------------------------------------------------
        # TAB 1: SYSTEM PROMPT
        # ---------------------------------------------------------------------
        with tab1:
            with st.container(border=True):
                st.markdown('<div class="section-title">Bot Configuration</div>', unsafe_allow_html=True)

                name_key = f"bot_name_{bot['id']}"
                prompt_key = f"bot_prompt_{bot['id']}"

                if name_key not in st.session_state:
                    st.session_state[name_key] = bot["name"]

                if prompt_key not in st.session_state:
                    st.session_state[prompt_key] = bot["prompt"]

                bot_name = st.text_input("Bot Label", key=name_key)
                bot_prompt = st.text_area(
                    "System Prompt",
                    key=prompt_key,
                    height=220,
                    placeholder="Define the assistant's behavior, tone, constraints, and knowledge boundaries.",
                )

                st.text_input(
                    "OpenAI API Key",
                    key="api_key",
                    type="password",
                    placeholder="sk-...",
                )

                clean_name = bot_name.strip()
                if clean_name:
                    bot["name"] = clean_name
                bot["prompt"] = bot_prompt

                st.caption("Changes are persisted in session state immediately.")

        # ---------------------------------------------------------------------
        # TAB 2: LIVE DEMO
        # ---------------------------------------------------------------------
        with tab2:
            with st.container(border=True):
                st.markdown(
                    f'<div class="section-title">Sandbox Chat for {html_escape(bot["name"])}</div>',
                    unsafe_allow_html=True,
                )
                st.caption("Test the chatbot using the current system prompt and API key.")

                history = get_chat_history(bot["id"])

                clear_col, _ = st.columns([1.4, 5.6], vertical_alignment="center")
                with clear_col:
                    if st.button("Clear Chat History", key=f"clear_chat_{bot['id']}", use_container_width=True):
                        reset_chat_history(bot["id"])
                        request_rerun()

                # Render existing messages
                for message in history:
                    role = message.get("role", "assistant")
                    content = message.get("content", "")
                    with st.chat_message(role):
                        st.markdown(content)

                user_prompt = st.chat_input(f"Ask {bot['name']} something...")
                if user_prompt:
                    history.append({"role": "user", "content": user_prompt})

                    with st.chat_message("user"):
                        st.markdown(user_prompt)

                    if not st.session_state.api_key.strip():
                        assistant_error = "Missing OpenAI API Key. Add it in the System Prompt tab."
                        with st.chat_message("assistant"):
                            st.error(assistant_error)
                        history.append({"role": "assistant", "content": assistant_error})
                    else:
                        try:
                            reply = generate_assistant_reply(
                                api_key=st.session_state.api_key,
                                bot=bot,
                                history=history,
                            )
                            with st.chat_message("assistant"):
                                st.markdown(reply)
                            history.append({"role": "assistant", "content": reply})
                        except Exception as exc:
                            error_message = f"API Error: {str(exc)}"
                            with st.chat_message("assistant"):
                                st.error(error_message)
                            history.append({"role": "assistant", "content": error_message})

        # ---------------------------------------------------------------------
        # TAB 3: EMBED CODE
        # ---------------------------------------------------------------------
        with tab3:
            with st.container(border=True):
                st.markdown('<div class="section-title">Production Deployment</div>', unsafe_allow_html=True)
                st.caption("Copy and paste this snippet into your website.")

                embed_code = (
                    f'<script src="https://chatbotbuilder.io/js/widget.js" '
                    f'data-id="{bot["id"]}" defer></script>'
                )
                st.code(embed_code, language="html")
                st.info("Use this widget snippet in your production site once the bot is configured.")

elif menu == "⚙️ Admin":
    render_page_heading(
        "Administration",
        "Manage plan details, usage, and enterprise controls.",
    )

    with st.container(border=True):
        st.markdown('<div class="section-title">Plan & Usage</div>', unsafe_allow_html=True)
        st.write("Plan Status: **PRO Enterprise**")
        st.progress(0.65)
        st.write("Monthly Token Usage: **650 / 1000**")

        if st.button("Billing Portal"):
            st.info("Billing portal action triggered. Connect this button to your billing provider.")


# =============================================================================
# 9) FOOTER
# =============================================================================
st.markdown(
    """
    <br>
    <hr>
    <center>
        <small style="color: #94a3b8;">
            OmniTools SaaS Architecture | Chatbot Builder v3.1
        </small>
    </center>
    """,
    unsafe_allow_html=True,
)
