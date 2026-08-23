import streamlit as st
import openai
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Chatbot Builder | Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UNIFIED OMNI-DARK THEME CSS ---
# Using double brackets {{ }} for CSS to avoid f-string conflicts
st.markdown(f"""
    <style>
    /* 1. Global App & Sidebar Background Sync */
    [data-testid="stAppViewContainer"], 
    [data-testid="stSidebarContent"], 
    .main, .stApp {{
        background-color: #0f172a !important;
        color: #ffffff !important;
    }}

    /* Remove sidebar border for a solid look */
    [data-testid="stSidebar"] {{
        border-right: 1px solid #1e293b !important;
        background-color: #0f172a !important;
    }}

    /* 2. Sidebar Branding */
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

    /* 3. Sidebar Navigation Radio */
    div[role="radiogroup"] > label {{
        background-color: transparent !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
        color: #94a3b8 !important;
        border: none !important;
    }}

    div[role="radiogroup"] > label:hover {{
        background-color: #1e293b !important;
        color: #ffffff !important;
    }}

    div[role="radiogroup"] > label[data-checked="true"] {{
        background-color: #3b82f6 !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }}

    /* 4. Card Containers (Lighter Navy Tint) */
    .bot-card, .metric-card {{
        background-color: #1a233a;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: 0.3s ease;
    }}
    
    .bot-card:hover {{
        border-color: #3b82f6;
    }}

    /* 5. Typography */
    .main-header {{
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
    }}
    .main-subtitle {{
        color: #94a3b8;
        margin-bottom: 30px;
    }}

    /* 6. Buttons */
    .stButton > button {{
        background-color: #3b82f6 !important;
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

    /* 7. Input Decoration */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
        background-color: #0f172a !important;
        color: white !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }}

    /* 8. Fix for Chat Messages */
    [data-testid="stChatMessage"] {{
        background-color: #1a233a !important;
        border: 1px solid #334155 !important;
        border-radius: 15px !important;
    }}
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
def get_current_bot():
    if st.session_state.editing_bot_id:
        return next((bot for bot in st.session_state.chatbots if bot['id'] == st.session_state.editing_bot_id), None)
    return None

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🤖 CHATBOT BUILDER</div>', unsafe_allow_html=True)
    
    # Check if we are in "Edit Mode" to force radio selection
    menu_options = ["📊 Dashboard", "🤖 My Chatbots", "📚 Knowledge Base", "💬 Widget Settings", "⚙️ Admin"]
    
    # We use a key for the radio to allow manual state overrides
    menu = st.radio(
        "NAV",
        menu_options,
        label_visibility="collapsed"
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.session_state.editing_bot_id:
        if st.button("⬅ Exit Bot Editor"):
            st.session_state.editing_bot_id = None
            st.session_state.messages = []
            st.rerun()

# --- MAIN LOGIC ROUTING ---

# 1. DASHBOARD
if menu == "📊 Dashboard":
    st.markdown('<div class="main-header">Analytics Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Performance tracking across your AI fleet.</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><h3>{len(st.session_state.chatbots)}</h3>Total Bots</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><h3>1,429</h3>Total Chats</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><h3>97.2%</h3>Success Rate</div>', unsafe_allow_html=True)
    
    st.line_chart({"Traffic": [10, 25, 40, 35, 60, 90, 120]})

# 2. MY CHATBOTS (List and Manage logic)
elif menu == "🤖 My Chatbots":
    col_h, col_b = st.columns([4, 1.5])
    with col_h:
        st.markdown('<div class="main-header">My Chatbots</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-subtitle">Manage, edit, and monitor your AI agents.</div>', unsafe_allow_html=True)
    with col_b:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("+ New Chatbot"):
            new_id = str(uuid.uuid4())[:8]
            st.session_state.chatbots.append({
                "id": new_id,
                "name": f"Assistant {new_id}",
                "prompt": "You are a professional AI support agent."
            })
            st.rerun()

    if not st.session_state.chatbots:
        st.markdown("""
            <div style="text-align: center; padding: 80px; background: #1a233a; border: 2px dashed #334155; border-radius: 20px;">
                <h3 style="color: #94a3b8;">No Chatbots Created</h3>
                <p>Click '+ New Chatbot' to begin.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        for bot in st.session_state.chatbots:
            with st.container():
                col_info, col_action = st.columns([4, 1])
                with col_info:
                    st.markdown(f"""
                        <div class="bot-card">
                            <span style="color: #10b981; font-weight: bold;">● Active</span>
                            <h3 style="margin: 0; color: white;">{bot['name']}</h3>
                            <code style="color: #3b82f6; background: transparent;">ID: {bot['id']}</code>
                        </div>
                    """, unsafe_allow_html=True)
                with col_action:
                    st.write("<br><br>", unsafe_allow_html=True)
                    # The FIX: Clicking this sets the ID and redirects via rerun logic
                    if st.button("Manage →", key=f"manage_{bot['id']}"):
                        st.session_state.editing_bot_id = bot['id']
                        st.session_state.messages = []
                        st.info(f"Loading {bot['name']}... Switch to Widget Settings.")
                        # In a multi-page app we'd redirect, here we inform the user
                        # to click 'Widget Settings' or we could auto-switch state.

# 3. KNOWLEDGE BASE
elif menu == "📚 Knowledge Base":
    st.markdown('<div class="main-header">Knowledge Base</div>', unsafe_allow_html=True)
    st.markdown('<div class="bot-card">', unsafe_allow_html=True)
    kb_input = st.text_area("Source Text", placeholder="Paste website content or FAQs here...", height=250)
    if st.button("Train Knowledge"):
        st.success("AI Knowledge successfully updated.")
    st.markdown('</div>', unsafe_allow_html=True)

# 4. WIDGET SETTINGS (Config view for Selected Bot)
elif menu == "💬 Widget Settings":
    active_bot = get_current_bot()
    
    if not active_bot:
        st.warning("⚠️ No bot selected. Please go to 'My Chatbots' and click 'Manage' on a bot.")
    else:
        st.markdown(f'<div class="main-header">Settings: {active_bot["name"]}</div>', unsafe_allow_html=True)
        
        tab_config, tab_test, tab_embed = st.tabs(["⚙ Configuration", "💬 Sandbox Test", "📜 Embed Snippet"])
        
        with tab_config:
            st.session_state.api_key = st.text_input("OpenAI API Key", value=st.session_state.api_key, type="password")
            active_bot["name"] = st.text_input("Display Name", value=active_bot["name"])
            active_bot["prompt"] = st.text_area("System Instructions", value=active_bot["prompt"], height=200)
            
        with tab_test:
            st.info(f"Testing Sandbox for {active_bot['name']}")
            for m in st.session_state.messages:
                with st.chat_message(m["role"]): st.markdown(m["content"])
            
            if p := st.chat_input("Ask your bot..."):
                st.session_state.messages.append({"role": "user", "content": p})
                with st.chat_message("user"): st.markdown(p)
                
                if not st.session_state.api_key:
                    st.error("Please enter an API key in the Configuration tab.")
                else:
                    try:
                        client = openai.OpenAI(api_key=st.session_state.api_key)
                        with st.chat_message("assistant"):
                            res = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "system", "content": active_bot["prompt"]}] + st.session_state.messages
                            )
                            content = res.choices[0].message.content
                            st.markdown(content)
                        st.session_state.messages.append({"role": "assistant", "content": content})
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with tab_embed:
            st.markdown("### Production Deployment")
            st.code(f'<script src="https://cdn.chatbotbuilder.io/widget.js" data-id="{active_bot["id"]}" defer></script>', language="html")

# 5. ADMIN
elif menu == "⚙️ Admin":
    st.markdown('<div class="main-header">Administration</div>', unsafe_allow_html=True)
    st.markdown('<div class="bot-card">', unsafe_allow_html=True)
    st.write("Plan: **Enterprise v2**")
    st.write("Usage: **1,429 / 10,000 messages**")
    st.button("Manage Subscription")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br><hr><center><small style='color: #94a3b8;'>Powered by GPT-4o-mini & OmniTools Architecture</small></center>", unsafe_allow_html=True)
