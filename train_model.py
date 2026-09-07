"""
model/train_model.py
====================
Trains a Random Forest Classifier on the student placement dataset.

Pipeline:
  1. Load & explore data
  2. Split into train/test (80/20, stratified)
  3. Scale features with StandardScaler
  4. Train Random Forest (200 trees)
  5. Evaluate: Accuracy, ROC-AUC, Confusion Matrix, Cross-Val
  6. Save model + scaler + feature list + metrics as .pkl files

Run once: python model/train_model.py
"""

import os, pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, roc_auc_score, f1_score
)

# ─── Paths ─────────────────────────────────────────────────────────────────────
ROOT      = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT, "dataset", "placement_data.csv")
MODEL_DIR = os.path.dirname(__file__)

# ─── Feature columns (order matters — must match app input order) ──────────────
FEATURE_COLS = [
    "cgpa",
    "aptitude_score",
    "communication_skills",
    "num_projects",
    "internships",
    "technical_skills",
    "certifications",
    "dsa_level",
    "attendance",
]
TARGET_COL = "placed"


def train_and_save():
    # ── Load data ──────────────────────────────────────────────────────────────
    print("\n📂  Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    print(f"    Shape   : {df.shape}")
    print(f"    Placed  : {df[TARGET_COL].mean()*100:.1f}%")

    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values

    # ── Train/Test split ───────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y   # keeps class balance in both splits
    )
    print(f"\n✂️   Train: {len(X_train)} rows | Test: {len(X_test)} rows")

    # ── Preprocessing: StandardScaler ─────────────────────────────────────────
    # Scales each feature to mean=0, std=1
    # Fit ONLY on training data to prevent data leakage
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    # ── Train Random Forest ────────────────────────────────────────────────────
    print("\n🌲  Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=200,          # 200 decision trees
        max_depth=12,              # Max depth per tree (controls overfitting)
        min_samples_split=5,       # Min samples required to split a node
        min_samples_leaf=2,        # Min samples in a leaf node
        max_features="sqrt",       # Use sqrt(n_features) at each split
        class_weight="balanced",   # Handle any minor class imbalance
        random_state=42,
        n_jobs=-1,                 # Use all CPU cores
    )
    model.fit(X_train_sc, y_train)

    # ── Evaluation ─────────────────────────────────────────────────────────────
    y_pred  = model.predict(X_test_sc)
    y_prob  = model.predict_proba(X_test_sc)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    auc      = roc_auc_score(y_test, y_prob)
    f1       = f1_score(y_test, y_pred)
    cm       = confusion_matrix(y_test, y_pred).tolist()

    # 5-Fold Stratified Cross-Validation on full dataset
    cv_scores = cross_val_score(
        model,
        scaler.transform(X),
        y,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring="accuracy",
        n_jobs=-1,
    )

    print(f"\n{'='*55}")
    print(f"  MODEL EVALUATION RESULTS")
    print(f"{'='*55}")
    print(f"  Accuracy       : {accuracy*100:.2f}%")
    print(f"  ROC-AUC        : {auc:.4f}")
    print(f"  F1-Score       : {f1:.4f}")
    print(f"  CV Mean Acc    : {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Not Placed', 'Placed'])}")

    # Feature Importance
    importance_df = pd.DataFrame({
        "feature":    FEATURE_COLS,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)
    print("🔑  Feature Importances:")
    print(importance_df.to_string(index=False))

    # ── Save artifacts ─────────────────────────────────────────────────────────
    metrics = {
        "accuracy":          round(accuracy * 100, 2),
        "roc_auc":           round(auc, 4),
        "f1_score":          round(f1, 4),
        "cv_mean":           round(cv_scores.mean() * 100, 2),
        "cv_std":            round(cv_scores.std() * 100, 2),
        "cv_scores":         cv_scores.tolist(),
        "confusion_matrix":  cm,
        "feature_importance": importance_df.to_dict(orient="list"),
        "n_train":           len(X_train),
        "n_test":            len(X_test),
        "total_samples":     len(X),
        "placed_pct":        round(df[TARGET_COL].mean() * 100, 1),
    }

    artifacts = {
        "rf_model.pkl":   model,
        "scaler.pkl":     scaler,
        "features.pkl":   FEATURE_COLS,
        "metrics.pkl":    metrics,
    }
    for fname, obj in artifacts.items():
        path = os.path.join(MODEL_DIR, fname)
        with open(path, "wb") as f:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"\n✅  All artifacts saved to: {MODEL_DIR}/")
    for fname in artifacts:
        size = os.path.getsize(os.path.join(MODEL_DIR, fname))
        print(f"    {fname:<22} {size/1024:.1f} KB")


if __name__ == "__main__":
    train_and_save()
