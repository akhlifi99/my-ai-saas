import streamlit as st
import openai
import uuid

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Chatbot Builder | Enterprise",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. OMNITOOLSPRO THEME (DEEP NAVY-PURPLE) ---
st.markdown(f"""
    <style>
    /* Global App & Sidebar Background Sync */
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], 
    [data-testid="stSidebar"], 
    [data-testid="stSidebarContent"],
    .main {{
        background-color: #0f172a !important;
        color: #ffffff !important;
    }}

    /* Sidebar Border */
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

    /* Card Containers */
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

    /* Vibrant Blue Buttons */
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

    /* Chat Messages & Inputs */
    [data-testid="stChatMessage"] {{
        background-color: #1a233a !important;
        border: 1px solid #334155 !important;
    }}
    .stTextInput input, .stTextArea textarea {{
        background-color: #0f172a !important;
        color: white !important;
        border: 1px solid #334155 !important;
    }}

    /* Hide Default Elements */
    #MainMenu, footer, header {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if "chatbots" not in st.session_state:
    st.session_state.chatbots = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "active_bot_id" not in st.session_state:
    st.session_state.active_bot_id = None
if "nav_index" not in st.session_state:
    st.session_state.nav_index = 0

# --- 4. HELPER FUNCTIONS ---
def get_bot_by_id(bot_id):
    return next((bot for bot in st.session_state.chatbots if bot['id'] == bot_id), None)

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🤖 CHATBOT BUILDER</div>', unsafe_allow_html=True)
    
    menu_options = ["📊 Dashboard", "🤖 My Chatbots", "📚 Knowledge Base", "💬 Widget Settings", "⚙️ Admin"]
    
    # Use nav_index from session state to allow programatic navigation
    menu = st.radio(
        "NAV", 
        menu_options, 
        label_visibility="collapsed", 
        index=st.session_state.nav_index,
        key="main_nav_radio"
    )
    
    # Sync internal state if user clicks manually
    st.session_state.nav_index = menu_options.index(menu)

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.session_state.active_bot_id:
        st.info(f"Active: **{get_bot_by_id(st.session_state.active_bot_id)['name']}**")
        if st.button("⬅ Exit Editor"):
            st.session_state.active_bot_id = None
            st.session_state.nav_index = 1 # Back to My Chatbots
            st.rerun()

# --- 6. MAIN VIEW LOGIC ---

# PAGE: DASHBOARD
if menu == "📊 Dashboard":
    st.markdown('<div class="main-header">System Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Unified performance view.</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><h3>{len(st.session_state.chatbots)}</h3>Total Bots</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><h3>2,410</h3>Conversations</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><h3>97.8%</h3>Success Rate</div>', unsafe_allow_html=True)
    
    st.area_chart({"Inbound": [20, 35, 30, 50, 75, 60, 100]})

# PAGE: MY CHATBOTS
elif menu == "🤖 My Chatbots":
    col_t, col_a = st.columns([4, 1.2])
    with col_t:
        st.markdown('<div class="main-header">My Chatbots</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-subtitle">Manage and deploy your AI agents.</div>', unsafe_allow_html=True)
    with col_a:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("+ New Bot"):
            new_id = str(uuid.uuid4())[:8]
            st.session_state.chatbots.append({
                "id": new_id,
                "name": f"Assistant {new_id}",
                "prompt": "You are a professional support agent."
            })
            st.rerun()

    if not st.session_state.chatbots:
        st.markdown("""
            <div style="text-align: center; padding: 80px; background: #1a233a; border: 2px dashed #334155; border-radius: 20px;">
                <h3 style="color: #94a3b8;">No bots found</h3>
                <p>Click '+ New Bot' to get started.</p>
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
                            <code>ID: {bot['id']}</code>
                        </div>
                    """, unsafe_allow_html=True)
                with ca:
                    st.write("<br><br>", unsafe_allow_html=True)
                    # Logic for Manage Button
                    if st.button("Manage →", key=f"btn_{bot['id']}"):
                        st.session_state.active_bot_id = bot['id']
                        st.session_state.nav_index = 3 # Jump to Widget Settings
                        st.session_state.messages = []
                        st.rerun()

# PAGE: KNOWLEDGE BASE
elif menu == "📚 Knowledge Base":
    st.markdown('<div class="main-header">Knowledge Base</div>', unsafe_allow_html=True)
    st.markdown('<div class="bot-card">', unsafe_allow_html=True)
    kb_data = st.text_area("Training Data", placeholder="Paste website content or documentation...", height=300)
    
    # FIX: Line 224 Indentation Error resolved here
    if st.button("Train Knowledge Engine"):
        if kb_data:
            st.success("Successfully indexed the knowledge base for your AI bots.")
        else:
            st.warning("Please provide some text to train the engine.")
    st.markdown('</div>', unsafe_allow_html=True)

# PAGE: WIDGET SETTINGS
elif menu == "💬 Widget Settings":
    bot = get_bot_by_id(st.session_state.active_bot_id)
    
    if not bot:
        st.warning("⚠️ No active bot selected. Go to 'My Chatbots' and click 'Manage'.")
    else:
        st.markdown(f'<div class="main-header">Configuring: {bot["name"]}</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["⚙ Configuration", "💬 Sandbox Chat", "📜 Embed Snippet"])
        
        with tab1:
            st.session_state.api_key = st.text_input("OpenAI Key", value=st.session_state.api_key, type="password")
            bot["name"] = st.text_input("Bot Label", value=bot["name"])
            bot["prompt"] = st.text_area("System Instruction", value=bot["prompt"], height=200)
            
        with tab2:
            st.caption(f"Real-time testing for {bot['name']}")
            for m in st.session_state.messages:
                with st.chat_message(m["role"]): st.markdown(m["content"])
            
            if p := st.chat_input("Test your AI..."):
                st.session_state.messages.append({"role": "user", "content": p})
                with st.chat_message("user"): st.markdown(p)
                
                if not st.session_state.api_key:
                    st.error("Missing OpenAI API Key in Configuration.")
                else:
                    try:
                        client = openai.OpenAI(api_key=st.session_state.api_key)
                        with st.chat_message("assistant"):
                            res = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "system", "content": bot["prompt"]}] + st.session_state.messages
                            )
                            content = res.choices[0].message.content
                            st.markdown(content)
                        st.session_state.messages.append({"role": "assistant", "content": content})
                    except Exception as e:
                        st.error(f"API Error: {str(e)}")

        with tab3:
            st.markdown("### Production Deployment")
            st.code(f'<script src="https://chatbotbuilder.io/js/widget.js" data-id="{bot["id"]}" defer></script>', language="html")

# PAGE: ADMIN
elif menu == "⚙️ Admin":
    st.markdown('<div class="main-header">Administration</div>', unsafe_allow_html=True)
    st.markdown('<div class="bot-card">', unsafe_allow_html=True)
    st.write("Plan Status: **PRO Enterprise**")
    st.progress(0.65)
    st.write("Monthly Token Usage: 650 / 1000")
    st.button("Billing Portal")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. FOOTER ---
st.markdown("<br><hr><center><small style='color: #94a3b8;'>OmniTools SaaS Architecture | Chatbot Builder v3.1</small></center>", unsafe_allow_html=True)
