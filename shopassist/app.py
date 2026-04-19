import streamlit as st
from datetime import datetime
from agent import run_agent

st.set_page_config(
    page_title="ShopAssist AI",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:        #faf7ff;
    --surface:   #ffffff;
    --sidebar:   #1a0533;
    --card:      #f3eeff;
    --border:    #e4d9ff;
    --accent:    #7c3aed;
    --accent2:   #a855f7;
    --teal:      #0d9488;
    --orange:    #ea580c;
    --pink:      #db2777;
    --green:     #059669;
    --blue:      #2563eb;
    --text:      #1e1b4b;
    --muted:     #6b7280;
    --user-bg:   #7c3aed;
    --bot-bg:    #ffffff;
}

html, body, [data-testid="stApp"] {
    background: var(--bg) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text) !important;
}
#MainMenu, footer { display:none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #e9d5ff !important; }

.main .block-container { padding: 1.5rem 2rem !important; max-width: 920px !important; }

/* ── Header ── */
.app-header {
    display: flex; align-items: center; gap: 16px;
    padding: 1.4rem 2rem;
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #db2777 100%);
    border-radius: 20px;
    margin-bottom: 1.4rem;
    box-shadow: 0 8px 32px rgba(124,58,237,0.35);
    position: relative; overflow: hidden;
}
.app-header::after {
    content:''; position:absolute; top:-40%; right:-5%;
    width:200px; height:200px; border-radius:50%;
    background: rgba(255,255,255,0.07);
}
.app-header .logo { font-size:2.6rem; z-index:1; }
.app-header h1 {
    margin:0 !important; font-size:1.9rem !important; font-weight:800 !important;
    color:white !important; letter-spacing:-0.5px; z-index:1;
}
.app-header .sub { font-size:0.8rem; color:rgba(255,255,255,0.75); margin-top:3px; z-index:1; }
.online-pill {
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(255,255,255,0.2); border-radius:20px;
    padding:2px 10px; font-size:0.72rem; color:white; font-weight:600;
}
.dot-green { width:7px;height:7px;background:#4ade80;border-radius:50%;animation:blink 1.8s infinite; }
@keyframes blink { 0%,100%{opacity:1}50%{opacity:0.2} }

/* ── Messages ── */
.msg-wrap { margin-bottom:16px; }
.msg-row { display:flex; align-items:flex-end; gap:10px; }
.msg-row.user { flex-direction:row-reverse; }

.avatar {
    width:38px; height:38px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:1rem; font-weight:800; flex-shrink:0;
    box-shadow: 0 3px 10px rgba(0,0,0,0.15);
}
.avatar.bot  { background: linear-gradient(135deg,#7c3aed,#a855f7); color:white; }
.avatar.user { background: linear-gradient(135deg,#ea580c,#f97316); color:white; }

.bubble {
    max-width:68%; padding:13px 17px;
    font-size:0.875rem; line-height:1.7; white-space:pre-wrap; word-break:break-word;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.bubble.bot {
    background: white;
    border: 1px solid #e4d9ff;
    border-radius: 18px 18px 18px 4px;
    color: #1e1b4b;
}
.bubble.user {
    background: linear-gradient(135deg, #7c3aed, #9333ea);
    border-radius: 18px 18px 4px 18px;
    color: white;
}
.sender {
    font-size:0.68rem; font-weight:700; letter-spacing:0.08em;
    text-transform:uppercase; margin-bottom:4px;
}
.bubble.bot .sender  { color:#7c3aed; }
.bubble.user .sender { color:rgba(255,255,255,0.75); }
.msg-time { font-size:0.65rem; color:#9ca3af; margin-top:5px; text-align:right; }
.bubble.bot .msg-time { text-align:left; }

/* ── Badges ── */
.badge {
    display:inline-flex; align-items:center; gap:4px;
    font-size:0.67rem; font-weight:700; padding:3px 9px;
    border-radius:10px; margin-top:7px; letter-spacing:0.04em;
}
.badge-faq     { background:#ede9fe; color:#7c3aed; }
.badge-order   { background:#d1fae5; color:#065f46; }
.badge-unknown { background:#fce7f3; color:#9d174d; }

/* ── Welcome ── */
.welcome {
    background: linear-gradient(135deg,#faf5ff,#fdf2f8);
    border: 2px solid #e9d5ff;
    border-radius:20px; padding:28px; margin-bottom:20px; text-align:center;
}
.welcome h3 { font-size:1.15rem; font-weight:800; color:#4c1d95; margin:0 0 8px; }
.welcome p  { font-size:0.84rem; color:#6b7280; margin:0; line-height:1.7; }

/* ── Feature pills on welcome ── */
.feat-row { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin-top:14px; }
.feat-pill {
    background:white; border:1.5px solid #e4d9ff; border-radius:20px;
    padding:5px 13px; font-size:0.75rem; font-weight:600; color:#7c3aed;
    box-shadow:0 1px 4px rgba(124,58,237,0.1);
}

/* ── Quick chips ── */
.stButton > button {
    background: white !important;
    color: #4c1d95 !important;
    border: 1.5px solid #c4b5fd !important;
    border-radius: 22px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    padding: 7px 15px !important;
    transition: all 0.2s !important;
    box-shadow: 0 1px 4px rgba(124,58,237,0.12) !important;
}
.stButton > button:hover {
    background: #7c3aed !important;
    color: white !important;
    border-color: #7c3aed !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(124,58,237,0.3) !important;
}

/* New conv button */
.newbtn > div > button {
    background: linear-gradient(135deg,#a855f7,#7c3aed) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    font-size: 0.88rem !important;
    box-shadow: 0 4px 14px rgba(168,85,247,0.5) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    border: 2px solid #c4b5fd !important;
    border-radius: 16px !important;
    background: white !important;
    box-shadow: 0 4px 16px rgba(124,58,237,0.1) !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
    color: #0f172a !important;
    background: #ffffff !important;
    caret-color: #7c3aed !important; 
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}

textarea {
    color: #0f172a !important;
}

/* ── Sidebar cards ── */
.scard {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px; padding:14px; margin-bottom:12px;
}
.scard-title {
    font-size:0.68rem; font-weight:700; letter-spacing:0.12em;
    text-transform:uppercase; color:#c084fc !important; margin-bottom:9px;
}
.scard p { font-size:0.79rem; color:#d8b4fe !important; margin:3px 0; }

/* ── Stat cards ── */
.stats-row { display:flex; gap:8px; margin-bottom:14px; }
.stat-box {
    flex:1; background:rgba(255,255,255,0.08);
    border:1px solid rgba(255,255,255,0.12);
    border-radius:12px; padding:10px; text-align:center;
}
.stat-num { font-size:1.5rem; font-weight:800; color:#e879f9 !important; }
.stat-lbl { font-size:0.65rem; color:#a78bfa !important; margin-top:1px; }

/* ── Memory tags ── */
.mem-tag {
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(167,139,250,0.2); border:1px solid rgba(167,139,250,0.35);
    border-radius:20px; padding:3px 10px; font-size:0.74rem;
    color:#e9d5ff !important; margin:2px;
}

/* ── Divider ── */
hr.div { border:none; border-top:1px solid rgba(255,255,255,0.1); margin:12px 0; }

/* ── Section label ── */
.section-lbl {
    font-size:0.75rem; font-weight:700; color:#7c3aed;
    letter-spacing:0.06em; text-transform:uppercase;
    margin:0 0 8px; display:flex; align-items:center; gap:6px;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State ─────────────────────────────────────────────────────────
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {"messages": [], "memory": {}}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "msg_count" not in st.session_state:
    st.session_state.msg_count = 0

def ts():
    return datetime.now().strftime("%I:%M %p")

def get_badge(text: str) -> str:
    tl = text.lower()
    if any(k in tl for k in ["order #", "out for delivery", "shipped", "processing",
                               "delivered", "cancelled", "courier", "eta:"]):
        return '<span class="badge badge-order">📦 Order Tracking</span>'
    if "don't have that information" in tl or "outside our" in tl:
        return '<span class="badge badge-unknown">⚠ Out of Scope</span>'
    return '<span class="badge badge-faq">📚 Knowledge Base</span>'

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:18px 0 22px">
        <div style="font-size:3rem">🛍️</div>
        <div style="font-weight:800;font-size:1.2rem;color:#e9d5ff;margin-top:6px">ShopAssist AI</div>
        <div style="font-size:0.72rem;color:#9f7aea;margin-top:3px">Groq LLaMA 3.3 · LangGraph · ChromaDB</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="newbtn">', unsafe_allow_html=True)
    if st.button("✦  New Conversation", use_container_width=True):
        st.session_state.agent_state = {"messages": [], "memory": {}}
        st.session_state.chat_history = []
        st.session_state.msg_count = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="div">', unsafe_allow_html=True)

    total_msgs = len([x for x in st.session_state.chat_history if x[0] == "user"])
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-box"><div class="stat-num">{total_msgs}</div><div class="stat-lbl">Chats</div></div>
        <div class="stat-box"><div class="stat-num">10</div><div class="stat-lbl">Topics</div></div>
        <div class="stat-box"><div class="stat-num">5</div><div class="stat-lbl">Orders</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="scard">
        <div class="scard-title">⚙ About</div>
        <p>AI support agent for e-commerce. Uses RAG + LangGraph for accurate, memory-aware responses.</p>
    </div>
    <div class="scard">
        <div class="scard-title">📚 Topics Covered</div>
        <p>🔄 Return Policy (30 days)</p>
        <p>💸 Refund Policy</p>
        <p>🚚 Shipping &amp; Delivery</p>
        <p>❌ Order Cancellation</p>
        <p>💳 Payment Methods</p>
        <p>🛡️ Product Warranty</p>
        <p>⏱ Delivery Delays</p>
        <p>🎧 Customer Support</p>
        <p>🔁 Exchange Policy</p>
        <p>📦 Order Tracking</p>
    </div>
    <div class="scard">
        <div class="scard-title">🔍 Test Order IDs</div>
        <p>Try: <b>123</b> · <b>456</b> · <b>789</b> · <b>321</b> · <b>654</b></p>
        <p style="font-size:0.7rem;color:#7c6fad!important;margin-top:3px">Each returns a different status</p>
    </div>
    """, unsafe_allow_html=True)

    memory = st.session_state.agent_state.get("memory", {})
    if memory:
        tags = ""
        if memory.get("user_name"):
            tags += f'<span class="mem-tag">👤 {memory["user_name"]}</span>'
        if memory.get("order_id"):
            tags += f'<span class="mem-tag">📦 #{memory["order_id"]}</span>'
        st.markdown(f'<div class="scard"><div class="scard-title">🧠 Session Memory</div>{tags}</div>',
                    unsafe_allow_html=True)

    st.markdown('<hr class="div">', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.68rem;color:#4c3575;text-align:center">ShopAssist v1.0 · AI may make mistakes</p>',
                unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="logo">🛍️</div>
    <div>
        <h1>ShopAssist AI</h1>
        <div class="sub">
            <span class="online-pill"><span class="dot-green"></span>Online</span>
            &nbsp;·&nbsp; E-Commerce Customer Support Agent
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Welcome screen ──────────────────────────────────────────────────────────
if not st.session_state.chat_history:
    st.markdown("""
    <div class="welcome">
        <h3>👋 Hey! I'm ShopAssist, your AI support agent.</h3>
        <p>Ask me about returns, refunds, shipping, payments — or track any order instantly.<br>
        I remember your order ID and name throughout our conversation!</p>
        <div class="feat-row">
            <span class="feat-pill">🧠 Memory-aware</span>
            <span class="feat-pill">📚 10 FAQ topics</span>
            <span class="feat-pill">📦 Order tracking</span>
            <span class="feat-pill">🚫 No hallucination</span>
            <span class="feat-pill">⚡ Instant answers</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-lbl">✦ Try asking something</div>', unsafe_allow_html=True)
    chips = [
        "What is your return policy?",
        "How long does delivery take?",
        "How do I cancel my order?",
        "What payment methods do you accept?",
        "Track order id 123",
        "What is your refund process?",
    ]
    cols = st.columns(3)
    for i, chip in enumerate(chips):
        if cols[i % 3].button(chip, key=f"chip_{i}"):
            with st.spinner("Thinking..."):
                answer, new_state = run_agent(chip, st.session_state.agent_state)
            st.session_state.agent_state = new_state
            st.session_state.chat_history.append(("user", chip, ts()))
            st.session_state.chat_history.append(("bot", answer, ts()))
            st.session_state.msg_count += 1
            st.rerun()

# ─── Chat History ────────────────────────────────────────────────────────────
for role, text, t in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"""
        <div class="msg-wrap">
          <div class="msg-row user">
            <div class="avatar user">U</div>
            <div class="bubble user">
              <div class="sender">You</div>
              {text}
              <div class="msg-time">{t}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        badge = get_badge(text)
        st.markdown(f"""
        <div class="msg-wrap">
          <div class="msg-row bot">
            <div class="avatar bot">🤖</div>
            <div class="bubble bot">
              <div class="sender">ShopAssist</div>
              {text}
              {badge}
              <div class="msg-time">{t}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

# ─── Chat Input ──────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask me about returns, shipping, orders... (press Enter to send)")

if user_input and user_input.strip():
    q = user_input.strip()
    with st.spinner("ShopAssist is thinking..."):
        answer, new_state = run_agent(q, st.session_state.agent_state)
    st.session_state.agent_state = new_state
    st.session_state.chat_history.append(("user", q, ts()))
    st.session_state.chat_history.append(("bot", answer, ts()))
    st.session_state.msg_count += 1
    st.rerun()