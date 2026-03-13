"""
pages/1_Overview.py  —  VoltGuard Dashboard Overview
Practical, hackathon-ready with real data insights.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.data_loader import load_raw

st.set_page_config(page_title="VoltGuard · Overview", page_icon="⬡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Mono','Courier New',monospace!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:1.4rem;padding-bottom:2rem}
[data-testid="stMetric"]{background:rgba(255,255,255,0.03);border:1px solid rgba(0,229,255,0.12);border-radius:12px;padding:16px 20px!important}
[data-testid="stMetricValue"]{font-family:'Syne',sans-serif!important;font-weight:800!important;font-size:1.75rem!important;color:#e8f4f8!important}
[data-testid="stMetricLabel"]{font-size:10px!important;letter-spacing:0.1em;color:#5a8a9f!important;text-transform:uppercase}
[data-testid="stMetricDelta"]{font-size:11px!important}
hr{border-color:rgba(0,229,255,0.08)!important}
.vg-section{font-size:10px;letter-spacing:0.14em;color:#2a4a5e;font-weight:600;text-transform:uppercase;margin-bottom:10px;padding-bottom:5px;border-bottom:1px solid rgba(0,229,255,0.07)}
.vg-info{background:rgba(0,229,255,0.04);border:1px solid rgba(0,229,255,0.1);border-radius:10px;padding:14px 18px;font-size:12px;color:#4a8a9e;margin-top:8px}
[data-testid="stSidebar"]{background:#0a1a26!important;border-right:1px solid rgba(0,229,255,0.1)}
[data-testid="stSidebar"] .stRadio label{font-size:13px!important}
</style>
""", unsafe_allow_html=True)

C = {
    "bg": "#050d14", "paper": "#0a1a26",
    "grid": "rgba(0,229,255,0.07)", "text": "#e8f4f8",
    "muted": "#3a6a7e", "cyan": "#00e5ff",
    "red": "#ff3b3b", "orange": "#ffa500", "green": "#6dffb3",
}
_L = dict(
    paper_bgcolor=C["paper"], plot_bgcolor=C["bg"],
    font=dict(family="DM Mono, monospace", color=C["text"], size=11),
    margin=dict(l=16, r=16, t=28, b=16),
    xaxis=dict(gridcolor=C["grid"], zerolinecolor=C["grid"], color=C["muted"]),
    yaxis=dict(gridcolor=C["grid"], zerolinecolor=C["grid"], color=C["muted"]),
)

def assign_priority(score, p33, p67):
    if pd.isna(score): return "LOW"
    if score <= p33:   return "HIGH"
    if score <= p67:   return "MEDIUM"
    return "LOW"

def get_data(zone):
    df = load_raw(zone)
    if df.empty:
        return df, pd.DataFrame()
    df["datetime"] = pd.to_datetime(df["datetime"])
    anom = df[df["anomaly"] == -1].copy()
    if not anom.empty:
        p33 = anom["anomaly_score"].quantile(0.33)
        p67 = anom["anomaly_score"].quantile(0.67)
        anom["alert_priority"] = anom["anomaly_score"].apply(lambda s: assign_priority(s, p33, p67))
        df.loc[anom.index, "alert_priority"] = anom["alert_priority"]
    return df, anom

# ── Sidebar ───────────────────────────────────────────────────────────────────
ZONES = ["Industrial", "Rural", "Urban"]
zone  = st.session_state.get("zone", "Industrial")

with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:10px 0 20px;">
        <svg width="26" height="26" viewBox="0 0 28 28">
            <polygon points="14,2 26,8 26,20 14,26 2,20 2,8" fill="none" stroke="#00e5ff" stroke-width="1.5"/>
            <polygon points="14,7 21,11 21,17 14,21 7,17 7,11" fill="rgba(0,229,255,0.12)" stroke="#00e5ff" stroke-width="1"/>
            <circle cx="14" cy="14" r="3" fill="#00e5ff"/>
        </svg>
        <span style="font-family:'Syne',sans-serif;font-weight:800;font-size:18px;letter-spacing:-0.02em;">
            VOLT<span style="color:#00e5ff;">GUARD</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="vg-section">ZONE SELECT</div>', unsafe_allow_html=True)
    zone = st.radio("zone", ZONES, index=ZONES.index(zone), label_visibility="collapsed")
    st.session_state["zone"] = zone
    st.divider()
    st.markdown('<div style="font-size:10px;color:#1a3a4e;letter-spacing:0.08em;">Isolation Forest · Q-Learning RL<br>VoltGuard v2.1</div>', unsafe_allow_html=True)

# ── Load ──────────────────────────────────────────────────────────────────────
df, anom = get_data(zone)

total         = len(df)
n_anom        = len(anom)
detection_rate= round(n_anom / total * 100, 1) if total else 0
high_c  = int((anom["alert_priority"] == "HIGH").sum())   if not anom.empty else 0
med_c   = int((anom["alert_priority"] == "MEDIUM").sum()) if not anom.empty else 0
low_c   = int((anom["alert_priority"] == "LOW").sum())    if not anom.empty else 0
total_supplied = df["energy_supplied_kwh"].sum()
total_billed   = df["energy_billed_kwh"].sum()
energy_lost    = round(total_supplied - total_billed, 1)
avg_loss_ratio = round(df["loss_ratio"].mean() * 100, 2)
anom_loss_ratio= round(anom["loss_ratio"].mean() * 100, 2) if not anom.empty else 0
date_min = df["datetime"].min().strftime("%b %Y") if not df.empty else "—"
date_max = df["datetime"].max().strftime("%b %Y") if not df.empty else "—"

month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    f'<h2 style="font-family:Syne,sans-serif;font-weight:800;font-size:1.5rem;margin-bottom:2px">'
    f'{zone} <span style="color:#00e5ff">Zone Overview</span></h2>'
    f'<p style="color:#3a6a7e;font-size:12px;margin-bottom:14px;letter-spacing:0.04em">'
    f'Isolation Forest · Q-Learning RL &nbsp;·&nbsp; {date_min} → {date_max}</p>',
    unsafe_allow_html=True,
)

# ── Row 1: KPI cards ──────────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("Total Records",     f'{total:,}')
c2.metric("Anomalies",         f'{n_anom:,}')
c3.metric("HIGH Priority",     f'{high_c:,}')
c4.metric("Avg Loss Ratio",    f'{avg_loss_ratio}%')
c5.metric("Energy Lost",       f'{energy_lost:,} kWh')
c6.metric("Total Supplied",    f'{int(total_supplied):,} kWh')

st.divider()

# ── Row 2: Donut + Monthly bar ────────────────────────────────────────────────
col_a, col_b = st.columns([1, 2.2])

with col_a:
    st.markdown('<div class="vg-section">ALERT PRIORITY SPLIT</div>', unsafe_allow_html=True)
    fig_d = go.Figure(go.Pie(
        labels=["HIGH","MEDIUM","LOW"], values=[high_c,med_c,low_c], hole=0.62,
        marker=dict(colors=[C["red"],C["orange"],C["cyan"]], line=dict(color=C["bg"],width=3)),
        textinfo="label+percent", textfont=dict(size=11, family="DM Mono, monospace"),
        hovertemplate="<b>%{label}</b><br>%{value} alerts · %{percent}<extra></extra>",
    ))
    fig_d.update_layout(
        **{k:v for k,v in _L.items() if k!="margin"},
        showlegend=False, height=260, margin=dict(l=8,r=8,t=8,b=8),
        annotations=[dict(text=f'<b>{n_anom:,}</b><br><span style="font-size:10px">anomalies</span>',
                         x=0.5,y=0.5,showarrow=False,
                         font=dict(size=16,color=C["text"],family="DM Mono, monospace"))],
    )
    st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar":False})

with col_b:
    st.markdown('<div class="vg-section">MONTHLY ENERGY LOSS (kWh) + ANOMALY COUNT</div>', unsafe_allow_html=True)
    monthly = df.groupby("month").agg(
        total_loss=("loss_kwh","sum"),
        anomaly_count=("anomaly", lambda x: (x==-1).sum())
    ).reset_index()
    monthly["month_name"] = monthly["month"].map(month_names)
    q75 = monthly["total_loss"].quantile(0.75)
    q50 = monthly["total_loss"].quantile(0.50)

    fig_m = go.Figure()
    fig_m.add_trace(go.Bar(
        x=monthly["month_name"], y=monthly["total_loss"], name="Loss kWh",
        marker_color=[C["red"] if v>q75 else C["orange"] if v>q50 else C["cyan"]
                      for v in monthly["total_loss"]],
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Loss: %{y:.1f} kWh<extra></extra>",
    ))
    fig_m.add_trace(go.Scatter(
        x=monthly["month_name"], y=monthly["anomaly_count"],
        name="Anomalies", yaxis="y2",
        line=dict(color="rgba(255,165,0,0.8)",width=2,dash="dot"),
        mode="lines+markers", marker=dict(size=5),
        hovertemplate="Anomalies: %{y}<extra></extra>",
    ))
    fig_m.update_layout(
        **{k:v for k,v in _L.items() if k not in ("xaxis","yaxis")}, height=260, bargap=0.2,
        yaxis=dict(**_L["yaxis"], title="Loss kWh"),
        yaxis2=dict(overlaying="y", side="right", title="Anomaly Count",
                    color=C["muted"], gridcolor="rgba(0,0,0,0)", zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0.3)", font=dict(size=10), x=0.01, y=0.99),
    )
    st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar":False})

# ── Row 3: Loss Distribution + Score Timeline ────────────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.markdown('<div class="vg-section">LOSS RATIO DISTRIBUTION — NORMAL vs ANOMALY</div>', unsafe_allow_html=True)
    normal_df = df[df["anomaly"] == 1]
    fig_hist = go.Figure()
    if not normal_df.empty:
        fig_hist.add_trace(go.Histogram(
            x=normal_df["loss_ratio"], nbinsx=40, name="Normal",
            marker_color="rgba(0,229,255,0.4)", marker_line_color=C["bg"],
            marker_line_width=1, opacity=0.75,
            hovertemplate="Loss: %{x:.3f}<br>Count: %{y}<extra></extra>",
        ))
    if not anom.empty:
        fig_hist.add_trace(go.Histogram(
            x=anom["loss_ratio"], nbinsx=40, name="Anomaly",
            marker_color="rgba(255,59,59,0.6)", marker_line_color=C["bg"],
            marker_line_width=1, opacity=0.75,
            hovertemplate="Loss: %{x:.3f}<br>Count: %{y}<extra></extra>",
        ))
    fig_hist.update_layout(
        **{k:v for k,v in _L.items() if k not in ("xaxis","yaxis")}, barmode="overlay", height=260,
        xaxis=dict(**_L["xaxis"], title="Loss Ratio"),
        yaxis=dict(**_L["yaxis"], title="Count"),
        legend=dict(bgcolor="rgba(0,0,0,0.3)", font=dict(size=10)),
    )
    st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar":False})

with col_d:
    st.markdown('<div class="vg-section">ANOMALY SCORE TIMELINE — PRIORITY COLOURED</div>', unsafe_allow_html=True)
    if not anom.empty:
        fig_tl = go.Figure()
        for pri, color in [("HIGH",C["red"]),("MEDIUM",C["orange"]),("LOW",C["cyan"])]:
            sub = anom[anom["alert_priority"]==pri]
            if sub.empty: continue
            fig_tl.add_trace(go.Scatter(
                x=sub["datetime"], y=sub["anomaly_score"],
                mode="markers", name=pri,
                marker=dict(color=color, size=5, opacity=0.75,
                            line=dict(color=C["bg"], width=0.5)),
                hovertemplate="%{x|%Y-%m-%d %H:%M}<br>Score: %{y:.4f}<extra></extra>",
            ))
        fig_tl.add_hline(y=anom["anomaly_score"].mean(), line_dash="dot",
                         line_color="rgba(255,165,0,0.5)",
                         annotation_text="mean score",
                         annotation_font=dict(color="rgba(255,165,0,0.7)",size=10))
        fig_tl.update_layout(
            **{k:v for k,v in _L.items() if k not in ("xaxis","yaxis")}, height=260,
            xaxis=dict(**_L["xaxis"], title=""),
            yaxis=dict(**_L["yaxis"], title="Anomaly Score"),
            legend=dict(bgcolor="rgba(0,0,0,0.3)", font=dict(size=10)),
            hovermode="closest",
        )
        st.plotly_chart(fig_tl, use_container_width=True, config={"displayModeBar":False})


