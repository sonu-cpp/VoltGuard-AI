"""
pages/3_Model_Info.py
──────────────────────
Model Layers: Isolation Forest params, Q-Learning RL params,
Q-table heatmap, per-zone pkl status.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from utils.model_loader import load_if_bundle, load_rl_bundle, model_status

st.set_page_config(page_title="VoltGuard · Model Info", page_icon="◎", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Mono','Courier New',monospace!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:1.6rem}
hr{border-color:rgba(0,229,255,0.1)!important}
.vg-section{font-size:10px;letter-spacing:0.14em;color:#2a4a5e;font-weight:600;text-transform:uppercase;margin-bottom:10px;padding-bottom:5px;border-bottom:1px solid rgba(0,229,255,0.07)}
.vg-info{background:rgba(0,229,255,0.04);border:1px solid rgba(0,229,255,0.1);border-radius:10px;padding:14px 18px;font-size:12px;color:#4a8a9e;margin-top:10px}
.vg-card{background:rgba(255,255,255,0.02);border:1px solid rgba(0,229,255,0.1);border-radius:12px;padding:20px 24px;margin-bottom:16px}
.param-val{font-family:'Syne',sans-serif;font-weight:800;font-size:1.6rem;color:#00e5ff}
.param-key{font-size:10px;letter-spacing:0.1em;color:#3a6a7e;text-transform:uppercase;margin-bottom:4px}
.param-note{font-size:10px;color:#2a5a6e;margin-top:3px}
.status-ok{color:#6dffb3;font-size:11px;font-weight:700}
.status-miss{color:#ff6b6b;font-size:11px;font-weight:700}
[data-testid="stSidebar"]{background:#0a1a26!important;border-right:1px solid rgba(0,229,255,0.1)}
</style>
""", unsafe_allow_html=True)

# ── Zone selector ─────────────────────────────────────────────────────────────
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
    f'<h2 style="font-family:Syne,sans-serif;font-weight:800;font-size:1.5rem;margin-bottom:4px">'
    f'Model <span style="color:#00e5ff">Layers</span></h2>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="color:#3a6a7e;font-size:12px;margin-bottom:20px">'
    'Isolation Forest + Q-Learning RL · Configuration & Q-Table Viewer</p>',
    unsafe_allow_html=True,
)

# ── Layer 1: Isolation Forest ─────────────────────────────────────────────────
st.markdown("### Layer 1 — Isolation Forest")
st.markdown('<div style="font-size:11px;color:#3a6a7e;margin-bottom:14px">sklearn.ensemble · Unsupervised anomaly detection</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
params_if = [
    ("contamination", "0.03", "3% expected anomaly rate", c1),
    ("n_estimators",  "200",  "Ensemble tree count",       c2),
    ("random_state",  "42",   "Reproducibility seed",      c3),
]
for key, val, note, col in params_if:
    col.markdown(f"""
    <div class="vg-card">
        <div class="param-key">{key}</div>
        <div class="param-val">{val}</div>
        <div class="param-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="vg-info">
    <strong>Features:</strong> energy_supplied_kwh · energy_billed_kwh · loss_ratio · hour · day · month · rolling_loss_mean · rolling_loss_std<br>
    <strong>Output:</strong> anomaly (−1 = anomaly, +1 = normal) · anomaly_score (decision function — more negative = more anomalous)
</div>
""", unsafe_allow_html=True)

# Try loading actual model to confirm
if_bundle = load_if_bundle(zone)
if if_bundle and "model" in if_bundle:
    m = if_bundle["model"]
    st.markdown(f"""
    <div style="margin-top:12px;font-size:11px;color:#3a6a7e">
        ✅ &nbsp; Model loaded from pkl &nbsp;·&nbsp;
        n_estimators: <span style="color:#00e5ff">{m.n_estimators}</span> &nbsp;·&nbsp;
        n_features: <span style="color:#00e5ff">{getattr(m, 'n_features_in_', 'N/A')}</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div style="margin-top:10px;font-size:11px;color:#ff6b6b">⚠ pkl not found — showing config defaults</div>', unsafe_allow_html=True)

st.divider()

# ── Layer 2: Q-Learning RL ────────────────────────────────────────────────────
st.markdown("### Layer 2 — Q-Learning RL Agent")
st.markdown('<div style="font-size:11px;color:#3a6a7e;margin-bottom:14px">Alert priority optimisation · Bellman equation · State space 3×3×3</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
params_rl = [
    ("alpha (α)",   "0.1", "Learning rate",     c1),
    ("gamma (γ)",   "0.9", "Discount factor",    c2),
    ("epsilon (ε)", "0.2", "Exploration rate",   c3),
    ("episodes",    "5",   "Training episodes",  c4),
]
for key, val, note, col in params_rl:
    col.markdown(f"""
    <div class="vg-card" style="border-color:rgba(255,165,0,0.15)">
        <div class="param-key">{key}</div>
        <div class="param-val" style="color:#ffa500">{val}</div>
        <div class="param-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="vg-info">
    <strong>State space:</strong> (severity × time_of_day × loss_trend) = 3 × 3 × 3 = 27 states<br>
    <strong>Actions:</strong> 0 → LOW &nbsp;·&nbsp; 1 → MEDIUM &nbsp;·&nbsp; 2 → HIGH<br>
    <strong>Q-Table shape:</strong> [3, 3, 3, 3] — argmax over action axis gives chosen priority per state<br>
    <strong>Update rule:</strong> Q(s,a) ← Q(s,a) + α · [r + γ · max Q(s',a') − Q(s,a)]
</div>
""", unsafe_allow_html=True)


# ── Per-zone pkl status ───────────────────────────────────────────────────────
st.markdown('<div class="vg-section">MODEL FILE STATUS — ALL ZONES</div>', unsafe_allow_html=True)

cols = st.columns(3)
for i, z in enumerate(ZONES):
    ms = model_status(z)
    with cols[i]:
        border_col = "rgba(0,229,255,0.3)" if z == zone else "rgba(0,229,255,0.07)"
        label_col  = "#00e5ff" if z == zone else "#4a7a8e"
        st.markdown(f"""
        <div class="vg-card" style="border-color:{border_col}">
            <div style="font-weight:700;font-size:13px;margin-bottom:10px;color:{label_col}">{z}</div>
            <div style="font-size:11px;line-height:2">
                IF pkl: &nbsp;<span style="color:{'#6dffb3' if ms['if_loaded'] else '#ff6b6b'}">{ms['if_file']}</span><br>
                RL pkl: &nbsp;<span style="color:{'#6dffb3' if ms['rl_loaded'] else '#ff6b6b'}">{ms['rl_file']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
