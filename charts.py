"""
utils/charts.py
===============
All Plotly chart helpers. Every function returns a go.Figure
with the shared dark theme applied — consistent across all pages.

Import: from utils.charts import gauge, radar, feat_importance, ...
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ── Shared dark theme tokens ───────────────────────────────────────────────────
_BG       = "#080C14"
_SURFACE  = "#0D1424"
_CARD     = "#0F1829"
_BORDER   = "#1E3A5F"
_TEXT     = "#CDD6F4"
_MUTED    = "#475569"
_ACCENT   = "#3B82F6"
_GREEN    = "#10B981"
_ORANGE   = "#F59E0B"
_RED      = "#EF4444"
_PURPLE   = "#A78BFA"
_PINK     = "#EC4899"
_CYAN     = "#06B6D4"

_LAYOUT = dict(
    paper_bgcolor = _BG,
    plot_bgcolor  = _CARD,
    font          = dict(family="Outfit, sans-serif", color=_TEXT, size=12),
    margin        = dict(l=20, r=20, t=44, b=20),
    hoverlabel    = dict(
        bgcolor   = _SURFACE,
        bordercolor=_BORDER,
        font_color =_TEXT,
        font_family="Outfit, sans-serif",
    ),
)

_AXIS_STYLE = dict(
    gridcolor   = _BORDER,
    linecolor   = _BORDER,
    tickcolor   = _MUTED,
    tickfont    = dict(color=_MUTED, size=11),
    zerolinecolor=_BORDER,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  1. PROBABILITY GAUGE
# ═══════════════════════════════════════════════════════════════════════════════

def gauge(probability: float, label: str) -> go.Figure:
    """Animated radial gauge showing placement probability."""
    color_map = {"High": _GREEN, "Medium": _ORANGE, "Low": _RED}
    color = color_map.get(label, _ACCENT)

    fig = go.Figure(go.Indicator(
        mode  = "gauge+number+delta",
        value = probability,
        delta = {
            "reference": 50,
            "increasing": {"color": _GREEN},
            "decreasing": {"color": _RED},
            "font": {"size": 14},
        },
        number = {
            "suffix": "%",
            "font": {"size": 52, "color": color, "family": "JetBrains Mono, monospace"},
        },
        gauge = {
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": _MUTED,
                "tickfont": {"size": 10, "color": _MUTED},
                "nticks": 6,
            },
            "bar":      {"color": color, "thickness": 0.22},
            "bgcolor":  _CARD,
            "borderwidth": 0,
            "steps": [
                {"range": [0,  45], "color": "#1A0A0A"},
                {"range": [45, 70], "color": "#1A1500"},
                {"range": [70,100], "color": "#001A0D"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.88,
                "value": probability,
            },
        },
        title = {
            "text": f"Placement Probability<br><b style='color:{color}'>{label} Chance</b>",
            "font": {"size": 14, "color": _TEXT},
        },
    ))
    fig.update_layout(**_LAYOUT, height=310)
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  2. SKILL RADAR
# ═══════════════════════════════════════════════════════════════════════════════

def radar(student: dict) -> go.Figure:
    """Spider/radar chart comparing student vs benchmark."""
    cats   = ["CGPA", "Aptitude", "Communication", "Projects",
              "Internships", "Tech Skills", "Certifications", "DSA", "Attendance"]
    keys   = ["cgpa", "aptitude_score", "communication_skills", "num_projects",
              "internships", "technical_skills", "certifications", "dsa_level", "attendance"]
    maxes  = [10, 100, 10, 10, 4, 15, 7, 10, 100]
    bench  = [8.5, 75, 7.5, 5, 2, 9, 3, 7.5, 85]   # industry benchmark (same scale)

    student_norm = [min(student.get(k, 0) / m * 10, 10) for k, m in zip(keys, maxes)]
    bench_norm   = [min(b / m * 10, 10)                  for b, m in zip(bench, maxes)]

    # Close the polygon
    c_full = cats + [cats[0]]
    s_full = student_norm + [student_norm[0]]
    b_full = bench_norm   + [bench_norm[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=b_full, theta=c_full, fill="toself", name="Industry Benchmark",
        line=dict(color=_MUTED, width=1.5, dash="dot"),
        fillcolor="rgba(71,85,105,0.08)",
        hovertemplate="<b>%{theta}</b><br>Benchmark: %{r:.1f}/10<extra></extra>",
    ))
    fig.add_trace(go.Scatterpolar(
        r=s_full, theta=c_full, fill="toself", name="Your Profile",
        line=dict(color=_ACCENT, width=2.5),
        fillcolor="rgba(59,130,246,0.18)",
        marker=dict(size=6, color=_ACCENT),
        hovertemplate="<b>%{theta}</b><br>Score: %{r:.1f}/10<extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT,
        polar=dict(
            bgcolor=_CARD,
            radialaxis=dict(
                visible=True, range=[0, 10],
                color=_MUTED, gridcolor=_BORDER,
                tickfont=dict(size=9, color=_MUTED),
            ),
            angularaxis=dict(color=_TEXT, gridcolor=_BORDER,
                             tickfont=dict(size=10, color=_TEXT)),
        ),
        legend=dict(
            bgcolor=_SURFACE, bordercolor=_BORDER, borderwidth=1,
            font=dict(color=_TEXT, size=11), x=0.0, y=1.1, orientation="h",
        ),
        title=dict(text="Skill Profile vs Industry Benchmark",
                   font=dict(size=14, color=_TEXT), x=0.5, xanchor="center"),
        height=420,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  3. FEATURE IMPORTANCE
# ═══════════════════════════════════════════════════════════════════════════════

def feat_importance(fi_dict: dict) -> go.Figure:
    """Horizontal bar chart of Random Forest feature importances."""
    df = pd.DataFrame(fi_dict).sort_values("importance")
    df["feature_clean"] = df["feature"].str.replace("_", " ").str.title()

    # Color gradient: low → high importance
    norm = (df["importance"] - df["importance"].min()) / \
           (df["importance"].max() - df["importance"].min() + 1e-9)
    colors_list = [
        f"rgba(59,130,246,{0.35 + 0.65*v:.2f})" for v in norm
    ]

    fig = go.Figure(go.Bar(
        x            = df["importance"],
        y            = df["feature_clean"],
        orientation  = "h",
        marker_color = colors_list,
        marker_line  = dict(width=0),
        text         = [f"{v:.3f}" for v in df["importance"]],
        textposition = "outside",
        textfont     = dict(color=_TEXT, size=10),
        hovertemplate= "<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT,
        title=dict(text="Feature Importance (Random Forest)",
                   font=dict(size=14, color=_TEXT), x=0, xanchor="left"),
        xaxis=dict(title="Importance Score", **_AXIS_STYLE),
        yaxis=dict(color=_TEXT, gridcolor="rgba(0,0,0,0)",
                   tickfont=dict(size=11, color=_TEXT)),
        height=370,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  4. CONFUSION MATRIX HEATMAP
# ═══════════════════════════════════════════════════════════════════════════════

def confusion_heatmap(cm: list) -> go.Figure:
    """Styled confusion matrix heatmap."""
    labels   = ["Not Placed", "Placed"]
    cm_arr   = [[int(v) for v in row] for row in cm]
    total    = sum(sum(r) for r in cm_arr)
    pct      = [[f"{v/total*100:.1f}%" for v in row] for row in cm_arr]
    text_2d  = [[f"{cm_arr[i][j]}<br>{pct[i][j]}"
                 for j in range(2)] for i in range(2)]

    fig = go.Figure(go.Heatmap(
        z           = cm_arr,
        x           = [f"Pred: {l}" for l in labels],
        y           = [f"Actual: {l}" for l in labels],
        text        = text_2d,
        texttemplate= "%{text}",
        textfont    = dict(size=14, color=_TEXT),
        colorscale  = [[0.0, _CARD], [0.5, "#0D2B5E"], [1.0, _ACCENT]],
        showscale   = False,
        hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT,
        title=dict(text="Confusion Matrix",
                   font=dict(size=14, color=_TEXT), x=0, xanchor="left"),
        xaxis=dict(color=_TEXT, gridcolor="rgba(0,0,0,0)", tickfont=dict(color=_TEXT)),
        yaxis=dict(color=_TEXT, gridcolor="rgba(0,0,0,0)", tickfont=dict(color=_TEXT)),
        height=320,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  5. CGPA vs PLACEMENT RATE  (bar)
# ═══════════════════════════════════════════════════════════════════════════════

def cgpa_placement_bar(df: pd.DataFrame) -> go.Figure:
    """Placement rate by CGPA range."""
    bins   = [4, 5.5, 6.5, 7.5, 8.5, 10.1]
    labels = ["4–5.5", "5.5–6.5", "6.5–7.5", "7.5–8.5", "8.5–10"]
    df2    = df.copy()
    df2["cgpa_bin"] = pd.cut(df2["cgpa"], bins=bins, labels=labels, right=False)
    rate   = df2.groupby("cgpa_bin")["placed"].mean().reset_index()
    rate["pct"] = (rate["placed"] * 100).round(1)

    palette = [_RED, _ORANGE, _ACCENT, _GREEN, "#00FFC6"]
    fig = go.Figure(go.Bar(
        x            = rate["cgpa_bin"].astype(str),
        y            = rate["pct"],
        marker_color = palette[:len(rate)],
        marker_line  = dict(width=0),
        text         = [f"{v:.1f}%" for v in rate["pct"]],
        textposition = "outside",
        textfont     = dict(color=_TEXT, size=11),
        hovertemplate= "CGPA %{x}<br>Placement Rate: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT,
        title=dict(text="Placement Rate by CGPA Range",
                   font=dict(size=14, color=_TEXT), x=0, xanchor="left"),
        xaxis=dict(title="CGPA Range", **_AXIS_STYLE),
        yaxis=dict(title="Placement Rate (%)", range=[0, 115], **_AXIS_STYLE),
        height=350,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  6. INTERNSHIPS vs PLACEMENT RATE  (line + area)
# ═══════════════════════════════════════════════════════════════════════════════

def internship_trend(df: pd.DataFrame) -> go.Figure:
    """Placement rate as function of internship count."""
    rate = df.groupby("internships")["placed"].mean().reset_index()
    rate["pct"] = (rate["placed"] * 100).round(1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rate["internships"], y=rate["pct"],
        mode="lines+markers",
        line=dict(color=_ACCENT, width=3),
        marker=dict(size=9, color=_GREEN, line=dict(color=_ACCENT, width=2)),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.10)",
        hovertemplate="Internships: %{x}<br>Placement Rate: %{y:.1f}%<extra></extra>",
        name="Placement Rate",
    ))
    fig.update_layout(
        **_LAYOUT,
        title=dict(text="Placement Rate vs Internship Count",
                   font=dict(size=14, color=_TEXT), x=0, xanchor="left"),
        xaxis=dict(title="Number of Internships", tickmode="linear", dtick=1, **_AXIS_STYLE),
        yaxis=dict(title="Placement Rate (%)", **_AXIS_STYLE),
        height=310,
        showlegend=False,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  7. DSA vs PLACEMENT RATE  (line)
# ═══════════════════════════════════════════════════════════════════════════════

def dsa_trend(df: pd.DataFrame) -> go.Figure:
    rate = df.groupby("dsa_level")["placed"].mean().reset_index()
    rate["pct"] = (rate["placed"] * 100).round(1)

    fig = go.Figure(go.Scatter(
        x=rate["dsa_level"], y=rate["pct"],
        mode="lines+markers",
        line=dict(color=_PURPLE, width=3),
        marker=dict(size=9, color=_PINK, line=dict(color=_PURPLE, width=2)),
        fill="tozeroy", fillcolor="rgba(167,139,250,0.10)",
        hovertemplate="DSA Level: %{x}<br>Placement Rate: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT,
        title=dict(text="Placement Rate vs DSA Level",
                   font=dict(size=14, color=_TEXT), x=0, xanchor="left"),
        xaxis=dict(title="DSA Level (1–10)", tickmode="linear", dtick=1, **_AXIS_STYLE),
        yaxis=dict(title="Placement Rate (%)", **_AXIS_STYLE),
        height=310,
        showlegend=False,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  8. CGPA BOX PLOT  (Placed vs Not Placed)
# ═══════════════════════════════════════════════════════════════════════════════

def cgpa_boxplot(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for val, name, color in [(1, "Placed", _GREEN), (0, "Not Placed", _RED)]:
        subset = df[df["placed"] == val]
        fig.add_trace(go.Box(
            y=subset["cgpa"], name=name,
            marker_color=color,
            line_color=color,
            fillcolor="rgba(16,185,129,0.15)",
            boxmean=True,
            hovertemplate=f"<b>{name}</b><br>CGPA: %{{y:.2f}}<extra></extra>",
        ))
    fig.update_layout(
        **_LAYOUT,
        title=dict(text="CGPA Distribution: Placed vs Not Placed",
                   font=dict(size=14, color=_TEXT), x=0, xanchor="left"),
        yaxis=dict(title="CGPA", **_AXIS_STYLE),
        xaxis=dict(color=_TEXT, **_AXIS_STYLE),
        legend=dict(bgcolor=_SURFACE, bordercolor=_BORDER, borderwidth=1,
                    font=dict(color=_TEXT)),
        height=340,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  9. IMPROVEMENT IMPACT FORECAST  (combo bar + line)
# ═══════════════════════════════════════════════════════════════════════════════

def improvement_forecast(suggestions: list, current_prob: float) -> go.Figure:
    """Bar for per-tip gain + line for cumulative probability."""
    if not suggestions:
        return go.Figure()

    top     = suggestions[:6]
    labels  = [s["tip"].split("—")[0].split("–")[0].strip()[:28] for s in top]
    gains   = [s["gain"] for s in top]
    cumul   = []
    running = current_prob
    for g in gains:
        running = min(running + g, 99)
        cumul.append(round(running, 1))

    palette = [_ACCENT, _GREEN, _PURPLE, _ORANGE, _PINK, _CYAN]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=gains,
        name="Expected Gain (%)",
        marker_color=palette[:len(top)],
        marker_line=dict(width=0),
        text=[f"+{g}%" for g in gains],
        textposition="outside",
        textfont=dict(color=_TEXT, size=10),
        yaxis="y",
        hovertemplate="<b>%{x}</b><br>Gain: +%{y}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=cumul,
        name="Cumulative Probability (%)",
        mode="lines+markers",
        line=dict(color=_GREEN, width=2.5),
        marker=dict(size=8, color=_GREEN),
        yaxis="y2",
        hovertemplate="Cumulative: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
    **_LAYOUT,

    title=dict(
        text="Improvement Impact Forecast",
        font=dict(size=14, color=_TEXT),
        x=0,
        xanchor="left"
    ),

    yaxis=dict(
        title="Gain (%)",
        **_AXIS_STYLE
    ),

    yaxis2=dict(
        title="Cumulative Prob. (%)",
        overlaying="y",
        side="right",
        color=_GREEN,
        gridcolor="rgba(0,0,0,0)",
        tickfont=dict(color=_GREEN, size=10)
    ),

    xaxis=dict(
        **_AXIS_STYLE,
        tickangle=-18
    ),

    legend=dict(
        bgcolor=_SURFACE,
        bordercolor=_BORDER,
        borderwidth=1,
        font=dict(color=_TEXT, size=11),
        orientation="h",
        x=0,
        y=1.12
    ),

    barmode="group",
    height=380,
)
    return fig
