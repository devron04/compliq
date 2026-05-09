---
title: CompliQ
emoji: 🏛️
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.0.1
python_version: "3.10"
app_file: app.py
pinned: false
license: mit
---

# CompliQ: AI-Powered BIS Standards Recommendation Engine

**CompliQ** is a high-performance RAG (Retrieval-Augmented Generation) system designed to instantly match product descriptions with relevant **Bureau of Indian Standards (BIS)**. Built for the BIS Hackathon, it solves the challenge of navigating complex regulatory documents using state-of-the-art AI.

---

## 🎥 Deliverables
* **Presentation Deck**: [Link to presentation.pdf (Add your link here)](#)
* **Demo Video**: [Link to 7-minute demo (Add your YouTube/Drive link here)](#)

---

## 🚀 Performance Metrics
*   **Hit Rate @ 3**: **100.00%** (Target: >80%)
*   **MRR @ 5 (Mean Reciprocal Rank)**: **0.8333** (Target: >0.7)
*   **Avg. Latency**: **~1.98 seconds** (Target: <5s)

---

## 🛠️ Technical Architecture

### 1. Hybrid Retrieval Pipeline
Unlike standard RAG systems that only use vector search, CompliQ uses a **Dual-Engine Retrieval** strategy:
*   **Semantic Search (FAISS)**: Captures the "meaning" and intent behind the query using `BAAI/bge-small-en-v1.5` embeddings.
*   **Keyword Search (Rank-BM25)**: Ensures 100% accuracy for specific technical terms and IS numbers (e.g., "IS 269", "Grade 53").
*   **RRF (Reciprocal Rank Fusion)**: Combines both engines to deliver the most relevant results at the top.

### 2. Anti-Hallucination Layer
We implemented a strict **Double-Verification** mechanism:
*   **Context Injection**: The LLM (Llama-3.1-8B via Groq) is restricted to a specific retrieved context.
*   **Python Logic Filter**: Any IS number suggested by the AI is cross-referenced against the actual retrieved document IDs. If it doesn't exist in the database, it is filtered out.

### 3. Structural PDF Parsing
Standard chunking (fixed size) breaks technical tables and IS numbers. We built a **Custom Structural Parser** that understands the hierarchy of BIS documents, ensuring chunks preserve the relationship between a Standard ID and its Scope.

---

## 🖥️ User Interface
CompliQ features a **Lightweight Gradio UI** optimized for performance. It provides:
*   Natural language product querying.
*   Category-based filtering (Cement, Steel, Aggregates, etc.).
*   Detailed rationales for every recommendation.
*   Real-time latency tracking.

---

## 🛠️ Tech Stack
*   **LLM**: Llama-3.1-8B (Groq Cloud)
*   **Embeddings**: BAAI/bge-small-en-v1.5 (HuggingFace)
*   **Vector DB**: FAISS
*   **Search**: Rank-BM25
*   **UI**: Gradio
*   **Language**: Python 3.13

---

## ⚙️ Installation & Setup

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/devron04/compliq.git
   cd compliq
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**:
   Create a `.env` file and add:
   ```env
   GROQ_API_KEY=your_key_here
   ```

4. **Run the App**:
   ```bash
   python src/app.py
   ```

---

## 📂 Project Structure
*   `src/ingest.py`: Structural PDF parsing and chunking.
*   `src/retriever.py`: Hybrid Search implementation (FAISS + BM25).
*   `src/pipeline.py`: Orchestration and Anti-Hallucination logic.
*   `src/app.py`: Gradio Web UI.
*   `inference.py`: Automated batch evaluation script.

---

## 📜 Disclosures & Constraints
* **External APIs**: This project uses the **Groq Cloud API** (`llama-3.1-8b-instant`) for extremely fast, low-latency LLM generation. An active internet connection and valid API key are required to run the full pipeline.
* **Hardware Requirements**: The hybrid retrieval system (FAISS + BM25) and sentence embeddings run entirely on CPU. It has been tested and is fully runnable on standard consumer hardware.
* **Dataset Integrity**: All retrieval and generation are strictly grounded in the official provided dataset (BIS SP 21 Summaries). No external knowledge or internet search is utilized to answer queries.

---
*Developed for the BIS Hackathon by devron04*
