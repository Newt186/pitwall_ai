# 🏎️ PitWall AI

> Your personal AI pit wall for every F1 race.

**PitWall AI** is a fan intelligence platform built for the F1 Fan Experience Hackathon 2025. It combines a free LLM chatbot, a machine learning race strategy engine, and real-time data visualisations — all inside a single Streamlit app, 100% Python, no JavaScript.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/LLM-Groq%20%2F%20Llama%203-orange.svg)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 👥 Team

| Name | Role | Module |
|------|------|--------|
| **Newt** | AI Lead | Fan Copilot (Groq + FAISS RAG) |
| **Rizwan** | ML Lead | Race Brain (FastF1 + XGBoost) |
| **Krishna** | Frontend Lead | Streamlit App + Live Pulse Charts |

---

## 🧩 Modules

### 🤖 Fan Copilot
An AI chatbot powered by **Groq (Llama 3)** with **FAISS RAG** over F1 rules, driver profiles, and race history. Ask it anything — from "What is DRS?" to "Why did Leclerc lose positions in Monaco?"

### 🧠 Race Brain
A **XGBoost** predictive engine trained on 3 seasons of FastF1 telemetry. Predicts:
- Pit stop windows (probability per lap)
- Tyre degradation rate
- Undercut risk score
- Predicted finishing position

### 📊 Live Pulse
Real-time **Plotly** charts inside Streamlit:
- Gap to leader chart
- Lap time trends with pit markers
- Tyre age tracker (per compound)
- Sector heatmap

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| `FastF1` | F1 race telemetry and lap data |
| `Groq API` (free) | LLM inference — Llama 3 8B |
| `FAISS + sentence-transformers` | Local vector search for RAG |
| `XGBoost` | Pit stop and position prediction |
| `scikit-learn` | Preprocessing and evaluation |
| `Streamlit` | Entire frontend |
| `Plotly` | Live Pulse visualisations |
| `pandas / numpy` | Data manipulation |
| `joblib` | Model serialisation |

---

## 📁 Project Structure

```
pitwall_ai/
│
├── app.py                  # Streamlit entry point (Krishna)
│
├── copilot/                # Fan Copilot module (Newt)
│   ├── build_index.py      # Build FAISS index from F1 docs
│   └── rag.py              # RAG retrieval + Groq chat function
│
├── racebrain/              # Race Brain module (Rizwan)
│   ├── data_pull.py        # FastF1 data collection
│   ├── features.py         # Feature engineering
│   ├── train.py            # XGBoost model training
│   └── predict.py          # Prediction functions (imported by app.py)
│
├── data/
│   ├── raw/                # F1 glossary, rules, driver profiles (.txt)
│   ├── processed/          # Cleaned CSVs + demo predictions
│   └── f1_cache/           # FastF1 local cache (gitignored)
│
├── models/                 # Saved FAISS index + XGBoost pkl files
│
├── secrets.py              # API keys (gitignored)
├── requirements.txt
└── README.md
```

---

## ⚡ Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/Newt186/pitwall_ai.git
cd pitwall_ai
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get a free Groq API key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up — no credit card needed
3. Navigate to **API Keys → Create Key**
4. Copy the key

### 5. Add your API key

Create a file called `secrets.py` in the project root:

```python
GROQ_API_KEY = "your_groq_api_key_here"
```

> ⚠️ `secrets.py` is gitignored. Never commit your API key.

### 6. Build the FAISS knowledge base (run once)

```bash
python copilot/build_index.py
```

This reads all `.txt` files from `data/raw/`, generates embeddings, and saves the FAISS index to `models/`.

### 7. Pull F1 race data and train models (run once)

```bash
python racebrain/data_pull.py
python racebrain/features.py
python racebrain/train.py
```

This pulls 2022–2024 season data via FastF1, engineers features, trains both XGBoost models, and saves them to `models/`.

> ⏱️ First run takes 10–20 minutes as FastF1 downloads race data. Subsequent runs use the local cache and are instant.

### 8. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Push this repo to [github.com/Newt186/pitwall_ai](https://github.com/Newt186/pitwall_ai)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → connect your GitHub repo
4. Set **Main file path** to `app.py`
5. Go to **Settings → Secrets** and add:
   ```
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
6. Click **Deploy**

---

## 🗂️ Git Workflow

Each team member works on their own branch and merges to `main` only when their module is working.

```bash
# Newt
git checkout -b newt/copilot

# Rizwan
git checkout -b rizwan/racebrain

# Krishna
git checkout -b krishna/frontend
```

**Merge to main:**
```bash
git checkout main
git merge newt/copilot       # after Fan Copilot is done
git merge rizwan/racebrain   # after Race Brain is done
git merge krishna/frontend   # after frontend is done
```

---

## 🔌 Module Contracts

Krishna imports both modules directly — no APIs, no HTTP, pure Python.

```python
# Fan Copilot
from copilot.rag import ask_copilot

response = ask_copilot(
    question="What is an undercut?",
    history=[]          # list of previous {'role': ..., 'content': ...} dicts
)
# returns: str

# Race Brain
from racebrain.predict import predict_pit, predict_position

pit = predict_pit(
    lap=28,
    tyre_life=18,
    compound=0,         # 0=SOFT, 1=MEDIUM, 2=HARD
    deg_rate=0.4,
    gap_ahead=8.5,
    undercut_risk=1,
    position=4
)
# returns: {'probability': float, 'recommended': bool, 'undercut_risk': int}

pos = predict_position(
    lap=28,
    tyre_life=18,
    compound=0,
    deg_rate=0.4,
    gap_ahead=8.5,
    undercut_risk=1,
    position=4
)
# returns: int (predicted finishing position, 1–20)
```

---

## 📦 Requirements

```
fastf1
groq
faiss-cpu
sentence-transformers
xgboost
scikit-learn
streamlit
plotly
pandas
numpy
joblib
```

Generate with:
```bash
pip freeze > requirements.txt
```

---

## 🚫 .gitignore

```
venv/
__pycache__/
*.pyc
.env
secrets.py
data/f1_cache/
models/faiss.index
models/chunks.pkl
models/pit_model.pkl
models/pos_model.pkl
*.DS_Store
```

---

## 📄 License

MIT — free to use, fork, and build on.

---

<p align="center">
  Built with 🏁 by <strong>Newt</strong>, <strong>Rizwan</strong>, and <strong>Krishna</strong> — Hackathon 2026
</p>
