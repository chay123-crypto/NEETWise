# 🧬 NeetWise

**A RAG-powered Biology tutor for NEET aspirants — grounded strictly in NCERT textbooks.**

> Ask any Biology question. Get a clear, cited answer. Or type what you *think* you understand — and get corrected.

🚀 **[Live Demo on Hugging Face Spaces](https://huggingface.co/spaces/chay123-crypto/NeetWise)** · 🟢 Uptime monitored via UptimeRobot

---

## What It Does

NeetWise is a domain-specific Q&A chatbot built for students preparing for the NEET biology exam. Unlike general-purpose LLMs that can hallucinate or go off-syllabus, NeetWise answers *only* from NCERT Class 11 and Class 12 Biology textbooks — with source citations.

It has two core modes:

**📖 Ask a Question**
Type any biology question and get a detailed, NCERT-grounded answer with chapter and page citations. Supports English and Hinglish output, and a "Simple mode" for easier explanations.

**🔍 Misconception Checker**
Write what you think you understand about a concept. The app evaluates it against NCERT content and tells you if you're right, wrong, or partially correct — with specific corrections.

---

## Architecture

```
User Query
    │
    ▼
Ensemble Retriever (BM25 + FAISS)
    │  BM25 weight: 0.35  │  FAISS weight: 0.65
    ▼
Cross-Encoder Reranker (ms-marco-MiniLM-L-6-v2)
    │  Top-3 chunks selected
    ▼
LLM (Llama 3.1-8B via Cerebras)
    │  Streamed response via SSE
    ▼
Answer + Chapter/Page Citations
```

The retrieval pipeline uses a two-stage approach: an ensemble of BM25 (keyword) and FAISS (semantic) retrievers for broad recall, followed by a cross-encoder to rerank and select the most relevant chunks. This is more accurate than single-stage retrieval alone.

An out-of-domain guard is also in place — if the best reranker score is below a threshold, the app declines to answer rather than hallucinate.

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Llama 3.1-8B (via Cerebras API) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Store | FAISS |
| Keyword Retriever | BM25 (LangChain) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Framework | Flask + LangChain |
| Deployment | Hugging Face Spaces (Docker) |
| Streaming | Server-Sent Events (SSE) |
| Monitoring | UptimeRobot (5-min interval health checks) |

---

## Knowledge Base

Covers all NCERT Biology chapters for Classes 11 and 12:

**Class 11** — The Living World, Biological Classification, Plant Kingdom, Animal Kingdom, Cell Biology, Biomolecules, Cell Division, Photosynthesis, Respiration, Neural & Chemical Coordination, and more (19 chapters).

**Class 12** — Reproduction, Genetics & Inheritance, Molecular Biology, Evolution, Human Health, Biotechnology, Ecology, Biodiversity (13 chapters).

---

## Features

- **Streaming responses** — tokens appear as they're generated, no waiting for the full answer
- **Source citations** — every answer cites the NCERT chapter and page number
- **Hinglish support** — answers in a Hindi-English mix for students more comfortable in that register (no Devanagari script)
- **Simple mode** — explains concepts using everyday analogies, suited for beginners
- **Misconception detection** — evaluates student understanding and gives targeted corrections
- **Out-of-domain rejection** — refuses to answer non-biology or off-NCERT questions

---

## Running Locally

```bash
git clone https://huggingface.co/spaces/chay123-crypto/NeetWise
cd NeetWise
pip install -r requirements.txt
```

Create a `.env` file:
```
CEREBRAS_API_KEY=your_cerebras_key
```

Add your NCERT PDF files to:
```
datasets/kebo1dd/   ← Class 11 PDFs (kebo101.pdf ... kebo119.pdf)
datasets/lebo1dd/   ← Class 12 PDFs (lebo101.pdf ... lebo113.pdf)
```

Then run:
```bash
python app.py
```

The app will be available at `http://localhost:7860`.

> **Note:** On first run, the vectorstore is built from the PDFs and saved to `index/`. Subsequent runs load it directly.

---

## Project Structure

```
NeetWise/
├── app.py          # Flask routes, SSE streaming
├── chains.py       # RAG chains, misconception detection, citation logic
├── retriever.py    # BM25 + FAISS ensemble, cross-encoder setup
├── vectorstore.py  # FAISS index build/load
├── loaders.py      # PDF loading and chunking
├── config.py       # Models, paths, chapter map
├── evaluation.py   # Retrieval evaluation utilities
├── templates/      # HTML frontend
└── index/          # Saved FAISS index (generated on first run)
```

---

## Evaluation

The RAG pipeline was evaluated using [RAGAS](https://docs.ragas.io/) on a set of 6 biology questions from different chapters across 11th and 12th with ground-truth answers drawn from NCERT content (implemented in `evaluation.py` via the `evaluate_results` function — backend only, not surfaced in the UI):

| Metric | Score |
|---|---|
| Faithfulness | **0.9487** |
| Answer Relevancy | **0.9325** |
| Context Precision | **0.8333** |

- **Faithfulness (0.95)** — answers are closely grounded in the retrieved NCERT chunks with minimal hallucination.
- **Answer Relevancy (0.93)** — responses are highly relevant to the questions asked.
- **Context Precision (0.83)** — the retriever surfaces the right chunks for the majority of queries.

---

## Limitations

- Answers are limited to NCERT content — advanced or competitive-level biology beyond the syllabus won't be covered
- The app runs on CPU; reranking adds a small latency per query
- Currently supports English and Hinglish only
- UI is not responsive — does not render well on mobile screens

---

## Monitoring

Live uptime is monitored via [UptimeRobot](https://uptimerobot.com), which pings the app every 5 minutes and triggers an alert if it goes down — ensuring the demo stays reliably accessible.

---

## Future Improvements

- **Responsive / Mobile UI** — the current frontend is desktop-only and breaks on smaller screens; a redesign using a mobile-first framework (Tailwind CSS or React) is planned
- **React or Next.js frontend** — replace Jinja/HTML templates with a proper component-based UI for better UX and maintainability
- **Multi-subject support** — extend the knowledge base to Physics and Chemistry for full NEET coverage
- **Chat history** — add conversational memory so students can ask follow-up questions in context
- **Quiz mode** — auto-generate MCQs from retrieved chunks to help students self-test
- **Evaluation dashboard** — wire up `evaluation.py` to a visible benchmark tracking retrieval quality (MRR, NDCG) over time
- **Replace pickle store** — migrate `all_docs.pkl` to JSON/Parquet to remove the HuggingFace security flag

---

## Author

Built by [chay123-crypto](https://huggingface.co/chay123-crypto)
