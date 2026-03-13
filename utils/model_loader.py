"""
utils/model_loader.py
─────────────────────
Loads .pkl bundles for each zone at startup (cached).
"""
import pickle
import streamlit as st
from pathlib import Path

ROOT = Path(__file__).parent.parent

PKL_IF = {
    "Industrial": ["voltguard_industrial_model.pkl", "voltguard_model.pkl"],
    "Rural":      ["voltguard_rural_model.pkl"],
    "Urban":      ["voltguard_urban_model.pkl"],
}

PKL_RL = {
    "Industrial": ["voltguard_industrial_rl.pkl", "voltguard_rl.pkl"],
    "Rural":      ["voltguard_rural_rl.pkl"],
    "Urban":      ["voltguard_urban_rl.pkl"],
}


def _find_pkl(candidates: list):
    for name in candidates:
        p = ROOT / "models" / name
        if p.exists():
            return p
    return None


@st.cache_resource(show_spinner=False)
def load_if_bundle(zone: str):
    path = _find_pkl(PKL_IF.get(zone, []))
    if path is None:
        return None
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def load_rl_bundle(zone: str):
    path = _find_pkl(PKL_RL.get(zone, []))
    if path is None:
        return None
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


def get_q_table(zone: str):
    bundle = load_rl_bundle(zone)
    if bundle is None:
        return None
    return bundle.get("q_table")


def model_status(zone: str) -> dict:
    if_path = _find_pkl(PKL_IF.get(zone, []))
    rl_path = _find_pkl(PKL_RL.get(zone, []))
    return {
        "if_file":   if_path.name if if_path else "not found",
        "if_loaded": if_path is not None,
        "rl_file":   rl_path.name if rl_path else "not found",
        "rl_loaded": rl_path is not None,
    }
