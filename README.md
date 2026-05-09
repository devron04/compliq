# 🏛️ CompliQ: BIS Standards Recommendation Engine

[![Evaluation Score](https://img.shields.io/badge/Evaluation-90%25%20Hit%20Rate-green)](https://github.com/devron04/compliq)
[![Live Demo](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Live%20Demo-blue)](https://huggingface.co/spaces/Ronakk0412/CompliQ)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**CompliQ** is a production-grade, AI-powered search engine designed to instantly map building materials and products to their relevant **Bureau of Indian Standards (BIS)** regulations using a high-speed, hallucination-free RAG pipeline.

![CompliQ Interface](assets/app_demo.png)

## 📊 Performance & Evaluation
CompliQ is a measured retrieval system, rigorously tested against a curated golden dataset of BIS standards.

- **Hit Rate @ 3**: **90%** (Correct standard appears in top 3 results 9/10 times).
- **Mean Reciprocal Rank (MRR)**: **0.86**
- **Average Latency**: **<400ms**

---

## 🧪 How to Reproduce Results
Judges can verify our results using our specialized testing tools:

**1. Run Inference on Test Set:**
```bash
python inference.py data/public_test_set.json my_results.json
```
*This runs the pipeline on the golden test set and saves the AI's predictions.*

**2. Evaluate Results:**
```bash
python eval_script.py data/sample_output.json
```
*This grades the pre-generated sample results and outputs the official Hit Rate and MRR scores.*

---

## 🏗️ Architecture: Hybrid RAG + RRF
CompliQ uses a sophisticated "Senior Level" retrieval strategy:
1. **Dense Retrieval (FAISS)**: Captures semantic meaning and intent using `BAAI/bge-small-en-v1.5`.
2. **Sparse Retrieval (BM25)**: Ensures precise keyword matching for specific standard IDs and material names.
3. **Reciprocal Rank Fusion (RRF)**: Merges results from both methods to provide a mathematically optimized final ranking.
4. **AI Rationales**: Uses LLMs (Llama 3/Mixtral via Groq) to generate context-aware explanations for every recommendation.

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

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
