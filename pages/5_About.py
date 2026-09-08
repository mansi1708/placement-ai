import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.ui import inject_global_css, page_header, sidebar_brand
inject_global_css()

if "artifacts" not in st.session_state:
    st.error("Please open the app from the Home page first.")
    st.stop()

m = st.session_state["artifacts"]["metrics"]
with st.sidebar:
    sidebar_brand(m.get("accuracy"), m.get("roc_auc"), m.get("cv_mean"), m.get("total_samples"))

page_header("About This Project",
            "Architecture, ML pipeline, and how to explain this project in interviews.", "ℹ️")

# Project summary
acc_s = f"{float(m['accuracy']):.2f}"
auc_s = f"{float(m['roc_auc']):.4f}"
st.markdown(
    '<div style="background:linear-gradient(135deg,rgba(59,130,246,.06),rgba(167,139,250,.04));'
    'border:1px solid #1E3A5F;border-radius:18px;padding:24px 26px;margin-bottom:24px">'
    '<h3 style="color:#93C5FD;margin:0 0 10px;font-size:1.1rem">🎯 Project Goal</h3>'
    '<p style="color:#94A3B8;font-size:.9rem;line-height:1.7;margin:0">'
    'The <strong style="color:#E2E8F0">AI Placement Prediction System</strong> is an end-to-end '
    'machine learning web application that helps students gauge their placement readiness. '
    'It analyses 9 key academic and skill-based features using a '
    '<strong style="color:#E2E8F0">Random Forest Classifier</strong> trained on 2,000 synthetic '
    f'student records, achieving <strong style="color:#10B981">{acc_s}% accuracy</strong> and '
    f'<strong style="color:#10B981">{auc_s} ROC-AUC</strong>.'
    '</p></div>',
    unsafe_allow_html=True,
)

# Architecture columns
st.markdown("#### 🏗️ System Architecture")
c1, c2, c3 = st.columns(3)
layers = [
    ("🖥️ Frontend", "#3B82F6", "Streamlit", [
        "Multi-page navigation",  "Interactive input forms",
        "Plotly dark-theme charts","PDF report download",
        "Dark glassmorphism UI",
    ]),
    ("🧠 ML Backend", "#10B981", "Scikit-learn", [
        "NumPy data generation",   "StandardScaler preprocessing",
        "Random Forest (200 trees)","Probability calibration",
        "Feature importance output",
    ]),
    ("📦 Utilities", "#A78BFA", "Python modules", [
        "utils/ml_engine.py — inference",
        "utils/ui.py — CSS & components",
        "utils/charts.py — Plotly charts",
        "model/train_model.py — training",
        "PDF report via ReportLab",
    ]),
]
for col, (title, color, tech, items) in zip([c1, c2, c3], layers):
    with col:
        bullets = "".join(
            f'<li style="color:#94A3B8;font-size:.82rem;margin-bottom:3px">{i}</li>'
            for i in items
        )
        st.markdown(
            f'<div style="background:#0F1829;border:1px solid {color}33;border-top:3px solid {color};'
            f'border-radius:14px;padding:20px 18px;height:100%">'
            f'<div style="font-weight:700;color:{color};font-size:.95rem;margin-bottom:4px">{title}</div>'
            f'<div style="font-size:.72rem;color:#475569;font-weight:700;margin-bottom:12px">{tech}</div>'
            f'<ul style="padding-left:16px;margin:0">{bullets}</ul>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ML Pipeline steps
st.markdown("#### 🔬 ML Pipeline")
pipeline_steps = [
    ("1. Data Generation",     "#3B82F6",
     "2,000 synthetic student records with realistic distributions (NumPy seed=42)."),
    ("2. Feature Engineering", "#10B981",
     "9 features: CGPA, Aptitude, Communication, Projects, Internships, Technical Skills, Certifications, DSA, Attendance."),
    ("3. Preprocessing",       "#A78BFA",
     "StandardScaler normalises all features to zero mean / unit variance. Fit on train set only (no leakage)."),
    ("4. Model Training",      "#F59E0B",
     "Random Forest: 200 estimators, max_depth=12, stratified 80/20 train-test split."),
    ("5. Evaluation",          "#EC4899",
     f"Accuracy {acc_s}%, ROC-AUC {auc_s}, 5-fold cross-validation."),
    ("6. Deployment",          "#06B6D4",
     "Model + scaler serialised with pickle. Loaded once via @st.cache_resource — fast across all pages."),
]
for step, color, desc in pipeline_steps:
    st.markdown(
        f'<div style="display:flex;gap:14px;margin-bottom:10px;align-items:flex-start">'
        f'<div style="background:{color}18;border:1px solid {color}44;border-radius:8px;'
        f'padding:5px 12px;font-size:.75rem;font-weight:700;color:{color};'
        f'white-space:nowrap;flex-shrink:0">{step}</div>'
        f'<div style="color:#94A3B8;font-size:.87rem;line-height:1.55;padding-top:4px">{desc}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# Interview explanation
st.markdown("#### 🎤 How to Explain in an Interview")
with st.expander("Click to see a sample 30-second explanation"):
    st.markdown(
        f'> *"I built an end-to-end AI Placement Prediction System using Python, Streamlit, '
        f'and Scikit-learn. The core is a Random Forest Classifier trained on 2,000 student '
        f'records with 9 features like CGPA, DSA level, and internship count. The model achieves '
        f'{acc_s}% accuracy and {auc_s} ROC-AUC. Beyond prediction, the system gives smart improvement '
        f'suggestions with quantified probability gains, generates personalised interview questions, '
        f'and exports a professional PDF report. The Streamlit frontend has 5 pages with interactive '
        f'Plotly charts on a dark glassmorphism theme."*'
    )
    st.markdown("**Likely follow-up questions:**")
    faqs = [
        ("Why Random Forest?",
         "Handles non-linear relationships, robust to outliers, gives feature importance natively, "
         "and outperforms Logistic Regression on this dataset."),
        ("How did you handle class imbalance?",
         "The dataset is roughly balanced (~50/50 placed/not-placed). I also used "
         "class_weight='balanced' in the classifier as a safeguard."),
        ("What is ROC-AUC?",
         f"Area under the ROC curve — measures discrimination ability independent of threshold. "
         f"{auc_s} means excellent class separation."),
        ("How would you improve it?",
         "Collect real placement data, tune hyperparameters with GridSearchCV, try XGBoost/LightGBM, "
         "add resume NLP features, implement SHAP explanations."),
    ]
    for q, a in faqs:
        st.markdown(f"**Q: {q}**")
        st.markdown(f"> {a}")
        st.markdown("")

# Project structure
st.markdown("#### 📁 Project Structure")
st.code(
    "placement_ai/\n"
    "├── app.py                     # Entry point + Home page\n"
    "├── .streamlit/config.toml     # Dark theme config\n"
    "├── requirements.txt\n"
    "├── dataset/\n"
    "│   ├── generate_data.py       # Synthetic dataset generator\n"
    "│   └── placement_data.csv     # 2,000 student records\n"
    "├── model/\n"
    "│   ├── train_model.py         # ML training pipeline\n"
    "│   ├── rf_model.pkl           # Trained Random Forest\n"
    "│   ├── scaler.pkl             # StandardScaler\n"
    "│   ├── features.pkl           # Feature name list\n"
    "│   └── metrics.pkl            # Accuracy, AUC, CM, FI\n"
    "├── pages/\n"
    "│   ├── 2_🔮_Prediction.py     # ML inference + results\n"
    "│   ├── 3_📊_Analytics.py      # Charts dashboard\n"
    "│   ├── 4_❓_Interview.py      # Q&A generator\n"
    "│   └── 5_ℹ️_About.py          # Architecture & tips\n"
    "└── utils/\n"
    "    ├── ml_engine.py           # predict(), suggestions, PDF\n"
    "    ├── ui.py                  # CSS + component helpers\n"
    "    └── charts.py              # All Plotly chart functions",
    language="",
)
