import streamlit as st
import openai
import uuid

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Chatbot Builder | Enterprise AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. OMNITOOLSPRO HIGH-CONTRAST DARK THEME ---
# We use double curly braces {{ }} to prevent f-string conflicts with CSS
st.markdown(f"""
    <style>
    /* Unified Deep Navy-Purple Background */
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], 
    [data-testid="stSidebar"], 
    [data-testid="stSidebarContent"],
    .main {{
        background-color: #0f172a !important;
        color: #ffffff !important;
    }}

    /* Sidebar Border & Styling */
    [data-testid="stSidebar"] {{
        border-right: 1px solid #1e293b !important;
    }}

    /* Branding Header */
    .sidebar-brand {{
        font-size: 20px;
        font-weight: 800;
        color: #3b82f6;
        padding: 25px 0px;
        text-align: center;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 20px;
        letter-spacing: 1px;
    }}

    /* Elevated Card Containers */
    .metric-card, .bot-card {{
        background-color: #1a233a;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }}
    
    .bot-card:hover {{
        border-color: #3b82f6;
        transform: translateY(-2px);
    }}

    /* Typography */
    .main-header {{
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 8px;
    }}
    .main-subtitle {{
        color: #94a3b8;
        margin-bottom: 32px;
    }}

    /* Vibrant Blue Action Buttons */
    .stButton > button {{
        background-color: #1d4ed8 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 0.6rem 2.2rem !important;
        transition: 0.3s;
    }}
    
    .stButton > button:hover {{
        background-color: #2563eb !important;
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.4);
    }}

    /* Navigation Radio Overrides */
    div[role="radiogroup"] > label {{
        color: #94a3b8 !important;
        background-color: transparent !important;
        padding: 10px 15px !important;
        border-radius: 8px !important;
    }}
    div[role="radiogroup"] > label:hover {{
        color: #ffffff !important;
        background-color: #1e293b !important;
    }}
    div[role="radiogroup"] > label[data-checked="true"] {{
        background-color: #1d4ed8 !important;
        color: white !important;
    }}

    /* Chat & Input Styling */
    [data-testid="stChatMessage"] {{
        background-color: #1a233a !important;
        border: 1px solid #334155 !important;
    }}
    .stTextInput input, .stTextArea textarea {{
        background-color: #0f172a !important;
        color: white !important;
        border: 1px solid #334155 !important;
    }}

    /* Hide Default Streamlit Elements */
    #MainMenu, footer, header {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE AUDIT & INITIALIZATION ---
if "chatbots" not in st.session_state:
    st.session_state.chatbots = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "active_bot_id" not in st.session_state:
    st.session_state.active_bot_id = None

# --- 4. HELPER FUNCTIONS ---
def get_bot_by_id(bot_id):
    return next((bot for bot in st.session_state.chatbots if bot['id'] == bot_id), None)

def manage_bot(bot_id):
    st.session_state.active_bot_id = bot_id
    st.session_state.messages = []  # Reset sandbox for new bot
    # We don't need a rerun here because the next radio button logic will catch the change

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🤖 CHATBOT BUILDER</div>', unsafe_allow_html=True)
    
    # Navigation Logic
    menu_options = ["📊 Dashboard", "🤖 My Chatbots", "📚 Knowledge Base", "💬 Widget Settings", "⚙️ Admin"]
    
    # Auto-switch to "Widget Settings" if an active bot is selected via "Manage" button
    default_index = 0
    if st.session_state.active_bot_id:
        default_index = 3 # Index of Widget Settings

    menu = st.radio("MAIN NAV", menu_options, label_visibility="collapsed", index=default_index)

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.session_state.active_bot_id:
        if st.button("⬅ Back to Dashboard"):
            st.session_state.active_bot_id = None
            st.rerun()

# --- 6. MAIN VIEW ROUTING ---

# --- PAGE: DASHBOARD ---
if menu == "📊 Dashboard":
    st.markdown('<div class="main-header">System Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Overview of your AI performance and active agents.</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><h3>{len(st.session_state.chatbots)}</h3>Active Chatbots</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><h3>2,104</h3>Total Conversations</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><h3>98.2%</h3>AI Accuracy</div>', unsafe_allow_html=True)
    
    st.area_chart({"Inquiries": [15, 30, 25, 45, 60, 55, 90]})

# --- PAGE: MY CHATBOTS ---
elif menu == "🤖 My Chatbots":
    col_t, col_a = st.columns([4, 1.2])
    with col_t:
        st.markdown('<div class="main-header">My Chatbots</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-subtitle">Create and manage your AI assistants.</div>', unsafe_allow_html=True)
    with col_a:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("+ New Chatbot"):
            new_id = str(uuid.uuid4())[:8]
            st.session_state.chatbots.append({
                "id": new_id,
                "name": f"Assistant {new_id}",
                "prompt": "You are a helpful customer support agent."
            })
            st.rerun()

    if not st.session_state.chatbots:
        st.markdown("""
            <div style="text-align: center; padding: 80px; background: #1a233a; border: 2px dashed #334155; border-radius: 20px;">
                <h3 style="color: #94a3b8;">No Chatbots Created</h3>
                <p>Click '+ New Chatbot' to get started on your first AI agent.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        for bot in st.session_state.chatbots:
            with st.container():
                ci, ca = st.columns([4, 1])
                with ci:
                    st.markdown(f"""
                        <div class="bot-card">
                            <span style="color: #10b981; font-weight: bold;">● Active</span>
                            <h3 style="margin: 0; color: white;">{bot['name']}</h3>
                            <code style="color: #3b82f6; background: transparent;">ID: {bot['id']}</code>
                        </div>
                    """, unsafe_allow_html=True)
                with ca:
                    st.write("<br><br>", unsafe_allow_html=True)
                    # FIX: Click sets state and prompts user to move to settings
                    if st.button("Manage →", key=f"btn_{bot['id']}"):
                        st.session_state.active_bot_id = bot['id']
                        st.session_state.messages = []
                        st.rerun()

# --- PAGE: KNOWLEDGE BASE ---
elif menu == "📚 Knowledge Base":
    st.markdown('<div class="main-header">Knowledge Base</div>', unsafe_allow_html=True)
    st.markdown('<div class="bot-card">', unsafe_allow_html=True)
    kb_data = st.text_area("Paste Content", placeholder="Enter documentation, FAQs, or company info here...", height=300)
    if st.button("Train Knowledge Engine"):
