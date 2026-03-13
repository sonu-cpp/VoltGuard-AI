"""
pages/2_Alert_Feed.py
──────────────────────
Alert Feed — two modes:
  • LIVE FEED  : simulates transformer readings streaming in, anomalies flash red
  • TABLE VIEW : full filterable dataframe of all anomaly records

Priority fix: thresholds adjusted to match real anomaly_score distribution
(scores in this dataset are small negatives, −0.005 to −0.05)
"""
import sys, time, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from utils.data_loader import load_anomalies, load_stats, load_raw
from utils.charts      import loss_ratio_histogram

st.set_page_config(page_title="VoltGuard · Alert Feed", page_icon="◈", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', 'Courier New', monospace !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.4rem; padding-bottom: 2rem; }

/* ── metrics ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(0,229,255,0.12);
    border-radius: 12px;
    padding: 14px 18px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.8rem !important;
    color: #e8f4f8 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 10px !important;
    letter-spacing: 0.1em;
    color: #5a8a9f !important;
    text-transform: uppercase;
}

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: #0a1a26 !important;
    border-right: 1px solid rgba(0,229,255,0.1);
}

/* ── section label ── */
.vg-section {
    font-size: 10px;
    letter-spacing: 0.14em;
    color: #2a4a5e;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1px solid rgba(0,229,255,0.07);
}

hr { border-color: rgba(0,229,255,0.1) !important; }

/* ── LIVE FEED TABLE ── */
.feed-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
    font-family: 'DM Mono', monospace;
}
.feed-table th {
    font-size: 9px;
    letter-spacing: 0.14em;
    color: #2a4a5e;
    font-weight: 600;
    text-transform: uppercase;
    padding: 10px 14px;
    border-bottom: 1px solid rgba(0,229,255,0.1);
    text-align: left;
    white-space: nowrap;
}
.feed-table td {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(0,229,255,0.04);
    color: #c8e4f0;
    white-space: nowrap;
    font-size: 12px;
}
.feed-table tr.normal-row:hover td { background: rgba(0,229,255,0.03); }
.feed-table tr.anomaly-HIGH td   { background: rgba(255,59,59,0.10); }
.feed-table tr.anomaly-MEDIUM td { background: rgba(255,165,0,0.08); }
.feed-table tr.anomaly-LOW td    { background: rgba(0,229,255,0.05); }
.feed-table tr.new-row td        { animation: flashIn 0.6s ease; }

@keyframes flashIn {
    0%   { opacity: 0; transform: translateY(-4px); }
    40%  { opacity: 1; background: rgba(0,229,255,0.12); }
    100% { opacity: 1; }
}

.pill-HIGH   { background:rgba(255,59,59,0.18); border:1px solid #ff3b3b; color:#ff6b6b;
               padding:2px 9px; border-radius:99px; font-size:10px; font-weight:700; white-space:nowrap; }
.pill-MEDIUM { background:rgba(255,165,0,0.15);  border:1px solid #ffa500; color:#ffb733;
               padding:2px 9px; border-radius:99px; font-size:10px; font-weight:700; white-space:nowrap; }
.pill-LOW    { background:rgba(0,229,255,0.10);  border:1px solid #00e5ff; color:#00e5ff;
               padding:2px 9px; border-radius:99px; font-size:10px; font-weight:700; white-space:nowrap; }
.pill-NORMAL { background:rgba(109,255,179,0.08);border:1px solid #6dffb3; color:#6dffb3;
               padding:2px 9px; border-radius:99px; font-size:10px; font-weight:700; white-space:nowrap; }

.live-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #00e5ff;
    margin-right: 8px;
    animation: blink 1.2s ease infinite;
}
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 6px #00e5ff} 50%{opacity:0.3;box-shadow:none} }

.feed-status {
    font-size: 11px;
    color: #3a6a7e;
    letter-spacing: 0.06em;
    margin-bottom: 10px;
}

.anomaly-alert {
    background: rgba(255,59,59,0.08);
    border: 1px solid rgba(255,59,59,0.3);
    border-left: 3px solid #ff3b3b;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 12px;
    color: #ff8888;
    margin-bottom: 8px;
    animation: flashIn 0.4s ease;
}

.vg-info {
    background: rgba(0,229,255,0.04);
    border: 1px solid rgba(0,229,255,0.1);
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 12px;
    color: #4a8a9e;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── Priority thresholds — calibrated to real score range ─────────────────────
# Your data: scores roughly −0.005 to −0.05, all anomalies (anomaly == −1)
# We use percentile-based thresholds relative to the zone's own score distribution
def assign_priority(score, p33, p67):
    """Map anomaly_score to priority using zone-relative percentiles."""
    if pd.isna(score):
        return "LOW"
    if score <= p33:   # worst 33% → HIGH
        return "HIGH"
    if score <= p67:   # middle 33% → MEDIUM
        return "MEDIUM"
    return "LOW"       # least anomalous 33% → LOW


def get_anomalies_with_priority(zone, priority_filter="ALL"):
    """Load anomalies and assign percentile-based priority."""
    df = load_raw(zone)
    if df.empty:
        return df
    anom = df[df["anomaly"] == -1].copy()
    if anom.empty:
        return anom

    # Use percentiles of this zone's anomaly score distribution
    p33 = anom["anomaly_score"].quantile(0.33)
    p67 = anom["anomaly_score"].quantile(0.67)
    anom["alert_priority"] = anom["anomaly_score"].apply(
        lambda s: assign_priority(s, p33, p67)
    )
    anom = anom.sort_values("datetime", ascending=False).reset_index(drop=True)

    if priority_filter != "ALL":
        anom = anom[anom["alert_priority"] == priority_filter]
    return anom


def get_stats_with_priority(zone):
    """Recompute stats using percentile-based priority."""
    df = load_raw(zone)
    if df.empty:
        return {"total":0,"anomalies":0,"high":0,"medium":0,"low":0,"loss_reduction":"N/A"}
    anom = df[df["anomaly"] == -1].copy()
    if anom.empty:
        return {"total":len(df),"anomalies":0,"high":0,"medium":0,"low":0,"loss_reduction":"N/A"}
    p33 = anom["anomaly_score"].quantile(0.33)
    p67 = anom["anomaly_score"].quantile(0.67)
    anom["alert_priority"] = anom["anomaly_score"].apply(lambda s: assign_priority(s, p33, p67))
    counts = anom["alert_priority"].value_counts()
    mean_all  = df["loss_ratio"].mean()
    mean_anom = anom["loss_ratio"].mean()
    loss_red  = abs((mean_anom - mean_all) / mean_all * 100) if mean_all else 0
    return {
        "total":          len(df),
        "anomalies":      len(anom),
        "high":           int(counts.get("HIGH",   0)),
        "medium":         int(counts.get("MEDIUM", 0)),
        "low":            int(counts.get("LOW",    0)),
        "loss_reduction": f"{loss_red:.1f}%",
    }


# ── Zone + mode selector (sidebar) ───────────────────────────────────────────
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

    st.divider()
    st.markdown('<div class="vg-section">VIEW MODE</div>', unsafe_allow_html=True)
    mode = st.radio(
        "mode",
        ["🔴  Live Feed", "📋  Table View"],
        label_visibility="collapsed",
    )

    if "📋" in mode:
        st.divider()
        st.markdown('<div class="vg-section">FILTER BY PRIORITY</div>', unsafe_allow_html=True)
        priority_filter = st.radio(
            "priority", ["ALL", "HIGH", "MEDIUM", "LOW"],
            label_visibility="collapsed",
        )
    else:
        priority_filter = "ALL"
        st.divider()
        st.markdown('<div class="vg-section">LIVE FEED SETTINGS</div>', unsafe_allow_html=True)
        speed = st.select_slider(
            "Interval (sec)", options=[0.3, 0.5, 0.8, 1.0, 1.5, 2.0],
            value=0.8, label_visibility="collapsed",
        )
        max_rows = st.slider("Max rows visible", 10, 40, 20, label_visibility="collapsed",
                             help="How many rows to show in the live table")

# ── Load data ─────────────────────────────────────────────────────────────────
stats = get_stats_with_priority(zone)
df_all = get_anomalies_with_priority(zone, priority_filter)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    f'<h2 style="font-family:Syne,sans-serif;font-weight:800;font-size:1.5rem;margin-bottom:4px">'
    f'{zone} <span style="color:#00e5ff">Alert Feed</span></h2>',
    unsafe_allow_html=True,
)

# ── Stat cards ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Anomalies", f'{stats["anomalies"]:,}')
c2.metric("HIGH",   f'{stats["high"]:,}')
c3.metric("MEDIUM", f'{stats["medium"]:,}')
c4.metric("LOW",    f'{stats["low"]:,}')

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# MODE 1 — LIVE FEED
# ═════════════════════════════════════════════════════════════════════════════
if "🔴" in mode:

    # Load ALL raw rows sorted oldest → newest for playback
    raw = load_raw(zone).sort_values("datetime").reset_index(drop=True)
    if raw.empty:
        st.warning("No data found. Check outputs/ folder.")
        st.stop()

    # Precompute priority thresholds for the whole zone
    anom_mask = raw["anomaly"] == -1
    anom_scores = raw.loc[anom_mask, "anomaly_score"]
    p33 = anom_scores.quantile(0.33) if len(anom_scores) else -0.02
    p67 = anom_scores.quantile(0.67) if len(anom_scores) else -0.01

    # ── Controls ──────────────────────────────────────────────────────────────
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 5])
    start_btn = ctrl_col1.button("▶  START", type="primary", use_container_width=True)
    stop_btn  = ctrl_col2.button("⏹  STOP",  use_container_width=True)

    if start_btn:
        st.session_state["feed_running"] = True
        st.session_state["feed_index"]   = 0
        st.session_state["feed_rows"]    = []
        st.session_state["alert_log"]    = []

    if stop_btn:
        st.session_state["feed_running"] = False

    running   = st.session_state.get("feed_running", False)
    feed_idx  = st.session_state.get("feed_index",   0)
    feed_rows = st.session_state.get("feed_rows",    [])
    alert_log = st.session_state.get("alert_log",    [])

    # ── Status bar ────────────────────────────────────────────────────────────
    status_col, count_col = st.columns([3, 1])
    status_placeholder = status_col.empty()
    count_placeholder  = count_col.empty()

    if running:
        status_placeholder.markdown(
            f'<div class="feed-status"><span class="live-dot"></span>'
            f'LIVE · {zone.upper()} ZONE · Reading {feed_idx + 1} / {len(raw)}</div>',
            unsafe_allow_html=True,
        )
    else:
        status_placeholder.markdown(
            '<div class="feed-status" style="color:#2a4a5e">⏸ Paused — press START to begin live stream</div>',
            unsafe_allow_html=True,
        )

    # ── Live table ────────────────────────────────────────────────────────────
    st.markdown('<div class="vg-section">INCOMING TRANSFORMER READINGS</div>', unsafe_allow_html=True)
    table_placeholder = st.empty()

    _IFRAME_CSS = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap');
    *{box-sizing:border-box;margin:0;padding:0}
    body{background:transparent;font-family:'DM Mono',monospace}
    .wrap{background:rgba(10,26,38,0.7);border:1px solid rgba(0,229,255,0.1);border-radius:10px;overflow:hidden}
    table{width:100%;border-collapse:collapse;font-size:12.5px}
    thead th{font-size:9px;letter-spacing:.14em;color:#2a4a5e;font-weight:600;text-transform:uppercase;
             padding:10px 14px;border-bottom:1px solid rgba(0,229,255,0.1);text-align:left;
             white-space:nowrap;background:rgba(5,13,20,0.6)}
    tbody td{padding:9px 14px;border-bottom:1px solid rgba(0,229,255,0.04);
             color:#c8e4f0;white-space:nowrap;font-size:12px}
    tr.nr:hover td{background:rgba(0,229,255,0.03)}
    tr.aH td{background:rgba(255,59,59,0.09)}
    tr.aM td{background:rgba(255,165,0,0.07)}
    tr.aL td{background:rgba(0,229,255,0.04)}
    @keyframes sI{from{opacity:0;transform:translateY(-5px)}to{opacity:1;transform:translateY(0)}}
    tr.new td{animation:sI .45s ease forwards}
    .pill{padding:2px 9px;border-radius:99px;font-size:10px;font-weight:700;display:inline-block}
    .pH{background:rgba(255,59,59,.18);border:1px solid #ff3b3b;color:#ff6b6b}
    .pM{background:rgba(255,165,0,.15);border:1px solid #ffa500;color:#ffb733}
    .pL{background:rgba(0,229,255,.10);border:1px solid #00e5ff;color:#00e5ff}
    .pN{background:rgba(109,255,179,.08);border:1px solid #6dffb3;color:#6dffb3}
    .abox{background:rgba(255,59,59,.07);border:1px solid rgba(255,59,59,.25);
          border-left:3px solid #ff3b3b;border-radius:7px;padding:9px 14px;
          font-size:12px;color:#ff9090;margin-bottom:7px;font-family:'DM Mono',monospace}
    </style>"""

    _PILL = {"HIGH":"pH","MEDIUM":"pM","LOW":"pL","NORMAL":"pN"}
    _ROW_CLS = {"HIGH":"aH","MEDIUM":"aM","LOW":"aL","NORMAL":"nr"}

    def play_beep(priority: str):
        """Inject JS beep sound based on alert priority."""
        if priority == "HIGH":
            # Same as MEDIUM beep but 2 times back to back
            beep_js = """
            <script>
            (function(){
                const ctx = new (window.AudioContext||window.webkitAudioContext)();
                function beep(start){
                    const o=ctx.createOscillator(), g=ctx.createGain();
                    o.connect(g); g.connect(ctx.destination);
                    o.type='sine';
                    o.frequency.value=620;
                    g.gain.setValueAtTime(0.5, start);
                    g.gain.exponentialRampToValueAtTime(0.001, start+0.3);
                    o.start(start); o.stop(start+0.35);
                }
                const t=ctx.currentTime;
                beep(t);
                beep(t+0.4);
            })();
            </script>"""
        elif priority == "MEDIUM":
            # 1 normal clean beep
            beep_js = """
            <script>
            (function(){
                const ctx = new (window.AudioContext||window.webkitAudioContext)();
                const o=ctx.createOscillator(), g=ctx.createGain();
                o.connect(g); g.connect(ctx.destination);
                o.type='sine';
                o.frequency.value=620;
                g.gain.setValueAtTime(0.5, ctx.currentTime);
                g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime+0.3);
                o.start(ctx.currentTime);
                o.stop(ctx.currentTime+0.35);
            })();
            </script>"""
        else:
            # LOW: silent
            beep_js = "<script></script>"
        components.html(beep_js, height=0)

    def render_table(rows, newest_id=None):
        trs = ""
        for r in rows:
            p    = r.get("priority","NORMAL")
            rc   = _ROW_CLS.get(p,"nr") + (" new" if r["alert_id"]==newest_id else "")
            ac   = {"HIGH":"#ff6b6b","MEDIUM":"#ffb733","LOW":"#00e5ff","NORMAL":"#4a7a8e"}[p]
            ratc = "#ff6b6b" if r["loss_ratio"]>0.3 else "#ffb733" if r["loss_ratio"]>0.2 else "#c8e4f0"
            scc  = "#ff6b6b" if r["score"]<p33 else "#ffb733" if r["score"]<p67 else "#4a7a8e"
            trs += (f'<tr class="{rc}">' +
                    f'<td style="color:{ac};font-weight:600">{r["alert_id"]}</td>' +
                    f'<td style="color:#4a7a8e">{r["datetime"]}</td>' +
                    f'<td style="color:{ratc}">{r["loss_ratio"]:.4f}</td>' +
                    f'<td style="color:{scc}">{r["score"]:.4f}</td>' +
                    f'<td>{r["supplied"]:.1f}</td><td>{r["billed"]:.1f}</td><td>{r["loss_kwh"]:.1f}</td>' +
                    f'<td><span class="pill {_PILL[p]}">{p}</span></td></tr>')
        ht = 44 + 38*len(rows) + 10
        return (_IFRAME_CSS +
                '<div class="wrap"><table><thead><tr>' +
                '<th>Alert ID</th><th>Timestamp</th><th>Loss Ratio</th><th>Score</th>' +
                '<th>Supplied kWh</th><th>Billed kWh</th><th>Loss kWh</th><th>Status</th>' +
                f'</tr></thead><tbody>{trs}</tbody></table></div>'), ht

    def render_alert_log(alerts):
        if not alerts:
            return "", 0
        boxes = "".join(
            f'<div class="abox">⚠ &nbsp;ANOMALY &nbsp;·&nbsp; {a["id"]} &nbsp;·&nbsp; ' +
            f'{a["time"]} &nbsp;·&nbsp; Loss: {a["loss"]:.4f} &nbsp;·&nbsp; Priority: <strong>{a["priority"]}</strong></div>'
            for a in alerts[-3:]
        )
        return _IFRAME_CSS + boxes, 46*min(len(alerts),3)+10

    # ── Initial render ────────────────────────────────────────────────────────
    if feed_rows:
        html, ht = render_table(feed_rows)
        with table_placeholder:
            components.html(html, height=ht, scrolling=False)

    # ── Stream loop ───────────────────────────────────────────────────────────
    if running and feed_idx < len(raw):
        row = raw.iloc[feed_idx]

        is_anom  = int(row.get("anomaly", 1)) == -1
        score    = float(row.get("anomaly_score", 0))
        priority = assign_priority(score, p33, p67) if is_anom else "NORMAL"

        prefix   = {"Industrial":"IND","Rural":"RUR","Urban":"URB"}.get(zone,"ALT")
        alert_id = f"{prefix}-{str(feed_idx+1).zfill(5)}"

        dt_str = str(row["datetime"])[:16] if pd.notna(row.get("datetime")) else "—"

        new_entry = {
            "alert_id":   alert_id,
            "datetime":   dt_str,
            "loss_ratio": float(row.get("loss_ratio", 0)),
            "score":      score,
            "supplied":   float(row.get("energy_supplied_kwh", 0)),
            "billed":     float(row.get("energy_billed_kwh", 0)),
            "loss_kwh":   float(row.get("loss_kwh", 0)),
            "is_anomaly": is_anom,
            "priority":   priority,
        }

        # Prepend newest at top, cap at max_rows
        feed_rows = [new_entry] + feed_rows
        if len(feed_rows) > max_rows:
            feed_rows = feed_rows[:max_rows]

        # Update alert log + play beep on anomaly
        if is_anom:
            alert_log = [{
                "id":       alert_id,
                "time":     dt_str,
                "loss":     new_entry["loss_ratio"],
                "priority": priority,
            }] + alert_log
            alert_log = alert_log[:5]
            play_beep(priority)  # 🔔 beep based on severity

        # Save state
        st.session_state["feed_index"] = feed_idx + 1
        st.session_state["feed_rows"]  = feed_rows
        st.session_state["alert_log"]  = alert_log

        # Render
        html, ht = render_table(feed_rows, newest_id=alert_id)
        with table_placeholder:
            components.html(html, height=min(ht, 620), scrolling=False)

        time.sleep(speed)
        st.rerun()

    elif running and feed_idx >= len(raw):
        st.session_state["feed_running"] = False
        status_placeholder.markdown(
            '<div class="feed-status" style="color:#6dffb3">✓ Stream complete — all records processed</div>',
            unsafe_allow_html=True,
        )

# ═════════════════════════════════════════════════════════════════════════════
# MODE 2 — TABLE VIEW
# ═════════════════════════════════════════════════════════════════════════════
else:
    st.markdown(
        f'<p style="color:#3a6a7e;font-size:12px;margin-bottom:16px">'
        f'{len(df_all)} alerts · filter: <strong style="color:#00e5ff">{priority_filter}</strong></p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="vg-section">ANOMALY RECORDS</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.info("No alerts found for this filter.")
    else:
        possible_cols = [
            "alert_id", "datetime", "loss_ratio", "anomaly_score",
            "alert_priority", "energy_supplied_kwh", "energy_billed_kwh",
            "loss_kwh", "hour", "day", "month",
        ]
        display_cols = [c for c in possible_cols if c in df_all.columns]
        display_df   = df_all[display_cols].copy()

        for col in ["loss_ratio", "anomaly_score"]:
            if col in display_df.columns:
                display_df[col] = display_df[col].round(4)
        for col in ["energy_supplied_kwh", "energy_billed_kwh", "loss_kwh"]:
            if col in display_df.columns:
                display_df[col] = display_df[col].round(2)

        def highlight_priority(val):
            c = {"HIGH":"rgba(255,59,59,0.15)","MEDIUM":"rgba(255,165,0,0.12)","LOW":"rgba(0,229,255,0.08)"}
            return f"background-color:{c.get(val,'transparent')}"

        st.dataframe(
            display_df.style.map(highlight_priority, subset=["alert_priority"])
            if "alert_priority" in display_df.columns else display_df,
            use_container_width=True,
            height=460,
            column_config={
                "alert_id":            st.column_config.TextColumn("Alert ID",      width=100),
                "datetime":            st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm"),
                "loss_ratio":          st.column_config.NumberColumn("Loss Ratio",  format="%.4f", width=100),
                "anomaly_score":       st.column_config.NumberColumn("Score",       format="%.4f", width=90),
                "alert_priority":      st.column_config.TextColumn("Priority",      width=90),
                "energy_supplied_kwh": st.column_config.NumberColumn("Supplied kWh",format="%.1f", width=110),
                "energy_billed_kwh":   st.column_config.NumberColumn("Billed kWh",  format="%.1f", width=100),
                "loss_kwh":            st.column_config.NumberColumn("Loss kWh",    format="%.1f", width=90),
                "hour":                st.column_config.NumberColumn("Hour",         width=60),
                "day":                 st.column_config.NumberColumn("Day",          width=60),
                "month":               st.column_config.NumberColumn("Month",        width=70),
            },
            hide_index=True,
        )

        csv_bytes = display_df.to_csv(index=False).encode()
        st.download_button(
            label="⬇ Download filtered alerts as CSV",
            data=csv_bytes,
            file_name=f"voltguard_{zone.lower()}_alerts_{priority_filter.lower()}.csv",
            mime="text/csv",
        )

    st.divider()

    col_hist, col_stats = st.columns([2, 1])
    with col_hist:
        st.markdown('<div class="vg-section">LOSS RATIO DISTRIBUTION</div>', unsafe_allow_html=True)
        st.plotly_chart(loss_ratio_histogram(df_all), use_container_width=True,
                        config={"displayModeBar": False})

    with col_stats:
        st.markdown('<div class="vg-section">SCORE STATISTICS</div>', unsafe_allow_html=True)
        if not df_all.empty and "anomaly_score" in df_all.columns:
            s = df_all["anomaly_score"].describe()
            for label, val in [
                ("Min score",   f'{s["min"]:.4f}'),
                ("Max score",   f'{s["max"]:.4f}'),
                ("Mean score",  f'{s["mean"]:.4f}'),
                ("Std dev",     f'{s["std"]:.4f}'),
                ("P33 (HIGH ≤)",f'{df_all["anomaly_score"].quantile(0.33):.4f}'),
                ("P67 (MED ≤)", f'{df_all["anomaly_score"].quantile(0.67):.4f}'),
                ("Count",       int(s["count"])),
            ]:
                l, v = st.columns([3,2])
                l.markdown(f'<span style="font-size:11px;color:#3a6a7e">{label}</span>', unsafe_allow_html=True)
                v.markdown(f'<span style="font-size:12px;color:#00e5ff;font-weight:600">{val}</span>', unsafe_allow_html=True)
