import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetMind — AI Meeting Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --bg:          #07090f;
    --surface:     #0e1117;
    --surface-2:   #141822;
    --surface-3:   #1c2033;
    --border:      #1e2236;
    --border-soft: #252b40;
    --indigo:      #6366f1;
    --indigo-glow: #818cf8;
    --indigo-dim:  rgba(99,102,241,0.12);
    --cyan:        #22d3ee;
    --cyan-dim:    rgba(34,211,238,0.10);
    --emerald:     #10b981;
    --emerald-dim: rgba(16,185,129,0.12);
    --amber:       #f59e0b;
    --rose:        #f43f5e;
    --text:        #e8eaf6;
    --text-sub:    #9499b8;
    --text-muted:  #555f80;
    --radius-sm:   6px;
    --radius-md:   10px;
    --radius-lg:   14px;
    --shadow-card: 0 2px 12px rgba(0,0,0,0.5);
    --shadow-glow: 0 0 24px rgba(99,102,241,0.18);
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
    -webkit-font-smoothing: antialiased;
}

.stApp { background: var(--bg) !important; }

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: radial-gradient(circle, rgba(99,102,241,0.06) 1px, transparent 1px);
    background-size: 28px 28px;
    pointer-events: none;
    z-index: 0;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.55rem 1.25rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    margin-bottom: 1.75rem;
}
.topbar-left { display: flex; align-items: center; gap: 0.75rem; }
.topbar-logo {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1rem; font-weight: 800; letter-spacing: -0.02em;
    background: linear-gradient(120deg, #ffffff 0%, var(--indigo-glow) 60%, var(--cyan) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.topbar-divider { width: 1px; height: 18px; background: var(--border-soft); }
.topbar-sub { font-size: 0.7rem; color: var(--text-muted); letter-spacing: 0.08em; text-transform: uppercase; font-weight: 500; }
.topbar-right { display: flex; align-items: center; gap: 1rem; }
.topbar-author { font-size: 0.75rem; color: var(--text-sub); font-weight: 500; }
.topbar-gh {
    display: inline-flex; align-items: center; gap: 0.35rem;
    padding: 0.3rem 0.75rem; background: var(--surface-2);
    border: 1px solid var(--border-soft); border-radius: 20px;
    font-size: 0.7rem; font-weight: 600; color: var(--indigo-glow) !important;
    text-decoration: none !important; letter-spacing: 0.03em;
    transition: border-color 0.2s, background 0.2s;
}
.topbar-gh:hover { border-color: var(--indigo); background: var(--indigo-dim); }

[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] * { color: var(--text) !important; }

.sidebar-brand {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;
    background: linear-gradient(120deg, #fff 0%, var(--indigo-glow) 70%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    line-height: 1.2; margin-bottom: 0.25rem;
}
.sidebar-tagline { font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.15em; font-weight: 500; }

.section-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--text-muted);
    margin-bottom: 0.6rem; padding-left: 2px;
}

.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 1.4rem 1.5rem;
    margin-bottom: 1rem; position: relative; overflow: hidden;
    box-shadow: var(--shadow-card); transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.card:hover { border-color: var(--border-soft); box-shadow: var(--shadow-card), 0 0 0 1px rgba(99,102,241,0.07); }
.card-accent-bar {
    position: absolute; top: 0; left: 0; width: 100%; height: 2px;
    background: linear-gradient(90deg, var(--indigo), var(--cyan)); opacity: 0.6;
}
.card-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--text-muted);
    margin-bottom: 0.85rem; display: flex; align-items: center; gap: 0.45rem;
}
.card-content { font-size: 0.875rem; line-height: 1.75; color: var(--text-sub); }

.session-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.25rem; font-weight: 700; letter-spacing: -0.01em;
    color: var(--text); line-height: 1.3;
}

.badge {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.22rem 0.65rem; border-radius: 20px;
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; font-family: 'Inter', sans-serif;
}
.badge-indigo  { background: var(--indigo-dim);   color: var(--indigo-glow); border: 1px solid rgba(99,102,241,0.25); }
.badge-cyan    { background: var(--cyan-dim);      color: var(--cyan);        border: 1px solid rgba(34,211,238,0.25); }
.badge-emerald { background: var(--emerald-dim);   color: var(--emerald);     border: 1px solid rgba(16,185,129,0.25); }
.badge-amber   { background: rgba(245,158,11,0.1); color: var(--amber);       border: 1px solid rgba(245,158,11,0.25); }

.pipeline-row {
    display: flex; align-items: center; gap: 0.65rem;
    padding: 0.55rem 0.8rem; background: var(--surface-2);
    border-radius: var(--radius-sm); margin-bottom: 0.35rem;
    border: 1px solid var(--border); font-size: 0.78rem;
    color: var(--text-sub); transition: border-color 0.2s;
}
.pipeline-row.active { border-color: var(--indigo); color: var(--text); }
.pipeline-row.done   { border-color: rgba(16,185,129,0.3); }
.pip-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.pip-dot.active  { background: var(--indigo-glow); box-shadow: 0 0 7px var(--indigo-glow); animation: blink 1.4s ease-in-out infinite; }
.pip-dot.done    { background: var(--emerald); }
.pip-dot.pending { background: var(--border-soft); }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

.stTextInput > div > div > input {
    background: var(--surface-2) !important; border: 1px solid var(--border-soft) !important;
    border-radius: var(--radius-md) !important; color: var(--text) !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.875rem !important;
    padding: 0.55rem 0.85rem !important; transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--indigo) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important; outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-muted) !important; }
.stSelectbox > div > div {
    background: var(--surface-2) !important; border: 1px solid var(--border-soft) !important;
    border-radius: var(--radius-md) !important; color: var(--text) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--indigo) 0%, #4f46e5 100%) !important;
    color: #fff !important; border: none !important; border-radius: var(--radius-md) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important;
    font-size: 0.82rem !important; letter-spacing: 0.04em !important;
    padding: 0.6rem 1.4rem !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    text-transform: uppercase !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(99,102,241,0.35) !important; }
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important; border: 1px solid var(--border-soft) !important;
    color: var(--text-sub) !important;
}
.stButton > button[kind="secondary"]:hover { border-color: var(--rose) !important; color: var(--rose) !important; box-shadow: none !important; }

.chat-wrap {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 1.1rem 1.25rem;
    max-height: 430px; overflow-y: auto; margin-bottom: 0.75rem;
    display: flex; flex-direction: column; gap: 1rem;
}
.chat-msg { display: flex; flex-direction: column; gap: 0.2rem; }
.chat-role { font-size: 0.6rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; }
.chat-bubble { display: inline-block; padding: 0.65rem 1rem; border-radius: 10px; font-size: 0.84rem; line-height: 1.65; max-width: 88%; }
.user-role   { color: var(--indigo-glow); }
.bot-role    { color: var(--cyan); }
.user-bubble { background: var(--indigo-dim); border: 1px solid rgba(99,102,241,0.22); align-self: flex-end; }
.bot-bubble  { background: var(--cyan-dim);   border: 1px solid rgba(34,211,238,0.18);  align-self: flex-start; }

.transcript-scroll {
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1.1rem 1.25rem;
    font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;
    line-height: 1.85; max-height: 310px; overflow-y: auto;
    color: var(--text-muted); white-space: pre-wrap; word-break: break-word;
}

.footer {
    display: flex; align-items: center; justify-content: center;
    gap: 0.6rem; padding: 1.25rem; margin-top: 2.5rem;
    border-top: 1px solid var(--border); font-size: 0.7rem; color: var(--text-muted);
}
.footer a { color: var(--indigo-glow) !important; text-decoration: none !important; font-weight: 600; transition: color 0.2s; }
.footer a:hover { color: var(--cyan) !important; }
.footer-dot { color: var(--border-soft); }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }
h1, h2, h3, h4, h5, h6 { font-family: 'Plus Jakarta Sans', sans-serif !important; color: var(--text) !important; }
label { color: var(--text-muted) !important; font-size: 0.78rem !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text-sub) !important; }
.stProgress > div > div > div { background: var(--indigo) !important; }
.stSpinner > div { border-top-color: var(--indigo) !important; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-soft); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--indigo); }

[data-testid="stExpander"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-lg) !important; }
[data-testid="stExpander"] summary { color: var(--text-sub) !important; font-size: 0.82rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Helpers ──────────────────────────────────────────────────────────────────
def pip_class(key: str) -> str:
    return st.session_state.pipeline_steps.get(key, "pending")

def render_pipeline_row(label: str, key: str, icon: str):
    cls     = pip_class(key)
    row_cls = {"active": "active", "done": "done"}.get(cls, "")
    dot_cls = cls
    st.markdown(
        f'<div class="pipeline-row {row_cls}">'
        f'<div class="pip-dot {dot_cls}"></div>'
        f'<span>{icon}&nbsp; {label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">🎬 MeetMind</div>'
        '<div class="sidebar-tagline">AI Meeting Intelligence</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown('<div class="section-label">Source</div>', unsafe_allow_html=True)
    source = st.text_input(
        "YouTube URL or File Path",
        placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4",
        label_visibility="collapsed",
    )

    st.markdown('<div class="section-label" style="margin-top:0.75rem">Language</div>', unsafe_allow_html=True)
    language = st.selectbox("Language", ["english", "hinglish"], index=0, label_visibility="collapsed")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    run_btn = st.button("⚡  Analyse", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<div class="section-label">Pipeline Status</div>', unsafe_allow_html=True)
        for step, icon, label in [
            ("audio",      "🔊", "Audio Processing"),
            ("transcript", "📝", "Transcription"),
            ("title",      "🏷️",  "Title Generation"),
            ("summary",    "📋", "Summarisation"),
            ("extract",    "🔍", "Extraction"),
            ("rag",        "🧠", "RAG Engine"),
        ]:
            render_pipeline_row(label, step, icon)

    st.markdown(
        '<div style="position:fixed;bottom:1.1rem;left:1rem;right:1rem">'
        '<div style="font-size:0.65rem;color:#555f80;text-align:center;line-height:1.6">'
        'Built by <span style="color:#818cf8;font-weight:600">Deepak Kumar</span><br>'
        '<a href="https://github.com/connect4deepak" target="_blank" '
        'style="color:#818cf8;text-decoration:none;font-weight:600">'
        '&#8997; github.com/connect4deepak'
        '</a></div></div>',
        unsafe_allow_html=True,
    )

# ── Top Nav Bar ───────────────────────────────────────────────────────────────
st.markdown(
    '<div class="topbar">'
    '<div class="topbar-left">'
    '<span class="topbar-logo">🎬 MeetMind</span>'
    '<div class="topbar-divider"></div>'
    '<span class="topbar-sub">AI Meeting Intelligence</span>'
    '</div>'
    '<div class="topbar-right">'
    '<span class="topbar-author">Deepak Kumar</span>'
    '<a class="topbar-gh" href="https://github.com/connect4deepak" target="_blank">'
    '<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">'
    '<path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57'
    ' 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695'
    '-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99'
    '.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225'
    '-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405'
    'c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225'
    ' 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3'
    ' 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>'
    '</svg>connect4deepak</a></div></div>',
    unsafe_allow_html=True,
)

# ── Pipeline Execution ────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Please enter a YouTube URL or a local file path.")
    else:
        st.session_state.pipeline_done  = False
        st.session_state.result         = None
        st.session_state.chat_history   = []
        st.session_state.pipeline_steps = {}

        progress_ph = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            with progress_ph.container():
                st.info("⚙️ Pipeline running — live status in the sidebar.")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items = extract_action_items(transcript)
            decisions    = extract_key_decisions(transcript)
            questions    = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title":          title,
                "transcript":     transcript,
                "summary":        summary,
                "action_items":   action_items,
                "key_decisions":  decisions,
                "open_questions": questions,
                "rag_chain":      rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_ph.success("✅ Analysis complete!")
            time.sleep(0.5)
            progress_ph.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio", "transcript", "title", "summary", "extract", "rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_ph.error(f"❌ {e}")

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    st.markdown(
        f'<div class="card"><div class="card-accent-bar"></div>'
        f'<div class="card-title">📌 Session Title</div>'
        f'<div class="session-title">{r["title"]}</div></div>',
        unsafe_allow_html=True,
    )

    col_s, col_t = st.columns([3, 2], gap="medium")
    with col_s:
        st.markdown(
            f'<div class="card"><div class="card-accent-bar"></div>'
            f'<div class="card-title">📋 Summary</div>'
            f'<div class="card-content">{r["summary"]}</div></div>',
            unsafe_allow_html=True,
        )
    with col_t:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(
                f'<div class="transcript-scroll">{r["transcript"]}</div>',
                unsafe_allow_html=True,
            )

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(
            f'<div class="card"><div class="card-accent-bar"></div>'
            f'<div class="card-title">✅ Action Items</div>'
            f'<div class="card-content">{r["action_items"]}</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="card"><div class="card-accent-bar"></div>'
            f'<div class="card-title">🔑 Key Decisions</div>'
            f'<div class="card-content">{r["key_decisions"]}</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="card"><div class="card-accent-bar"></div>'
            f'<div class="card-title">❓ Open Questions</div>'
            f'<div class="card-content">{r["open_questions"]}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.markdown(
        '<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem">'
        '<span style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:1.05rem;font-weight:700;color:#e8eaf6">💬 Chat with your Meeting</span>'
        '<span class="badge badge-indigo">RAG</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.chat_history:
        chat_html = '<div class="chat-wrap">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += (
                    '<div class="chat-msg" style="align-items:flex-end">'
                    '<span class="chat-role user-role">You</span>'
                    f'<div class="chat-bubble user-bubble">{msg["content"]}</div>'
                    '</div>'
                )
            else:
                chat_html += (
                    '<div class="chat-msg" style="align-items:flex-start">'
                    '<span class="chat-role bot-role">Assistant</span>'
                    f'<div class="chat-bubble bot-bubble">{msg["content"]}</div>'
                    '</div>'
                )
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="card" style="text-align:center;padding:2.5rem 1.5rem">'
            '<div class="card-accent-bar"></div>'
            '<div style="font-size:2rem;margin-bottom:0.6rem">💬</div>'
            '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:0.9rem;font-weight:600;color:#e8eaf6;margin-bottom:0.3rem">Ask anything about your meeting</div>'
            '<div style="font-size:0.78rem;color:#555f80">Powered by retrieval-augmented generation over the full transcript</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    chat_in, chat_btn = st.columns([5, 1], gap="small")
    with chat_in:
        user_input = st.text_input(
            "Ask a question",
            placeholder="e.g. What were the key decisions made?",
            label_visibility="collapsed",
        )
    with chat_btn:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️  Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # ── Empty State ───────────────────────────────────────────────────────────
    # HTML is built via string concatenation — zero multiline indentation so
    # Markdown's 4-space code-block rule never fires on any inner tag.
    _badge = (
        'display:inline-flex;align-items:center;padding:0.22rem 0.65rem;'
        'border-radius:20px;font-size:0.62rem;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;'
    )
    empty_html = (
        '<div style="display:flex;flex-direction:column;align-items:center;'
        'justify-content:center;padding:5rem 2rem;text-align:center;">'

        '<div style="width:64px;height:64px;border-radius:16px;'
        'background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:1.8rem;margin-bottom:1.5rem;">&#127916;</div>'

        '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:1.4rem;'
        'font-weight:800;color:#e8eaf6;letter-spacing:-0.02em;margin-bottom:0.5rem;">'
        'Ready to Analyse</div>'

        '<div style="color:#555f80;font-size:0.84rem;max-width:380px;'
        'line-height:1.75;margin-bottom:2rem;">'
        'Paste a YouTube URL or local file path in the sidebar, select the language, and click '
        '<strong style="color:#818cf8;">Analyse</strong> to get started.</div>'

        '<div style="display:flex;gap:0.6rem;flex-wrap:wrap;justify-content:center;">'

        f'<span style="{_badge}background:rgba(99,102,241,0.12);color:#818cf8;'
        'border:1px solid rgba(99,102,241,0.25);">Transcription</span>'

        f'<span style="{_badge}background:rgba(34,211,238,0.10);color:#22d3ee;'
        'border:1px solid rgba(34,211,238,0.25);">Summarisation</span>'

        f'<span style="{_badge}background:rgba(16,185,129,0.12);color:#10b981;'
        'border:1px solid rgba(16,185,129,0.25);">RAG Chat</span>'

        f'<span style="{_badge}background:rgba(245,158,11,0.10);color:#f59e0b;'
        'border:1px solid rgba(245,158,11,0.25);">Action Items</span>'

        '</div></div>'
    )
    st.markdown(empty_html, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">'
    '<span>Built by</span>'
    '<strong style="color:#e8eaf6">Deepak Kumar</strong>'
    '<span class="footer-dot">·</span>'
    '<a href="https://github.com/connect4deepak" target="_blank">github.com/connect4deepak</a>'
    '<span class="footer-dot">·</span>'
    '<span>MeetMind v1.0</span>'
    '</div>',
    unsafe_allow_html=True,
)