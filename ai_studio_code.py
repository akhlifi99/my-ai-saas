import streamlit as st
import openai
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Chatbot SaaS Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL SAAS STYLING ---
st.markdown("""
    <style>
    /* Main Background and Text */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }

    /* Sidebar Background and Borders */
    [data-testid="stSidebar"] {
        background-color: #0b192c !important;
        border-right: 1px solid #1e293b;
    }

    /* Sidebar Branding */
    .sidebar-brand {
        font-size: 24px;
        font-weight: 800;
        color: #3b82f6;
        padding: 20px 0px;
        text-align: center;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 20px;
    }

    /* Custom Sidebar Navigation Items */
    .stRadio > div {
        background-color: transparent !important;
    }
    
    label[data-baseweb="radio"] {
        background-color: transparent !important;
        padding: 10px 15px !important;
        border-radius: 8px !important;
        transition: 0.3s;
        color: #94a3b8 !important;
    }

    label[data-baseweb="radio"]:hover {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }

    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #1d4ed8 !important;
        color: white !important;
    }

    /* Main Dashboard Header */
    .main-header {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .main-subtitle {
        color: #94a3b8;
        margin-bottom: 30px;
    }

    /* Chatbot Cards */
    .bot-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }

    /* Primary Action Buttons */
    .stButton > button {
        background-color: #1d4ed8 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
    }

    /* Profile Section Bottom of Sidebar */
    .sidebar-profile {
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 220px;
        padding: 15px;
        background-color: #1e293b;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE MANAGEMENT ---
if "chatbots" not in st.session_state:
    st.session_state.chatbots = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🤖 AI Chatbot SaaS</div>', unsafe_allow_html=True)
    
    menu = st.radio(
        "NAVIGATION",
        ["📊 Dashboard", "🤖 My Chatbots", "📚 Knowledge Base", "💬 Widget Settings", "⚙️ Admin"],
        label_visibility="collapsed"
    )
    
    # Profile section spacer
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Static Profile UI
    st.markdown("""
        <div class="sidebar-profile">
            <small style="color: #94a3b8;">User Profile</small><br>
            <strong>Alex Mitchell</strong><br>
            <small style="color: #3b82f6;">Pro Plan</small>
        </div>
    """, unsafe_allow_html=True)

# --- APP LOGIC ROUTING ---

# 1. MY CHATBOTS PAGE (Default view logic)
if menu == "🤖 My Chatbots":
    col_title, col_action = st.columns([3, 1])
    
    with col_title:
        st.markdown('<div class="main-header">My Chatbots</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-subtitle">One chatbot = one website = its own knowledge base.</div>', unsafe_allow_html=True)
    
    with col_action:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("+ New Chatbot"):
            st.session_state.chatbots.append({"id": str(uuid.uuid4())[:8], "name": f"Chatbot {len(st.session_state.chatbots)+1}"})
            st.rerun()

    if not st.session_state.chatbots:
        # Empty State
        st.markdown("""
            <div style="text-align: center; padding: 100px; border: 2px dashed #334155; border-radius: 20px;">
                <h3 style="color: #94a3b8;">No chatbot yet</h3>
                <p>Click '+ New Chatbot' to create your first one and start automating your support.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # List Active Bots
        for bot in st.session_state.chatbots:
            with st.container():
                st.markdown(f"""
                    <div class="bot-card">
                        <span style="color: #3b82f6; font-weight: bold;">● Active</span>
                        <h3 style="margin: 5px 0px;">{bot['name']}</h3>
                        <small style="color: #94a3b8;">ID: {bot['id']} | Last trained: Just now</small>
                    </div>
                """, unsafe_allow_html=True)

# 2. KNOWLEDGE BASE PAGE
elif menu == "📚 Knowledge Base":
    st.markdown('<div class="main-header">Knowledge Base</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Upload docs or paste text to train your AI on your business data.</div>', unsafe_allow_html=True)
    
    kb_text = st.text_area("Source Text", placeholder="Paste your company FAQs or documentation here...", height=300)
    if st.button("Train AI Model"):
        st.success("Knowledge base updated and indexed successfully!")

# 3. WIDGET SETTINGS PAGE (Functional AI Config)
elif menu == "💬 Widget Settings":
    st.markdown('<div class="main-header">Widget Configuration</div>', unsafe_allow_html=True)
    
    tab_settings, tab_preview, tab_embed = st.tabs(["⚙️ Settings", "👁️ Live Preview", "📜 Embed Code"])
    
    with tab_settings:
        st.session_state.api_key = st.text_input("OpenAI API Key", value=st.session_state.api_key, type="password")
        bot_name = st.text_input("Display Name", value="Support Bot")
        system_prompt = st.text_area("System Instructions", value="You are a helpful customer support bot for our website.")
        
    with tab_preview:
        st.markdown("### Test your widget response")
        # Chat Sandbox Logic
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Type a message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if not st.session_state.api_key:
                st.error("Missing API Key in Settings.")
            else:
                try:
                    client = openai.OpenAI(api_key=st.session_state.api_key)
                    with st.chat_message("assistant"):
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                            stream=False
                        )
                        full_res = response.choices[0].message.content
                        st.markdown(full_res)
                    st.session_state.messages.append({"role": "assistant", "content": full_res})
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab_embed:
        st.markdown("### Website Embed Script")
        snippet = f"""<script src="https://cdn.myaiapp.io/widget.js" data-id="{str(uuid.uuid4())[:8]}" defer></script>"""
        st.code(snippet, language="html")

# 4. DASHBOARD PAGE (Analytics Mock)
elif menu == "📊 Dashboard":
    st.markdown('<div class="main-header">Analytics Overview</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Chats", "1,284", "+12%")
    c2.metric("Leads Captured", "142", "+5%")
    c3.metric("AI Accuracy", "98.2%", "0.4%")
    st.line_chart({"chats": [10, 20, 15, 40, 50, 45, 70]})

# 5. ADMIN PAGE
elif menu == "⚙️ Admin":
    st.markdown('<div class="main-header">Admin Settings</div>', unsafe_allow_html=True)
    st.checkbox("Enable Auto-billing")
    st.checkbox("Allow Multi-agent handoff")
    st.button("Save System Settings")

# --- FOOTER ---
st.markdown("<br><hr><center><small>Powered by GPT-4o-mini & Streamlit SaaS Framework</small></center>", unsafe_allow_html=True)
