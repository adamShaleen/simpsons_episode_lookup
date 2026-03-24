# The Simpsons Episode Lookup

A mobile app (iOS/SwiftUI) that accepts a description or keywords and returns a matching Simpsons episode using semantic search.

---

## Architecture

### Ingest Pipeline *(run once / on-demand)*
```
Simpsons Episode API → Bedrock Titan Embeddings → FAISS index → S3
```

### Query Path *(per user request)*
```
iOS → API Gateway → Lambda → Titan Embeddings → FAISS search → Claude Haiku → iOS
```

---

## Stack

| Layer | Technology |
|---|---|
| Mobile | SwiftUI (iOS 17+) |
| API | AWS API Gateway (HTTP API) |
| Compute | AWS Lambda (container image) |
| Embeddings | Amazon Bedrock — Titan Text Embeddings v2 |
| LLM | Amazon Bedrock — Claude Haiku |
| Vector store | FAISS index file in S3 |

---

## Project Status

| Component | Status |
|---|---|
| Project scaffolding | ✅ Complete |
| Python tooling (ruff + pytest) | ✅ Complete |
| Backend — ingest script | 🔄 In progress |
| Backend — Lambda handler | 🔄 In progress |
| iOS app | 🔄 In progress |
| AWS infrastructure | ⏳ Not started |
| API Gateway setup | ⏳ Not started |
| Deployment pipeline | ⏳ Not started |

---

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -r backend/ingest/requirements.txt
pip install -r backend/lambda/requirements.txt
```

Copy `.env.example` to `.env` and fill in your AWS values before running the ingest script.

---

## Running Tests

```bash
pytest
```

## Linting & Formatting

```bash
ruff check backend/
ruff format backend/
```
