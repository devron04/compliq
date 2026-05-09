# 🏛️ CompliQ: BIS Standards Recommendation Engine

**CompliQ** is a high-performance, AI-powered search engine designed to help construction professionals, manufacturers, and regulators instantly find the relevant **Bureau of Indian Standards (BIS)** for any building material or product.

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Ronakk0412/CompliQ)

## 🚀 Live Demo
Access the live application here: **[CompliQ on Hugging Face](https://huggingface.co/spaces/Ronakk0412/CompliQ)**

## ✨ Key Features
- **Hybrid Search Architecture**: Combines semantic understanding (FAISS) with precise keyword matching (BM25).
- **AI-Powered Rationales**: Provides clear explanations for why a specific standard was recommended.
- **Ultra-Low Latency**: Optimized pipeline delivers results in under 500ms.
- **Verified Context**: Every result is checked against the original BIS dataset to prevent hallucinations.

## 🛠️ Technology Stack
- **Engine**: Python 3.10
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Retriever**: Rank-BM25
- **LLM Interface**: Groq API (Llama 3 / Mixtral)
- **UI Framework**: Gradio 5

## 📁 Project Structure
- `app.py`: Main entry point for the Hugging Face Space.
- `src/`: Core logic (Pipeline, Retriever, Embeddings).
- `data/`: Indexed BIS standards and pre-computed vector stores.
- `requirements.txt`: Project dependencies.

## 🤝 Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
