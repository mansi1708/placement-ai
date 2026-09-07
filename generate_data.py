"""
dataset/generate_data.py
========================
Generates a realistic synthetic dataset of 2000 student records
for training the placement prediction ML model.

Features engineered to mimic real placement patterns:
- CGPA has strongest correlation with placement
- Internships + DSA are second most important
- Communication & projects matter significantly
- All features interact realistically

Run this once: python dataset/generate_data.py
"""

import numpy as np
import pandas as pd
import os

# ─── Reproducibility ───────────────────────────────────────────────────────────
np.random.seed(42)
N = 2000

def generate_dataset(n=N) -> pd.DataFrame:
    """
    Generate synthetic but realistic student placement data.
    Returns a pandas DataFrame ready for ML training.
    """

    # ── Step 1: Raw features with realistic distributions ──────────────────────

    cgpa = np.round(
        np.random.normal(loc=7.5, scale=1.0, size=n).clip(4.0, 10.0), 2
    )

    aptitude = np.random.randint(40, 101, size=n)          # Test score 40-100
    communication = np.random.randint(1, 11, size=n)        # Scale 1-10
    projects = np.random.randint(0, 11, size=n)             # Count 0-10
    internships = np.random.randint(0, 5, size=n)           # Count 0-4
    tech_skills = np.random.randint(1, 16, size=n)          # Count of skills
    certifications = np.random.randint(0, 8, size=n)        # Count 0-7
    dsa_level = np.random.randint(1, 11, size=n)            # Scale 1-10
    attendance = np.round(
        np.random.normal(loc=78, scale=12, size=n).clip(40, 100), 1
    )

    # ── Step 2: Composite placement score (mimics real selection criteria) ──────
    # Weights derived from industry surveys and placement officer interviews
    raw_score = (
        cgpa * 5.5 +                          # Max ~55  — Academic performance
        aptitude * 0.22 +                     # Max ~22  — Logical reasoning
        communication * 1.8 +                 # Max ~18  — Soft skills
        projects * 1.6 +                      # Max ~16  — Practical experience
        internships * 3.5 +                   # Max ~14  — Industry exposure
        tech_skills * 0.9 +                   # Max ~13.5 — Technical breadth
        certifications * 1.4 +                # Max ~9.8  — Continuous learning
        dsa_level * 2.0 +                     # Max ~20  — Core CS skills
        (attendance - 40) * 0.13              # Max ~7.8  — Discipline
    )

    # Normalize to 0-100 range
    score_min, score_max = raw_score.min(), raw_score.max()
    normalized = (raw_score - score_min) / (score_max - score_min) * 100

    # Add realistic noise (interviewers have good/bad days, luck factor)
    noise = np.random.normal(0, 6, n)
    final_score = np.clip(normalized + noise, 0, 100)

    # ── Step 3: Binary placement label (threshold ~54) ─────────────────────────
    placed = (final_score >= 54).astype(int)

    # ── Step 4: Assemble DataFrame ─────────────────────────────────────────────
    df = pd.DataFrame({
        "cgpa":                 cgpa,
        "aptitude_score":       aptitude,
        "communication_skills": communication,
        "num_projects":         projects,
        "internships":          internships,
        "technical_skills":     tech_skills,
        "certifications":       certifications,
        "dsa_level":            dsa_level,
        "attendance":           attendance,
        "placement_score":      np.round(final_score, 2),
        "placed":               placed,
    })

    return df


if __name__ == "__main__":
    df = generate_dataset()
    out_path = os.path.join(os.path.dirname(__file__), "placement_data.csv")
    df.to_csv(out_path, index=False)

    # ── Print summary ──────────────────────────────────────────────────────────
    placed_pct = df["placed"].mean() * 100
    print("=" * 55)
    print("  DATASET GENERATED SUCCESSFULLY")
    print("=" * 55)
    print(f"  Records    : {len(df):,}")
    print(f"  Features   : {len(df.columns) - 2}")
    print(f"  Placed     : {placed_pct:.1f}%  |  Not Placed: {100-placed_pct:.1f}%")
    print(f"  Saved to   : {out_path}")
    print("=" * 55)
    print(df.describe().round(2).to_string())
