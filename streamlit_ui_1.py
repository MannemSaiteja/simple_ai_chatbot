"""
Gemini-style Chat UI for FastAPI + Gemini Chatbot
Uses Streamlit's NATIVE sidebar and chat components — no layout hacks.
Run: streamlit run streamlit_ui.py
FastAPI must be running at http://127.0.0.1:8000
"""

import streamlit as st
import requests
import time

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gemini Chat",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Theme CSS (cosmetic only — no layout hacks) ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600&family=Roboto:wght@300;400;500&display=swap');

/* Global font */
html, body, [class*="css"] {
    font-family: 'Roboto', sans-serif !important;
}

/* Hide Streamlit default chrome */
#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background-color: #f0f4f9 !important;
    border-right: 1px solid #dadce0 !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* Sidebar title */
.sb-header {
    display: flex; align-items: center; gap: 10px;
    padding: 18px 16px 14px;
    border-bottom: 1px solid #dadce0;
}
.sb-gem {
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg, #4285f4, #9b59b6);
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 15px; flex-shrink: 0;
}
.sb-title {
    font-family: 'Google Sans', sans-serif;
    font-size: 1.15rem; font-weight: 600; color: #1f1f1f;
}

/* Sidebar new-chat button */
[data-testid="stSidebar"] .stButton > button {
    background: #ffffff !important;
    border: 1px solid #dadce0 !important;
    border-radius: 24px !important;
    color: #1f1f1f !important;
    font-family: 'Google Sans', sans-serif !important;
    font-size: 0.87rem !important;
    font-weight: 500 !important;
    width: calc(100% - 24px) !important;
    margin: 10px 12px 4px !important;
    padding: 9px 16px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    box-shadow: none !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #e8eaed !important;
}

/* Sidebar active conversation */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #d3e3fd !important;
    border-color: #aecbfa !important;
    color: #1a3461 !important;
    font-weight: 500 !important;
}

/* Sidebar section label */
.sb-label {
    font-size: 0.7rem; font-weight: 500;
    color: #5f6368; text-transform: uppercase;
    letter-spacing: 0.09em;
    padding: 10px 16px 2px;
    font-family: 'Roboto', sans-serif;
}

/* Sidebar history items */
[data-testid="stSidebar"] .stButton.hist > button {
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    margin: 1px 8px !important;
    width: calc(100% - 16px) !important;
    padding: 7px 12px !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
    color: #1f1f1f !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
[data-testid="stSidebar"] .stButton.hist > button:hover {
    background: #e2e6ea !important;
}

/* Sidebar footer */
.sb-footer {
    padding: 10px 16px;
    border-top: 1px solid #dadce0;
    font-size: 0.75rem; color: #5f6368;
    display: flex; align-items: center; gap: 8px;
    margin-top: 12px;
}
.green-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #34a853; flex-shrink: 0;
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* ── MAIN AREA ── */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Top bar */
.topbar {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    height: 56px;
    border-bottom: 1px solid #dadce0;
    background: #fff;
    margin-bottom: 0;
}
.topbar-title {
    font-family: 'Google Sans', sans-serif;
    font-size: 1rem; font-weight: 500; color: #1f1f1f;
}
.model-pill {
    background: #e8f0fe; color: #1a73e8;
    border-radius: 20px; padding: 4px 12px;
    font-size: 0.77rem; font-weight: 500;
    font-family: 'Google Sans', sans-serif;
}

/* Welcome screen */
.welcome {
    text-align: center;
    padding: 60px 20px 30px;
}
.w-gem {
    width: 64px; height: 64px; border-radius: 50%;
    background: linear-gradient(135deg, #4285f4, #9b59b6 50%, #34a853);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 1.8rem; color: #fff;
    box-shadow: 0 4px 20px rgba(66,133,244,.2);
    margin-bottom: 16px;
}
.welcome h2 {
    font-family: 'Google Sans', sans-serif;
    font-size: 1.75rem; font-weight: 600;
    background: linear-gradient(135deg, #4285f4, #9b59b6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 8px;
}
.welcome p { color: #5f6368; font-size: 0.93rem; margin-bottom: 28px; }
.chips { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; max-width: 560px; margin: 0 auto; }
.chip {
    background: #fff; border: 1px solid #dadce0;
    border-radius: 20px; padding: 8px 16px;
    font-size: 0.83rem; color: #1f1f1f;
    font-family: 'Google Sans', sans-serif;
}

/* Native chat message overrides */
[data-testid="stChatMessage"] {
    padding: 8px 0 !important;
    max-width: 800px !important;
    margin: 0 auto !important;
    background: transparent !important;
    border: none !important;
}

/* User message bubble */
[data-testid="stChatMessage"][data-testid*="user"] .stMarkdown,
[data-testid="stChatMessage"]:has([aria-label="user avatar"]) .stMarkdown p {
    background: #e8f0fe !important;
    border-radius: 18px 4px 18px 18px !important;
    padding: 10px 15px !important;
    display: inline-block !important;
    color: #1a3461 !important;
    max-width: 70% !important;
    float: right !important;
}

/* User avatar */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse !important;
}

/* Override avatar styles */
[data-testid="stChatMessageAvatarUser"] {
    background: linear-gradient(135deg, #4285f4, #9b59b6) !important;
    color: white !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
    background: linear-gradient(135deg, #4285f4, #34a853 60%, #fbbc04) !important;
    color: white !important;
}

/* Input bar */
[data-testid="stChatInput"] textarea {
    font-family: 'Roboto', sans-serif !important;
    font-size: 0.93rem !important;
    border-radius: 28px !important;
}
[data-testid="stBottom"] {
    background: white !important;
    border-top: 1px solid #dadce0 !important;
    padding: 10px 0 6px !important;
}
[data-testid="stBottom"] > div {
    max-width: 800px !important;
    margin: 0 auto !important;
    padding: 0 24px !important;
}

.input-hint {
    text-align: center; font-size: 0.7rem;
    color: #bdc1c6; padding: 4px 0 2px;
    font-family: 'Roboto', sans-serif;
}

/* Error */
.err-box {
    background: #fce8e6; border: 1px solid #f5c6c2;
    border-radius: 12px; padding: 10px 14px;
    color: #c5221f; font-size: 0.87rem;
    max-width: 800px; margin: 6px auto;
}

/* Thinking dots */
.thinking { display: flex; gap: 6px; align-items: center; padding: 4px 0; }
.dot { width: 9px; height: 9px; border-radius: 50%; animation: bounce 1.2s ease-in-out infinite; }
.d1 { background: #4285f4; }
.d2 { background: #34a853; animation-delay: .2s; }
.d3 { background: #fbbc04; animation-delay: .4s; }
@keyframes bounce {
    0%,80%,100% { transform: translateY(0); opacity:.4; }
    40%          { transform: translateY(-7px); opacity:1; }
}
</style>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────────────────
API_URL = "http://127.0.0.1:8000/chat"

# ─── Session State ───────────────────────────────────────────────────────────
if "conversations" not in st.session_state:
    st.session_state.conversations = []   # list of {title, messages:[]}
if "active_conv" not in st.session_state:
    st.session_state.active_conv = None

# ─── Helpers ─────────────────────────────────────────────────────────────────
def call_api(message: str) -> str:
    try:
        r = requests.post(API_URL, json={"message": message}, timeout=30)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            return f"__ERR__:{data['error']}"
        return data.get("response", "No response.")
    except requests.exceptions.ConnectionError:
        return "__ERR__:Cannot connect to FastAPI. Make sure it's running on port 8000."
    except requests.exceptions.Timeout:
        return "__ERR__:Request timed out."
    except Exception as e:
        return f"__ERR__:{e}"

def active_messages():
    i = st.session_state.active_conv
    if i is not None and 0 <= i < len(st.session_state.conversations):
        return st.session_state.conversations[i]["messages"]
    return None

def fmt_time():
    return time.strftime("%I:%M %p")

# ══════════════════════════════════════════
#  NATIVE SIDEBAR
# ══════════════════════════════════════════
with st.sidebar:
    # Logo
    st.markdown("""
    <div class="sb-header">
        <div class="sb-gem">✦</div>
        <span class="sb-title">Gemini</span>
    </div>
    """, unsafe_allow_html=True)

    # New chat
    if st.button("✏️  New chat", key="new_chat"):
        st.session_state.active_conv = None
        st.rerun()

    # History
    convs = st.session_state.conversations
    if convs:
        st.markdown('<div class="sb-label">Recent</div>', unsafe_allow_html=True)
        for i, conv in enumerate(reversed(convs)):
            real_idx = len(convs) - 1 - i
            is_active = (st.session_state.active_conv == real_idx)
            label = conv["title"][:30] + ("…" if len(conv["title"]) > 30 else "")
            if is_active:
                st.button(f"💬  {label}", key=f"c_{real_idx}", type="primary", use_container_width=True)
            else:
                if st.button(f"💬  {label}", key=f"c_{real_idx}", use_container_width=True):
                    st.session_state.active_conv = real_idx
                    st.rerun()
    else:
        st.markdown("""
        <div style="padding:10px 16px; font-size:0.82rem; color:#9aa0a6; line-height:1.6;">
            Your chats will appear here.
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="sb-footer">
        <div class="green-dot"></div>
        FastAPI · localhost:8000
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════
#  MAIN CONTENT
# ══════════════════════════════════════════
messages = active_messages()

# Top bar
conv_title = "New conversation"
if st.session_state.active_conv is not None and messages is not None:
    conv_title = st.session_state.conversations[st.session_state.active_conv]["title"]

st.markdown(f"""
<div class="topbar">
    <span class="topbar-title">{conv_title}</span>
    <span class="model-pill">Gemini 2.5 Flash</span>
</div>
""", unsafe_allow_html=True)

# Messages
if not messages:
    st.markdown("""
    <div class="welcome">
        <div class="w-gem">✦</div>
        <h2>Hello, there</h2>
        <p>How can I help you today?</p>
        <div class="chips">
            <span class="chip">Explain quantum computing</span>
            <span class="chip">Write a Python function</span>
            <span class="chip">Summarize a concept</span>
            <span class="chip">Debug my code</span>
            <span class="chip">Brainstorm ideas</span>
            <span class="chip">Draft an email</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in messages:
        role    = msg["role"]
        content = msg["content"]
        ts      = msg.get("time", "")

        if content.startswith("__ERR__:"):
            st.markdown(f'<div class="err-box">⚠ {content[8:]}</div>', unsafe_allow_html=True)
            continue

        avatar = "🤖" if role == "assistant" else "👤"
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)
            st.caption(ts)

# Input
if prompt := st.chat_input("Ask Gemini anything…"):
    if st.session_state.active_conv is None:
        st.session_state.conversations.append({
            "title": prompt[:48],
            "messages": []
        })
        st.session_state.active_conv = len(st.session_state.conversations) - 1

    st.session_state.conversations[st.session_state.active_conv]["messages"].append({
        "role": "user", "content": prompt, "time": fmt_time()
    })
    st.rerun()

st.markdown('<div class="input-hint">Gemini may make mistakes. Consider checking important info.</div>',
            unsafe_allow_html=True)

# ── Auto-respond ──────────────────────────────────────────────────────────────
messages = active_messages()
if messages and messages[-1]["role"] == "user":
    last = messages[-1]["content"]

    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("""
        <div class="thinking">
            <div class="dot d1"></div>
            <div class="dot d2"></div>
            <div class="dot d3"></div>
        </div>
        """, unsafe_allow_html=True)

    with st.spinner(""):
        reply = call_api(last)

    idx = st.session_state.active_conv
    st.session_state.conversations[idx]["messages"].append({
        "role": "assistant", "content": reply, "time": fmt_time()
    })
    st.rerun()
