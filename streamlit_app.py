# ============================================================
# TatvaAI v6 - Streamlit Web App
# Multi-AI Consensus Research System
# Free | Educational | Made in India 🇮🇳
# ============================================================

import os
import datetime
import streamlit as st
from dotenv import load_dotenv
from google import genai
from groq import Groq
import wikipedia
from ddgs import DDGS
from fpdf import FPDF, XPos, YPos

load_dotenv()

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="TatvaAI — Multi-AI Research System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Constants ─────────────────────────────────────────────────
VERSION = "6.0"
CURRENT_YEAR = datetime.datetime.now().year
BLOCKED_TOPICS = [
    "bomb","weapon","kill","hack","virus",
    "drug","poison","terror","suicide","explosive"
]

# ── CSS Styling ───────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0a0a1a; }
    .stApp { background: linear-gradient(135deg, #0a0a1a 0%, #0d0d2b 100%); }
    h1, h2, h3 { color: #00d4ff !important; }
    .tatva-header {
        background: linear-gradient(135deg, #0f0f3d, #1a1a6e);
        border: 1px solid #00d4ff;
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        margin-bottom: 24px;
    }
    .tatva-title {
        font-size: 48px;
        font-weight: 900;
        color: #00d4ff;
        letter-spacing: 6px;
        margin: 0;
    }
    .tatva-subtitle {
        font-size: 16px;
        color: #a0c4ff;
        margin-top: 8px;
        letter-spacing: 2px;
    }
    .answer-box {
        background: #0d1b2a;
        border: 1px solid #00d4ff33;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
    }
    .step-badge {
        background: #00d4ff22;
        border: 1px solid #00d4ff;
        border-radius: 20px;
        padding: 4px 16px;
        color: #00d4ff;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }
    .disclaimer {
        background: #1a0a0a;
        border-left: 4px solid #ff4444;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        color: #ffaaaa;
        font-size: 13px;
    }
    .sidebar-info {
        background: #0d1b2a;
        border: 1px solid #00d4ff33;
        border-radius: 10px;
        padding: 16px;
        margin: 8px 0;
        font-size: 13px;
        color: #a0c4ff;
    }
    .stButton>button {
        background: linear-gradient(135deg, #00d4ff, #0066ff);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 32px;
        font-size: 16px;
        font-weight: 700;
        width: 100%;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00ffff, #0088ff);
        transform: translateY(-2px);
    }
    .stTextArea textarea {
        background: #0d1b2a !important;
        color: #ffffff !important;
        border: 1px solid #00d4ff55 !important;
        border-radius: 10px !important;
        font-size: 15px !important;
    }
    .metric-card {
        background: #0d1b2a;
        border: 1px solid #00d4ff33;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Init Clients ──────────────────────────────────────────────
@st.cache_resource
def init_clients():
    gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return gemini, groq

gemini_client, groq_client = init_clients()

# ── Helper Functions ──────────────────────────────────────────
def clean_text(text):
    if not text:
        return ""
    replacements = {
        "\u2022":"-","\u2019":"'","\u2018":"'",
        "\u201c":'"',"\u201d":'"',"\u2013":"-",
        "\u2014":"-","\u2026":"...","\u00a0":" ",
        "\u00ae":"(R)","\u2122":"(TM)","\u00a9":"(C)",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode('latin-1', errors='replace').decode('latin-1')

def safety_check(query):
    for topic in BLOCKED_TOPICS:
        if topic in query.lower():
            return False, topic
    return True, None

def ask_gemini(query):
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash", contents=query)
        return response.text.strip()
    except Exception as e:
        return f"Gemini Error: {str(e)}"

def ask_groq(query):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":query}])
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Groq Error: {str(e)}"

def get_wikipedia(query):
    try:
        wikipedia.set_lang("en")
        results = wikipedia.search(query, results=2)
        if results:
            page = wikipedia.page(results[0])
            return page.summary[:600], page.url
        return "Wikipedia article nahi mila.", ""
    except:
        return "Wikipedia article nahi mila.", ""

def get_web_search(query):
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=3):
                results.append(f"• {r['title']}: {r['body'][:150]}")
        return "\n".join(results) if results else "Web results nahi mile."
    except Exception as e:
        return f"Web search error: {str(e)}"

def check_consensus(ans1, ans2, query):
    try:
        prompt = f"""Two AIs answered: "{query}"
AI-1: {ans1[:200]}
AI-2: {ans2[:200]}
Do both agree on main point? Reply ONLY: YES or NO"""
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt)
        return "YES" in response.text.upper()
    except:
        return False

def get_best_answer(query, g_ans, gr_ans, wiki, web):
    try:
        prompt = f"""You are TatvaAI. Create a comprehensive fact-checked answer.
Question: {query}
Gemini: {g_ans[:400]}
Groq: {gr_ans[:400]}
Wikipedia: {wiki[:300]}
Web: {web[:300]}
Write balanced answer with:
1. Key Facts
2. Main Arguments
3. Clear Conclusion
Simple English. Numbered lists."""
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt)
        return response.text.strip()
    except:
        return g_ans

def get_cross_questions(query, best_answer):
    try:
        prompt = f"""You are a debate coach.
Topic: "{query}"
Answer: {best_answer[:400]}
Generate 15 cross-questions with answers.
Format:
Q1: [Question]
A1: [Answer]
Q2: [Question]
A2: [Answer]
...till Q15. Progressive difficulty."""
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def save_pdf(query, g_ans, gr_ans, wiki, web, best, related, cross):
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_fill_color(15,15,80)
        pdf.set_text_color(255,255,255)
        pdf.set_font("Helvetica","B",22)
        pdf.cell(0,16,"TatvaAI Research Report",
                 new_x=XPos.LMARGIN,new_y=YPos.NEXT,align="C",fill=True)
        pdf.set_font("Helvetica","",10)
        pdf.set_fill_color(30,30,120)
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0,8,f"Generated: {ts}  |  TatvaAI v{VERSION}  |  (C) {CURRENT_YEAR}",
                 new_x=XPos.LMARGIN,new_y=YPos.NEXT,align="C",fill=True)
        pdf.set_text_color(0,0,0)
        pdf.ln(5)

        def sec(title,r,g,b):
            pdf.set_font("Helvetica","B",12)
            pdf.set_fill_color(r,g,b)
            pdf.set_text_color(255,255,255)
            pdf.cell(0,9,f"  {title}",new_x=XPos.LMARGIN,new_y=YPos.NEXT,fill=True)
            pdf.set_text_color(0,0,0)
            pdf.set_font("Helvetica","",10)
            pdf.ln(2)

        def txt(t,lim=2000):
            pdf.multi_cell(0,6,clean_text(str(t))[:lim])
            pdf.ln(3)

        sec("QUESTION",15,15,80); txt(query)
        sec("GEMINI 2.5 ANSWER",0,100,160); txt(g_ans,1500)
        sec("GROQ LLAMA ANSWER",0,140,80); txt(gr_ans,1500)
        sec("WIKIPEDIA FACTS",160,100,0); txt(wiki,800)
        sec("WEB SEARCH",100,0,120); txt(web,800)
        pdf.add_page()
        sec("VERIFIED BEST ANSWER",0,120,0); txt(best,3000)
        sec("RELATED QUESTIONS",0,100,160); txt(related,1000)
        pdf.add_page()
        sec("CROSS QUESTIONS & ANSWERS (15)",120,0,0); txt(cross,5000)

        fname = f"TatvaAI_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
        pdf.output(fpath)
        return fpath, fname
    except Exception as e:
        return None, str(e)

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class='sidebar-info'>
        <b style='color:#00d4ff'>🔍 TatvaAI v{VERSION}</b><br><br>
        Multi-AI Consensus Research System<br><br>
        <b>Powered by:</b><br>
        • Gemini 2.5 Flash<br>
        • Groq Llama 3.3<br>
        • Wikipedia<br>
        • Live Web Search<br><br>
        <b>Process:</b><br>
        ✅ 2 AI Answers<br>
        ✅ Wikipedia Facts<br>
        ✅ Web Search<br>
        ✅ Consensus Check<br>
        ✅ Best Answer<br>
        ✅ 15 Cross Questions<br>
        ✅ PDF Report<br><br>
        <b style='color:#ffaa00'>100% Free | Made in India 🇮🇳</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div class='disclaimer'>
        ⚠️ <b>Disclaimer</b><br><br>
        TatvaAI ke answers sirf educational
        aur research purposes ke liye hain.
        Yeh professional advice nahi hai.<br><br>
        Medical, legal, financial decisions
        ke liye qualified professionals se milein.<br><br>
        <small>(C) {CURRENT_YEAR} TatvaAI | IT Act 2000 compliant</small>
    </div>
    """, unsafe_allow_html=True)

# ── MAIN UI ───────────────────────────────────────────────────
st.markdown(f"""
<div class='tatva-header'>
    <div class='tatva-title'>🔍 TATVA AI</div>
    <div class='tatva-subtitle'>
        Multi-AI Consensus Research System v{VERSION}<br>
        Gemini 2.5 + Groq Llama + Wikipedia + Web Search
    </div>
</div>
""", unsafe_allow_html=True)

# Stats row
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("<div class='metric-card'><h3 style='color:#00d4ff'>2</h3><p style='color:#aaa'>AI Models</p></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='metric-card'><h3 style='color:#00ff88'>15</h3><p style='color:#aaa'>Cross Questions</p></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='metric-card'><h3 style='color:#ffaa00'>100%</h3><p style='color:#aaa'>Free</p></div>", unsafe_allow_html=True)
with c4:
    st.markdown("<div class='metric-card'><h3 style='color:#ff6688'>PDF</h3><p style='color:#aaa'>Report</p></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Input
query = st.text_area(
    "🔎 Apna sawaal yahan likho:",
    placeholder="Koi bhi sawaal Hindi ya English mein...",
    height=100
)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    search_btn = st.button("🔍 RESEARCH KARO", use_container_width=True)

# ── PROCESSING ────────────────────────────────────────────────
if search_btn and query.strip():
    is_safe, blocked = safety_check(query)
    if not is_safe:
        st.error(f"⛔ Blocked Topic: '{blocked}' — TatvaAI harmful topics par kaam nahi karta.")
        st.stop()

    st.markdown("---")

    # Step 1 - AI Answers
    st.markdown("<div class='step-badge'>Step 1 — AI Answers</div>", unsafe_allow_html=True)
    with st.spinner("Gemini aur Groq se jawab le raha hoon..."):
        g_ans = ask_gemini(query)
        gr_ans = ask_groq(query)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🤖 Gemini 2.5 Flash**")
        st.markdown(f"<div class='answer-box'>{g_ans[:500]}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("**⚡ Groq Llama 3.3**")
        st.markdown(f"<div class='answer-box'>{gr_ans[:500]}</div>", unsafe_allow_html=True)

    # Step 2 - Wikipedia
    st.markdown("<br><div class='step-badge'>Step 2 — Wikipedia Facts</div>", unsafe_allow_html=True)
    with st.spinner("Wikipedia check kar raha hoon..."):
        wiki_facts, wiki_url = get_wikipedia(query)
    st.markdown(f"<div class='answer-box'>📖 {wiki_facts}<br><br><a href='{wiki_url}' target='_blank' style='color:#00d4ff'>{wiki_url}</a></div>", unsafe_allow_html=True)

    # Step 3 - Web Search
    st.markdown("<br><div class='step-badge'>Step 3 — Live Web Search</div>", unsafe_allow_html=True)
    with st.spinner("Live web search kar raha hoon..."):
        web_results = get_web_search(query)
    st.markdown(f"<div class='answer-box'>🌐 {web_results}</div>", unsafe_allow_html=True)

    # Step 4 - Best Answer
    st.markdown("<br><div class='step-badge'>Step 4 — Verified Best Answer</div>", unsafe_allow_html=True)
    with st.spinner("Best verified answer generate ho raha hai..."):
        best_answer = get_best_answer(query, g_ans, gr_ans, wiki_facts, web_results)
        agreed = check_consensus(g_ans, gr_ans, query)

    consensus_color = "#00ff88" if agreed else "#ffaa00"
    consensus_text = "✅ Dono AIs Agree" if agreed else "⚠️ Mixed Views"
    st.markdown(f"""
    <div class='answer-box' style='border-color:{consensus_color}66'>
        <span style='color:{consensus_color};font-weight:700'>{consensus_text}</span><br><br>
        {best_answer[:1500]}
    </div>
    """, unsafe_allow_html=True)

    # Step 5 - Related Questions
    st.markdown("<br><div class='step-badge'>Step 5 — Related Questions</div>", unsafe_allow_html=True)
    with st.spinner("Related questions generate ho rahe hain..."):
        related_q = ask_gemini(f"Give 5 related follow-up questions for: {query}")
    st.markdown(f"<div class='answer-box'>{related_q[:600]}</div>", unsafe_allow_html=True)

    # Step 6 - Cross Questions
    st.markdown("<br><div class='step-badge'>Step 6 — 15 Psychology-Based Cross Questions</div>", unsafe_allow_html=True)
    with st.spinner("15 cross questions ban rahe hain..."):
        cross_qa = get_cross_questions(query, best_answer)

    with st.expander("📋 Cross Questions Dekho (15 Total)", expanded=False):
        st.markdown(f"<div class='answer-box'>{cross_qa}</div>", unsafe_allow_html=True)

    # PDF Download
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='step-badge'>Step 7 — PDF Report</div>", unsafe_allow_html=True)
    with st.spinner("Professional PDF ban rahi hai..."):
        fpath, fname = save_pdf(
            query, g_ans, gr_ans, wiki_facts,
            web_results, best_answer, related_q, cross_qa
        )

    if fpath and os.path.exists(fpath):
        with open(fpath, "rb") as f:
            st.download_button(
                label="📄 PDF Report Download Karo",
                data=f,
                file_name=fname,
                mime="application/pdf",
                use_container_width=True
            )
        st.success(f"✅ PDF ready hai — Download karo!")
    else:
        st.error(f"PDF Error: {fname}")

elif search_btn and not query.strip():
    st.warning("⚠️ Pehle koi sawaal likho!")

# ── ABOUT SECTION ─────────────────────────────────────────────
st.markdown("---")
with st.expander("ℹ️ TatvaAI ke baare mein", expanded=False):
    st.markdown(f"""
    <div class='answer-box'>
        <h3 style='color:#00d4ff'>🔍 TatvaAI v{VERSION}</h3>
        <p style='color:#a0c4ff'>
        TatvaAI ek free educational research tool hai jo aapke har sawaal ko
        2 powerful AIs (Gemini + Groq), Wikipedia aur Live Web Search se
        verify karke ek single fact-checked answer deta hai.
        </p>
        <br>
        <b style='color:#00d4ff'>Legal & Compliance:</b>
        <p style='color:#a0c4ff'>
        • IT Act 2000 compliant<br>
        • DPDP Act 2023 compliant<br>
        • No personal data stored<br>
        • Educational use only<br>
        • Harmful content blocked
        </p>
        <br>
        <b style='color:#00d4ff'>Contact:</b>
        <p style='color:#a0c4ff'>
        📧 anuragbahadur.17@gmail.com<br>
        🌍 Made in India 🇮🇳<br>
        (C) {CURRENT_YEAR} TatvaAI | Free for Everyone
        </p>
    </div>
    """, unsafe_allow_html=True)