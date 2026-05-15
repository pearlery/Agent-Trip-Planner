import os
import json


from dotenv import load_dotenv
load_dotenv()

import streamlit as st

st.set_page_config(
    page_title="Travel Planning Agent",
    page_icon="✈️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: 700; }
    .step-thought {
        background: #1e1e00; border-left: 4px solid #ffd700;
        padding: 10px 14px; border-radius: 6px; margin: 6px 0;
        font-size: 0.9rem;
    }
    .step-action {
        background: #001e1e; border-left: 4px solid #00bcd4;
        padding: 10px 14px; border-radius: 6px; margin: 6px 0;
        font-size: 0.9rem;
    }
    .step-obs {
        background: #001e00; border-left: 4px solid #4caf50;
        padding: 10px 14px; border-radius: 6px; margin: 6px 0;
        font-size: 0.9rem;
    }
    div[data-testid="stChatMessage"] { padding: 6px 0; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Step renderers (defined early so they can be used in chat history below)
# ---------------------------------------------------------------------------
def _render_step(step: dict):
    t = step["type"]
    if t == "thought":
        st.markdown(
            f'<div class="step-thought">💭 <b>Thought</b> (รอบที่ {step.get("iteration","?")})<br>{step["content"]}</div>',
            unsafe_allow_html=True,
        )
    elif t == "action":
        st.markdown(
            f'<div class="step-action">⚡ <b>Action:</b> <code>{step["action"]}</code><br>'
            f'<pre>{json.dumps(step["input"], ensure_ascii=False, indent=2)}</pre></div>',
            unsafe_allow_html=True,
        )
    elif t == "observation":
        preview = step["content"][:500] + "..." if len(step["content"]) > 500 else step["content"]
        st.markdown(
            f'<div class="step-obs">📋 <b>Observation</b><br><pre style="white-space:pre-wrap">{preview}</pre></div>',
            unsafe_allow_html=True,
        )


def render_step_live(step: dict, container):
    with container:
        _render_step(step)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image("https://em-content.zobj.net/source/apple/354/airplane_2708-fe0f.png", width=60)
    st.title("Travel Planning Agent")
    st.caption("ระบบวางแผนการเดินทางต่างประเทศด้วย AI")
    st.divider()

    st.subheader("⚙️ การตั้งค่า")
    show_steps = st.toggle("แสดง Agent Steps", value=True)
    n_results = st.slider("จำนวนผลลัพธ์จาก RAG", min_value=1, max_value=5, value=3)

    st.divider()
    st.subheader("💡 ตัวอย่างคำถาม")
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
    st.caption(f"🤖 {backend} / {model}")

# ---------------------------------------------------------------------------
# Load agent (cached — runs once)
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
# Chat history
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "✈️"):
        if msg["role"] == "assistant" and show_steps and msg.get("steps"):
            with st.expander("🔍 Agent Steps", expanded=False):
                for step in msg["steps"]:
                    _render_step(step)
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Handle input
# ---------------------------------------------------------------------------
query = st.chat_input("✈️ ถามเรื่องการเดินทาง เช่น วางแผนทริปญี่ปุ่น 5 วัน งบ 50,000 บาท")

if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(query)

    with st.chat_message("assistant", avatar="✈️"):
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
