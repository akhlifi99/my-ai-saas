import streamlit as st
import openai
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Chatbot Builder | Enterprise AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UNIFIED DEEP PURPLE THEME CSS ---
st.markdown("""
    <style>
    /* Main App & Sidebar Background Sync */
    .stApp, [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #130d24 !important;
        color: #ffffff;
    }

    /* Remove sidebar border/line for seamless look */
    [data-testid="stSidebar"] {
        border-right: 1px solid #2d2445;
    }

    /* Sidebar Branding */
    .sidebar-brand {
        font-size: 20px;
        font-weight: 800;
        color: #a78bfa;
        padding: 25px 0px;
        text-align: center;
        border-bottom: 1px solid #2d2445;
        margin-bottom: 20px;
        letter-spacing: 1px;
    }

    /* Sidebar Navigation Overrides */
    div[role="radiogroup"] > label {
        background-color: transparent !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        border: none !important;
    }

    div[role="radiogroup"] > label:hover {
        background-color: rgba(167, 139, 250, 0.1) !important;
    }

    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #1d4ed8 !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(29, 78, 216, 0.3);
    }

    /* Card Containers */
    .metric-card, .bot-card {
        background-color: #1a122e;
        border: 1px solid #352a52;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        transition: transform 0.2s ease;
    }
    
    .bot-card:hover {
        border-color: #1d4ed8;
    }

    /* Typography */
    .main-header {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
    }
    .main-subtitle {
        color: #a78bfa;
        margin-bottom: 30px;
    }

    /* Buttons */
    .stButton > button {
        background-color: #1d4ed8 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 0.6rem 2rem !important;
    }
    
    .stButton > button:hover {
        background-color: #2563eb !important;
        box-shadow: 0 10px 20px rgba(29, 78, 216, 0.4);
    }

    /* Chat Styling */
    [data-testid="stChatMessage"] {
        background-color: #241b3a !important;
        border: 1px solid #352a52 !important;
        border-radius: 15px !important;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a122e;
        color: #ffffff;
        border-radius: 8px 8px 0 0;
        border: 1px solid #352a52;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1d4ed8 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "chatbots" not in st.session_state:
    st.session_state.chatbots = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "editing_bot_id" not in st.session_state:
    st.session_state.editing_bot_id = None

# --- HELPER FUNCTIONS ---
def get_bot_by_id(bot_id):
    return next((bot for bot in st.session_state.chatbots if bot['id'] == bot_id), None)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🤖 CHATBOT BUILDER</div>', unsafe_allow_html=True)
    
    # If we are editing a bot, we might want to stay in "Widget Settings"
    default_nav = "🤖 My Chatbots" if st.session_state.editing_bot_id else "📊 Dashboard"
    
    menu = st.radio(
        "NAV",
        ["📊 Dashboard", "🤖 My Chatbots", "📚 Knowledge Base", "💬 Widget Settings", "⚙️ Admin"],
        label_visibility="collapsed",
        index=1 if st.session_state.editing_bot_id else 0
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.session_state.editing_bot_id:
        if st.button("⬅ Back to List"):
            st.session_state.editing_bot_id = None
            st.session_state.messages = []
            st.rerun()

# --- MAIN LOGIC ROUTING ---

# 1. DASHBOARD
if menu == "📊 Dashboard":
    st.markdown('<div class="main-header">Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">System-wide performance metrics.</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Bots", len(st.session_state.chatbots))
    c2.metric("Total Conversations", "1,842", "+12%")
    c3.metric("Avg. Response Time", "1.2s", "-0.1s")
    
    st.area_chart({"Chats": [10, 25, 45, 30, 60, 80, 75]})

# 2. MY CHATBOTS (List View)
elif menu == "🤖 My Chatbots":
    if st.session_state.editing_bot_id is None:
        col_h, col_b = st.columns([4, 1.2])
        with col_h:
            st.markdown('<div class="main-header">My Chatbots</div>', unsafe_allow_html=True)
            st.markdown('<div class="main-subtitle">Manage your fleet of AI assistants.</div>', unsafe_allow_html=True)
        with col_b:
            if st.button("+ New Chatbot"):
                new_bot = {
                    "id": str(uuid.uuid4())[:8],
                    "name": f"New Assistant {len(st.session_state.chatbots)+1}",
                    "prompt": "You are a helpful AI assistant.",
                    "color": "#1d4ed8"
                }
                st.session_state.chatbots.append(new_bot)
                st.rerun()

        if not st.session_state.chatbots:
            st.markdown("""
                <div style="text-align: center; padding: 100px; background: #1a122e; border: 2px dashed #352a52; border-radius: 20px;">
                    <h3 style="color: #a78bfa;">No Chatbots Found</h3>
                    <p>Create your first AI agent to see it listed here.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            for bot in st.session_state.chatbots:
                with st.container():
                    col_info, col_btn = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"""
                            <div class="bot-card">
                                <span style="color: #10b981; font-weight: bold; font-size: 12px;">● ONLINE</span>
                                <h3 style="margin: 0; color: white;">{bot['name']}</h3>
                                <code style="color: #a78bfa; background: transparent;">ID: {bot['id']}</code>
                            </div>
                        """, unsafe_allow_html=True)
                    with col_btn:
                        st.write("<br>", unsafe_allow_html=True)
                        if st.button(f"Manage →", key=f"btn_{bot['id']}"):
                            st.session_state.editing_bot_id = bot['id']
                            st.session_state.messages = [] # Clear test chat
                            st.rerun()
    else:
        # Redirect to settings view automatically if a bot is being edited
        st.info(f"Currently managing: **{get_bot_by_id(st.session_state.editing_bot_id)['name']}**")
        st.markdown("Please head to the **💬 Widget Settings** tab to configure this bot.")

# 3. KNOWLEDGE BASE
elif menu == "📚 Knowledge Base":
    st.markdown('<div class="main-header">Knowledge Base</div>', unsafe_allow_html=True)
    st.text_area("Paste Content", placeholder="Enter documentation...", height=300)
    if st.button("Train AI"):
        st.success("Indexing complete.")

# 4. WIDGET SETTINGS (The "Manage" View)
elif menu == "💬 Widget Settings":
    current_bot = get_bot_by_id(st.session_state.editing_bot_id)
    
    if not current_bot:
        st.warning("Please select a chatbot from the 'My Chatbots' list first.")
    else:
        st.markdown(f'<div class="main-header">Configure: {current_bot["name"]}</div>', unsafe_allow_html=True)
        
        t1, t2, t3 = st.tabs(["⚙ Settings", "💬 Sandbox Test", "📜 Embed Code"])
        
        with t1:
            st.session_state.api_key = st.text_input("OpenAI API Key", value=st.session_state.api_key, type="password")
            current_bot["name"] = st.text_input("Chatbot Name", value=current_bot["name"])
            current_bot["prompt"] = st.text_area("System Prompt", value=current_bot["prompt"], height=200)
            
        with t2:
            st.caption("Test your AI configuration in real-time.")
            for m in st.session_state.messages:
                with st.chat_message(m["role"]): st.markdown(m["content"])
            
            if p := st.chat_input("Type a message..."):
                st.session_state.messages.append({"role": "user", "content": p})
                with st.chat_message("user"): st.markdown(p)
                
                if st.session_state.api_key:
                    try:
                        client = openai.OpenAI(api_key=st.session_state.api_key)
                        with st.chat_message("assistant"):
                            res = client.chat.completions.create(
                                model="gpt-4o-mini", 
                                messages=[{"role": "system", "content": current_bot["prompt"]}] + st.session_state.messages
                            )
                            content = res.choices[0].message.content
                            st.markdown(content)
                        st.session_state.messages.append({"role": "assistant", "content": content})
                    except Exception as e: st.error(str(e))

        with t3:
            st.markdown("### Production Script")
            st.code(f'<script src="https://cdn.builder.io/js" data-id="{current_bot["id"]}" defer></script>', language="html")

# 5. ADMIN
elif menu == "⚙️ Admin":
    st.markdown('<div class="main-header">Admin Panel</div>', unsafe_allow_html=True)
    st.write("Subscription: **Premium Plan**")
    st.button("Manage Billing")

# --- FOOTER ---
st.markdown("<br><hr><center><small style='color: #a78bfa;'>Chatbot Builder Engine v3.0 | Deep Purple Suite</small></center>", unsafe_allow_html=True)
