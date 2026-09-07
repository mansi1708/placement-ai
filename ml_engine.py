"""
utils/ml_engine.py
==================
Core ML utility functions shared across all pages:

  load_artifacts()       — load model, scaler, features, metrics
  predict()              — run inference, return probability + label
  get_suggestions()      — smart improvement tips with gain estimates
  build_pdf_report()     — generate downloadable PDF report
  get_strengths_weaknesses() — analyse profile for report card
"""

import os, pickle
import numpy as np
import pandas as pd
from io import BytesIO

# ─── Paths ─────────────────────────────────────────────────────────────────────
_ROOT      = os.path.dirname(os.path.dirname(__file__))
_MODEL_DIR = os.path.join(_ROOT, "model")
_DATA_PATH = os.path.join(_ROOT, "dataset", "placement_data.csv")

# ─── Feature display names (for UI) ──────────────────────────────────────────
FEATURE_LABELS = {
    "cgpa":                 "CGPA",
    "aptitude_score":       "Aptitude Score",
    "communication_skills": "Communication Skills",
    "num_projects":         "Number of Projects",
    "internships":          "Internships",
    "technical_skills":     "Technical Skills",
    "certifications":       "Certifications",
    "dsa_level":            "DSA Knowledge Level",
    "attendance":           "Attendance %",
}

# ─── Improvement suggestion rules ────────────────────────────────────────────
# Each rule: (feature_key, below_threshold, tip_text, max_gain_pct)
SUGGESTION_RULES = [
    ("cgpa",                 7.0,  "📚 Improve your CGPA — target 7.5+ by focusing on core subjects and consistent study habits.", 10),
    ("dsa_level",            6,    "💻 Level up your DSA skills — solve 2 problems daily on LeetCode / HackerRank (focus: arrays, trees, DP).", 11),
    ("num_projects",         4,    "🔨 Build more projects — aim for 4+ with GitHub READMEs. Try ML, web, or API-based projects.", 8),
    ("aptitude_score",       65,   "🧠 Practice aptitude daily — use IndiaBix, PrepInsta, and previous year papers for 30 mins/day.", 6),
    ("communication_skills", 6,    "🗣️ Strengthen communication — join Toastmasters, do mock GDs, or record yourself presenting.", 7),
    ("internships",          1,    "🏢 Get at least one internship — apply to companies on Internshala, LinkedIn, or your college portal.", 9),
    ("technical_skills",     8,    "⚙️ Add technical skills — learn 2-3 more tools (Docker, AWS, FastAPI, React) relevant to your target role.", 5),
    ("certifications",       2,    "🏅 Earn certifications — start with Google IT Support, AWS Cloud Practitioner, or Coursera ML.", 4),
    ("attendance",           75,   "📅 Maintain ≥75% attendance — it signals discipline and affects internal marks.", 3),
]


# ═══════════════════════════════════════════════════════════════════════════════
#  Model Loading (cached in session_state by the Streamlit app)
# ═══════════════════════════════════════════════════════════════════════════════

def load_artifacts() -> dict:
    """Load all saved model artifacts from disk. Returns a dict."""
    files = ["rf_model.pkl", "scaler.pkl", "features.pkl", "metrics.pkl"]
    arts  = {}
    for fname in files:
        key = fname.replace(".pkl", "")
        with open(os.path.join(_MODEL_DIR, fname), "rb") as f:
            arts[key] = pickle.load(f)
    arts["data"] = pd.read_csv(_DATA_PATH)
    return arts


# ═══════════════════════════════════════════════════════════════════════════════
#  Prediction
# ═══════════════════════════════════════════════════════════════════════════════

def predict(artifacts: dict, student: dict) -> tuple[float, str]:
    """
    Run the Random Forest model on a student profile.

    Args:
        artifacts : dict returned by load_artifacts()
        student   : dict keyed by FEATURE_COLS

    Returns:
        (probability_pct: float, label: str)
        label ∈ {"High", "Medium", "Low"}
    """
    model   = artifacts["rf_model"]
    scaler  = artifacts["scaler"]
    features= artifacts["features"]

    row    = pd.DataFrame([student])[features].values
    row_sc = scaler.transform(row)
    prob   = model.predict_proba(row_sc)[0][1]          # P(placed)
    pct    = round(prob * 100, 2)

    if   pct >= 70: label = "High"
    elif pct >= 45: label = "Medium"
    else:           label = "Low"

    return pct, label


# ═══════════════════════════════════════════════════════════════════════════════
#  Smart Improvement Suggestions
# ═══════════════════════════════════════════════════════════════════════════════

def get_suggestions(student: dict, current_prob: float) -> list[dict]:
    """
    Evaluate student profile against thresholds.
    Returns sorted list of suggestion dicts:
        {feature, tip, gain, current_value, target_value}
    """
    suggestions = []
    for feat, threshold, tip, max_gain in SUGGESTION_RULES:
        val = student.get(feat, 0)
        if val < threshold:
            # Scale gain by how far below the threshold they are
            gap_ratio = (threshold - val) / threshold
            gain      = round(max_gain * (0.4 + 0.6 * gap_ratio), 1)
            suggestions.append({
                "feature":       feat,
                "label":         FEATURE_LABELS.get(feat, feat),
                "tip":           tip,
                "gain":          gain,
                "current_value": val,
                "target_value":  threshold,
            })

    # Sort by highest expected gain first
    suggestions.sort(key=lambda x: x["gain"], reverse=True)
    return suggestions


# ═══════════════════════════════════════════════════════════════════════════════
#  Strengths & Weaknesses Analysis
# ═══════════════════════════════════════════════════════════════════════════════

# Benchmark thresholds for "strong" vs "weak"
BENCHMARKS = {
    "cgpa":                 (8.0,  7.0),   # (strong, weak) thresholds
    "aptitude_score":       (80,   55),
    "communication_skills": (8,    5),
    "num_projects":         (5,    2),
    "internships":          (2,    0),
    "technical_skills":     (10,   5),
    "certifications":       (3,    1),
    "dsa_level":            (7,    4),
    "attendance":           (85,   70),
}

def get_strengths_weaknesses(student: dict) -> tuple[list, list]:
    """Return (strengths_list, weaknesses_list) for report card."""
    strengths, weaknesses = [], []
    for feat, (strong_t, weak_t) in BENCHMARKS.items():
        val  = student.get(feat, 0)
        label= FEATURE_LABELS.get(feat, feat)
        if val >= strong_t:
            strengths.append(f"✅ {label}: {val} (Excellent)")
        elif val < weak_t:
            weaknesses.append(f"⚠️ {label}: {val} (Needs Improvement)")
    return strengths, weaknesses


# ═══════════════════════════════════════════════════════════════════════════════
#  PDF Report Generation
# ═══════════════════════════════════════════════════════════════════════════════

def build_pdf_report(
    name: str,
    student: dict,
    probability: float,
    label: str,
    suggestions: list,
    strengths: list,
    weaknesses: list,
    metrics: dict,
) -> bytes:
    """
    Generate a professional PDF placement report.
    Returns raw bytes (ready for st.download_button).
    Requires: reportlab
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        Table, TableStyle, HRFlowable, KeepTogether
    )
    from datetime import date

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    S      = getSampleStyleSheet()
    NAVY   = colors.HexColor("#0D2137")
    BLUE   = colors.HexColor("#2563EB")
    GREEN  = colors.HexColor("#16A34A")
    ORANGE = colors.HexColor("#EA580C")
    RED    = colors.HexColor("#DC2626")
    LGRAY  = colors.HexColor("#F1F5F9")
    GRAY   = colors.HexColor("#64748B")

    label_colour = {"High": GREEN, "Medium": ORANGE, "Low": RED}[label]

    # ── Custom paragraph styles ────────────────────────────────────────────────
    def style(name, base="Normal", **kw):
        return ParagraphStyle(name, parent=S[base], **kw)

    title_s   = style("T",  "Title",  fontSize=22, textColor=NAVY, spaceAfter=4)
    h2_s      = style("H2", "Heading2", fontSize=13, textColor=NAVY, spaceBefore=10, spaceAfter=4)
    body_s    = style("B",  "Normal", fontSize=9.5, leading=14, textColor=colors.HexColor("#1E293B"))
    caption_s = style("C",  "Normal", fontSize=8.5, textColor=GRAY, leading=12)
    tip_s     = style("TP", "Normal", fontSize=9, leading=13, textColor=colors.HexColor("#1E293B"))

    story = []

    # ── Header ─────────────────────────────────────────────────────────────────
    story.append(Paragraph("🎓 AI Placement Prediction Report", title_s))
    story.append(Paragraph(
        f"Prepared for: <b>{name or 'Student'}</b> &nbsp;|&nbsp; {date.today().strftime('%d %B %Y')}",
        caption_s,
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=10))

    # ── Placement Result ───────────────────────────────────────────────────────
    story.append(Paragraph("Placement Prediction", h2_s))
    res_data = [
        ["Metric", "Value"],
        ["Placement Probability", f"{probability:.1f}%"],
        ["Placement Chance",      f"{label} Chance"],
        ["Model Used",            "Random Forest Classifier (200 trees)"],
        ["Model Accuracy",        f"{metrics.get('accuracy','—')}%"],
        ["ROC-AUC Score",         str(metrics.get('roc_auc','—'))],
    ]
    t = Table(res_data, colWidths=[6*cm, 10*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9.5),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [LGRAY, colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("TEXTCOLOR",     (1,2), (1,2), label_colour),
        ("FONTNAME",      (1,2), (1,2), "Helvetica-Bold"),
        ("FONTSIZE",      (1,2), (1,2), 11),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # ── Student Profile ────────────────────────────────────────────────────────
    story.append(Paragraph("Student Profile", h2_s))
    profile_data = [["Feature", "Your Value", "Strong Threshold"]]
    thresholds = {k: v[0] for k, v in BENCHMARKS.items()}
    for feat, lbl in FEATURE_LABELS.items():
        val = student.get(feat, "—")
        thr = thresholds.get(feat, "—")
        profile_data.append([lbl, str(val), f"≥ {thr}"])
    pt = Table(profile_data, colWidths=[6*cm, 5*cm, 5.5*cm])
    pt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,-1), "Helvetica"),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [LGRAY, colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
    ]))
    story.append(pt)
    story.append(Spacer(1, 0.4*cm))

    # ── Strengths & Weaknesses ─────────────────────────────────────────────────
    if strengths or weaknesses:
        story.append(Paragraph("Strengths & Weaknesses", h2_s))
        sw_data = [["✅ Strengths", "⚠️ Weaknesses"]]
        max_len = max(len(strengths), len(weaknesses), 1)
        for i in range(max_len):
            s = strengths[i]  if i < len(strengths)  else ""
            w = weaknesses[i] if i < len(weaknesses) else ""
            sw_data.append([s, w])
        sw = Table(sw_data, colWidths=[8*cm, 8*cm])
        sw.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#1E3A5F")),
            ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8.5),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [LGRAY, colors.white]),
            ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
        ]))
        story.append(sw)
        story.append(Spacer(1, 0.4*cm))

    # ── Improvement Roadmap ────────────────────────────────────────────────────
    if suggestions:
        story.append(Paragraph("📍 Improvement Roadmap", h2_s))
        cumulative = current = probability
        for i, sug in enumerate(suggestions[:6], 1):
            cumulative = min(cumulative + sug["gain"], 99)
            story.append(Paragraph(
                f"<b>{i}. {sug['tip']}</b>",
                tip_s,
            ))
            story.append(Paragraph(
                f"   Expected probability gain: <b>+{sug['gain']}%</b> → cumulative: <b>{cumulative:.1f}%</b>",
                caption_s,
            ))
            story.append(Spacer(1, 0.15*cm))

    # ── Footer ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1")))
    story.append(Paragraph(
        "<i>Generated by AI Placement Prediction System · "
        "Built with Python, Scikit-learn & Streamlit · For academic & demo purposes.</i>",
        caption_s,
    ))

    doc.build(story)
    return buf.getvalue()
