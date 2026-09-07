import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.ui import inject_global_css, page_header, result_banner, tip_card, sidebar_brand
from utils.ml_engine import predict, get_suggestions, get_strengths_weaknesses, build_pdf_report
inject_global_css()

if "artifacts" not in st.session_state:
    st.error("Please open the app from the Home page first.")
    st.stop()

arts = st.session_state["artifacts"]
m    = arts["metrics"]

with st.sidebar:
    sidebar_brand(m.get("accuracy"), m.get("roc_auc"), m.get("cv_mean"), m.get("total_samples"))

page_header("Placement Prediction",
            "Enter your academic profile — the Random Forest model predicts your placement probability.",
            "🔮")

# ── Input form ─────────────────────────────────────────────────────────────────
with st.form("pred_form"):
    st.markdown(
        '<div style="font-size:.75rem;font-weight:700;color:#475569;text-transform:uppercase;'
        'letter-spacing:1px;margin-bottom:14px">Student Academic Profile</div>',
        unsafe_allow_html=True,
    )

    student_name = st.text_input("👤 Your Name", placeholder="e.g. Arjun Sharma",
                                  help="Used in PDF report only")

    st.markdown(
        '<div style="font-size:.72rem;font-weight:700;color:#475569;text-transform:uppercase;'
        'letter-spacing:.9px;margin:14px 0 10px">Academic & Skill Metrics</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        cgpa        = st.number_input("📊 CGPA", min_value=4.0, max_value=10.0, value=7.5, step=0.01)
        aptitude    = st.slider("🧠 Aptitude Score (0–100)", 0, 100, 65)
        attendance  = st.slider("📅 Attendance (%)", 40, 100, 78)
    with col2:
        communication = st.slider("🗣️ Communication (1–10)", 1, 10, 6)
        dsa           = st.slider("💻 DSA Knowledge (1–10)", 1, 10, 5)
        projects      = st.slider("🔨 Projects", 0, 10, 2)
    with col3:
        internships = st.slider("🏢 Internships", 0, 4, 0)
        tech_skills = st.slider("⚙️ Technical Skills", 1, 15, 6)
        certs       = st.slider("🏅 Certifications", 0, 7, 1)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button(
        "🚀 Predict My Placement Chance",
        use_container_width=True,
        type="primary",
    )

# ── Results ────────────────────────────────────────────────────────────────────
if submitted:
    student = {
        "cgpa": cgpa, "aptitude_score": aptitude,
        "communication_skills": communication, "num_projects": projects,
        "internships": internships, "technical_skills": tech_skills,
        "certifications": certs, "dsa_level": dsa, "attendance": attendance,
    }

    probability, label         = predict(arts, student)
    suggestions                = get_suggestions(student, probability)
    strengths, weaknesses      = get_strengths_weaknesses(student)

    st.session_state["last_student"]     = student
    st.session_state["last_probability"] = probability
    st.session_state["last_label"]       = label

    st.markdown("---")

    # Result banner + radar
    col_res, col_radar = st.columns([1.05, 1])
    with col_res:
        st.markdown("#### 🎯 Your Result")
        result_banner(probability, label)

        st.markdown("<br>", unsafe_allow_html=True)
        color_map = {"High": "#10B981", "Medium": "#F59E0B", "Low": "#EF4444"}
        lc = color_map[label]
        total_gain = round(sum(s["gain"] for s in suggestions), 1)
        sc1, sc2, sc3 = st.columns(3)
        for col, val, lbl, fc in [
            (sc1, f"{probability:.1f}%", "Probability",  lc),
            (sc2, label,                 "Chance Level", lc),
            (sc3, f"+{total_gain}%",     "Max Gain",     "#3B82F6"),
        ]:
            with col:
                st.markdown(
                    f'<div style="background:#0F1829;border:1px solid #1E3A5F;border-radius:12px;'
                    f'padding:13px;text-align:center">'
                    f'<div style="font-size:1.3rem;font-weight:800;color:{fc};'
                    f'font-family:\'JetBrains Mono\',monospace">{val}</div>'
                    f'<div style="color:#475569;font-size:.68rem;margin-top:3px">{lbl}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with col_radar:
        st.markdown("#### 📡 Skill Radar")
        try:
            from utils.charts import radar
            st.plotly_chart(radar(student), use_container_width=True)
        except ImportError:
            st.info("Install plotly: `pip install plotly`")

    # Strengths & Weaknesses
    st.markdown("---")
    col_s, col_w = st.columns(2)
    with col_s:
        st.markdown("#### ✅ Strengths")
        if strengths:
            for s in strengths:
                st.markdown(
                    f'<div style="background:rgba(16,185,129,.06);border:1px solid rgba(16,185,129,.20);'
                    f'border-left:3px solid #10B981;border-radius:10px;padding:10px 14px;'
                    f'margin-bottom:6px;color:#E2E8F0;font-size:.85rem">{s}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Keep improving to build a strong profile!")

    with col_w:
        st.markdown("#### ⚠️ Areas to Improve")
        if weaknesses:
            for w in weaknesses:
                st.markdown(
                    f'<div style="background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.20);'
                    f'border-left:3px solid #EF4444;border-radius:10px;padding:10px 14px;'
                    f'margin-bottom:6px;color:#E2E8F0;font-size:.85rem">{w}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("🌟 No major weaknesses — great profile!")

    # Improvement tips + forecast
    if suggestions:
        st.markdown("---")
        col_tips, col_chart = st.columns([1, 1.05])
        with col_tips:
            st.markdown("#### 💡 Improvement Roadmap")
            total  = round(sum(s["gain"] for s in suggestions), 1)
            capped = min(probability + total, 99)
            st.info(
                f"This roadmap could raise your probability from "
                f"**{probability:.1f}%** to **{capped:.1f}%** (+{total}%)"
            )
            for i, sug in enumerate(suggestions[:6], 1):
                tip_card(i, sug["tip"], sug["gain"],
                         sug["current_value"], sug["target_value"], sug["label"])

        with col_chart:
            st.markdown("#### 📈 Impact Forecast")
            try:
                from utils.charts import improvement_forecast
                st.plotly_chart(improvement_forecast(suggestions, probability),
                                use_container_width=True)
            except ImportError:
                st.info("Install plotly: `pip install plotly`")
    else:
        st.success("🎉 Excellent profile — no major improvements needed!")

    # PDF export
    st.markdown("---")
    st.markdown("#### 📄 Download Your Report")
    col_dl, col_info = st.columns([1, 2])
    with col_dl:
        try:
            pdf_bytes = build_pdf_report(
                name=student_name or "Student", student=student,
                probability=probability, label=label,
                suggestions=suggestions, strengths=strengths,
                weaknesses=weaknesses, metrics=arts["metrics"],
            )
            st.download_button(
                "⬇️ Download PDF Report", data=pdf_bytes,
                file_name=f"placement_report_{(student_name or 'student').replace(' ','_').lower()}.pdf",
                mime="application/pdf", use_container_width=True,
            )
        except ImportError:
            st.warning("Install reportlab: `pip install reportlab`")
        except Exception as e:
            st.error(f"PDF error: {e}")
    with col_info:
        st.markdown(
            '<div style="background:#0F1829;border:1px solid #1E3A5F;border-radius:12px;'
            'padding:15px 17px;font-size:.83rem;color:#94A3B8;line-height:1.6">'
            '<strong style="color:#93C5FD">Report includes:</strong> Placement score · '
            'Skill profile · Strengths &amp; weaknesses · Improvement roadmap · Model stats'
            '</div>',
            unsafe_allow_html=True,
        )
