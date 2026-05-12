<div align="center">

<!-- Animated Banner -->
<img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&size=30&duration=2500&pause=1000&color=00C2FF&center=true&vCenter=true&width=1000&lines=🏛️+CompliQ+-+BIS+Recommendation+Engine;🤖+Hybrid+RAG+%2B+RRF+Architecture;⚡+Hallucination-Free+AI+Search;🚀+Production+Grade+Retrieval+System" alt="Typing SVG" />

# 🏛️ CompliQ

### AI-Powered BIS Standards Recommendation Engine

<p align="center">
  <img src="https://img.shields.io/badge/Hit%20Rate-100%25-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/MRR-0.83-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Latency-2.1s-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Last%20Update-May%202026-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>

*A production-grade AI search engine that maps building materials to official BIS standards using Hybrid RAG pipelines.*

[🚀 Features](#-features) • [🏗️ Architecture](#️-architecture) • [⚙️ Setup](#️-quick-start) • [🧠 Tech Stack](#-technology-stack)

</div>

---

# 🌟 Features

<div align="center">

| ⚡ Fast Retrieval | 🧠 AI Re-ranking | 🛡️ Anti-Hallucination | 📊 Evaluation Ready |
|:---:|:---:|:---:|:---:|
| Semantic + Keyword Search | Llama 3 via Groq | Strict Context Filtering | Judge-ready pipeline |
| <img width="100" src="https://media.giphy.com/media/f3iwJFOVOwuy7K6FFw/giphy.gif"> | <img width="100" src="https://media.giphy.com/media/3o7TKsQ8UQK6mM0fLO/giphy.gif"> | <img width="100" src="https://media.giphy.com/media/l0HlRnAWXxn0MhKLK/giphy.gif"> | <img width="100" src="https://media.giphy.com/media/xT0xeJpnrWC4XWblEk/giphy.gif"> |

</div>

---

# 📊 Performance Metrics

<div align="center">

| Metric | Result |
|---|---|
| 🎯 Hit Rate @ 3 | **100%** |
| 📈 Mean Reciprocal Rank | **0.83** |
| ⚡ Average Latency | **~2.1s** |
| 🚀 Fast Query Response | **<400ms** |

</div>

---

# 🏗️ Architecture

<div align="center">

```ascii
┌───────────────────────────────────────────────────────────────┐
│                    🏛️ COMPLIQ PIPELINE                       │
└───────────────────────────────────────────────────────────────┘
```

</div>

## 🔄 Retrieval Workflow

```ascii
        ┌──────────────┐
        │ User Query   │
        └──────┬───────┘
               │
      ┌────────▼────────┐
      │ Hybrid Retrieval │
      └────────┬────────┘
               │
     ┌─────────┴─────────┐
     │                   │
┌────▼────┐       ┌──────▼─────┐
│  BM25   │       │   FAISS    │
│ Keyword │       │ Semantic   │
└────┬────┘       └──────┬─────┘
     │                   │
     └────────┬──────────┘
              ▼
      ┌──────────────┐
      │ RRF Fusion   │
      └──────┬───────┘
             ▼
     ┌───────────────┐
     │ LLM Re-ranking│
     └──────┬────────┘
            ▼
   ┌──────────────────┐
   │ Final BIS Result │
   └──────────────────┘
```

---

# ⚙️ Quick Start

## 📦 Prerequisites

- Python 3.10+
- Groq API Key

---

## 🚀 Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/devron04/compliq.git
cd compliq
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment

Create `.env`

```env
GROQ_API_KEY=your_api_key
```

### 4️⃣ Run Application

```bash
python app.py
```

---

# 🧪 Evaluation

## ▶️ Run Inference

```bash
python inference.py --input data/public_test_set.json --output data/public_test_results.json
```

## 📈 Evaluate Results

```bash
python eval_script.py --results data/public_test_results.json
```

---

# 🛠️ Technology Stack

<div align="center">

### ⚙️ Retrieval Layer

```ascii
┌─────────────────────────────────────────────────────┐
│                🔍 Retrieval System                  │
├─────────────────────────────────────────────────────┤
│  ⚡ FAISS  │  🧠 BM25  │  🔄 RRF Fusion             │
└─────────────────────────────────────────────────────┘
```

### 🤖 AI Layer

```ascii
┌─────────────────────────────────────────────────────┐
│                   🧠 LLM Layer                      │
├─────────────────────────────────────────────────────┤
│  🚀 Groq API  │  🦙 Llama 3  │  ⚡ Mixtral         │
└─────────────────────────────────────────────────────┘
```

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,fastapi,git,docker&theme=dark&perline=8" />
</p>

</div>

---

# 📁 Project Structure

```ascii
📦 compliq/
├── 📂 src/                  # Core application logic
├── 📂 data/                 # Vector stores & datasets
├── 🚀 app.py                # Gradio UI
├── 🧪 inference.py          # Judge inference script
├── 📈 eval_script.py        # Evaluation metrics
├── 📋 requirements.txt      # Dependencies
└── 📖 README.md
```

---

# 🔒 Key Highlights

- ✅ Hybrid Semantic + Keyword Retrieval
- ✅ Production-grade RAG Pipeline
- ✅ Hallucination Prevention Layer
- ✅ AI-based Re-ranking
- ✅ Ultra-fast Retrieval
- ✅ Judge-ready Evaluation

---

# ⚖️ License

This project is licensed under the MIT License.

---

<div align="center">

### ❤️ Built with AI, Retrieval Systems & Modern LLM Infrastructure

⭐ Star this repository if you found it useful!

</div>
