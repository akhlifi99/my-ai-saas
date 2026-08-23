import streamlit as st
import streamlit.components.v1 as components
import openai
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="WidgetAI - Lead Gen SaaS", page_icon="🪄", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    .lead-card { padding: 10px; border-radius: 5px; background: white; border-left: 5px solid #007BFF; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = ""
if 'leads' not in st.session_state:
    st.session_state.leads = []

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    st.info("This prototype uses GPT-4o to generate responsive widgets.")
    
    if st.button("Clear Dashboard"):
        st.session_state.leads = []
        st.rerun()

# --- MAIN INTERFACE ---
st.title("🪄 WidgetAI Builder")
st.subheader("Transform your lead generation with AI-powered interactive widgets.")

col_input, col_preview = st.columns([1, 1.5], gap="large")

with col_input:
    st.markdown("### 🛠️ Widget Designer")
    user_prompt = st.text_area(
        "Describe your widget:", 
        placeholder="e.g., A dark-themed popup for a 20% discount code in exchange for an email. Include a sleek animation.",
        height=150
    )
    
    generate_btn = st.button("Generate Widget")

    if generate_btn:
        if not api_key:
            st.error("Please add your OpenAI API Key in the sidebar.")
        else:
            try:
                with st.spinner("AI is coding your widget..."):
                    client = openai.OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are a professional web developer. Generate a single-file HTML/CSS/JS widget. Use internal <style> and <script>. Ensure there is an input for email and a button that calls a function sendLead(). Return ONLY the HTML code."},
                            {"role": "user", "content": f"Create this widget: {user_prompt}"}
                        ]
                    )
                    st.session_state.generated_code = response.choices[0].message.content
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if st.session_state.generated_code:
        st.markdown("### 📋 Embed Code")
        st.code(st.session_state.generated_code, language="html")
        st.success("Copy the code above and paste it into your website's <body>")

with col_preview:
    st.markdown("### 👁️ Live Preview")
    if st.session_state.generated_code:
        # Rendering the generated HTML in an Iframe
        components.html(st.session_state.generated_code, height=500, scrolling=True)
    else:
        st.info("Your generated widget preview will appear here.")

# --- LEAD CAPTURE SIMULATION ---
st.markdown("---")
st.markdown("### 📊 Lead Management Dashboard")

# Simulating a lead capture for the demo
if st.session_state.generated_code:
    st.caption("Simulator: Test your widget above. In a real app, the code below would be triggered via API.")
    with st.expander("Simulate a Lead Capture (For Demo Purposes)"):
        test_email = st.text_input("Enter a test email")
        if st.button("Submit Test Lead"):
            new_lead = {"Email": test_email, "Timestamp": "Just Now", "Status": "New"}
            st.session_state.leads.append(new_lead)
            st.toast("Lead captured successfully!", icon="✅")

if st.session_state.leads:
    st.table(st.session_state.leads)
else:
    st.write("No leads captured yet. Generate a widget and start testing!")

# --- FOOTER ---
st.markdown("---")
st.markdown("<center>Built with ❤️ for Global AI SaaS Entrepreneurs</center>", unsafe_allow_html=True)