import streamlit as st
import openai
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Studio | Chatbot Builder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN DARK THEME CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
        color: #f8fafc;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #131722 !important;
        border-right: 1px solid #1e293b;
    }
    
    /* Typography Styling */
    h1, h2, h3, p {
        font-family: 'Inter', sans-serif;
    }
    
    .stMarkdown h1 {
        color: #3b82f6;
        font-weight: 800;
        letter-spacing: -1px;
    }

    /* Input Fields & Text Areas */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #1a1f2c !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1f2c;
        border-radius: 10px 10px 0 0;
        color: #94a3b8;
        padding: 10px 20px;
        border: 1px solid #334155;
        border-bottom: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
        border-color: #3b82f6 !important;
    }

    /* Chat Bubbles Styling */
    [data-testid="stChatMessage"] {
        background-color: #1a1f2c !important;
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        margin-bottom: 12px !important;
        padding: 15px !important;
    }
    
    [data-test-role="user"] {
        border-left: 4px solid #3b82f6 !important;
    }
    
    [data-test-role="assistant"] {
        border-left: 4px solid #10b981 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }

    /* Code Block Styling */
    code {
        color: #60a5fa !important;
        background-color: #0f172a !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "bot_id" not in st.session_state:
    st.session_state.bot_id = str(uuid.uuid4())[:8]

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.markdown("# 🛠️ AI Configuration")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    
    st.markdown("---")
    bot_name = st.text_input("Bot Name", value="Nova Support")
    
    system_prompt = st.text_area(
        "System Prompt", 
        value="You are a professional AI assistant for a global SaaS platform. You are helpful, tech-savvy, and concise.",
        height=250
    )
    
    if st.button("🗑️ Reset Sandbox"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN DASHBOARD ---
st.title("⚡ AI Studio")
st.markdown("Build, test, and deploy modern AI chatbots in seconds.")

tab_demo, tab_embed = st.tabs(["🚀 Live Demo Sandbox", "🔗 Get Embed Code"])

# --- TAB 1: LIVE DEMO SANDBOX ---
with tab_demo:
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask your bot a question..."):
        if not api_key:
            st.warning("⚠️ Please provide an API Key in the sidebar to chat.")
        else:
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate response
            try:
                client = openai.OpenAI(api_key=api_key)
                
                with st.chat_message("assistant"):
                    messages_to_send = [{"role": "system", "content": system_prompt}] + [
                        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                    ]
                    
                    stream = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages_to_send,
                        stream=True,
                    )
                    response = st.write_stream(stream)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
            
            except Exception as e:
                st.error(f"API Error: {str(e)}")

# --- TAB 2: EMBED CODE ---
with tab_embed:
    st.markdown("### 📦 Deployment Snippet")
    st.write("Add the following code to your website's `<head>` or `<body>` tag.")
    
    embed_code = f"""<!-- AI Studio Chatbot Widget -->
<script>
  window.AI_STUDIO_CONFIG = {{
    botId: "{st.session_state.bot_id}",
    name: "{bot_name}",
    theme: "dark",
    primaryColor: "#3b82f6"
  }};
</script>
<script 
  src="https://cdn.jsdelivr.net/npm/ai-studio-widget@latest/dist/bundle.js" 
  defer>
</script>"""

    st.code(embed_code, language="html")
    
    st.success("✨ Your chatbot is ready for a global audience.")
    
    st.markdown("""
    **Installation Guides:**
    - **WordPress:** Use a 'Custom HTML' block or a Header/Footer plugin.
    - **Shopify:** Edit `theme.liquid` and paste before `</body>`.
    - **React/Next.js:** Use the `next/script` component.
    """)

# --- FOOTER ---
st.markdown("---")
st.caption("AI Studio SaaS Framework | Powered by GPT-4o-mini")
