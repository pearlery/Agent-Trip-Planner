import os
import json

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Travel Planner · AI",
    page_icon="✈️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# CSS — Brown Theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,300;0,500;1,300&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --gold:    #C49A45;
    --gold-lt: #E8C878;
    --bg:      #0B0705;
    --bg2:     #150F09;
    --bg3:     #1E1510;
    --bg4:     #281C12;
    --text:    #F0E6D3;
    --text2:   #BFA882;
    --text3:   #7A6245;
    --border:  rgba(196,154,69,0.18);
    --border2: rgba(196,154,69,0.35);
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes goldPulse {
    0%, 100% { opacity: 0.5; }
    50%       { opacity: 1; }
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App background ── */
.stApp {
    background: var(--bg);
    min-height: 100vh;
}

/* ── Main content area ── */
.main .block-container {
    padding-top: 0.5rem;
    padding-bottom: 9rem;
    max-width: 800px !important;
}

/* ── Topbar ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0 12px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
    animation: fadeUp 0.5s ease both;
}
.topbar-title {
    font-family: 'Fraunces', serif;
    font-size: 12px;
    font-weight: 300;
    font-style: italic;
    color: var(--text3);
    letter-spacing: 0.5px;
}

/* ── Hero ── */
.hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 0 24px;
    animation: fadeUp 0.6s ease 0.05s both;
}
.hero-eyebrow {
    font-size: 10px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--text3);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.hero-eyebrow::before, .hero-eyebrow::after {
    content: '';
    width: 32px;
    height: 1px;
    background: var(--border2);
}
.hero-name {
    font-family: 'Fraunces', serif;
    font-size: 44px;
    font-weight: 300;
    letter-spacing: 8px;
    text-transform: uppercase;
    color: var(--gold-lt);
    margin-bottom: 6px;
    line-height: 1;
}
.hero-tagline {
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text3);
    margin-bottom: 10px;
}
.hero-divider {
    width: 48px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
    margin: 10px auto;
    animation: goldPulse 3s ease-in-out infinite;
}
.hero-desc {
    font-size: 13px;
    color: var(--text3);
    font-style: italic;
    text-align: center;
}

/* ── Feature cards ── */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin: 24px 0 16px;
    width: 100%;
    animation: fadeUp 0.6s ease 0.15s both;
}
.feat-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 16px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.feat-card:hover {
    background: var(--bg4);
    border-color: var(--border2);
    transform: translateY(-2px);
}
.feat-card .fc-icon {
    width: 30px;
    height: 30px;
    background: rgba(196,154,69,0.1);
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 10px;
    font-size: 15px;
    line-height: 1;
}
.feat-card .fc-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 4px;
}
.feat-card .fc-desc {
    font-size: 11px;
    color: var(--text3);
    line-height: 1.5;
}
.hero-hint {
    font-size: 11px;
    color: var(--text3);
    letter-spacing: 1px;
    text-align: center;
    opacity: 0.7;
    margin-top: 4px;
    animation: fadeUp 0.6s ease 0.25s both;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stCaption {
    color: var(--text2) !important;
    font-size: 12px !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--gold-lt) !important;
    font-family: 'Fraunces', serif !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] hr {
    border-color: var(--border) !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: var(--text2) !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    text-align: left !important;
    padding: 6px 4px !important;
    transition: all 0.15s !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(196,154,69,0.08) !important;
    color: var(--gold-lt) !important;
    padding-left: 10px !important;
}

/* Toggle & Slider */
[data-testid="stSidebar"] .stToggle label span,
[data-testid="stSidebar"] .stSlider label {
    color: var(--text2) !important;
    font-size: 12px !important;
}

/* ── Chat messages ── */
div[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 4px 0 !important;
    animation: fadeUp 0.35s ease both;
}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background: var(--bg4);
    border: 1px solid var(--border2);
    border-radius: 12px 4px 12px 12px;
    padding: 12px 16px;
    color: var(--text) !important;
}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 4px 12px 12px 12px;
    padding: 12px 16px;
    color: var(--text) !important;
}
.msg-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--text3);
    margin-bottom: 3px;
    padding: 0 2px;
}
div[data-testid="stChatMessage"] .stMarkdown p { margin: 0.3em 0; font-size: 14px; line-height: 1.7; }
div[data-testid="stChatMessage"] .stMarkdown h1,
div[data-testid="stChatMessage"] .stMarkdown h2,
div[data-testid="stChatMessage"] .stMarkdown h3 {
    color: var(--gold-lt) !important;
    font-family: 'Fraunces', serif !important;
    font-weight: 500 !important;
}
div[data-testid="stChatMessage"] .stMarkdown strong { color: var(--gold-lt) !important; }
div[data-testid="stChatMessage"] .stMarkdown ul,
div[data-testid="stChatMessage"] .stMarkdown ol { padding-left: 1.4em; }
div[data-testid="stChatMessage"] .stMarkdown li { margin: 0.25em 0; }

/* ── Agent step rows ── */
.step-row {
    padding: 10px 14px 10px 18px;
    border-left: 2px solid transparent;
    font-size: 12px;
    line-height: 1.6;
    font-family: 'Inter', sans-serif;
}
.step-row + .step-row { border-top: 1px solid rgba(196,154,69,0.06); }
.step-row.thought { border-left-color: var(--gold);  background: rgba(196,154,69,0.04); color: #d4b870; }
.step-row.action  { border-left-color: #5ab8d0; background: rgba(90,184,208,0.04);  color: #90cfe0; }
.step-row.obs     { border-left-color: #5ab870; background: rgba(90,184,112,0.04);  color: #90d490; }
.step-tag {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 3px;
    opacity: 0.85;
}
.step-row code {
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    padding: 0 4px;
    font-size: 0.9em;
}
.step-row pre {
    background: rgba(0,0,0,0.25);
    border-radius: 5px;
    padding: 6px 10px;
    margin: 6px 0 0;
    font-size: 11px;
    overflow-x: auto;
    line-height: 1.5;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    color: var(--text2) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stExpander"] summary:hover { color: var(--gold-lt) !important; }

/* ── Input bar ── */
[data-testid="stBottom"] {
    position: fixed !important;
    left: 0 !important;
    width: 100% !important;
    bottom: 0 !important;
    z-index: 1000 !important;
    background: var(--bg) !important;
    border-top: 1px solid var(--border) !important;
    padding: 14px 1rem 18px !important;
    pointer-events: none !important;
}
[data-testid="stBottom"] > div,
[data-testid="stBottom"] [data-testid="stChatInputContainer"] {
    width: min(760px, calc(100vw - 2rem)) !important;
    margin: 0 auto !important;
    background: transparent !important;
    pointer-events: none !important;
}
[data-testid="stChatInput"] {
    width: 100% !important;
    pointer-events: auto !important;
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 14px !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text) !important;
    background: transparent !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text3) !important;
    font-style: italic;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--gold) !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] button {
    background: var(--gold) !important;
    border: none !important;
    border-radius: 10px !important;
    transition: all 0.15s !important;
}
[data-testid="stChatInput"] button:hover { background: var(--gold-lt) !important; }
[data-testid="stChatInput"] button svg { fill: var(--bg) !important; }

@media (max-width: 768px) {
    [data-testid="stBottom"] {
        left: 0 !important;
        padding: 12px 0.6rem max(0.8rem, env(safe-area-inset-bottom)) !important;
    }
    [data-testid="stBottom"] > div,
    [data-testid="stBottom"] [data-testid="stChatInputContainer"] {
        width: calc(100vw - 1.2rem) !important;
    }
    .hero-name { font-size: 30px !important; letter-spacing: 4px !important; }
    .cards-grid { grid-template-columns: 1fr 1fr !important; }
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--gold) !important; }

/* ── Override gray text ── */
.st-emotion-cache-pk3c77 { color: #ffffff !important; }

/* ── Hide toolbar ── */
[data-testid="stAppToolbar"] { display: none !important; }

/* ── Transparent Streamlit header ── */
[data-testid="stHeader"] {
    background: transparent !important;
    border-bottom: none !important;
    box-shadow: none !important;
}

/* ── Sidebar toggle ── */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarNavItems"] { display: block !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(196,154,69,0.5); }
</style>
""", unsafe_allow_html=True)

components.html(
    """
    <script>
    (() => {
      const getBottom = () =>
        window.parent.document.querySelector('[data-testid="stBottom"]') ||
        window.parent.document.querySelector('.stBottom.st-emotion-cache-1p2n2i4.e4man112') ||
        window.parent.document.querySelector('.stBottom');

      const applyChatInputLayout = () => {
        const doc = window.parent.document;
        const bottom = getBottom();
        const mainBlock = doc.querySelector('[data-testid="stMainBlockContainer"]');
        if (!bottom || !mainBlock) return;

        const rect = mainBlock.getBoundingClientRect();
        const vw = window.parent.innerWidth || doc.documentElement.clientWidth;
        const sidePad = vw <= 768 ? 10 : 16;
        const left = Math.max(0, rect.left + sidePad);
        const width = Math.max(280, Math.min(rect.width - (sidePad * 2), vw - (sidePad * 2)));

        bottom.style.setProperty('left', `${left}px`, 'important');
        bottom.style.setProperty('width', `${width}px`, 'important');
        bottom.style.setProperty('right', 'auto', 'important');
      };

      const run = () => window.requestAnimationFrame(applyChatInputLayout);
      window.parent.addEventListener('resize', run, { passive: true });
      window.parent.addEventListener('load', run);

      const observer = new MutationObserver(run);
      observer.observe(window.parent.document.body, { childList: true, subtree: true, attributes: true });

      run();
      setTimeout(run, 120);
      setTimeout(run, 500);
      setTimeout(run, 1200);
    })();
    </script>
    """,
    height=0,
)

# ---------------------------------------------------------------------------
# Topbar + Hero
# ---------------------------------------------------------------------------
st.markdown("""
<div class="topbar">
    <div class="topbar-title">AI Travel Assistant &mdash; For Explorers</div>
</div>
<div class="hero">
    <div class="hero-eyebrow">AI Travel Assistant</div>
    <div class="hero-name">Travel Planner</div>
    <div class="hero-tagline">By AI &middot; For Explorers</div>
    <div class="hero-divider"></div>
    <div class="hero-desc">วางแผนการเดินทางต่างประเทศด้วยปัญญาประดิษฐ์</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Step renderers
# ---------------------------------------------------------------------------
def _render_step(step: dict):
    t = step["type"]
    if t == "thought":
        st.markdown(
            f'<div class="step-row thought">'
            f'<div class="step-tag">💭 Thought — รอบที่ {step.get("iteration","?")}</div>'
            f'{step["content"]}</div>',
            unsafe_allow_html=True,
        )
    elif t == "action":
        st.markdown(
            f'<div class="step-row action">'
            f'<div class="step-tag">⚡ Action — <code>{step["action"]}</code></div>'
            f'<pre>{json.dumps(step["input"], ensure_ascii=False, indent=2)}</pre></div>',
            unsafe_allow_html=True,
        )
    elif t == "observation":
        preview = step["content"][:500] + "..." if len(step["content"]) > 500 else step["content"]
        st.markdown(
            f'<div class="step-row obs">'
            f'<div class="step-tag">📋 Observation</div>'
            f'<pre style="white-space:pre-wrap">{preview}</pre></div>',
            unsafe_allow_html=True,
        )


def render_step_live(step: dict, container):
    with container:
        _render_step(step)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ✈️ Travel Planner")
    st.caption("ระบบวางแผนการเดินทางต่างประเทศด้วย AI")
    st.divider()

    st.markdown("### ⚙️ การตั้งค่า")
    show_steps = st.toggle("แสดง Agent Steps", value=True)
    n_results = st.slider("จำนวนผลลัพธ์จาก RAG", min_value=1, max_value=5, value=3)

    st.divider()
    if st.button("🗑️ ล้างการสนทนา", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()

    st.markdown("### 💡 ตัวอย่างคำถาม")
    examples = [
        "วางแผนทริป 5 วัน ไปญี่ปุ่น งบ 50,000 บาท",
        "ทัวร์เกาหลี 7 วัน มีโปรแกรมอะไรแนะนำบ้าง",
        "อากาศโตเกียวเดือนเมษายนเป็นยังไง",
        "อากาศสิงคโปร์เดือนธันวาคมเหมาะเที่ยวไหม",
        "แลกเงิน 30,000 บาท เป็นเยน ได้เท่าไหร่",
        "ทัวร์ยุโรป ราคาไม่เกิน 80,000 บาท มีอะไรบ้าง",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True, key=f"ex_{ex}"):
            st.session_state.pending_query = ex

    st.divider()
    backend = os.getenv("LLM_BACKEND", "typhoon")
    model = os.getenv("TYPHOON_MODEL", "typhoon-v2.5-30b-a3b-instruct")
    st.caption(f"🤖 {backend} · {model}")

# ---------------------------------------------------------------------------
# Load agent (cached)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="กำลังโหลด Agent และ Vector DB...")
def load_agent():
    from rag.vector_store import TravelVectorStore, init_vector_db
    from tools.semantic_search import init_search_tool, semantic_search
    from tools.exchange_rate import get_exchange_rate
    # from tools.hotel_search import search_hotels   # requires AMADEUS_API_KEY
    # from tools.flight_search import search_flights  # requires AMADEUS_API_KEY
    from tools.weather import get_weather
    from agent import TravelAgent

    vs = TravelVectorStore()
    if vs.count() == 0:
        init_vector_db()
    init_search_tool(vs)

    ag = TravelAgent(
        model_name=os.getenv("TYPHOON_MODEL", "typhoon-v2.5-30b-a3b-instruct"),
        backend=os.getenv("LLM_BACKEND", "typhoon"),
    )
    ag.register_tool("semantic_search", semantic_search)
    ag.register_tool("get_exchange_rate", get_exchange_rate)
    # ag.register_tool("search_hotels", search_hotels)   # requires AMADEUS_API_KEY
    # ag.register_tool("search_flights", search_flights)  # requires AMADEUS_API_KEY
    ag.register_tool("get_weather", get_weather)
    return ag

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# ---------------------------------------------------------------------------
# Welcome screen (empty state)
# ---------------------------------------------------------------------------
if not st.session_state.messages:
    st.markdown("""
<div class="cards-grid">
  <div class="feat-card">
    <div class="fc-icon">🗾</div>
    <div class="fc-title">ญี่ปุ่น &amp; เกาหลี</div>
    <div class="fc-desc">วางแผนทริปเอเชียตะวันออก พร้อมโปรแกรมครบครัน</div>
  </div>
  <div class="feat-card">
    <div class="fc-icon">🏰</div>
    <div class="fc-title">ยุโรป</div>
    <div class="fc-desc">สำรวจเส้นทางยุโรปในฝัน พร้อมราคาและโปรโมชั่น</div>
  </div>
  <div class="feat-card">
    <div class="fc-icon">💱</div>
    <div class="fc-title">อัตราแลกเปลี่ยน</div>
    <div class="fc-desc">เช็คอัตราแลกเงินเรียลไทม์ก่อนออกเดินทาง</div>
  </div>
  <div class="feat-card">
    <div class="fc-icon">🌤️</div>
    <div class="fc-title">สภาพอากาศ</div>
    <div class="fc-desc">ตรวจสอบอากาศปลายทาง เลือกช่วงเวลาที่เหมาะสม</div>
  </div>
</div>
<div class="hero-hint">พิมพ์คำถาม หรือเลือกตัวอย่างจาก Sidebar</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    role = msg["role"]
    label = "คุณ" if role == "user" else "Travel Planner AI"
    with st.chat_message(role, avatar="🧑" if role == "user" else "✈️"):
        st.markdown(f'<div class="msg-label">{label}</div>', unsafe_allow_html=True)
        if role == "assistant" and show_steps and msg.get("steps"):
            with st.expander("🔍 Agent Steps", expanded=False):
                for step in msg["steps"]:
                    _render_step(step)
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Handle input
# ---------------------------------------------------------------------------
query = st.chat_input("ถามเรื่องการเดินทาง เช่น วางแผนทริปญี่ปุ่น 5 วัน งบ 50,000 บาท")

if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="🧑"):
        st.markdown('<div class="msg-label">คุณ</div>', unsafe_allow_html=True)
        st.markdown(query)

    with st.chat_message("assistant", avatar="✈️"):
        st.markdown('<div class="msg-label">Travel Planner AI</div>', unsafe_allow_html=True)
        agent = load_agent()
        steps = []
        final_answer = ""

        steps_placeholder = st.container()
        answer_placeholder = st.empty()

        if show_steps:
            steps_box = steps_placeholder.expander("🔍 Agent กำลังคิด...", expanded=True)
        else:
            steps_box = None

        with st.spinner("กำลังวางแผนการเดินทาง..."):
            for step in agent.run_stream(query):
                steps.append(step)

                if show_steps and steps_box is not None:
                    render_step_live(step, steps_box)

                if step["type"] == "final":
                    final_answer = step["content"]
                    answer_placeholder.markdown(final_answer)
                elif step["type"] == "error":
                    final_answer = f"เกิดข้อผิดพลาด: {step['content']}"
                    answer_placeholder.error(final_answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": final_answer,
            "steps": steps,
        })
