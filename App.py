"""
app.py  ─  VoltGuard Streamlit Entry Point
──────────────────────────────────────────
Run:  streamlit run app.py

Navigation is handled by Streamlit's built-in multi-page system (pages/ folder).
This file:
  • Sets global page config
  • Injects shared CSS
  • Renders the sidebar zone selector (persisted via st.session_state)
  • Shows a landing summary so the home page isn't blank
"""
import streamlit as st
import sys
from pathlib import Path

# Make utils importable from pages/
sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import load_stats

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VoltGuard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', 'Courier New', monospace !important;
}

/* ── hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.6rem; padding-bottom: 2rem; }

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: #0a1a26 !important;
    border-right: 1px solid rgba(0,229,255,0.1);
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 13px !important;
    letter-spacing: 0.04em;
}

/* ── metric cards ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(0,229,255,0.12);
    border-radius: 12px;
    padding: 16px 20px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.9rem !important;
    color: #e8f4f8 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    letter-spacing: 0.1em;
    color: #5a8a9f !important;
    text-transform: uppercase;
}

/* ── dataframe table ── */
[data-testid="stDataFrame"] table {
    font-size: 12px !important;
}

/* ── divider ── */
hr { border-color: rgba(0,229,255,0.1) !important; }

/* ── section headers ── */
.vg-section {
    font-size: 10px;
    letter-spacing: 0.14em;
    color: #2a4a5e;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(0,229,255,0.07);
}

/* ── priority pill ── */
.pill-HIGH   { background:rgba(255,59,59,0.15);  border:1px solid #ff3b3b; color:#ff6b6b;  padding:2px 10px; border-radius:99px; font-size:11px; font-weight:700; }
.pill-MEDIUM { background:rgba(255,165,0,0.15);  border:1px solid #ffa500; color:#ffb733; padding:2px 10px; border-radius:99px; font-size:11px; font-weight:700; }
.pill-LOW    { background:rgba(0,229,255,0.10);  border:1px solid #00e5ff; color:#00e5ff; padding:2px 10px; border-radius:99px; font-size:11px; font-weight:700; }

/* ── info box ── */
.vg-info {
    background: rgba(0,229,255,0.04);
    border: 1px solid rgba(0,229,255,0.1);
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 12px;
    color: #4a8a9e;
    margin-top: 10px;
}

/* ── code block ── */
.vg-code {
    background: rgba(0,0,0,0.35);
    border: 1px solid rgba(0,229,255,0.08);
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 12px;
    color: #4a8a9e;
    white-space: pre;
    overflow-x: auto;
    line-height: 1.9;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar: zone selector (shared across all pages) ─────────────────────────
ZONES = ["Industrial", "Rural", "Urban"]

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
    if "zone" not in st.session_state:
        st.session_state["zone"] = "Industrial"

    zone = st.radio(
        label="zone",
        options=ZONES,
        index=ZONES.index(st.session_state["zone"]),
        label_visibility="collapsed",
        key="zone_radio",
    )
    st.session_state["zone"] = zone

    st.divider()

    # Mini HIGH alert counts per zone
    st.markdown('<div class="vg-section">HIGH ALERTS / ZONE</div>', unsafe_allow_html=True)
    for z in ZONES:
        s = load_stats(z)
        col1, col2 = st.columns([3, 1])
        col1.markdown(
            f'<span style="color:{"#00e5ff" if z==zone else "#3a6a7e"};font-size:12px">{z}</span>',
            unsafe_allow_html=True,
        )
        col2.markdown(
            f'<span style="color:#ff6b6b;font-size:12px;font-weight:700">{s["high"]}</span>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        '<div style="font-size:10px;color:#1a3a4e;letter-spacing:0.08em;">'
        'Isolation Forest · Q-Learning RL<br>VoltGuard v2.1</div>',
        unsafe_allow_html=True,
    )

# ── Landing page ─────────────────────────────────────────────────────────────
st.markdown(
    '<h1 style="font-family:Syne,sans-serif;font-weight:800;font-size:2rem;letter-spacing:-0.02em;">'
    f'{zone} <span style="color:#00e5ff">Zone</span></h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="color:#3a6a7e;font-size:12px;letter-spacing:0.05em;">'
    'Isolation Forest · Q-Learning RL · Distribution Transformer Anomaly Detection</p>',
    unsafe_allow_html=True,
)

st.divider()

# Summary stat cards on landing
s = load_stats(zone)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Records",      f'{s["total"]:,}')
c2.metric("Anomalies Detected", f'{s["anomalies"]:,}')
c3.metric("HIGH Alerts",        f'{s["high"]:,}')
c4.metric("Loss Reduction",     s["loss_reduction"])

st.markdown('<div class="vg-info">⬡ &nbsp; Use the sidebar to navigate to <strong>Overview</strong>, <strong>Alert Feed</strong>, <strong>Model Info</strong>, or <strong>Data Pipeline</strong>.</div>', unsafe_allow_html=True)
