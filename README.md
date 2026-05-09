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

### What is MRR?
We utilize **MRR (Mean Reciprocal Rank)** to measure retrieval quality. A score of 0.86 indicates that our system consistently places the most relevant standard at the very top of the results, significantly reducing manual search time for engineers and compliance officers.

---

## ⚙️ Quick Start & Setup

### Prerequisites
- **Python 3.10+**
- **Groq API Key**: Obtain one for free at [console.groq.com](https://console.groq.com/).

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/devron04/compliq.git
   cd compliq
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

### Running Locally
To launch the interactive Gradio dashboard:
```bash
python app.py
```

---

## 🧪 How to Reproduce Results
Verify our performance metrics locally:

**1. Run Evaluation Suite:**
```bash
python eval_script.py
```
*Outputs the Hit Rate and MRR metrics for the entire test set.*

**2. Test Raw Inference:**
```bash
python inference.py --query "bricks for black soil"
```

---

## 🏗️ Architecture: Hybrid RAG + RRF
CompliQ uses a sophisticated "Senior Level" retrieval strategy:
1. **Dense Retrieval (FAISS)**: Captures semantic meaning and intent using `BAAI/bge-small-en-v1.5`.
2. **Sparse Retrieval (BM25)**: Ensures precise keyword matching for specific standard IDs and material names.
3. **Reciprocal Rank Fusion (RRF)**: Merges results from both methods to provide a mathematically optimized final ranking.
4. **AI Rationales**: Uses LLMs (Llama 3/Mixtral via Groq) to generate context-aware explanations for every recommendation.

## 🛠️ Technology Stack
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Retriever**: Rank-BM25
- **LLM Interface**: Groq API
- **UI**: Gradio 5 (Responsive Dark Theme)

## 📁 Project Structure
- `app.py`: Production entry point (Root).
- `src/`: Core logic (Pipeline, Retriever, Embeddings).
- `data/`: Pre-computed vector stores and BIS dataset.
- `assets/`: Documentation media and UI demonstrations.

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
