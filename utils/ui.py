"""
utils/ui.py  —  Single CSS source + reusable component helpers.
Import inject_global_css() at the top of every page.
"""
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
#  CSS — one string, injected once per page
# ─────────────────────────────────────────────────────────────────────────────
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root{
  --bg:       #080C14;
  --surface:  #0D1424;
  --card:     #0F1829;
  --raised:   #111D35;
  --border:   #1E3A5F;
  --bdl:      #253A5A;
  --blue:     #3B82F6;
  --blue-d:   #1D4ED8;
  --blue-gl:  rgba(59,130,246,.30);
  --green:    #10B981;
  --orange:   #F59E0B;
  --red:      #EF4444;
  --purple:   #A78BFA;
  --pink:     #EC4899;
  --cyan:     #06B6D4;
  --t1:       #E2E8F0;
  --t2:       #94A3B8;
  --t3:       #475569;
  --font:     'Outfit',sans-serif;
  --mono:     'JetBrains Mono',monospace;
  --r1:8px; --r2:14px; --r3:20px;
}

/* ── Base ── */
html,body,[class*="css"]{font-family:var(--font)!important;background:var(--bg)!important;color:var(--t1)!important;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stAppViewContainer"]{background:var(--bg)!important;}
[data-testid="stAppViewBlockContainer"]{padding-top:.8rem!important;}

/* ── Sidebar ── */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#060A12,#0A1020 50%,#060A12)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"] *{color:var(--t1)!important;}
[data-testid="stSidebarNav"] a{border-radius:10px!important;padding:8px 12px!important;margin:2px 4px!important;transition:all .2s!important;}
[data-testid="stSidebarNav"] a:hover{background:rgba(59,130,246,.12)!important;}
[data-testid="stSidebarNav"] a[aria-current="page"]{background:linear-gradient(90deg,rgba(59,130,246,.25),rgba(59,130,246,.05))!important;border-left:3px solid var(--blue)!important;}

/* ── Form ── */
[data-testid="stForm"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--r3)!important;padding:1.6rem 1.4rem!important;}
input[type="text"],input[type="number"],[data-baseweb="input"] input{background:var(--raised)!important;border:1px solid var(--border)!important;color:var(--t1)!important;border-radius:var(--r1)!important;font-family:var(--font)!important;transition:border-color .2s,box-shadow .2s!important;}
input:focus{border-color:var(--blue)!important;box-shadow:0 0 0 3px var(--blue-gl)!important;outline:none!important;}
[data-baseweb="select"]>div,[data-baseweb="multi-select"]>div{background:var(--raised)!important;border:1px solid var(--border)!important;border-radius:var(--r1)!important;}
[data-testid="stNumberInput"] input{text-align:center!important;}
[data-testid="stNumberInput"] button{background:var(--raised)!important;border:1px solid var(--border)!important;color:var(--t1)!important;border-radius:var(--r1)!important;}

/* ── Slider ── */
[data-testid="stSlider"] [role="slider"]{background:var(--blue)!important;box-shadow:0 0 8px var(--blue-gl)!important;}
[data-testid="stSlider"]>div>div>div{background:linear-gradient(90deg,var(--blue),var(--purple))!important;}

/* ── Buttons ── */
.stButton>button{background:linear-gradient(135deg,#1D4ED8,#1E40AF)!important;color:#fff!important;border:1px solid #2563EB!important;border-radius:var(--r2)!important;font-family:var(--font)!important;font-weight:600!important;font-size:.9rem!important;transition:all .25s cubic-bezier(.4,0,.2,1)!important;box-shadow:0 4px 15px rgba(29,78,216,.3)!important;}
.stButton>button:hover{background:linear-gradient(135deg,#2563EB,#1D4ED8)!important;transform:translateY(-2px)!important;box-shadow:0 8px 28px rgba(37,99,235,.5)!important;border-color:#3B82F6!important;}
.stButton>button:active{transform:translateY(0)!important;}
[data-testid="stDownloadButton"]>button{background:linear-gradient(135deg,#065F46,#047857)!important;border-color:#10B981!important;box-shadow:0 4px 15px rgba(5,150,105,.3)!important;}
[data-testid="stDownloadButton"]>button:hover{background:linear-gradient(135deg,#047857,#059669)!important;box-shadow:0 8px 28px rgba(5,150,105,.5)!important;transform:translateY(-2px)!important;}

/* ── Tabs ── */
[data-baseweb="tab-list"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--r2)!important;padding:4px!important;gap:4px!important;}
[data-baseweb="tab"]{border-radius:10px!important;font-family:var(--font)!important;font-weight:500!important;color:var(--t3)!important;transition:all .2s!important;}
[aria-selected="true"][data-baseweb="tab"]{background:linear-gradient(135deg,var(--blue-d),#1E40AF)!important;color:#fff!important;font-weight:600!important;box-shadow:0 4px 12px rgba(29,78,216,.4)!important;}

/* ── Expander ── */
[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--r2)!important;}
[data-testid="stExpander"] summary{font-weight:600!important;color:#93C5FD!important;font-family:var(--font)!important;}

/* ── Alerts ── */
[data-testid="stAlert"]{border-radius:var(--r2)!important;}

/* ── Metrics ── */
[data-testid="metric-container"]{background:linear-gradient(135deg,var(--card),var(--raised))!important;border:1px solid var(--border)!important;border-radius:var(--r2)!important;padding:1rem 1.2rem!important;transition:transform .2s,box-shadow .2s!important;}
[data-testid="metric-container"]:hover{transform:translateY(-2px)!important;box-shadow:0 0 30px rgba(59,130,246,.15)!important;}
[data-testid="stMetricValue"]{color:var(--blue)!important;font-weight:800!important;font-family:var(--mono)!important;}
[data-testid="stMetricLabel"]{color:var(--t3)!important;}

/* ── DataFrames ── */
[data-testid="stDataFrame"]{border-radius:var(--r2)!important;overflow:hidden!important;border:1px solid var(--border)!important;}
.dvn-scroller{background:var(--card)!important;}

/* ── Misc ── */
hr{border:none!important;border-top:1px solid var(--border)!important;margin:1.5rem 0!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px;}
::-webkit-scrollbar-thumb:hover{background:var(--blue);}
[data-testid="stProgress"]>div>div{background:linear-gradient(90deg,var(--blue),var(--purple))!important;border-radius:999px!important;}
[data-testid="stProgress"]>div{background:var(--raised)!important;border-radius:999px!important;}

/* ── Animations ── */
@keyframes fadeInUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulseGlow{0%,100%{box-shadow:0 0 15px rgba(59,130,246,.2)}50%{box-shadow:0 0 35px rgba(59,130,246,.5)}}
@keyframes floatY{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.anim-in{animation:fadeInUp .55s ease both;}
</style>
"""


def inject_global_css():
    st.markdown(_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Reusable components
# ─────────────────────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str, icon: str = ""):
    icon_html = f'<div style="font-size:2rem;flex-shrink:0">{icon}</div>' if icon else ""
    st.markdown(
        f'<div style="padding:24px 0 18px;border-bottom:1px solid #1E3A5F;margin-bottom:24px">'
        f'<div style="display:flex;align-items:center;gap:14px">'
        f'{icon_html}'
        f'<div>'
        f'<h1 style="font-size:1.85rem;font-weight:900;color:#E2E8F0;margin:0;letter-spacing:-.4px">{title}</h1>'
        f'<p style="color:#475569;font-size:.88rem;margin:4px 0 0">{subtitle}</p>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )


def kpi_card(icon: str, value: str, label: str, color: str, sublabel: str = ""):
    sub = f'<div style="color:#475569;font-size:.65rem;margin-top:2px">{sublabel}</div>' if sublabel else ""
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0F1829,#111D35);border:1px solid #1E3A5F;'
        f'border-top:3px solid {color};border-radius:14px;padding:16px 12px;text-align:center">'
        f'<div style="font-size:1.3rem;margin-bottom:5px">{icon}</div>'
        f'<div style="font-size:1.45rem;font-weight:800;color:{color};font-family:\'JetBrains Mono\',monospace;line-height:1">{value}</div>'
        f'<div style="font-size:.68rem;color:#475569;margin-top:4px;text-transform:uppercase;letter-spacing:.5px;font-weight:600">{label}</div>'
        f'{sub}</div>',
        unsafe_allow_html=True,
    )


def feature_card(icon: str, title: str, desc: str, badge_text: str, color: str):
    st.markdown(
        f'<div style="background:linear-gradient(135deg,{color}0A,transparent);border:1px solid {color}22;'
        f'border-radius:20px;padding:22px 18px;transition:transform .25s,border-color .25s,box-shadow .25s" '
        f'onmouseover="this.style.transform=\'translateY(-4px)\';this.style.borderColor=\'{color}55\';this.style.boxShadow=\'0 12px 32px rgba(0,0,0,.4)\'" '
        f'onmouseout="this.style.transform=\'translateY(0)\';this.style.borderColor=\'{color}22\';this.style.boxShadow=\'none\'">'
        f'<div style="display:flex;align-items:center;gap:11px;margin-bottom:12px">'
        f'<div style="background:{color}1A;border:1px solid {color}33;border-radius:11px;'
        f'width:44px;height:44px;display:flex;align-items:center;justify-content:center;font-size:1.25rem">{icon}</div>'
        f'<div>'
        f'<div style="font-weight:700;color:#E2E8F0;font-size:.92rem">{title}</div>'
        f'<span style="background:{color}18;color:{color};border:1px solid {color}33;border-radius:999px;'
        f'padding:2px 9px;font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px">{badge_text}</span>'
        f'</div></div>'
        f'<p style="color:#475569;font-size:.82rem;line-height:1.6;margin:0">{desc}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def result_banner(probability: float, label: str):
    colors = {"High": "#10B981", "Medium": "#F59E0B", "Low": "#EF4444"}
    emojis = {"High": "🎉", "Medium": "📈", "Low": "💪"}
    msgs   = {
        "High":   "You are well prepared! Keep refining your skills.",
        "Medium": "You are on track — targeted improvements will make a big difference.",
        "Low":    "Don't worry! Follow the roadmap below to improve significantly.",
    }
    c = colors[label]
    bar_w = max(4, int(probability))
    st.markdown(
        f'<div style="background:linear-gradient(135deg,{c}0C,{c}05);border:1px solid {c}44;'
        f'border-radius:20px;padding:26px 28px;position:relative;overflow:hidden">'
        f'<div style="position:absolute;top:-40px;right:-40px;width:150px;height:150px;'
        f'background:radial-gradient(circle,{c}18,transparent 70%);pointer-events:none"></div>'
        f'<div style="display:flex;align-items:center;gap:16px;margin-bottom:14px">'
        f'<div style="background:{c}22;border:1px solid {c}44;border-radius:14px;padding:11px;font-size:1.8rem">{emojis[label]}</div>'
        f'<div>'
        f'<div style="font-size:2.5rem;font-weight:900;color:{c};font-family:\'JetBrains Mono\',monospace;line-height:1">{probability:.1f}%</div>'
        f'<div style="font-size:.95rem;color:#94A3B8;margin-top:2px"><strong style="color:{c}">{label} Placement Chance</strong></div>'
        f'</div></div>'
        f'<div style="background:{c}18;border-radius:999px;height:9px;margin-bottom:12px;overflow:hidden">'
        f'<div style="width:{bar_w}%;height:100%;background:linear-gradient(90deg,{c},{c}99);border-radius:999px"></div></div>'
        f'<p style="color:#94A3B8;font-size:.88rem;margin:0">{msgs[label]}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def tip_card(rank: int, tip: str, gain: float, current, target, feature_label: str):
    palette = ["#3B82F6","#10B981","#A78BFA","#F59E0B","#EC4899","#06B6D4"]
    c = palette[(rank - 1) % len(palette)]
    st.markdown(
        f'<div style="background:#0F1829;border:1px solid #1E3A5F;border-left:4px solid {c};'
        f'border-radius:14px;padding:15px 18px;margin-bottom:9px;'
        f'transition:transform .2s,box-shadow .2s" '
        f'onmouseover="this.style.transform=\'translateX(4px)\';this.style.boxShadow=\'0 4px 20px rgba(0,0,0,.3)\'" '
        f'onmouseout="this.style.transform=\'translateX(0)\';this.style.boxShadow=\'none\'">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">'
        f'<div style="flex:1">'
        f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:6px">'
        f'<span style="background:{c}22;color:{c};border:1px solid {c}44;border-radius:50%;'
        f'width:20px;height:20px;display:inline-flex;align-items:center;justify-content:center;'
        f'font-size:.68rem;font-weight:800;flex-shrink:0">{rank}</span>'
        f'<span style="font-size:.68rem;color:{c};font-weight:700;text-transform:uppercase;letter-spacing:.4px">{feature_label}</span>'
        f'</div>'
        f'<p style="margin:0;color:#E2E8F0;font-size:.87rem;line-height:1.5">{tip}</p>'
        f'<div style="margin-top:7px;font-size:.73rem;color:#475569">'
        f'Current: <strong style="color:#94A3B8">{current}</strong>'
        f' &nbsp;&#8594;&nbsp; '
        f'Target: <strong style="color:{c}">{target}+</strong>'
        f'</div></div>'
        f'<div style="background:{c}14;border:1px solid {c}30;border-radius:10px;'
        f'padding:8px 13px;text-align:center;flex-shrink:0;min-width:68px">'
        f'<div style="font-size:1.15rem;font-weight:800;color:{c};font-family:\'JetBrains Mono\',monospace">+{gain}%</div>'
        f'<div style="font-size:.62rem;color:#475569;text-transform:uppercase;letter-spacing:.3px">gain</div>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )


def sidebar_brand(accuracy=None, roc_auc=None, cv_mean=None, total_samples=None):
    st.markdown(
        '<div style="padding:22px 8px 14px;text-align:center">'
        '<div style="width:58px;height:58px;margin:0 auto 11px;background:linear-gradient(135deg,#1D4ED8,#7C3AED);'
        'border-radius:17px;display:flex;align-items:center;justify-content:center;font-size:1.7rem;'
        'box-shadow:0 8px 24px rgba(29,78,216,.45)">🎓</div>'
        '<div style="font-size:1rem;font-weight:800;color:#E2E8F0;letter-spacing:-.2px">AI Placement</div>'
        '<div style="font-size:.7rem;color:#475569;margin-top:2px">Prediction System v2.0</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div style="border-top:1px solid #1E3A5F;margin:0 8px"></div>', unsafe_allow_html=True)

    if all(v is not None for v in [accuracy, roc_auc, cv_mean, total_samples]):
        acc_s   = f"{float(accuracy):.2f}"
        auc_s   = f"{float(roc_auc):.4f}"
        cv_s    = f"{float(cv_mean):.2f}"
        total_s = f"{int(total_samples):,}"
        st.markdown(
            f'<div style="padding:13px 8px 8px">'
            f'<div style="font-size:.62rem;color:#475569;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:1px;margin-bottom:9px;padding-left:4px">Model Stats</div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">'
            f'<div style="background:#0A1628;border:1px solid #1E3A5F;border-radius:10px;padding:9px 6px;text-align:center">'
            f'<div style="color:#3B82F6;font-size:1.05rem;font-weight:800;font-family:\'JetBrains Mono\',monospace">{acc_s}%</div>'
            f'<div style="color:#475569;font-size:.6rem;margin-top:2px">Accuracy</div></div>'
            f'<div style="background:#0A1628;border:1px solid #1E3A5F;border-radius:10px;padding:9px 6px;text-align:center">'
            f'<div style="color:#10B981;font-size:1.05rem;font-weight:800;font-family:\'JetBrains Mono\',monospace">{auc_s}</div>'
            f'<div style="color:#475569;font-size:.6rem;margin-top:2px">ROC-AUC</div></div>'
            f'<div style="background:#0A1628;border:1px solid #1E3A5F;border-radius:10px;padding:9px 6px;text-align:center">'
            f'<div style="color:#A78BFA;font-size:1.05rem;font-weight:800;font-family:\'JetBrains Mono\',monospace">{cv_s}%</div>'
            f'<div style="color:#475569;font-size:.6rem;margin-top:2px">CV Score</div></div>'
            f'<div style="background:#0A1628;border:1px solid #1E3A5F;border-radius:10px;padding:9px 6px;text-align:center">'
            f'<div style="color:#F59E0B;font-size:1.05rem;font-weight:800;font-family:\'JetBrains Mono\',monospace">{total_s}</div>'
            f'<div style="color:#475569;font-size:.6rem;margin-top:2px">Records</div></div>'
            f'</div>'
            f'<div style="text-align:center;color:#475569;font-size:.62rem;margin-top:7px">'
            f'🌲 Random Forest · 200 trees · 9 features</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="border-top:1px solid #1E3A5F;margin:8px 8px 0"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="padding:9px 8px 5px;text-align:center;color:#1E3A5F;font-size:.66rem;line-height:1.6">'
        'Python · Streamlit · Scikit-learn · Plotly</div>',
        unsafe_allow_html=True,
    )
