import streamlit as st
import streamlit.components.v1 as components
import openai

st.set_page_config(page_title="AI Chatbot SaaS", page_icon="🤖", layout="wide")

with st.sidebar:
    st.title("⚙️ الإعدادات")
    api_key = st.text_input("أدخل مفتاح OpenAI API Key", type="password")
    system_prompt = st.text_area(
        "تعليمات الشات بوت (System Prompt):",
        value="أنت مساعد خدمة عملاء ذكي ومؤدب، تجيب عن استفسارات الزوار باختصار ولطافة."
    )

st.title("🤖 AI Website Chatbot Builder")
st.write("أنشئ شات بوت بالذكاء الاصطناعي لزرعه في أي موقع خلال ثوانٍ.")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 💬 تجربة الشات بوت (Live Demo)")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_input := st.chat_input("اكتب رسالتك هنا..."):
        if not api_key:
            st.error("يرجى إدخال مفتاح OpenAI API أولاً من القائمة الجانبية.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)

            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages
            )
            bot_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.chat_message("assistant").write(bot_reply)

with col2:
    st.markdown("### 📜 كود التضمين في أي موقع (Embed Code)")
    embed_script = f"""<!-- AI Chatbot Widget -->
<script>
  window.CHATBOT_CONFIG = {{
    apiKey: "{api_key if api_key else 'YOUR_API_KEY'}",
    prompt: "{system_prompt}"
  }};
</script>
<script src="https://cdn.jsdelivr.net/gh/your-username/chatbot-widget/widget.js" async></script>"""
    
    st.code(embed_script, language="html")
