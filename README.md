# ⚡ VoltGuard-AI

> AI-powered power theft detection for distribution transformers.

VoltGuard tackles this at the transformer level using a two-layer machine learning pipeline that detects abnormal energy loss patterns and prioritizes alerts for field teams.

---

## 🧠 How It Works

| Layer | Model | Purpose |
|-------|-------|---------|
| Layer 1 | Isolation Forest | Anomaly detection — flags abnormal energy loss readings |
| Layer 2 | Q-Learning (RL) | Alert prioritization — ranks anomalies as HIGH / MEDIUM / LOW |

Trained on **3 separate datasets** across distribution zones:
- **Industrial** 
- **Rural** 
- **Urban** 

Each zone has **~1 lakh readings** spanning Oct 2014 → Mar 2026.

---

## 🖥️ Tech Stack

- **ML:** Scikit-learn (Isolation Forest), Custom Q-Learning agent
- **Frontend & Backend:** Streamlit
- **Data:** Pandas, NumPy

---

## 🚀 Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/sonu-cpp/VoltGuard-AI.git
cd VoltGuard-AI
```
OR
clone it via GitHub Desktop

**2. Create a virtual environment**
```bash
python3 -m venv venv
```

**3. Activate the environment**
```bash
# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

**5. Run the app**
```bash
streamlit run App.py
```

---

Built as a prototype to demonstrate that transformer-level power theft detection is feasible with open data and minimal infrastructure.
