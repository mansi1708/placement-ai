import streamlit as st
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.ui import inject_global_css, page_header, sidebar_brand
inject_global_css()

if "artifacts" not in st.session_state:
    st.error("Please open the app from the Home page first.")
    st.stop()

m = st.session_state["artifacts"]["metrics"]
with st.sidebar:
    sidebar_brand(m.get("accuracy"), m.get("roc_auc"), m.get("cv_mean"), m.get("total_samples"))

page_header("Interview Q&A Generator",
            "Select your skills and weak areas to get personalised interview questions.", "❓")

# ── Question bank ──────────────────────────────────────────────────────────────
QBANK = {
    "Python": {
        "Technical": [
            "What is the difference between a list and a tuple?",
            "Explain Python's GIL (Global Interpreter Lock).",
            "What are decorators? Give a real-world example.",
            "How does memory management work in Python?",
            "What is the difference between *args and **kwargs?",
            "Explain list comprehension with an example.",
            "What is a generator? How does it differ from a list?",
            "How do you handle exceptions using try/except/finally?",
        ],
        "OOP": [
            "Explain the four pillars of Object-Oriented Programming.",
            "What is the difference between __str__ and __repr__?",
            "How does method overriding work in Python?",
            "What is multiple inheritance? Explain MRO.",
            "What is encapsulation and why is it important?",
        ],
        "HR": [
            "Why do you want to work at our company?",
            "Describe a challenging project and how you handled it.",
            "Where do you see yourself in 5 years?",
        ],
    },
    "Machine Learning": {
        "Technical": [
            "What is the difference between supervised and unsupervised learning?",
            "Explain bias-variance trade-off.",
            "What is overfitting? How do you prevent it?",
            "Explain precision, recall, and F1-score.",
            "What is cross-validation and why is it important?",
            "How does gradient descent work?",
            "What is the difference between bagging and boosting?",
            "How does a Random Forest work?",
        ],
        "OOP": [
            "How would you design a reusable ML pipeline in Python?",
            "Explain abstraction in the context of ML libraries like Scikit-learn.",
        ],
        "HR": [
            "How do you keep up with the latest ML research?",
            "Describe an ML project you are proud of.",
        ],
    },
    "SQL": {
        "Technical": [
            "What is the difference between INNER JOIN and LEFT JOIN?",
            "Explain GROUP BY vs HAVING.",
            "What are window functions? Give an example.",
            "How would you find the second highest salary in a table?",
            "What is database normalization? Explain 1NF, 2NF, 3NF.",
            "What are indexes and when should you use them?",
            "Explain ACID properties in databases.",
        ],
        "OOP": [
            "How would you design a database schema for an e-commerce application?",
        ],
        "HR": [
            "How do you handle large datasets efficiently in SQL?",
        ],
    },
    "Data Structures & Algorithms": {
        "Technical": [
            "What is the time complexity of binary search?",
            "Explain the difference between BFS and DFS.",
            "How does a hash map work internally?",
            "What is dynamic programming? Give an example.",
            "Explain merge sort and its time complexity.",
            "What is a balanced BST? Why is it important?",
            "Explain Dijkstra's algorithm.",
            "What is a stack vs a queue?",
        ],
        "OOP": [
            "Design a Stack class with push, pop, and getMin in O(1).",
            "Implement a Singleton pattern in Python.",
        ],
        "HR": [
            "How do you approach a problem you have never seen before?",
            "Tell me about a time you optimised a slow algorithm.",
        ],
    },
    "Web Development": {
        "Technical": [
            "What is the difference between GET and POST?",
            "Explain REST API design principles.",
            "What is CORS and why does it matter?",
            "How does session management work?",
            "What is the difference between cookies and localStorage?",
        ],
        "OOP": [
            "Design the backend architecture for a URL shortener.",
        ],
        "HR": [
            "Walk me through a full-stack project you have built.",
        ],
    },
}

ALL_SKILLS = list(QBANK.keys())

# ── Controls ───────────────────────────────────────────────────────────────────
col_s, col_w = st.columns(2)
with col_s:
    selected_skills = st.multiselect("✅ Your Skills", ALL_SKILLS,
                                      default=["Python", "SQL"])
with col_w:
    weak_areas = st.multiselect("⚠️ Weak Areas (extra questions)", ALL_SKILLS,
                                 default=["Data Structures & Algorithms"])

col_cat, col_n = st.columns(2)
with col_cat:
    categories = st.multiselect("📂 Categories", ["Technical","OOP","HR"],
                                 default=["Technical","OOP","HR"])
with col_n:
    n_q = st.slider("Questions per category", 2, 8, 4)

shuffle = st.checkbox("🔀 Shuffle questions", value=True)

if st.button("🚀 Generate Questions", type="primary", use_container_width=True):
    all_topics = list(dict.fromkeys(selected_skills + weak_areas))
    total_rendered = 0

    if not all_topics:
        st.warning("Please select at least one skill or weak area.")
    else:
        st.markdown("---")
        for topic in all_topics:
            if topic not in QBANK:
                continue
            st.markdown(
                f'<div style="font-size:1.1rem;font-weight:800;color:#E2E8F0;'
                f'margin:20px 0 12px;border-bottom:1px solid #1E3A5F;padding-bottom:8px">'
                f'🔹 {topic}</div>',
                unsafe_allow_html=True,
            )
            for cat in categories:
                qs = QBANK[topic].get(cat, [])
                if not qs:
                    continue
                sample = random.sample(qs, min(n_q, len(qs))) if shuffle else qs[:n_q]

                cat_colors = {"Technical": "#3B82F6", "OOP": "#A78BFA", "HR": "#F59E0B"}
                cc = cat_colors.get(cat, "#94A3B8")
                st.markdown(
                    f'<span style="background:{cc}18;color:{cc};border:1px solid {cc}33;'
                    f'border-radius:999px;padding:3px 13px;font-size:.68rem;font-weight:700;'
                    f'text-transform:uppercase;letter-spacing:.5px">{cat}</span>',
                    unsafe_allow_html=True,
                )
                for i, q in enumerate(sample, 1):
                    st.markdown(
                        f'<div style="background:#0F1829;border:1px solid #1E3A5F;'
                        f'border-left:3px solid {cc};border-radius:11px;'
                        f'padding:12px 16px;margin:6px 0;color:#E2E8F0;font-size:.88rem;line-height:1.5">'
                        f'<strong style="color:{cc}">Q{i}.</strong> {q}</div>',
                        unsafe_allow_html=True,
                    )
                    total_rendered += 1
                st.markdown("<br>", unsafe_allow_html=True)

        st.info(f"✅ **{total_rendered} questions generated** across {len(all_topics)} topic(s).")

        st.markdown("---")
        st.markdown("#### 🎯 Interview Tips")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                '<div style="background:#0F1829;border:1px solid #1E3A5F;border-radius:14px;'
                'padding:18px 20px">'
                '<div style="font-weight:700;color:#93C5FD;margin-bottom:10px">Before the Interview</div>'
                '<ul style="color:#94A3B8;font-size:.84rem;line-height:1.9;padding-left:18px;margin:0">'
                '<li>Revise all selected topics thoroughly</li>'
                '<li>Practice coding on paper or whiteboard</li>'
                '<li>Prepare 2–3 clear project explanations</li>'
                '<li>Research the company and its tech stack</li>'
                '<li>Do mock interviews with friends or online</li>'
                '</ul></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                '<div style="background:#0F1829;border:1px solid #1E3A5F;border-radius:14px;'
                'padding:18px 20px">'
                '<div style="font-weight:700;color:#93C5FD;margin-bottom:10px">During the Interview</div>'
                '<ul style="color:#94A3B8;font-size:.84rem;line-height:1.9;padding-left:18px;margin:0">'
                '<li>Think aloud — explain your reasoning</li>'
                '<li>Clarify the problem before you code</li>'
                '<li>Manage time carefully per question</li>'
                '<li>Ask smart, genuine questions at the end</li>'
                '<li>Relate answers back to your own projects</li>'
                '</ul></div>',
                unsafe_allow_html=True,
            )
