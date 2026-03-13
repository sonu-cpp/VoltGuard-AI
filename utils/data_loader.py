"""
utils/data_loader.py
────────────────────
Loads anomaly CSVs and computes all stats needed by the dashboard.
No transformer_id in source data — we generate alert IDs from row index.
"""
import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Map zone name → anomaly CSV filename
CSV_MAP = {
    "Industrial": ROOT / "outputs" / "industrial_anomalies.csv",
    "Rural":      ROOT / "outputs" / "rural_anomalies.csv",
    "Urban":      ROOT / "outputs" / "urban_anomalies.csv",
}

# Map zone name → full raw CSV (for total record counts)
RAW_CSV_MAP = {
    "Industrial": ROOT / "data" / "industrial.csv",
    "Rural":      ROOT / "data" / "rural.csv",
    "Urban":      ROOT / "data" / "urban.csv",
}

# Zone prefix for generated alert IDs
ID_PREFIX = {
    "Industrial": "IND",
    "Rural":      "RUR",
    "Urban":      "URB",
}


@st.cache_data(show_spinner=False)
def load_raw(zone: str) -> pd.DataFrame:
    """
    Load the full anomaly CSV for a zone.
    Adds:
      - alert_id        : IND-00001, RUR-00002 …
      - alert_priority  : HIGH / MEDIUM / LOW  (from alert_priority col if present,
                          else derived from anomaly_score)
    """
    path = CSV_MAP[zone]
    if not path.exists():
        # Return empty frame with correct columns so app doesn't crash
        return pd.DataFrame(columns=[
            "alert_id", "datetime", "loss_ratio",
            "anomaly_score", "anomaly", "alert_priority",
            "hour", "loss_kwh",
        ])

    df = pd.read_csv(path)

    # ── normalise datetime ──────────────────────────────────────────
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"])
    else:
        df["datetime"] = pd.NaT

    # ── derive hour if missing ──────────────────────────────────────
    if "hour" not in df.columns and "datetime" in df.columns:
        df["hour"] = df["datetime"].dt.hour

    # ── generate alert_id from row position ────────────────────────
    prefix = ID_PREFIX.get(zone, "ALT")
    df["alert_id"] = [f"{prefix}-{str(i+1).zfill(5)}" for i in range(len(df))]

    # ── ensure alert_priority exists ───────────────────────────────
    if "alert_priority" not in df.columns:
        # Derive from anomaly_score if RL notebook hasn't been run yet
        def score_to_priority(score):
            if pd.isna(score):
                return "LOW"
            if score < -0.1:
                return "HIGH"
            if score < 0:
                return "MEDIUM"
            return "LOW"
        df["alert_priority"] = df["anomaly_score"].apply(score_to_priority)

    return df


@st.cache_data(show_spinner=False)
def load_anomalies(zone: str, priority: str = "ALL") -> pd.DataFrame:
    """Return only anomaly rows (anomaly == -1), optionally filtered by priority."""
    df = load_raw(zone)
    if df.empty:
        return df
    anomalies = df[df["anomaly"] == -1].copy()
    if priority != "ALL":
        anomalies = anomalies[anomalies["alert_priority"] == priority]
    return anomalies.sort_values("datetime", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_stats(zone: str) -> dict:
    """Compute summary statistics from the raw CSV."""
    df = load_raw(zone)
    if df.empty:
        return {
            "total": 0, "anomalies": 0,
            "high": 0, "medium": 0, "low": 0,
            "loss_reduction": "N/A", "accuracy": "N/A",
        }

    anomalies = df[df["anomaly"] == -1]
    counts     = anomalies["alert_priority"].value_counts()

    # Total + normal baseline from full raw CSV
    raw_path = RAW_CSV_MAP.get(zone)
    total_records = len(df)
    mean_normal   = 0.0
    if raw_path and raw_path.exists():
        raw_df = pd.read_csv(raw_path)
        total_records = len(raw_df)
        raw_df["loss_ratio"] = (
            (raw_df["energy_supplied_kwh"] - raw_df["energy_billed_kwh"])
            / raw_df["energy_supplied_kwh"]
        )
        mean_normal = raw_df["loss_ratio"].mean()

    # Loss reduction: anomaly avg loss vs overall avg loss
    mean_anom = anomalies["loss_ratio"].mean() if len(anomalies) else 0
    if mean_normal > 0:
        loss_red = round((mean_anom - mean_normal) / mean_normal * 100, 1)
    else:
        loss_red = 0.0

    return {
        "total":          total_records,
        "anomalies":      len(anomalies),
        "high":           int(counts.get("HIGH",   0)),
        "medium":         int(counts.get("MEDIUM", 0)),
        "low":            int(counts.get("LOW",    0)),
        "loss_reduction": f"{abs(loss_red):.1f}%",
        "accuracy":       "N/A",          # needs labelled ground-truth to compute
    }


@st.cache_data(show_spinner=False)
def load_sparkline(zone: str, n_hours: int = 48) -> pd.DataFrame:
    """
    Return the last n_hours rows of (datetime, loss_ratio) for the zone.
    Used to draw the zone-level 48h loss trend on the Overview page.
    """
    df = load_raw(zone)
    if df.empty or "datetime" not in df.columns:
        return pd.DataFrame(columns=["datetime", "loss_ratio"])
    df = df.dropna(subset=["datetime"]).sort_values("datetime")
    return df[["datetime", "loss_ratio"]].tail(n_hours).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_hourly_profile(zone: str) -> pd.DataFrame:
    """
    Average loss_ratio grouped by hour-of-day (0-23).
    Used for the 24h heatmap / bar chart on the Overview page.
    """
    df = load_raw(zone)
    if df.empty or "hour" not in df.columns:
        return pd.DataFrame({"hour": range(24), "loss_ratio": [0.0] * 24})
    return (
        df.groupby("hour")["loss_ratio"]
        .mean()
        .reset_index()
        .rename(columns={"loss_ratio": "avg_loss_ratio"})
    )
