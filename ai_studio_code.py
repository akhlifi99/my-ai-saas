import streamlit as st
import openai
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Chatbot SaaS | Professional",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- VIBRANT & CRISP CUSTOM STYLING ---
st.markdown("""
    <style>
    /* Main App Background */
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
    }

    /* Sidebar Background (Vibrant Blue) */
    [data-testid="stSidebar"] {
        background-color: #1d4ed8 !important;
        border-right: 1px solid #e2e8f0;
    }

    /* Sidebar Branding & Text - Pure White */
    [data-testid="stSidebar"] .stMarkdown h1, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    .sidebar-brand {
        font-size: 22px;
        font-weight: 800;
        color: #ffffff;
        padding: 25px 0px;
        text-align: center;
        border-bottom: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 20px;
    }

    /* Sidebar Navigation Overrides */
    div[role="radiogroup"] > label {
        background-color: transparent !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
        font-weight: 500 !important;
    }

    div[role="radiogroup"] > label:hover {
        background-color: rgba(255,255,255,0.1) !important;
    }

    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        color: #1d4ed8 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    div[role="radiogroup"] > label[data-checked="true"] span {
        color: #1d4ed8 !important;
    }

    /* Card Containers (White with subtle borders) */
    .metric-card, .bot-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Main Dashboard Titles */
    .main-header {
        font-size: 32px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 5px;
    }
    .main-subtitle {
        color: #64748b;
        margin-bottom: 30px;
    }

    /* Profile Section Bottom of Blue Sidebar */
    .sidebar-profile {
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 220px;
        padding: 15px;
        background-color: rgba(255,255,255,0.15);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }

    /* Primary Buttons */
    .stButton > button {
        background-color: #1d4ed8 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 0.6rem 2rem !important;
        transition: 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #1e40af !important;
        box-shadow: 0 10px 15px -3px rgba(29, 78, 216, 0.3);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #ffffff;
        border-radius: 8px 8px 0 0;
        border: 1px solid #e2e8f0;
        padding: 10px 20px;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1d4ed8 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "chatbots" not in st.session_state:
    st.session_state.chatbots = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# --- SIDEBAR: VIBRANT NAVIGATION ---
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🤖 AI STUDIO</div>', unsafe_allow_html=True)
    
    menu = st.radio(
        "NAVIGATION",
        ["📊 Dashboard", "🤖 My Chatbots", "📚 Knowledge Base", "💬 Widget Settings", "⚙️ Admin"],
        label_visibility="collapsed"
    )
    
    # Profile Card at the bottom
    st.markdown(f"""
        <div class="sidebar-profile">
            <small style="color: rgba(255,255,255,0.7);">Logged in as</small><br>
            <strong style="color: white;">Alex Mitchell</strong><br>
            <span style="font-size: 12px; background: white; color: #1d4ed8; padding: 2px 8px; border-radius: 20px; font-weight: bold;">PRO PLAN</span>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN APP LOGIC ---

# 1. DASHBOARD
if menu == "📊 Dashboard":
    st.markdown('<div class="main-header">Analytics Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Real-time performance tracking for your active chatbots.</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Chats", "2,540", "+18%")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Leads Generated", "412", "+7%")
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Handoff Rate", "4.2%", "-2%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.line_chart({"Daily Chats": [12, 45, 32, 67, 89, 75, 110]})

# 2. MY CHATBOTS
elif menu == "🤖 My Chatbots":
    col_h, col_b = st.columns([4, 1])
    with col_h:
        st.markdown('<div class="main-header">My Chatbots</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-subtitle">Manage and deploy your automated AI assistants.</div>', unsafe_allow_html=True)
    with col_b:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("+ New Chatbot"):
            new_id = str(uuid.uuid4())[:8]
            st.session_state.chatbots.append({"id": new_id, "name": f"Assistant {new_id}"})
            st.rerun()

    if not st.session_state.chatbots:
        st.markdown("""
            <div style="text-align: center; padding: 80px; background: white; border: 2px dashed #cbd5e1; border-radius: 20px;">
                <h3 style="color: #64748b;">Ready to automate?</h3>
                <p>No chatbots created yet. Your first one is just a click away.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        for bot in st.session_state.chatbots:
            st.markdown(f"""
                <div class="bot-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: #10b981; font-weight: bold;">● Active</span>
                            <h3 style="margin: 0; color: #0f172a;">{bot['name']}</h3>
                            <small style="color: #64748b;">ID: {bot['id']} | Last Activity: 2 mins ago</small>
                        </div>
                        <div style="color: #1d4ed8; cursor: pointer; font-weight: bold;">Edit Bot →</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# 3. KNOWLEDGE BASE
elif menu == "📚 Knowledge Base":
    st.markdown('<div class="main-header">Knowledge Base</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Train your bots on specific data sources.</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="bot-card">', unsafe_allow_html=True)
        kb_input = st.text_area("Document Content", placeholder="Enter text or documentation to train your AI...", height=250)
        if st.button("Index & Train"):
            st.success("Knowledge base successfully indexed with Vector Embeddings.")
        st.markdown('</div>', unsafe_allow_html=True)

# 4. WIDGET SETTINGS
elif menu == "💬 Widget Settings":
    st.markdown('<div class="main-header">Widget Configuration</div>', unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["⚙️ Global Settings", "👁️ Live Sandbox", "📜 Embed Script"])
    
    with t1:
        st.session_state.api_key = st.text_input("OpenAI API Key", value=st.session_state.api_key, type="password")
        st.text_input("Widget Title", "AI Support Assistant")
        st.color_picker("Brand Color", "#1d4ed8")
        
    with t2:
        st.info("Test your chatbot responses below using gpt-4o-mini.")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if p := st.chat_input("Ask something..."):
            st.session_state.messages.append({"role": "user", "content": p})
            with st.chat_message("user"): st.markdown(p)
            
            if st.session_state.api_key:
                try:
                    client = openai.OpenAI(api_key=st.session_state.api_key)
                    with st.chat_message("assistant"):
                        res = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.messages)
                        content = res.choices[0].message.content
                        st.markdown(content)
                    st.session_state.messages.append({"role": "assistant", "content": content})
                except Exception as e: st.error(str(e))

    with t3:
        st.markdown("### Deployment Code")
        st.code(f'<script src="https://app.aistudio.com/widget.js" data-id="{str(uuid.uuid4())[:8]}" defer></script>', language="html")

# 5. ADMIN
elif menu == "⚙️ Admin":
    st.markdown('<div class="main-header">System Admin</div>', unsafe_allow_html=True)
    st.markdown('<div class="bot-card">', unsafe_allow_html=True)
    st.write("Current Plan: **Business Pro**")
    st.write("Active Connections: **12 / 50**")
    st.button("Upgrade Subscription")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br><hr><center><small style='color: #94a3b8;'>AI Studio SaaS Engine v2.0 | Built with Streamlit</small></center>", unsafe_allow_html=True)
