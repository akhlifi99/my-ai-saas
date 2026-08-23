import uuid
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

    /* Branding */
    .sidebar-brand {
        font-size: 20px;
        font-weight: 800;
        color: #3b82f6;
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
        margin-bottom: 24px;
        font-size: 15px;
    }

    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 8px 0;
    }

    .muted-text {
        color: #94a3b8;
    }

    /* Cards / containers */
    .metric-card,
    .bot-card,
    .section-card {
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
    .bot-card:hover,
    .section-card:hover {
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
        border: 1px solid #334155;
        color: #cbd5e1;
        font-size: 12px;
    }

    .status-dot {
        color: #10b981;
        font-weight: 800;
        margin-right: 6px;
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
        "chat_histories": {},  # per-bot chat history: {bot_id: [messages...]}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state.nav_page not in PAGES:
        st.session_state.nav_page = DEFAULT_PAGE

    # Validate active bot
    if st.session_state.active_bot_id is not None:
        if get_bot_by_id(st.session_state.active_bot_id) is None:
            st.session_state.active_bot_id = None

    # Normalize chat_histories
    if not isinstance(st.session_state.chat_histories, dict):
        st.session_state.chat_histories = {}


# =============================================================================
# 5) HELPERS
# =============================================================================
def get_bot_by_id(bot_id: str | None):
    if not bot_id:
        return None
    return next((bot for bot in st.session_state.chatbots if bot["id"] == bot_id), None)


def get_active_bot():
    return get_bot_by_id(st.session_state.active_bot_id)


def navigate_to(page: str) -> None:
    if page in PAGES:
        st.session_state.nav_page = page
        st.rerun()


def select_bot_and_open_editor(bot_id: str) -> None:
    st.session_state.active_bot_id = bot_id
    st.session_state.nav_page = "💬 Widget Settings"
    st.rerun()


def get_chat_history(bot_id: str):
    if bot_id not in st.session_state.chat_histories:
        st.session_state.chat_histories[bot_id] = []
    return st.session_state.chat_histories[bot_id]


def reset_chat_history(bot_id: str) -> None:
    st.session_state.chat_histories[bot_id] = []


def generate_assistant_reply(api_key: str, bot: dict, history: list[dict]) -> str:
    if OpenAI is None:
        raise RuntimeError(
            "The OpenAI Python SDK is not installed or could not be imported."
        )

    client = OpenAI(api_key=api_key.strip())
    messages = [{"role": "system", "content": bot["prompt"]}] + history

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
    )

    content = response.choices[0].message.content
    return content or "No response content returned by the model."


def render_metric_card(title: str, value: str, subtitle: str = "") -> None:
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <h3>{value}</h3>
            <p style="margin-top: 6px; font-size: 14px; color: #cbd5e1; font-weight: 700;">{title}</p>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_bot_card(bot: dict) -> None:
    st.markdown(
        f"""
        <div class="bot-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
                <div>
                    <div style="margin-bottom:8px;">
                        <span class="status-dot">●</span>
                        <span style="color:#10b981; font-weight:800;">Active</span>
                    </div>
                    <h3 style="margin:0; color:#ffffff; font-size:20px; font-weight:800;">{bot["name"]}</h3>
                    <div class="bot-id">ID: {bot["id"]}</div>
                </div>
            </div>
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
    st.markdown('<div class="sidebar-brand">🤖 CHATBOT BUILDER</div>', unsafe_allow_html=True)

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
            <div class="section-card">
                <div style="font-size:12px; color:#94a3b8; margin-bottom:6px;">Current Editor</div>
                <div style="font-size:16px; font-weight:800; color:#ffffff;">{active_bot["name"]}</div>
                <div class="bot-id" style="margin-top:10px;">{active_bot["id"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("⬅ Exit Editor", use_container_width=True):
            st.session_state.active_bot_id = None
            st.session_state.nav_page = "🤖 My Chatbots"
            st.rerun()
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

# =============================================================================
# 8) MAIN VIEW ROUTING
# =============================================================================
if menu == "📊 Dashboard":
    st.markdown('<div class="main-header">System Analytics</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Unified performance view across your AI agents and deployment surface.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Total Bots", str(len(st.session_state.chatbots)), "All active chatbot projects")
    with c2:
        render_metric_card("Conversations", "2,410", "Simulated monthly usage")
    with c3:
        render_metric_card("Success Rate", "97.8%", "Average task completion")

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Traffic Trend</div>', unsafe_allow_html=True)
    st.area_chart({"Inbound": [20, 35, 30, 50, 75, 60, 100]}, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "🤖 My Chatbots":
    header_col, action_col = st.columns([4, 1.2], vertical_alignment="center")
    with header_col:
        st.markdown('<div class="main-header">My Chatbots</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="main-subtitle">Create, manage, and deploy your AI agents.</div>',
            unsafe_allow_html=True,
        )

    with action_col:
        if st.button("+ New Bot", use_container_width=True):
            new_id = str(uuid.uuid4())[:8]
            st.session_state.chatbots.append(
                {
                    "id": new_id,
                    "name": f"Assistant {new_id}",
                    "prompt": "You are a professional support agent.",
                }
            )
            st.session_state.chat_histories[new_id] = []
            st.session_state.active_bot_id = new_id
            st.session_state.nav_page = "💬 Widget Settings"
            st.rerun()

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    if not st.session_state.chatbots:
        st.markdown(
            """
            <div class="section-card" style="text-align:center; padding: 70px 30px; border-style: dashed;">
                <h3 style="color:#ffffff; margin-bottom:10px;">No bots found</h3>
                <p style="color:#94a3b8; margin:0;">Click <strong>+ New Bot</strong> to get started.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for bot in st.session_state.chatbots:
            left, right = st.columns([4.5, 1.2], vertical_alignment="center")
            with left:
                render_bot_card(bot)
            with right:
                st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
                if st.button("Manage ->", key=f"manage_{bot['id']}", use_container_width=True):
                    select_bot_and_open_editor(bot["id"])

elif menu == "📚 Knowledge Base":
    st.markdown('<div class="main-header">Knowledge Base</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Paste documentation, FAQs, or website content to use as training source material.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Training Data</div>', unsafe_allow_html=True)
    st.caption("This field is stored locally in session state for the current app session.")

    kb_text = st.text_area(
        "Knowledge Base Text",
        key="knowledge_base_text",
        placeholder="Paste website content, support docs, onboarding guides, policy text, etc.",
        height=300,
        label_visibility="collapsed",
    )

    c1, c2 = st.columns([1, 5], vertical_alignment="center")
    with c1:
        train_clicked = st.button("Train Knowledge Engine", use_container_width=True)

    if train_clicked:
        if kb_text.strip():
            st.success("Successfully indexed the knowledge base for your AI bots.")
        else:
            st.warning("Please provide some text to train the engine.")

    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "💬 Widget Settings":
    bot = get_active_bot()

    if not bot:
        st.warning("⚠️ No active bot selected. Go to 'My Chatbots' and click 'Manage ->'.")
    else:
        st.markdown(
            f'<div class="main-header">Configuring: {bot["name"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="main-subtitle">Bot ID: {bot["id"]} — update the system prompt, test the live demo, or copy the embed snippet.</div>',
            unsafe_allow_html=True,
        )

        tab1, tab2, tab3 = st.tabs(["System Prompt", "Live Demo", "Embed Code"])

        # ---------------------------------------------------------------------
        # TAB 1: SYSTEM PROMPT
        # ---------------------------------------------------------------------
        with tab1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Bot Configuration</div>', unsafe_allow_html=True)

            name_key = f"bot_name_{bot['id']}"
            prompt_key = f"bot_prompt_{bot['id']}"

            if name_key not in st.session_state:
                st.session_state[name_key] = bot["name"]
            if prompt_key not in st.session_state:
                st.session_state[prompt_key] = bot["prompt"]
            if "api_key" not in st.session_state:
                st.session_state.api_key = ""

            bot_name = st.text_input("Bot Label", key=name_key)
            bot_prompt = st.text_area(
                "System Prompt",
                key=prompt_key,
                height=220,
                placeholder="Define the assistant's behavior, tone, constraints, and knowledge boundaries.",
            )
            api_key = st.text_input(
                "OpenAI API Key",
                key="api_key",
                type="password",
                placeholder="sk-...",
            )

            bot["name"] = bot_name.strip() if bot_name.strip() else bot["name"]
            bot["prompt"] = bot_prompt
            st.caption("Changes are persisted in session state immediately.")

            st.markdown("</div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # TAB 2: LIVE DEMO
        # ---------------------------------------------------------------------
        with tab2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="section-title">Sandbox Chat for {bot["name"]}</div>',
                unsafe_allow_html=True,
            )
            st.caption("Test the chatbot using the current system prompt and API key.")

            history = get_chat_history(bot["id"])

            if st.button("Clear Chat History", key=f"clear_chat_{bot['id']}"):
                reset_chat_history(bot["id"])
                st.rerun()

            # Render existing messages
            for message in history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

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
                    except Exception as e:
                        error_message = f"API Error: {str(e)}"
                        with st.chat_message("assistant"):
                            st.error(error_message)
                        history.append({"role": "assistant", "content": error_message})

            st.markdown("</div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # TAB 3: EMBED CODE
        # ---------------------------------------------------------------------
        with tab3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Production Deployment</div>', unsafe_allow_html=True)
            st.caption("Copy and paste this snippet into your website.")
            embed_code = (
                f'<script src="https://chatbotbuilder.io/js/widget.js" '
                f'data-id="{bot["id"]}" defer></script>'
            )
            st.code(embed_code, language="html")
            st.info("Use this widget snippet in your production site once the bot is configured.")
            st.markdown("</div>", unsafe_allow_html=True)

elif menu == "⚙️ Admin":
    st.markdown('<div class="main-header">Administration</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Manage plan details, usage, and enterprise controls.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Plan & Usage</div>', unsafe_allow_html=True)
    st.write("Plan Status: **PRO Enterprise**")
    st.progress(0.65)
    st.write("Monthly Token Usage: **650 / 1000**")

    if st.button("Billing Portal"):
        st.info("Billing portal action triggered. Connect this button to your billing provider.")
    st.markdown("</div>", unsafe_allow_html=True)

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
