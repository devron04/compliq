# 🏛️ CompliQ: BIS Standards Recommendation Engine

[![Evaluation Score](https://img.shields.io/badge/Evaluation-100%25%20Hit%20Rate-brightgreen)](https://github.com/devron04/compliq)
[![Live Demo](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Live%20Demo-blue)](https://huggingface.co/spaces/Ronakk0412/CompliQ)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**CompliQ** is a production-grade, AI-powered search engine designed to instantly map building materials and products to their relevant **Bureau of Indian Standards (BIS)** regulations using a high-speed, hallucination-free RAG pipeline.

![CompliQ Interface](assets/app_demo.png)

## 📊 Performance & Evaluation
CompliQ is a measured retrieval system, rigorously tested against a curated golden dataset of BIS standards.

- **Hit Rate @ 3**: **100%** (Verified on official public test set).
- **Mean Reciprocal Rank (MRR)**: **0.83** (Exceeds 0.7 target).
- **Average Latency**: **~2.1s** (Safely under 5s target; <400ms for fast queries).

---

## 🧪 How to Reproduce Results (Judges)
Judges can verify our results using the mandatory evaluation entry-points:

**1. Generate Results (Inference):**
```bash
<<<<<<< HEAD
python inference.py --input data/public_test_set.json --output public_test_results.json
=======
python inference.py --input data/public_test_set.json --output data/public_test_results.json
>>>>>>> 3986eb67ec8d6151a4bdcd06c014589830cee584
```
*This command runs the RAG pipeline on the test set and saves the predictions.*

**2. Calculate Metrics (Evaluation):**
```bash
<<<<<<< HEAD
python eval_script.py --results public_test_results.json
=======
python eval_script.py --results data/public_test_results.json
>>>>>>> 3986eb67ec8d6151a4bdcd06c014589830cee584
```
*This script grades the generated results and outputs the official Hit Rate and MRR scores.*

---

## 🏗️ Architecture: Hybrid RAG + RRF
CompliQ uses a sophisticated "Senior Level" retrieval strategy:
1. **Dense Retrieval (FAISS)**: Captures semantic meaning and intent using `BAAI/bge-small-en-v1.5`.
2. **Sparse Retrieval (BM25)**: Ensures precise keyword matching for specific standard IDs and material names.
3. **Reciprocal Rank Fusion (RRF)**: Merges results from both methods to provide a mathematically optimized final ranking.
4. **AI Rationales & Re-ranking**: Uses LLMs (Llama 3 via Groq) to filter and rank the most specific product matches at the top.
5. **Anti-Hallucination Whitelist**: A strict code-level filter that discards any standard ID not found in the original retrieved context.
6. **Latency Guard**: A hard timeout mechanism that automatically falls back to raw retrieval if the LLM takes too long, guaranteeing a response within the 5s limit.

## ⚙️ Quick Start & Setup

### Prerequisites
- **Python 3.10+**
- **Groq API Key**: Obtain one for free at [console.groq.com](https://console.groq.com/).

### Installation
1. **Clone & Install:**
   ```bash
   git clone https://github.com/devron04/compliq.git
   pip install -r requirements.txt
   ```
2. **Configure Env:** Create a `.env` file and add `GROQ_API_KEY=your_key`.
3. **Run UI:** `python app.py`

## 🛠️ Technology Stack
- **Vector DB**: FAISS
- **Retriever**: Rank-BM25 (Hybrid Keyword + Semantic)
- **Embedding Model**: BAAI/bge-small-en-v1.5
- **LLM Interface**: Groq API (Llama 3 / Mixtral)

## 📁 Package Structure
- `/src`: Main application logic.
- `/data`: Public test sets and indexed vector stores.
- `app.py`: Gradio Web Interface entry point.
- `inference.py`: **Mandatory judge entry point.**
- `eval_script.py`: **Mandatory evaluation script.**
- `requirements.txt`: System dependencies.

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
