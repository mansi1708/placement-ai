import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="AI Placement Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.ui import inject_global_css, kpi_card, feature_card, sidebar_brand
inject_global_css()

# ── Load artifacts once ────────────────────────────────────────────────────────
@st.cache_resource
def _load():
    from utils.ml_engine import load_artifacts
    return load_artifacts()

if "artifacts" not in st.session_state:
    try:
        st.session_state["artifacts"] = _load()
    except Exception as e:
        st.error(f"Could not load model: {e}. Run generate_data.py then train_model.py first.")
        st.stop()

m = st.session_state["artifacts"]["metrics"]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_brand(
        accuracy=m.get("accuracy"),
        roc_auc=m.get("roc_auc"),
        cv_mean=m.get("cv_mean"),
        total_samples=m.get("total_samples"),
    )

# ═══════════════════════════════════════════════════════════════════════════════
#  HOME PAGE
# ═══════════════════════════════════════════════════════════════════════════════

# Hero
acc_val = f"{float(m.get('accuracy', 0)):.2f}"
st.markdown(
    '<div style="text-align:center;padding:50px 20px 30px;position:relative;overflow:hidden">'
    '<div style="position:absolute;top:-60px;left:50%;transform:translateX(-50%);width:680px;height:240px;'
    'background:radial-gradient(ellipse,rgba(59,130,246,.09) 0%,transparent 70%);pointer-events:none"></div>'
    '<div style="display:inline-flex;align-items:center;gap:8px;background:rgba(59,130,246,.10);'
    'border:1px solid rgba(59,130,246,.30);border-radius:999px;padding:6px 20px;font-size:.73rem;'
    'font-weight:700;color:#93C5FD;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:20px">'
    '<span style="width:6px;height:6px;background:#10B981;border-radius:50%;'
    'box-shadow:0 0 6px #10B981;display:inline-block"></span>'
    f'Machine Learning &nbsp;·&nbsp; Random Forest &nbsp;·&nbsp; {acc_val}% Accuracy'
    '</div>'
    '<h1 style="font-size:clamp(2.2rem,5.5vw,4rem);font-weight:900;line-height:1.08;margin:0 0 16px;'
    'background:linear-gradient(135deg,#E2E8F0 0%,#93C5FD 45%,#A78BFA 100%);'
    '-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-1.2px">'
    'AI Placement<br>Prediction System</h1>'
    '<p style="color:#64748B;font-size:1rem;max-width:520px;margin:0 auto 32px;line-height:1.75">'
    'Predict your campus placement probability with Machine Learning.<br>'
    'Get smart improvement tips, practice interview questions, and download a career report.'
    '</p></div>',
    unsafe_allow_html=True,
)

# CTA buttons
_, c1, c2, c3, _ = st.columns([1, 1.1, 1.1, 1.1, 1])
with c1:
    if st.button("🔮 Start Prediction", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Prediction.py")
with c2:
    if st.button("📊 Analytics Dashboard", use_container_width=True):
        st.switch_page("pages/3_Analytics.py")
with c3:
    if st.button("❓ Interview Practice", use_container_width=True):
        st.switch_page("pages/4_Interview.py")

st.markdown("<br>", unsafe_allow_html=True)

# KPI bar
acc_s  = f"{float(m.get('accuracy', 0)):.2f}"
auc_s  = f"{float(m.get('roc_auc', 0)):.4f}"
cv_s   = f"{float(m.get('cv_mean', 0)):.2f}"
tot_s  = f"{int(m.get('total_samples', 0)):,}"
cv_std = f"{float(m.get('cv_std', 0)):.2f}"

kpis = [
    ("🎯", f"{acc_s}%",  "Model Accuracy",   "#3B82F6", "Random Forest"),
    ("📈", auc_s,         "ROC-AUC Score",    "#10B981", "Excellent"),
    ("🔁", f"{cv_s}%",   "5-Fold CV",        "#A78BFA", f"± {cv_std}%"),
    ("📂", tot_s,         "Training Records", "#F59E0B", "Synthetic data"),
    ("🌲", "200",         "Decision Trees",   "#EC4899", "Max depth 12"),
    ("⚡", "9",           "Input Features",   "#06B6D4", "All normalised"),
]
cols = st.columns(6)
for col, (icon, val, label, color, sub) in zip(cols, kpis):
    with col:
        kpi_card(icon, val, label, color, sub)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# Feature cards
st.markdown(
    '<h2 style="text-align:center;font-size:1.7rem;font-weight:800;color:#E2E8F0;'
    'margin:26px 0 6px;letter-spacing:-.3px">Everything You Need to Get Placed</h2>'
    '<p style="text-align:center;color:#475569;font-size:.9rem;margin-bottom:26px">'
    'Five powerful tools built into one professional system</p>',
    unsafe_allow_html=True,
)

features = [
    ("🔮","ML Placement Prediction",
     "Random Forest analyses your CGPA, DSA, projects and 6 more signals "
     "to predict placement probability with high accuracy.",
     "Core Feature","#3B82F6"),
    ("💡","Smart Improvement Tips",
     "Know which skill to improve and see exactly how much your probability "
     "increases — with quantified +X% gain per suggestion.",
     "AI Powered","#10B981"),
    ("📊","Analytics Dashboard",
     "Skill radar, feature importance, confusion matrix, CGPA/internship "
     "trends — all interactive Plotly dark-theme charts.",
     "Interactive","#A78BFA"),
    ("❓","Interview Q&A Generator",
     "100+ technical, OOP and HR questions auto-generated based on your "
     "skills and weak areas across 5 tech domains.",
     "Practice","#F59E0B"),
    ("📄","PDF Report Export",
     "Professional placement report with score, strengths, weaknesses, "
     "improvement roadmap and model stats — download ready.",
     "Export","#EC4899"),
]

c1, c2, c3 = st.columns(3)
col_map = [c1, c2, c3, c1, c2]
for feat, col in zip(features, col_map):
    with col:
        feature_card(*feat)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# How it works
st.markdown(
    '<h2 style="text-align:center;font-size:1.5rem;font-weight:800;color:#E2E8F0;margin:22px 0 28px">'
    'How It Works — 4 Simple Steps</h2>',
    unsafe_allow_html=True,
)

steps = [
    ("01","Enter Your Profile","Fill 9 academic & skill metrics in the Prediction page.","#3B82F6"),
    ("02","Run the ML Model",  "Random Forest analyses your data in under 1 second.",    "#10B981"),
    ("03","Get Your Roadmap",  "Receive improvement tips ranked by highest gain.",        "#A78BFA"),
    ("04","Download & Prepare","Export PDF and practice with generated interview Q&A.",  "#F59E0B"),
]
cols = st.columns(4)
for col, (num, title, desc, color) in zip(cols, steps):
    with col:
        st.markdown(
            f'<div style="text-align:center;padding:14px 6px">'
            f'<div style="width:52px;height:52px;margin:0 auto 12px;'
            f'background:linear-gradient(135deg,{color}22,{color}0A);border:2px solid {color}44;'
            f'border-radius:15px;display:flex;align-items:center;justify-content:center;'
            f'font-size:1.1rem;font-weight:900;color:{color};font-family:\'JetBrains Mono\',monospace">{num}</div>'
            f'<div style="font-weight:700;color:#E2E8F0;font-size:.92rem;margin-bottom:7px">{title}</div>'
            f'<div style="color:#475569;font-size:.8rem;line-height:1.5">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# Tech stack
st.markdown(
    '<h3 style="text-align:center;color:#334155;font-size:.75rem;font-weight:700;'
    'text-transform:uppercase;letter-spacing:2px;margin-bottom:16px">Tech Stack</h3>',
    unsafe_allow_html=True,
)
tech = [
    ("🐍","Python 3.10+","#3B82F6"),("📊","Streamlit","#FF4B4B"),
    ("🌲","Scikit-learn","#F97316"),("📈","Plotly","#636EFA"),
    ("🐼","Pandas","#10B981"),      ("🔢","NumPy","#4ECDC4"),
    ("📄","ReportLab","#EC4899"),
]
cols = st.columns(7)
for col, (icon, name, color) in zip(cols, tech):
    with col:
        st.markdown(
            f'<div style="background:#0D1424;border:1px solid #1E3A5F;border-radius:12px;'
            f'padding:13px 6px;text-align:center;transition:border-color .2s" '
            f'onmouseover="this.style.borderColor=\'{color}66\'" '
            f'onmouseout="this.style.borderColor=\'#1E3A5F\'">'
            f'<div style="font-size:1.3rem">{icon}</div>'
            f'<div style="color:{color};font-size:.65rem;font-weight:700;margin-top:5px">{name}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# Footer
st.markdown(
    '<div style="text-align:center;padding:36px 0 10px;color:#1E3A5F;font-size:.75rem;line-height:1.8">'
    'Built with &#10084;&#65039; for college placements &amp; technical interviews<br>'
    'AI Placement Prediction System &nbsp;·&nbsp; Python &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp; Scikit-learn</div>',
    unsafe_allow_html=True,
)
