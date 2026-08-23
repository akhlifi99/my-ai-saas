import streamlit as st
import openai
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ChatBotify AI - Custom Chatbot Builder",
    page_icon="🤖",
    layout="wide"
)

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "bot_id" not in st.session_state:
    st.session_state.bot_id = str(uuid.uuid4())[:8]

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.title("🤖 Bot Settings")
    st.markdown("---")
    
    api_key = st.text_input("1. OpenAI API Key", type="password", help="Needed to power the Live Demo.")
    
    bot_name = st.text_input("2. Bot Name", value="Support AI")
    
    system_prompt = st.text_area(
        "3. System Prompt (Bot Personality)", 
        value="You are a helpful customer support assistant for a SaaS company. Be polite, concise, and professional.",
        height=200,
        help="Define how your bot should behave and what knowledge it should have."
    )
    
    st.markdown("---")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN INTERFACE ---
st.title("🚀 AI Website Chatbot Builder")
st.info("Configure your bot in the sidebar, test it here, and copy the embed code below.")

tab1, tab2 = st.tabs(["💬 Live Demo Sandbox", "💻 Get Embed Code"])

# --- TAB 1: LIVE DEMO ---
with tab1:
    st.subheader(f"Test Drive: {bot_name}")
    
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask your bot something..."):
        if not api_key:
            st.error("Please enter an OpenAI API Key in the sidebar to test the bot.")
        else:
            # Display user message
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            try:
                client = openai.OpenAI(api_key=api_key)
                
                # Prepare messages including system prompt
                api_messages = [{"role": "system", "content": system_prompt}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]

                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=api_messages,
                        stream=True,
                    )
                    response = st.write_stream(stream)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- TAB 2: EMBED CODE ---
with tab2:
    st.subheader("Add this bot to your website")
    st.write("Copy and paste this snippet before the closing `</body>` tag on your website (WordPress, Shopify, Webflow, etc.).")
    
    # This is a template for the JS Injector
    # In a real SaaS, 'YOUR_SaaS_API_ENDPOINT' would be your backend proxying the AI requests
    embed_snippet = f"""<!-- ChatBotify AI Widget -->
<script>
  window.CHATBOT_CONFIG = {{
    botId: "{st.session_state.bot_id}",
    botName: "{bot_name}",
    welcomeMessage: "Hello! How can I help you today?",
    primaryColor: "#007bff"
  }};
</script>
<script 
  src="https://cdn.jsdelivr.net/gh/your-username/chatbot-widget@main/widget.js" 
  defer>
</script>
<!-- End ChatBotify AI Widget -->"""

    st.code(embed_snippet, language="html")
    
    with st.expander("🛠️ How to deploy the production backend?"):
        st.markdown("""
        To make the embed code work on live websites without exposing your API Key:
        1. **Create a Backend API:** (Using FastAPI or Node.js) that receives messages from the widget.
        2. **Secure the Key:** Store the OpenAI Key on your server, not in the JavaScript.
        3. **Database:** Store the `system_prompt` in a database (like Supabase) linked to the `botId`.
        4. **CORS:** Enable CORS to allow your widget to talk to your API from any domain.
        """)

# --- FOOTER ---
st.markdown("---")
st.caption("Powered by gpt-4o-mini | Built for ChatBotify SaaS")
