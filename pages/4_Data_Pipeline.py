"""
pages/4_Data_Pipeline.py
─────────────────────────
Data Pipeline: end-to-end flow diagram, frontend + full
project directory trees, API endpoint reference.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

st.set_page_config(page_title="VoltGuard · Data Pipeline", page_icon="◇", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Mono','Courier New',monospace!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:1.6rem}
hr{border-color:rgba(0,229,255,0.1)!important}
.vg-section{font-size:10px;letter-spacing:0.14em;color:#2a4a5e;font-weight:600;text-transform:uppercase;margin-bottom:10px;padding-bottom:5px;border-bottom:1px solid rgba(0,229,255,0.07)}
.vg-code{background:rgba(0,0,0,0.35);border:1px solid rgba(0,229,255,0.08);border-radius:8px;padding:16px 20px;font-size:11px;color:#4a8a9e;white-space:pre;overflow-x:auto;line-height:1.9;font-family:'DM Mono',monospace}
.vg-info{background:rgba(0,229,255,0.04);border:1px solid rgba(0,229,255,0.1);border-radius:10px;padding:14px 18px;font-size:12px;color:#4a8a9e}
.step-card{background:rgba(255,255,255,0.02);border:1px solid rgba(0,229,255,0.08);border-radius:10px;padding:14px 18px;margin-bottom:10px}
[data-testid="stSidebar"]{background:#0a1a26!important;border-right:1px solid rgba(0,229,255,0.1)}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
ZONES = ["Industrial", "Rural", "Urban"]
zone  = st.session_state.get("zone", "Industrial")
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:10px 0 20px;">
        <svg width="26" height="26" viewBox="0 0 28 28">
            <polygon points="14,2 26,8 26,20 14,26 2,20 2,8" fill="none" stroke="#00e5ff" stroke-width="1.5"/>
            <circle cx="14" cy="14" r="3" fill="#00e5ff"/>
        </svg>
        <span style="font-family:'Syne',sans-serif;font-weight:800;font-size:18px;">
            VOLT<span style="color:#00e5ff;">GUARD</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="vg-section">ZONE SELECT</div>', unsafe_allow_html=True)
    zone = st.radio("zone", ZONES, index=ZONES.index(zone), label_visibility="collapsed")
    st.session_state["zone"] = zone

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    '<h2 style="font-family:Syne,sans-serif;font-weight:800;font-size:1.5rem;margin-bottom:4px">'
    'Data <span style="color:#00e5ff">Pipeline</span></h2>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="color:#3a6a7e;font-size:12px;margin-bottom:20px">End-to-end flow · Directory structure · Deployment guide</p>',
    unsafe_allow_html=True,
)

# ── Pipeline steps ────────────────────────────────────────────────────────────
st.markdown('<div class="vg-section">END-TO-END DATA PIPELINE</div>', unsafe_allow_html=True)

STEPS = [
    ("01", "Raw CSV Ingest",       "industrial.csv / rural.csv / urban.csv — transformer-level readings",               "#00e5ff", "data/"),
    ("02", "Feature Engineering",  "loss_kwh, loss_ratio, rolling_loss_mean/std, hour/day/month",                       "#00c4e0", "notebooks/VG_*.ipynb"),
    ("03", "StandardScaler",       "8 features normalised — prevents dominance by high-magnitude columns",              "#00a3c4", "scaler in .pkl"),
    ("04", "Isolation Forest",     "contamination=0.03, n_estimators=200 — anomaly label + anomaly_score",              "#ffa500", "outputs/*_anomalies.csv"),
    ("05", "Q-Learning Agent",     "State=(severity,time,trend), 5 episodes — assigns LOW/MEDIUM/HIGH priority",        "#ff8c00", "models/*_rl.pkl"),
    ("06", "Streamlit Dashboard",  "Reads CSVs + pkl directly — no backend needed. streamlit run app.py",               "#6dffb3", "app.py"),
]

for step, title, desc, color, file in STEPS:
    st.markdown(f"""
    <div class="step-card" style="border-left:3px solid {color}">
        <div style="display:flex;align-items:baseline;gap:14px;margin-bottom:5px">
            <span style="color:{color};font-size:10px;font-weight:700;letter-spacing:0.1em">{step}</span>
            <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:14px;color:#e8f4f8">{title}</span>
            <code style="font-size:10px;color:{color};background:rgba(0,0,0,0.3);padding:1px 8px;border-radius:4px">{file}</code>
        </div>
        <p style="font-size:12px;color:#4a7a8e;margin:0;line-height:1.5">{desc}</p>
    </div>
    """, unsafe_allow_html=True)
