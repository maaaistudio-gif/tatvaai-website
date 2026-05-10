# ============================================================
# TatvaAI v6 - Streamlit Web App
# Multi-AI Consensus Research System
# Intelligence for Every Indian | Made in India
# ============================================================

import os
import base64
import datetime
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from groq import Groq
import wikipedia
from ddgs import DDGS
from fpdf import FPDF, XPos, YPos

load_dotenv()

# ── Page Config ─────────────────────────────────────────────
st.set_page_config(
    page_title="TatvaAI - Intelligence for Every Indian",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

VERSION      = "6.0"
CURRENT_YEAR = datetime.datetime.now().year
BLOCKED_TOPICS = [
    "bomb","weapon","kill","hack","virus",
    "drug","poison","terror","suicide","explosive"
]

# ── Logo ─────────────────────────────────────────────────────
def get_logo_b64():
    for name in ["TATVA_AI_LOGO.png","logo.png","tatva_logo.png"]:
        p = Path(__file__).parent / name
        if p.exists():
            with open(p,"rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_b64()

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

html,body,[class*="css"]{ font-family:'Rajdhani',sans-serif; }

.stApp{
  background:#04040f;
  background-image:
    radial-gradient(ellipse at 20% 20%,rgba(0,180,255,.07) 0%,transparent 50%),
    radial-gradient(ellipse at 80% 80%,rgba(0,255,136,.05) 0%,transparent 50%),
    radial-gradient(ellipse at 50% 50%,rgba(255,100,50,.04) 0%,transparent 70%);
}
.main .block-container{ padding-top:1rem; padding-bottom:2rem; max-width:1200px; }

/* ── POPUP ── */
.popup-overlay{
  display:none; position:fixed; top:0; left:0;
  width:100vw; height:100vh;
  background:rgba(0,0,0,.75);
  z-index:9998; backdrop-filter:blur(4px);
}
.popup-overlay.active{ display:block; }

.logo-popup{
  display:none; position:fixed;
  top:50%; left:50%; transform:translate(-50%,-50%);
  z-index:9999; width:540px; max-width:92vw;
  max-height:88vh; overflow-y:auto;
  background:linear-gradient(135deg,#06061a,#080825);
  border:1px solid rgba(0,180,255,.35);
  border-radius:20px; padding:32px;
  box-shadow:0 24px 80px rgba(0,0,0,.9),0 0 40px rgba(0,180,255,.12);
  animation:popIn .3s ease;
}
.logo-popup.active{ display:block; }
@keyframes popIn{
  from{ opacity:0; transform:translate(-50%,-47%); }
  to  { opacity:1; transform:translate(-50%,-50%); }
}
.popup-close{
  position:absolute; top:14px; right:18px;
  font-size:22px; color:rgba(0,180,255,.6);
  cursor:pointer; transition:color .2s;
}
.popup-close:hover{ color:#00b4ff; }

.popup-logo-title{
  font-family:'Cinzel',serif; font-size:24px; font-weight:900;
  background:linear-gradient(135deg,#ff6432,#ffffff,#00ff88);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  background-clip:text; letter-spacing:5px; margin-bottom:4px;
}
.popup-tagline{
  font-size:11px; color:rgba(0,180,255,.55);
  letter-spacing:3px; margin-bottom:18px;
}
.popup-sec-title{
  font-size:10px; font-weight:700; letter-spacing:3px;
  color:#00b4ff; text-transform:uppercase;
  border-bottom:1px solid rgba(0,180,255,.15);
  padding-bottom:6px; margin:16px 0 10px;
}
.el-item{
  display:flex; gap:12px; align-items:flex-start;
  margin-bottom:9px; padding:10px 12px;
  background:rgba(0,180,255,.04);
  border:1px solid rgba(0,180,255,.08); border-radius:10px;
}
.el-icon{ font-size:20px; min-width:26px; text-align:center; margin-top:2px; }
.el-name{ font-size:12px; font-weight:700; color:#00b4ff; letter-spacing:1px; margin-bottom:3px; }
.el-desc{ font-size:12px; color:rgba(160,196,255,.7); line-height:1.5; }

.color-row{ display:flex; align-items:flex-start; gap:10px; margin-bottom:8px; }
.color-dot{ width:13px; height:13px; border-radius:50%; flex-shrink:0; margin-top:3px; }
.color-name{ font-size:12px; font-weight:700; color:#a0c4ff; }
.color-desc{ font-size:11px; color:rgba(160,196,255,.5); }

.why-item{
  display:flex; gap:8px; align-items:flex-start;
  margin-bottom:6px; font-size:12px;
  color:rgba(160,196,255,.75); line-height:1.5;
}
.why-dot{ color:#00ff88; font-size:14px; flex-shrink:0; margin-top:-1px; }

.overall-msg{
  background:rgba(0,180,255,.05);
  border:1px solid rgba(0,180,255,.15);
  border-radius:12px; padding:14px 16px;
  font-size:12px; color:rgba(160,196,255,.8);
  line-height:1.7; font-style:italic;
}

/* ── HERO ── */
.tatva-hero{
  background:linear-gradient(135deg,#060614,#0a0a20,#060614);
  border:1px solid rgba(0,180,255,.3);
  border-radius:20px; padding:40px 32px 32px;
  text-align:center; margin-bottom:28px; position:relative; overflow:hidden;
}
.tatva-hero::before{
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg,transparent,#ff6432,#ffffff,#00ff88,transparent);
}
.tatva-brand{
  font-family:'Cinzel',serif; font-size:52px; font-weight:900;
  background:linear-gradient(135deg,#ff6432 0%,#ffffff 50%,#00ff88 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  background-clip:text; letter-spacing:8px; margin:12px 0 8px; line-height:1;
}
.tatva-tagline{ font-size:15px; color:rgba(160,196,255,.8); letter-spacing:4px; text-transform:uppercase; margin-bottom:6px; }
.tatva-powered{ font-size:12px; color:rgba(120,150,200,.55); letter-spacing:2px; margin-top:8px; }
.india-badge{
  display:inline-block;
  background:linear-gradient(135deg,rgba(255,153,51,.15),rgba(255,255,255,.05),rgba(19,136,8,.15));
  border:1px solid rgba(255,153,51,.3); border-radius:20px;
  padding:4px 16px; font-size:12px; color:rgba(255,200,100,.8);
  letter-spacing:2px; margin-top:12px;
}
.logo-click-hint{ font-size:10px; color:rgba(0,180,255,.3); margin-top:10px; letter-spacing:1px; }

/* Logo hover */
.logo-btn{
  background:none; border:none; cursor:pointer; padding:0; display:inline-block;
}
.logo-btn img{
  height:100px; width:100px; object-fit:contain; border-radius:50%;
  border:2px solid rgba(0,180,255,.4);
  box-shadow:0 0 30px rgba(0,180,255,.2),0 0 60px rgba(0,180,255,.08);
  transition:all .3s ease; margin-bottom:14px;
}
.logo-btn img:hover{
  box-shadow:0 0 45px rgba(0,180,255,.5),0 0 90px rgba(0,180,255,.18);
  transform:scale(1.07);
}

/* ── METRICS ── */
.metric-row{
  display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:24px;
}
.metric-card{
  background:linear-gradient(135deg,#080820,#0a0a25);
  border:1px solid rgba(0,180,255,.15); border-radius:14px;
  padding:20px 16px; text-align:center; transition:all .3s ease;
}
.metric-card:hover{ border-color:rgba(0,180,255,.4); transform:translateY(-2px); }
.metric-num{ font-family:'Cinzel',serif; font-size:28px; font-weight:700; line-height:1; margin-bottom:6px; }
.metric-label{ font-size:12px; color:rgba(160,196,255,.6); letter-spacing:1px; text-transform:uppercase; }

/* ── INPUT ── */
.stTextArea textarea{
  background:#080820!important; color:#e0f0ff!important;
  border:1px solid rgba(0,180,255,.3)!important; border-radius:12px!important;
  font-family:'Rajdhani',sans-serif!important; font-size:16px!important; padding:14px!important;
}
.stTextArea label{
  color:rgba(0,180,255,.8)!important; font-family:'Rajdhani',sans-serif!important;
  font-size:15px!important; font-weight:600!important; letter-spacing:1px!important;
}

/* ── BUTTONS ── */
.stButton>button{
  background:linear-gradient(135deg,#0066cc,#00b4ff)!important;
  color:white!important; border:none!important; border-radius:10px!important;
  padding:14px 40px!important; font-family:'Cinzel',serif!important;
  font-size:15px!important; font-weight:700!important; letter-spacing:3px!important;
  width:100%!important; box-shadow:0 4px 24px rgba(0,180,255,.25)!important;
  transition:all .3s ease!important;
}
.stButton>button:hover{
  background:linear-gradient(135deg,#0088ff,#00ddff)!important;
  box-shadow:0 6px 32px rgba(0,180,255,.4)!important;
  transform:translateY(-2px)!important;
}
.stDownloadButton>button{
  background:linear-gradient(135deg,#003d00,#006600)!important;
  color:#00ff88!important; border:1px solid rgba(0,255,136,.3)!important;
  border-radius:10px!important; font-family:'Rajdhani',sans-serif!important;
  font-size:15px!important; font-weight:700!important;
  letter-spacing:2px!important; width:100%!important;
}

/* ── ANSWER BOXES ── */
.answer-box{
  background:linear-gradient(135deg,#080820,#080825);
  border:1px solid rgba(0,180,255,.15); border-radius:14px;
  padding:20px 24px; margin:10px 0; color:#c8deff; font-size:15px; line-height:1.7;
}
.answer-box-green{ border-color:rgba(0,255,136,.2); background:linear-gradient(135deg,#040f0a,#050f0a); }
.answer-box-orange{ border-color:rgba(255,100,50,.2); background:linear-gradient(135deg,#0f0804,#0f0804); }

/* ── STEP BADGE ── */
.step-badge{
  display:inline-flex; align-items:center; gap:8px;
  background:rgba(0,180,255,.1); border:1px solid rgba(0,180,255,.3);
  border-radius:30px; padding:6px 18px; color:#00b4ff;
  font-family:'Rajdhani',sans-serif; font-size:13px; font-weight:700;
  letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;
}
.consensus-agree{
  display:inline-block; background:rgba(0,255,136,.12);
  border:1px solid rgba(0,255,136,.4); border-radius:20px;
  padding:4px 16px; color:#00ff88; font-weight:700; font-size:13px; margin-bottom:12px;
}
.consensus-mixed{
  display:inline-block; background:rgba(255,180,0,.12);
  border:1px solid rgba(255,180,0,.4); border-radius:20px;
  padding:4px 16px; color:#ffb400; font-weight:700; font-size:13px; margin-bottom:12px;
}

/* ── SIDEBAR ── */
.sidebar-card{
  background:linear-gradient(135deg,#080820,#0a0a22);
  border:1px solid rgba(0,180,255,.15); border-radius:14px;
  padding:18px; margin-bottom:14px; color:#a0c4ff; font-size:14px; line-height:1.8;
}
.sidebar-title{ font-family:'Cinzel',serif; color:#00b4ff; font-size:16px; font-weight:700; margin-bottom:10px; letter-spacing:2px; }
.feature-item{ display:flex; align-items:center; gap:10px; padding:4px 0; color:#a0c4ff; font-size:13px; }
.feature-dot{ width:6px; height:6px; border-radius:50%; background:#00b4ff; flex-shrink:0; }
.disclaimer{
  background:rgba(255,60,60,.05); border-left:3px solid rgba(255,60,60,.5);
  border-radius:8px; padding:14px 16px; color:rgba(255,150,150,.8); font-size:12px; line-height:1.6;
}
hr{ border:none!important; border-top:1px solid rgba(0,180,255,.1)!important; margin:24px 0!important; }
</style>

<!-- Overlay -->
<div class="popup-overlay" id="popupOverlay" onclick="closePopup()"></div>

<!-- Logo Description Popup -->
<div class="logo-popup" id="logoPopup">
  <span class="popup-close" onclick="closePopup()">&#x2715;</span>

  <div style="text-align:center;margin-bottom:4px;">
    <div class="popup-logo-title">TatvaAI</div>
    <div class="popup-tagline">INTELLIGENCE FOR EVERY INDIAN</div>
    <div style="font-size:10px;color:rgba(255,153,51,.55);letter-spacing:2px;">
      FREE AI TOOLS &nbsp;|&nbsp; CARE &nbsp;•&nbsp; EMPOWER &nbsp;•&nbsp; ELEVATE
    </div>
  </div>

  <div class="popup-sec-title">Logo Ke Har Element Ka Matlab</div>

  <div class="el-item">
    <div class="el-icon">🔥</div>
    <div><div class="el-name">SAFFRON FLAME</div>
    <div class="el-desc">Energy, courage & rising ki spirit. India ka saffron TatvaAI ko upar se roshan karta hai — hum har Indian ke saath uthte hain.</div></div>
  </div>
  <div class="el-item">
    <div class="el-icon">✨</div>
    <div><div class="el-name">NEURAL YANTRA</div>
    <div class="el-desc">Sacred yantra geometry ko AI neural network ke roop mein reimagine kiya. Prachin Indian wisdom (Panch Tatva) meets futuristic machine intelligence.</div></div>
  </div>
  <div class="el-item">
    <div class="el-icon">⚙️</div>
    <div><div class="el-name">ASHOKA CHAKRA</div>
    <div class="el-desc">24-spoke Dharma Chakra — progress, movement & truth. TatvaAI mein har spoke ek data stream hai — hamesha aage badhta hai.</div></div>
  </div>
  <div class="el-item">
    <div class="el-icon">👥</div>
    <div><div class="el-name">PEOPLE OF INDIA</div>
    <div class="el-desc">Tricolor log — saffron, white, green — har Indian ko represent karte hain. TatvaAI sabke liye hai, bina kisi bhed ke.</div></div>
  </div>
  <div class="el-item">
    <div class="el-icon">🌟</div>
    <div><div class="el-name">GREEN GLOW</div>
    <div class="el-desc">Growth, harmony & hope. India ka green ek behtar kal ko symbolise karta hai. TatvaAI har user ke saath grow karta hai — free, forever.</div></div>
  </div>

  <div class="popup-sec-title">Yeh Colors Kyun?</div>
  <div class="color-row">
    <div class="color-dot" style="background:#FF9933;"></div>
    <div><div class="color-name">Saffron — Energy, Strength, Positivity</div>
    <div class="color-desc">Courage, motivation aur rising & winning ki spirit.</div></div>
  </div>
  <div class="color-row">
    <div class="color-dot" style="background:#00b4ff;"></div>
    <div><div class="color-name">Cyan — Innovation, Clarity, Future</div>
    <div class="color-desc">AI intelligence ka glow — har Indian ko roshan karta hai.</div></div>
  </div>
  <div class="color-row">
    <div class="color-dot" style="background:#00ff88;"></div>
    <div><div class="color-name">Green — Growth, Harmony, Hope</div>
    <div class="color-desc">Growth, success, harmony — sabke liye behtar kal.</div></div>
  </div>
  <div class="color-row">
    <div class="color-dot" style="background:#04040f;border:1px solid rgba(255,255,255,.2);"></div>
    <div><div class="color-name">Cosmic Black — Depth, Universe, Limitless</div>
    <div class="color-desc">AI ki koi seema nahi — bilkul cosmos ki tarah.</div></div>
  </div>

  <div class="popup-sec-title">Yeh Logo Kyun?</div>
  <div class="why-item"><span class="why-dot">✓</span>Hamare mission ko represent karta hai — har Indian ke liye free AI tools.</div>
  <div class="why-item"><span class="why-dot">✓</span>Prachin Indian wisdom (Yantra, Tatva) ko modern AI se connect karta hai.</div>
  <div class="why-item"><span class="why-dot">✓</span>Har Indian ke liye hamare commitment ko reflect karta hai — especially zarooratmand.</div>
  <div class="why-item"><span class="why-dot">✓</span>India ka tricolor har element mein — proudly Indian & global.</div>
  <div class="why-item"><span class="why-dot">✓</span>Futuristic, memorable aur scalable — har platform pe.</div>
  <div class="why-item"><span class="why-dot">✓</span>Ashoka Chakra — TatvaAI kabhi nahi rukta, hamesha aage.</div>

  <div class="popup-sec-title">Overall Message</div>
  <div class="overall-msg">
    TatvaAI — Tatva ka matlab Sanskrit mein "Essence" hai. Hum India ke liye AI ka essence hain.
    Jahan sacred geometry neural networks se milti hai, jahan prachin wisdom futuristic tools ko power karti hai.
    Har Indian ko support, empower aur uplift karne ke liye — completely free.<br><br>
    <span style="color:#ff6432;">Care</span> &nbsp;•&nbsp;
    <span style="color:#a0c4ff;">Empower</span> &nbsp;•&nbsp;
    <span style="color:#00ff88;">Elevate</span>
  </div>
</div>

<script>
function openPopup(){
  document.getElementById('logoPopup').classList.add('active');
  document.getElementById('popupOverlay').classList.add('active');
}
function closePopup(){
  document.getElementById('logoPopup').classList.remove('active');
  document.getElementById('popupOverlay').classList.remove('active');
}
document.addEventListener('keydown',function(e){ if(e.key==='Escape') closePopup(); });
</script>
""", unsafe_allow_html=True)

# ── Init Clients ─────────────────────────────────────────────
@st.cache_resource
def init_clients():
    g  = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    gr = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return g, gr

gemini_client, groq_client = init_clients()

# ── Helpers ───────────────────────────────────────────────────
def clean_text(text):
    if not text: return ""
    for old,new in {"\u2022":"-","\u2019":"'","\u2018":"'","\u201c":'"',"\u201d":'"',
                    "\u2013":"-","\u2014":"-","\u2026":"...","\u00a0":" ",
                    "\u00ae":"(R)","\u2122":"(TM)","\u00a9":"(C)"}.items():
        text = text.replace(old,new)
    return text.encode('latin-1',errors='replace').decode('latin-1')

def safety_check(q):
    for t in BLOCKED_TOPICS:
        if t in q.lower(): return False,t
    return True,None

def ask_gemini(q):
    try:
        r = gemini_client.models.generate_content(model="gemini-2.5-flash",contents=q)
        return r.text.strip()
    except Exception as e: return f"Error: {e}"

def ask_groq(q):
    try:
        r = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":q}])
        return r.choices[0].message.content.strip()
    except Exception as e: return f"Error: {e}"

def get_wikipedia(q):
    try:
        wikipedia.set_lang("en")
        res = wikipedia.search(q,results=2)
        if res:
            p = wikipedia.page(res[0])
            return p.summary[:600], p.url
        return "Wikipedia article nahi mila.",""
    except: return "Wikipedia article nahi mila.",""

def get_web_search(q):
    try:
        out=[]
        with DDGS() as d:
            for r in d.text(q,max_results=3):
                out.append(f"- {r['title']}: {r['body'][:150]}")
        return "\n".join(out) if out else "Web results nahi mile."
    except Exception as e: return f"Error: {e}"

def check_consensus(a1,a2,q):
    try:
        p=f'Two AIs answered: "{q}"\nAI-1: {a1[:200]}\nAI-2: {a2[:200]}\nDo both agree? Reply ONLY: YES or NO'
        r=gemini_client.models.generate_content(model="gemini-2.5-flash",contents=p)
        return "YES" in r.text.upper()
    except: return False

def get_best_answer(q,g,gr,wiki,web):
    try:
        p=f"""You are TatvaAI. Create a comprehensive fact-checked answer.
Question: {q}
Source 1: {g[:400]}
Source 2: {gr[:400]}
Wikipedia: {wiki[:300]}
Web: {web[:300]}
Write balanced answer: 1.Key Facts 2.Main Arguments 3.Clear Conclusion. Simple English."""
        r=gemini_client.models.generate_content(model="gemini-2.5-flash",contents=p)
        return r.text.strip()
    except: return g

def get_cross_questions(q,best):
    try:
        p=f"""You are a debate coach.
Topic: "{q}"
Answer: {best[:400]}
Generate 15 cross-questions with answers.
Format: Q1:[Question] A1:[Answer] ... till Q15. Progressive difficulty."""
        r=gemini_client.models.generate_content(model="gemini-2.5-flash",contents=p)
        return r.text.strip()
    except Exception as e: return f"Error: {e}"

def save_pdf(q,g,gr,wiki,web,best,related,cross):
    try:
        pdf=FPDF(); pdf.set_auto_page_break(auto=True,margin=15); pdf.add_page()
        pdf.set_fill_color(15,15,80); pdf.set_text_color(255,255,255)
        pdf.set_font("Helvetica","B",22)
        pdf.cell(0,16,"TatvaAI Research Report",new_x=XPos.LMARGIN,new_y=YPos.NEXT,align="C",fill=True)
        pdf.set_font("Helvetica","",10); pdf.set_fill_color(30,30,100)
        ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0,8,f"Generated: {ts}  |  TatvaAI v{VERSION}  |  (C) {CURRENT_YEAR}  |  Intelligence for Every Indian",
                 new_x=XPos.LMARGIN,new_y=YPos.NEXT,align="C",fill=True)
        pdf.set_text_color(0,0,0); pdf.ln(5)

        def sec(t,r,g,b):
            pdf.set_font("Helvetica","B",12); pdf.set_fill_color(r,g,b); pdf.set_text_color(255,255,255)
            pdf.cell(0,9,f"  {t}",new_x=XPos.LMARGIN,new_y=YPos.NEXT,fill=True)
            pdf.set_text_color(0,0,0); pdf.set_font("Helvetica","",10); pdf.ln(2)
        def txt(t,lim=2000):
            pdf.multi_cell(0,6,clean_text(str(t))[:lim]); pdf.ln(3)

        sec("QUESTION",15,15,80);             txt(q)
        sec("AI SOURCE 1 ANSWER",0,100,160);  txt(g,1500)
        sec("AI SOURCE 2 ANSWER",0,140,80);   txt(gr,1500)
        sec("WIKIPEDIA FACTS",160,100,0);     txt(wiki,800)
        sec("WEB SEARCH RESULTS",100,0,120);  txt(web,800)
        pdf.add_page()
        sec("VERIFIED BEST ANSWER",0,120,0);  txt(best,3000)
        sec("RELATED QUESTIONS",0,100,160);   txt(related,1000)
        pdf.add_page()
        sec("CROSS QUESTIONS & ANSWERS",120,0,0); txt(cross,5000)

        fname=f"TatvaAI_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        fpath=os.path.join(os.path.dirname(os.path.abspath(__file__)),fname)
        pdf.output(fpath)
        return fpath,fname
    except Exception as e: return None,str(e)

# ══════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════
with st.sidebar:
    if logo_b64:
        st.markdown(f"""
        <div style="text-align:center;padding:14px 0 6px;">
          <img src="data:image/png;base64,{logo_b64}"
               style="height:75px;width:75px;object-fit:contain;border-radius:50%;
                      border:2px solid rgba(0,180,255,.3);
                      box-shadow:0 0 20px rgba(0,180,255,.15);cursor:pointer;"
               onclick="openPopup()" title="Logo ke baare mein jaano" />
          <div style="font-size:10px;color:rgba(0,180,255,.35);margin-top:6px;letter-spacing:1px;">
            Logo pe click karo
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='sidebar-card'>
      <div class='sidebar-title'>TATVA AI</div>
      <div style="color:rgba(0,180,255,.45);font-size:10px;letter-spacing:2px;margin-bottom:14px;">
        INTELLIGENCE FOR EVERY INDIAN
      </div>
      <div class="feature-item"><div class="feature-dot"></div>Dual AI Verification System</div>
      <div class="feature-item"><div class="feature-dot"></div>Real-time Wikipedia Facts</div>
      <div class="feature-item"><div class="feature-dot"></div>Live Web Search</div>
      <div class="feature-item"><div class="feature-dot"></div>AI Consensus Analysis</div>
      <div class="feature-item"><div class="feature-dot"></div>15 Critical Cross Questions</div>
      <div class="feature-item"><div class="feature-dot"></div>Professional PDF Report</div>
      <div class="feature-item"><div class="feature-dot"></div>Harmful Content Blocked</div>
      <br>
      <div style="text-align:center;">
        <span style="background:linear-gradient(135deg,rgba(255,153,51,.15),rgba(255,255,255,.05),rgba(19,136,8,.15));
                     border:1px solid rgba(255,153,51,.3);border-radius:20px;
                     padding:4px 14px;font-size:10px;color:rgba(255,200,100,.8);letter-spacing:2px;">
          🇮🇳 MADE IN INDIA
        </span>
      </div>
      <div style="text-align:center;margin-top:10px;font-size:10px;color:rgba(120,150,200,.45);">
        Version {VERSION} &nbsp;|&nbsp; 100% Free Forever
      </div>
    </div>
    <div class='disclaimer'>
      <b style="color:rgba(255,120,120,.9);">Disclaimer</b><br><br>
      TatvaAI ke answers sirf educational aur research purposes ke liye hain. Yeh professional advice nahi hai.<br><br>
      Medical, legal, financial decisions ke liye qualified professionals se milein.<br><br>
      <span style="color:rgba(180,120,120,.55);font-size:10px;">
        (C) {CURRENT_YEAR} TatvaAI | IT Act 2000 Compliant
      </span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# MAIN — HERO
# ══════════════════════════════════════════════════
logo_hero = f"""
<button class="logo-btn" onclick="openPopup()" title="TatvaAI logo ke baare mein jaano">
  <img src="data:image/png;base64,{logo_b64}" alt="TatvaAI Logo" />
</button>""" if logo_b64 else '<div style="font-size:60px;cursor:pointer;" onclick="openPopup()">🔮</div>'

st.markdown(f"""
<div class='tatva-hero'>
  {logo_hero}
  <div class='tatva-brand'>TatvaAI</div>
  <div class='tatva-tagline'>Intelligence for Every Indian</div>
  <div class='tatva-powered'>
    Dual AI &nbsp;•&nbsp; Wikipedia &nbsp;•&nbsp; Live Web &nbsp;•&nbsp; Consensus &nbsp;•&nbsp; PDF Export
  </div>
  <div class='india-badge'>FREE &nbsp;|&nbsp; MADE IN INDIA 🇮🇳 &nbsp;|&nbsp; EDUCATIONAL</div>
  <div class='logo-click-hint'>Logo pe click karo — iske baare mein jaano</div>
</div>
""", unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────
st.markdown("""
<div class='metric-row'>
  <div class='metric-card'><div class='metric-num' style='color:#00b4ff'>2</div><div class='metric-label'>AI Sources</div></div>
  <div class='metric-card'><div class='metric-num' style='color:#00ff88'>15</div><div class='metric-label'>Cross Questions</div></div>
  <div class='metric-card'><div class='metric-num' style='color:#ffb400'>100%</div><div class='metric-label'>Free Always</div></div>
  <div class='metric-card'><div class='metric-num' style='color:#ff6432'>PDF</div><div class='metric-label'>Report Ready</div></div>
</div>
""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
query = st.text_area(
    "Apna sawaal yahan likho:",
    placeholder="Koi bhi sawaal Hindi ya English mein poochho...",
    height=110, key="main_query"
)
_,col_m,_ = st.columns([1,2,1])
with col_m:
    search_btn = st.button("RESEARCH KARO", use_container_width=True)

# ══════════════════════════════════════════════════
# PROCESSING
# ══════════════════════════════════════════════════
if search_btn and query.strip():
    is_safe,blocked = safety_check(query)
    if not is_safe:
        st.error(f"Blocked Topic: '{blocked}' — TatvaAI harmful topics par kaam nahi karta.")
        st.stop()

    st.markdown("<hr>", unsafe_allow_html=True)

    # Step 1
    st.markdown("<div class='step-badge'>STEP 1 &nbsp; DUAL AI ANALYSIS</div>", unsafe_allow_html=True)
    with st.spinner("Dono AI sources se jawab le raha hoon..."):
        g_ans=ask_gemini(query); gr_ans=ask_groq(query)
    c1,c2=st.columns(2)
    with c1:
        st.markdown(f"""<div class='answer-box'>
          <div style="color:#00b4ff;font-size:10px;letter-spacing:2px;margin-bottom:10px;font-weight:700;">AI SOURCE 1</div>
          {g_ans[:600]}</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='answer-box answer-box-green'>
          <div style="color:#00ff88;font-size:10px;letter-spacing:2px;margin-bottom:10px;font-weight:700;">AI SOURCE 2</div>
          {gr_ans[:600]}</div>""", unsafe_allow_html=True)

    # Step 2
    st.markdown("<br><div class='step-badge'>STEP 2 &nbsp; WIKIPEDIA VERIFICATION</div>", unsafe_allow_html=True)
    with st.spinner("Wikipedia facts check kar raha hoon..."):
        wiki_facts,wiki_url=get_wikipedia(query)
    wlink=f'<a href="{wiki_url}" target="_blank" style="color:#00b4ff;font-size:11px;">{wiki_url}</a>' if wiki_url else ""
    st.markdown(f"""<div class='answer-box'>
      <div style="color:rgba(255,180,0,.7);font-size:10px;letter-spacing:2px;margin-bottom:10px;font-weight:700;">WIKIPEDIA FACTS</div>
      {wiki_facts}<br>{wlink}</div>""", unsafe_allow_html=True)

    # Step 3
    st.markdown("<br><div class='step-badge'>STEP 3 &nbsp; LIVE WEB SEARCH</div>", unsafe_allow_html=True)
    with st.spinner("Live web search kar raha hoon..."):
        web_results=get_web_search(query)
    st.markdown(f"""<div class='answer-box'>
      <div style="color:rgba(180,0,255,.7);font-size:10px;letter-spacing:2px;margin-bottom:10px;font-weight:700;">WEB RESULTS</div>
      {web_results}</div>""", unsafe_allow_html=True)

    # Step 4
    st.markdown("<br><div class='step-badge'>STEP 4 &nbsp; CONSENSUS ANALYSIS</div>", unsafe_allow_html=True)
    with st.spinner("Best answer aur consensus check kar raha hoon..."):
        best_answer=get_best_answer(query,g_ans,gr_ans,wiki_facts,web_results)
        agreed=check_consensus(g_ans,gr_ans,query)
    badge = "<div class='consensus-agree'>CONSENSUS REACHED — Both Sources Agree</div>" if agreed \
            else "<div class='consensus-mixed'>MIXED VIEWS — Multiple Perspectives Found</div>"
    st.markdown(f"""<div class='answer-box {"answer-box-green" if agreed else ""}'>
      {badge}
      <div style="color:rgba(0,180,255,.5);font-size:10px;letter-spacing:2px;margin-bottom:12px;font-weight:700;">TATVAAI VERIFIED ANSWER</div>
      {best_answer[:2000]}</div>""", unsafe_allow_html=True)

    # Step 5
    st.markdown("<br><div class='step-badge'>STEP 5 &nbsp; RELATED QUESTIONS</div>", unsafe_allow_html=True)
    with st.spinner("Related questions generate ho rahe hain..."):
        related_q=ask_gemini(f"Give 5 related follow-up questions for: {query}")
    st.markdown(f"""<div class='answer-box'>
      <div style="color:rgba(0,180,255,.5);font-size:10px;letter-spacing:2px;margin-bottom:10px;font-weight:700;">EXPLORE FURTHER</div>
      {related_q[:600]}</div>""", unsafe_allow_html=True)

    # Step 6
    st.markdown("<br><div class='step-badge'>STEP 6 &nbsp; 15 CRITICAL CROSS QUESTIONS</div>", unsafe_allow_html=True)
    with st.spinner("15 psychology-based cross questions ban rahe hain..."):
        cross_qa=get_cross_questions(query,best_answer)
    with st.expander("Cross Questions Dekho (15 Total)", expanded=False):
        st.markdown(f"""<div class='answer-box answer-box-orange'>
          <div style="color:rgba(255,100,50,.7);font-size:10px;letter-spacing:2px;margin-bottom:10px;font-weight:700;">CRITICAL ANALYSIS — 15 QUESTIONS</div>
          {cross_qa}</div>""", unsafe_allow_html=True)

    # Step 7
    st.markdown("<br><div class='step-badge'>STEP 7 &nbsp; PDF REPORT</div>", unsafe_allow_html=True)
    with st.spinner("Professional PDF report ban rahi hai..."):
        fpath,fname=save_pdf(query,g_ans,gr_ans,wiki_facts,web_results,best_answer,related_q,cross_qa)
    if fpath and os.path.exists(fpath):
        with open(fpath,"rb") as f:
            st.download_button("PDF REPORT DOWNLOAD KARO",f,fname,"application/pdf",use_container_width=True)
        st.success("PDF ready hai — Download karo!")
    else:
        st.error(f"PDF Error: {fname}")

elif search_btn and not query.strip():
    st.warning("Pehle koi sawaal likho!")

# ══════════════════════════════════════════════════
# ABOUT
# ══════════════════════════════════════════════════
st.markdown("<hr>", unsafe_allow_html=True)
with st.expander("TatvaAI ke baare mein", expanded=False):
    st.markdown(f"""
    <div class='answer-box'>
      <div style="font-family:'Cinzel',serif;color:#00b4ff;font-size:20px;letter-spacing:4px;margin-bottom:6px;">TATVA AI v{VERSION}</div>
      <div style="color:rgba(0,180,255,.4);font-size:10px;letter-spacing:3px;margin-bottom:20px;">INTELLIGENCE FOR EVERY INDIAN</div>
      <p style="color:#a0c4ff;line-height:1.8;margin-bottom:20px;">
        TatvaAI ek free educational research platform hai jo aapke har sawaal ko
        dual AI verification, Wikipedia fact-checking aur live web search se
        cross-verify karke ek single, reliable answer deta hai — bilkul free.
      </p>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        <div>
          <div style="color:#00ff88;font-size:11px;letter-spacing:2px;margin-bottom:10px;font-weight:700;">FEATURES</div>
          <div style="color:#a0c4ff;font-size:13px;line-height:2;">
            - Dual AI Consensus System<br>- Wikipedia Fact Verification<br>
            - Real-time Web Search<br>- 15 Critical Cross Questions<br>
            - Professional PDF Report<br>- Harmful Content Blocked
          </div>
        </div>
        <div>
          <div style="color:#00ff88;font-size:11px;letter-spacing:2px;margin-bottom:10px;font-weight:700;">COMPLIANCE</div>
          <div style="color:#a0c4ff;font-size:13px;line-height:2;">
            - IT Act 2000 Compliant<br>- DPDP Act 2023 Compliant<br>
            - No Personal Data Stored<br>- Educational Use Only<br>
            - 100% Free Forever<br>- Made in India 🇮🇳
          </div>
        </div>
      </div>
      <hr style="border-color:rgba(0,180,255,.1);margin:20px 0;">
      <div style="color:rgba(120,150,200,.45);font-size:11px;text-align:center;">
        (C) {CURRENT_YEAR} TatvaAI &nbsp;|&nbsp; Intelligence for Every Indian &nbsp;|&nbsp; Free for Everyone
      </div>
    </div>""", unsafe_allow_html=True)