import streamlit as st
import openai
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Studio | Deep Purple Edition",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SOPHISTICATED DARK PURPLE THEME CSS ---
st.markdown("""
    <style>
    /* Main App Background - Deep Aubergine */
    .stApp {
        background-color: #1a122e;
        color: #ffffff;
    }

    /* Sidebar Background - Deeper Purple/Navy */
    [data-testid="stSidebar"] {
        background-color: #100a1f !important;
        border-right: 1px solid #2d2445;
    }

    /* Sidebar Branding & Text - High Contrast White */
    [data-testid="stSidebar"] .stMarkdown h1, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    .sidebar-brand {
        font-size: 22px;
        font-weight: 800;
        color: #a78bfa; /* Light Lilac accent */
        padding: 25px 0px;
        text-align: center;
        border-bottom: 1px solid #2d2445;
        margin-bottom: 20px;
    }

    /* Sidebar Navigation Overrides */
    div[role="radiogroup"] > label {
        background-color: transparent !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
        font-weight: 500 !important;
        color: #ffffff !important;
    }

    div[role="radiogroup"] > label:hover {
        background-color: rgba(167, 139, 250, 0.1) !important;
    }

    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #1d4ed8 !important; /* Preserved Vibrant Blue */
        color: white !important;
        box-shadow: 0 4px 12px rgba(29, 78, 216, 0.3);
    }
    
    div[role="radiogroup"] > label[data-checked="true"] span {
        color: white !important;
    }

    /* Card Containers - Sophisticated Dark Purple */
    .metric-card, .bot-card {
        background-color: #241b3a;
        border: 1px solid #352a52;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }

    /* Main Dashboard Titles */
    .main-header {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
    }
    .main-subtitle {
        color: #a78bfa; /* Lilac subtitle */
        margin-bottom: 30px;
    }

    /* Profile Section Bottom */
    .sidebar-profile {
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 220px;
        padding: 15px;
        background-color: #241b3a;
        border-radius: 12px;
        border: 1px solid #352a52;
    }

    /* Primary Action Buttons - Vibrant Blue */
    .stButton > button {
        background-color: #1d4ed8 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 0.6rem 2rem !important;
        transition: 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(29, 78, 216, 0.4);
    }

    /* Form Inputs */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #100a1f !important;
        color: white !important;
        border: 1px solid #352a52 !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #241b3a;
        border-radius: 8px 8px 0 0;
        border: 1px solid #352a52;
        color: #ffffff;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
    }

    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background-color: #241b3a !important;
        border: 1px solid #352a52 !important;
        border-radius: 15px !important;
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

# --- SIDEBAR: DEEP PURPLE NAVIGATION ---
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🔮 AI STUDIO</div>', unsafe_allow_html=True)
    
    menu = st.radio(
        "NAVIGATION",
        ["📊 Dashboard", "🤖 My Chatbots", "📚 Knowledge Base", "💬 Widget Settings", "⚙️ Admin"],
        label_visibility="collapsed"
    )
    
    # Profile Card
    st.markdown(f"""
        <div class="sidebar-profile">
            <small style="color: #a78bfa;">User Profile</small><br>
            <strong style="color: white;">Alex Mitchell</strong><br>
            <span style="font-size: 11px; background: #1d4ed8; color: white; padding: 2px 8px; border-radius: 20px; font-weight: bold;">PRO MEMBER</span>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN APP LOGIC ---

# 1. DASHBOARD
if menu == "📊 Dashboard":
    st.markdown('<div class="main-header">Dashboard Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Performance overview across all your AI instances.</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Chats", "14,201", "+22%")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Leads Captured", "892", "+5%")
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Resolution Rate", "94.2%", "0.8%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.area_chart({"Inquiries": [30, 55, 42, 88, 120, 95, 140]})

# 2. MY CHATBOTS
elif menu == "🤖 My Chatbots":
    col_h, col_b = st.columns([4, 1])
    with col_h:
        st.markdown('<div class="main-header">My Chatbots</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-subtitle">One chatbot = one website = its own knowledge base.</div>', unsafe_allow_html=True)
    with col_b:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("+ New Chatbot"):
            new_id = str(uuid.uuid4())[:8]
            st.session_state.chatbots.append({"id": new_id, "name": f"Assistant {new_id}"})
            st.rerun()

    if not st.session_state.chatbots:
        st.markdown("""
            <div style="text-align: center; padding: 80px; background: #241b3a; border: 2px dashed #352a52; border-radius: 20px;">
                <h3 style="color: #a78bfa;">Build your first AI Assistant</h3>
                <p style="color: white;">Automate your customer support in minutes.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        for bot in st.session_state.chatbots:
            st.markdown(f"""
                <div class="bot-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: #10b981; font-weight: bold; font-size: 12px;">● LIVE</span>
                            <h3 style="margin: 0; color: white;">{bot['name']}</h3>
                            <small style="color: #a78bfa;">ID: {bot['id']} | Last Activity: 1m ago</small>
                        </div>
                        <div style="color: #1d4ed8; font-weight: bold; cursor: pointer;">Manage →</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# 3. KNOWLEDGE BASE
elif menu == "📚 Knowledge Base":
    st.markdown('<div class="main-header">Knowledge Base</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Upload documentation to fine-tune your chatbot response logic.</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="bot-card">', unsafe_allow_html=True)
    kb_input = st.text_area("Source Documentation", placeholder="Paste website content or FAQs here...", height=300)
    if st.button("Sync Data"):
        st.success("Knowledge indexed and embedded.")
    st.markdown('</div>', unsafe_allow_html=True)

# 4. WIDGET SETTINGS
elif menu == "💬 Widget Settings":
    st.markdown('<div class="main-header">Widget & Deployment</div>', unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["⚙️ Config", "👁️ Live Test", "📜 Embed"])
    
    with t1:
        st.session_state.api_key = st.text_input("OpenAI API Key", value=st.session_state.api_key, type="password")
        st.text_input("Bot Brand Name", "Nova AI")
        st.color_picker("Accent Color", "#1d4ed8")
        
    with t2:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        if p := st.chat_input("Send a test message..."):
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
        st.code(f'<script src="https://cdn.ai-studio.io/widget.js" data-id="BOT_{str(uuid.uuid4())[:8]}" defer></script>', language="html")

# 5. ADMIN
elif menu == "⚙️ Admin":
    st.markdown('<div class="main-header">Settings & Billing</div>', unsafe_allow_html=True)
    st.markdown('<div class="bot-card">', unsafe_allow_html=True)
    st.write("Current Usage: **Advanced**")
    st.progress(65)
    st.button("Update Billing Details")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br><hr><center><small style='color: #a78bfa;'>AI Studio Deep Purple SaaS Engine | v2.1.0</small></center>", unsafe_allow_html=True)
