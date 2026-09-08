import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.ui import inject_global_css, page_header, kpi_card, sidebar_brand
inject_global_css()

if "artifacts" not in st.session_state:
    st.error("Please open the app from the Home page first.")
    st.stop()

arts = st.session_state["artifacts"]
m    = arts["metrics"]
df   = arts["data"]

with st.sidebar:
    sidebar_brand(m.get("accuracy"), m.get("roc_auc"), m.get("cv_mean"), m.get("total_samples"))

page_header("Analytics Dashboard",
            "Explore model performance, placement trends, and feature insights.", "📊")

# KPI row
acc_s = f"{float(m['accuracy']):.2f}"
auc_s = f"{float(m['roc_auc']):.4f}"
cv_s  = f"{float(m['cv_mean']):.2f}"
f1_s  = f"{float(m['f1_score']):.4f}"
cols = st.columns(4)
with cols[0]: kpi_card("🎯", f"{acc_s}%", "Accuracy",      "#3B82F6", "Test set")
with cols[1]: kpi_card("📈", auc_s,        "ROC-AUC",       "#10B981", "Excellent")
with cols[2]: kpi_card("🔁", f"{cv_s}%",  "5-Fold CV",     "#A78BFA", f"±{float(m['cv_std']):.2f}%")
with cols[3]: kpi_card("🏆", f1_s,         "F1 Score",      "#F59E0B", "Balanced")

st.markdown("<br>", unsafe_allow_html=True)

import plotly.graph_objects as go

from utils.charts import (
    feat_importance,
    confusion_heatmap,
    cgpa_placement_bar,
    internship_trend,
    dsa_trend,
    cgpa_boxplot,
   
    radar,
)

HAS_PLOTLY = True

tab1, tab2, tab3, tab4 = st.tabs(
    ["📉 Model Performance", "📊 Placement Trends", "🔍 Feature Analysis", "📋 Dataset"]
)

# ── Tab 1: Model Performance ───────────────────────────────────────────────────
with tab1:
    if HAS_PLOTLY:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(confusion_heatmap(m["confusion_matrix"]), use_container_width=True)
            with st.expander("What is a Confusion Matrix?"):
                st.markdown(
                    "**True Positive**: Predicted *Placed* — actually placed ✅  \n"
                    "**True Negative**: Predicted *Not Placed* — actually not placed ✅  \n"
                    "**False Positive**: Predicted *Placed* — not placed ❌  \n"
                    "**False Negative**: Predicted *Not Placed* — was placed ❌"
                )
        with c2:
            st.plotly_chart(feat_importance(m["feature_importance"]), use_container_width=True)
            with st.expander("What is Feature Importance?"):
                st.markdown(
                    "Feature importance shows **how much each input contributes** to the model's decisions.  \n"
                    "Higher value = stronger influence on placement prediction."
                )
    else:
        st.info("Plotly not installed — charts unavailable.")

    st.markdown("#### Model Summary")
    import pandas as pd
    summary = pd.DataFrame({
        "Metric":  ["Accuracy","ROC-AUC","F1 Score","5-Fold CV Mean","Train Samples","Test Samples","Algorithm"],
        "Value":   [f"{float(m['accuracy']):.2f}%", f"{float(m['roc_auc']):.4f}",
                    f"{float(m['f1_score']):.4f}",  f"{float(m['cv_mean']):.2f}%",
                    str(m["n_train"]), str(m["n_test"]),
                    "Random Forest (200 trees, max_depth=12)"],
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)

# ── Tab 2: Placement Trends ────────────────────────────────────────────────────
with tab2:
    if HAS_PLOTLY:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(cgpa_placement_bar(df), use_container_width=True)
       
        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(internship_trend(df), use_container_width=True)
        with c4:
            st.plotly_chart(dsa_trend(df), use_container_width=True)
        st.plotly_chart(cgpa_boxplot(df), use_container_width=True)
    else:
        st.info("Plotly not installed.")

# ── Tab 3: Feature Analysis ────────────────────────────────────────────────────
with tab3:
    st.markdown(
        '<p style="color:#475569;font-size:.88rem;margin-bottom:16px">'
        'Adjust the sliders to see how the skill radar changes in real time.</p>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        t_cgpa  = st.slider("CGPA",           4.0, 10.0, 7.5, 0.1, key="tc")
        t_apt   = st.slider("Aptitude",       40,  100,  70,       key="ta")
        t_comm  = st.slider("Communication",  1,   10,   6,        key="tco")
    with c2:
        t_proj  = st.slider("Projects",       0,   10,   3,        key="tp")
        t_intern= st.slider("Internships",    0,   4,    1,        key="ti")
        t_tech  = st.slider("Tech Skills",    1,   15,   7,        key="tte")
    with c3:
        t_cert  = st.slider("Certifications", 0,   7,    2,        key="tce")
        t_dsa   = st.slider("DSA Level",      1,   10,   6,        key="td")
        t_att   = st.slider("Attendance %",   40,  100,  80,       key="tat")

    demo = {
        "cgpa": t_cgpa, "aptitude_score": t_apt, "communication_skills": t_comm,
        "num_projects": t_proj, "internships": t_intern, "technical_skills": t_tech,
        "certifications": t_cert, "dsa_level": t_dsa, "attendance": t_att,
    }
    if HAS_PLOTLY:
        st.plotly_chart(radar(demo), use_container_width=True)

# ── Tab 4: Dataset ─────────────────────────────────────────────────────────────
with tab4:
    placed_filter = st.selectbox("Filter", ["All Students", "Placed Only", "Not Placed Only"])
    show = df.copy()
    if placed_filter == "Placed Only":       show = show[show["placed"] == 1]
    elif placed_filter == "Not Placed Only": show = show[show["placed"] == 0]
    st.caption(f"Showing {len(show):,} of {len(df):,} records")
    
    st.dataframe(
    show.head(100),
    use_container_width=True,
    height=500
)
    st.markdown("#### Statistical Summary")
    st.dataframe(df.describe().round(2), use_container_width=True)
