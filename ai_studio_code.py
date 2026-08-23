import streamlit as st
from openai import OpenAI

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS — HIGH CONTRAST / ACCESSIBLE CHAT UI
# ============================================================

st.markdown(
    """
    <style>
    /* ========================================================
       GLOBAL
       ======================================================== */

    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
        color: #f1f5f9 !important;
    }

    /* Main application text */
    .stMarkdown,
    .stMarkdown p,
    .stMarkdown span,
    .stMarkdown div,
    .stMarkdown li,
    .stMarkdown label {
        color: #f1f5f9 !important;
    }

    /* ========================================================
       CHAT MESSAGES
       ======================================================== */

    [data-testid="stChatMessage"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin-bottom: 0.75rem !important;
    }

    /* Every text element inside chat messages */
    [data-testid="stChatMessage"] *,
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] div,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] ul,
    [data-testid="stChatMessage"] ol,
    [data-testid="stChatMessage"] strong,
    [data-testid="stChatMessage"] em,
    [data-testid="stChatMessage"] b,
    [data-testid="stChatMessage"] i,
    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3,
    [data-testid="stChatMessage"] h4,
    [data-testid="stChatMessage"] h5,
    [data-testid="stChatMessage"] h6 {
        color: #f1f5f9 !important;
    }

    /* Chat links */
    [data-testid="stChatMessage"] a {
        color: #93c5fd !important;
        text-decoration: underline !important;
    }

    [data-testid="stChatMessage"] a:hover {
        color: #bfdbfe !important;
    }

    /* Inline code */
    [data-testid="stChatMessage"] code {
        color: #ffffff !important;
        background-color: #0f172a !important;
        border: 1px solid #475569 !important;
        border-radius: 5px !important;
        padding: 0.15rem 0.35rem !important;
    }

    /* Code blocks */
    [data-testid="stChatMessage"] pre {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        overflow-x: auto !important;
    }

    [data-testid="stChatMessage"] pre code {
        background-color: transparent !important;
        border: none !important;
        color: #f8fafc !important;
    }

    /* Tables inside chat */
    [data-testid="stChatMessage"] table {
        color: #f1f5f9 !important;
        border-collapse: collapse !important;
    }

    [data-testid="stChatMessage"] th,
    [data-testid="stChatMessage"] td {
        color: #f1f5f9 !important;
        border: 1px solid #475569 !important;
        padding: 0.5rem !important;
    }

    [data-testid="stChatMessage"] th {
        background-color: #334155 !important;
    }

    [data-testid="stChatMessage"] td {
        background-color: #1e293b !important;
    }

    /* Blockquotes */
    [data-testid="stChatMessage"] blockquote {
        color: #e2e8f0 !important;
        border-left: 4px solid #64748b !important;
        background-color: #0f172a !important;
        padding: 0.5rem 1rem !important;
    }

    /* ========================================================
       CHAT INPUT
       ======================================================== */

    [data-testid="stChatInput"] {
        background-color: transparent !important;
    }

    [data-testid="stChatInput"] > div {
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
        border-radius: 12px !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        background-color: #1e293b !important;
        caret-color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #cbd5e1 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #cbd5e1 !important;
    }

    [data-testid="stChatInput"] textarea:focus {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border-color: #94a3b8 !important;
        outline: none !important;
    }

    /* Chat input buttons */
    [data-testid="stChatInput"] button {
        color: #ffffff !important;
        background-color: #334155 !important;
    }

    [data-testid="stChatInput"] button:hover {
        background-color: #475569 !important;
    }

    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }

    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: #f1f5f9 !important;
    }

    /* ========================================================
       INPUTS / TEXT AREAS
       ======================================================== */

    input,
    textarea {
        color: #ffffff !important;
        background-color: #1e293b !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: #cbd5e1 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #cbd5e1 !important;
    }

    /* ========================================================
       SELECTBOX / MULTISELECT
       ======================================================== */

    [data-baseweb="select"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }

    [data-baseweb="select"] * {
        color: #ffffff !important;
    }

    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        color: #ffffff !important;
        background-color: #334155 !important;
        border: 1px solid #64748b !important;
    }

    .stButton > button:hover {
        color: #ffffff !important;
        background-color: #475569 !important;
        border-color: #94a3b8 !important;
    }

    /* ========================================================
       ALERTS / STATUS MESSAGES
       ======================================================== */

    [data-testid="stAlert"] {
        color: #f1f5f9 !important;
    }

    [data-testid="stAlert"] * {
        color: #f1f5f9 !important;
    }

    /* ========================================================
       EXPANDERS
       ======================================================== */

    [data-testid="stExpander"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
    }

    [data-testid="stExpander"] * {
        color: #f1f5f9 !important;
    }

    /* ========================================================
       CODE / PRE
       ======================================================== */

    pre,
    code {
        color: #f8fafc !important;
    }

    /* ========================================================
       DISABLED ELEMENTS
       ======================================================== */

    input:disabled,
    textarea:disabled,
    button:disabled {
        color: #cbd5e1 !important;
        -webkit-text-fill-color: #cbd5e1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# OPENAI CLIENT
# ============================================================

st.title("🤖 AI Studio")
st.caption("OpenAI-powered chat interface")

api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    help="Enter your OpenAI API key.",
)

model = st.sidebar.selectbox(
    "Model",
    [
        "gpt-5.6",
        "gpt-5.4",
        "gpt-5.2",
    ],
    index=0,
)

if st.sidebar.button("Clear conversation"):
    st.session_state.messages = []
    st.rerun()

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input("Message AI Studio...")

if prompt:
    # Store user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("Please enter your OpenAI API key in the sidebar.")

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "Please enter your OpenAI API key in the sidebar.",
            }
        )

    else:
        try:
            client = OpenAI(api_key=api_key)

            with st.chat_message("assistant"):
                response_placeholder = st.empty()

                response = client.responses.create(
                    model=model,
                    input=st.session_state.messages,
                )

                answer = response.output_text

                response_placeholder.markdown(answer)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        except Exception as exc:
            error_message = f"Error: {exc}"

            with st.chat_message("assistant"):
                st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )
