"""
utils/charts.py
───────────────
All Plotly figures used across the VoltGuard dashboard.
Each function returns a go.Figure ready for st.plotly_chart().
"""
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── shared colour palette ──────────────────────────────────────────────────
C = {
    "bg":     "#050d14",
    "paper":  "#0a1a26",
    "grid":   "rgba(0,229,255,0.07)",
    "text":   "#e8f4f8",
    "muted":  "#3a6a7e",
    "cyan":   "#00e5ff",
    "red":    "#ff3b3b",
    "orange": "#ffa500",
    "green":  "#6dffb3",
}

PRIORITY_COLORS = {"HIGH": C["red"], "MEDIUM": C["orange"], "LOW": C["cyan"]}

_LAYOUT = dict(
    paper_bgcolor=C["paper"],
    plot_bgcolor =C["bg"],
    font         =dict(family="DM Mono, monospace", color=C["text"], size=11),
    margin       =dict(l=16, r=16, t=32, b=16),
    xaxis        =dict(gridcolor=C["grid"], zerolinecolor=C["grid"], color=C["muted"]),
    yaxis        =dict(gridcolor=C["grid"], zerolinecolor=C["grid"], color=C["muted"]),
)


# ─────────────────────────────────────────────────────────────────────────────
def donut_chart(high: int, medium: int, low: int) -> go.Figure:
    """Alert distribution donut."""
    labels = ["HIGH", "MEDIUM", "LOW"]
    values = [high, medium, low]
    colors = [C["red"], C["orange"], C["cyan"]]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.65,
        marker=dict(colors=colors, line=dict(color=C["bg"], width=3)),
        textinfo="label+percent",
        textfont=dict(size=11, family="DM Mono, monospace"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
    ))
    total = high + medium + low
    fig.update_layout(
        showlegend=False,
        annotations=[dict(
            text=f"<b>{total}</b><br><span style='font-size:10px'>alerts</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color=C["text"], family="DM Mono, monospace"),
        )],
        height=280,
        margin=dict(l=8, r=8, t=8, b=8),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
def sparkline_chart(df: pd.DataFrame, zone: str) -> go.Figure:
    """
    48-hour loss_ratio trend line for the zone.
    df must have columns: datetime, loss_ratio
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**_LAYOUT, height=200,
            title=dict(text="No data available", font=dict(color=C["muted"])))
        return fig

    fig = go.Figure()

    # Shade area under line
    fig.add_trace(go.Scatter(
        x=df["datetime"], y=df["loss_ratio"],
        fill="tozeroy",
        fillcolor="rgba(0,229,255,0.06)",
        line=dict(color=C["cyan"], width=2),
        mode="lines",
        name="loss_ratio",
        hovertemplate="%{x|%Y-%m-%d %H:%M}<br>Loss Ratio: <b>%{y:.3f}</b><extra></extra>",
    ))

    # Danger threshold line at 0.3
    fig.add_hline(
        y=0.3, line_dash="dot",
        line_color="rgba(255,59,59,0.4)",
        annotation_text="threshold 0.30",
        annotation_font=dict(color="rgba(255,59,59,0.6)", size=10),
    )

    fig.update_layout(
        height=220,
        title=dict(
            text=f"{zone} — Loss Ratio (last 48h)",
            font=dict(size=12, color=C["muted"]),
            x=0,
        ),
        xaxis=dict(**_LAYOUT["xaxis"], title=""),
        yaxis=dict(**_LAYOUT["yaxis"], title="loss ratio", tickformat=".2f"),
        hovermode="x unified",
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
def hourly_bar_chart(df: pd.DataFrame) -> go.Figure:
    """
    Average loss_ratio by hour-of-day (0–23).
    df must have columns: hour, avg_loss_ratio
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**_LAYOUT, height=200)
        return fig

    colors = [
        C["red"] if v > 0.3 else C["orange"] if v > 0.2 else C["cyan"]
        for v in df["avg_loss_ratio"]
    ]

    fig = go.Figure(go.Bar(
        x=df["hour"], y=df["avg_loss_ratio"],
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="Hour %{x}:00<br>Avg Loss: <b>%{y:.3f}</b><extra></extra>",
    ))
    fig.update_layout(
        height=200,
        title=dict(text="Avg Loss Ratio by Hour of Day", font=dict(size=12, color=C["muted"]), x=0),
        xaxis=dict(**_LAYOUT["xaxis"], title="hour", tickvals=list(range(0, 24, 3))),
        yaxis=dict(**_LAYOUT["yaxis"], title="avg loss ratio"),
        bargap=0.15,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
def priority_timeline(df: pd.DataFrame) -> go.Figure:
    """
    Scatter plot of anomaly_score over time, coloured by priority.
    df = anomalies dataframe with datetime, anomaly_score, alert_priority, alert_id
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**_LAYOUT, height=260,
            title=dict(text="No anomalies to display", font=dict(color=C["muted"])))
        return fig

    fig = go.Figure()
    for priority, color in PRIORITY_COLORS.items():
        sub = df[df["alert_priority"] == priority]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["datetime"], y=sub["anomaly_score"],
            mode="markers",
            name=priority,
            marker=dict(color=color, size=7, opacity=0.8,
                        line=dict(color=C["bg"], width=1)),
            hovertemplate=(
                "<b>%{customdata}</b><br>"
                "%{x|%Y-%m-%d %H:%M}<br>"
                "Score: %{y:.4f}<extra></extra>"
            ),
            customdata=sub["alert_id"],
        ))

    fig.add_hline(y=0, line_dash="dash", line_color=C["muted"],
                  annotation_text="decision boundary", annotation_font=dict(color=C["muted"], size=10))

    fig.update_layout(
        height=260,
        title=dict(text="Anomaly Score Timeline", font=dict(size=12, color=C["muted"]), x=0),
        xaxis=dict(**_LAYOUT["xaxis"], title=""),
        yaxis=dict(**_LAYOUT["yaxis"], title="anomaly score"),
        legend=dict(bgcolor="rgba(0,0,0,0.3)", bordercolor=C["grid"],
                    borderwidth=1, font=dict(size=10)),
        hovermode="closest",
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
def loss_ratio_histogram(df: pd.DataFrame) -> go.Figure:
    """Distribution of loss_ratio across all anomaly records."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**_LAYOUT, height=220)
        return fig

    fig = go.Figure(go.Histogram(
        x=df["loss_ratio"], nbinsx=30,
        marker_color=C["cyan"],
        marker_line_color=C["bg"],
        marker_line_width=1,
        opacity=0.85,
        hovertemplate="Loss ratio: %{x:.3f}<br>Count: %{y}<extra></extra>",
    ))
    fig.update_layout(
        height=220,
        title=dict(text="Loss Ratio Distribution (anomalies only)", font=dict(size=12, color=C["muted"]), x=0),
        xaxis=dict(**_LAYOUT["xaxis"], title="loss_ratio"),
        yaxis=dict(**_LAYOUT["yaxis"], title="count"),
        bargap=0.05,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
def q_table_heatmap(q_table, severity_idx: int = 0) -> go.Figure:
    """
    Visualise Q-values for a given severity level.
    q_table shape: [severity(3), time(3), trend(3), action(3)]
    Shows: time_of_day vs loss_trend, with cell colour = max Q-value action.
    """
    if q_table is None:
        fig = go.Figure()
        fig.update_layout(**_LAYOUT, height=260,
            title=dict(text="Q-table not loaded", font=dict(color=C["muted"])))
        return fig

    q = np.array(q_table)
    # Slice at given severity: shape [time(3), trend(3), action(3)]
    slice_ = q[severity_idx]
    # Best action per (time, trend)
    best_action = np.argmax(slice_, axis=2)      # shape [3,3]
    best_q      = np.max(slice_, axis=2)         # shape [3,3]

    action_labels = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}
    text_matrix   = [[action_labels[v] for v in row] for row in best_action]

    time_labels  = ["Night (0–8)", "Day (8–18)", "Evening (18–24)"]
    trend_labels = ["Decreasing", "Stable", "Increasing"]

    fig = go.Figure(go.Heatmap(
        z=best_q,
        x=trend_labels,
        y=time_labels,
        text=text_matrix,
        texttemplate="%{text}",
        colorscale=[[0,"rgba(0,229,255,0.15)"], [0.5,"rgba(255,165,0,0.5)"], [1,"rgba(255,59,59,0.8)"]],
        showscale=True,
        hovertemplate="Time: %{y}<br>Trend: %{x}<br>Best Action: %{text}<br>Q-value: %{z:.3f}<extra></extra>",
        colorbar=dict(
            title="Q-value", tickfont=dict(color=C["muted"], size=10),
            titlefont=dict(color=C["muted"], size=10),
            bgcolor=C["paper"], bordercolor=C["grid"],
        ),
    ))

    severity_names = ["LOW", "MEDIUM", "HIGH"]
    fig.update_layout(
        height=260,
        title=dict(
            text=f"Q-Table — Severity: {severity_names[severity_idx]}",
            font=dict(size=12, color=C["muted"]), x=0,
        ),
        xaxis=dict(**_LAYOUT["xaxis"], title="Loss Trend"),
        yaxis=dict(**_LAYOUT["yaxis"], title="Time of Day"),
    )
    return fig
