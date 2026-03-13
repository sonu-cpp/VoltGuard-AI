# ⚡ VoltGuard-AI

> AI-powered power theft detection for distribution transformers — built for Indian DISCOMs.

India loses approximately **₹20,000 crore every year** to electricity theft. VoltGuard tackles this at the transformer level using a two-layer machine learning pipeline that detects abnormal energy loss patterns and prioritizes alerts for field teams.

---

## 🧠 How It Works

| Layer | Model | Purpose |
|-------|-------|---------|
| Layer 1 | Isolation Forest | Anomaly detection — flags abnormal energy loss readings |
| Layer 2 | Q-Learning (RL) | Alert prioritization — ranks anomalies as HIGH / MEDIUM / LOW |

Trained on **3 separate datasets** across distribution zones:
- 🏭 **Industrial** — high supply, moderate loss baseline
- 🌾 **Rural** — low supply, higher baseline loss (aging infrastructure)
- 🏙️ **Urban** — medium supply, lowest loss (well-maintained grid)

Each zone has **~1 lakh readings** spanning Oct 2014 → Mar 2026.

---

## 🖥️ Tech Stack

- **ML:** Scikit-learn (Isolation Forest), Custom Q-Learning agent
- **Frontend & Backend:** Streamlit
- **Visualization:** Plotly
- **Data:** Pandas, NumPy

---

## 🚀 Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/sonu-cpp/VoltGuard-AI.git
cd VoltGuard-AI
```

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

## 📁 Project Structure

```
VoltGuard-AI/
├── data/                   # Raw CSVs (industrial, rural, urban)
├── models/                 # Trained .pkl files per zone
├── notebooks/              # Training notebooks (IF + RL)
├── outputs/                # Anomaly CSVs per zone
├── pages/                  # Streamlit multi-page app
│   ├── 1_Overview.py
│   ├── 2_Alert_Feed.py
│   ├── 3_Model_Info.py
│   └── 4_Data_Pipeline.py
├── utils/                  # Data loader, model loader, charts
├── App.py                  # Entry point
└── requirements.txt
```

---

## 📊 Dashboard Pages

- **Overview** — Zone-level KPIs, monthly energy loss trends, anomaly score timeline
- **Alert Feed** — Filterable anomaly table with priority labels
- **Model Info** — Isolation Forest & RL parameters, per-zone model status
- **Data Pipeline** — Raw data preview and feature breakdown

---

> Built as a prototype to demonstrate that transformer-level power theft detection is feasible with open data and minimal infrastructure.
