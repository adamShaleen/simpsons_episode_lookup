# CLAUDE.md — Simpsons Episode Finder

## Project Overview

A mobile app (iOS/SwiftUI) that accepts a user's description or keywords and returns a matching Simpsons episode, powered by semantic search via Amazon Bedrock and a FAISS vector index built from the Simpsons episode API.

---

## Architecture

### Ingest Pipeline (run once / on-demand)

```
Simpsons Episode API (free, public)
  → ingest Lambda (or local script)
  → Amazon Bedrock Titan Embeddings (text-embedding-v2)
  → FAISS index built in-memory
  → index serialized and uploaded to S3
```

### Query Path (per user request)

```
iOS (SwiftUI)
  → API Gateway (HTTP API)
  → query Lambda (container image)
      → embed user query via Titan Embeddings
      → load FAISS index from S3 (cached in /tmp after first load)
      → top-k nearest neighbor search
      → fetch matched episode objects from Simpsons API (or from cached JSON in S3)
      → pass episode data + user query to Claude Haiku
      → return formatted response
  → iOS displays result
```

---

## AWS Services & Rationale

| Service                                   | Purpose                                         | Cost                               |
| ----------------------------------------- | ----------------------------------------------- | ---------------------------------- |
| Amazon Bedrock — Titan Text Embeddings v2 | Embed episode synopses + user queries           | Per-token, near zero at this scale |
| Amazon Bedrock — Claude Haiku             | Format final response from matched episode data | ~$0.001/query                      |
| S3                                        | Store FAISS index file + episode JSON cache     | Effectively $0                     |
| Lambda (container image)                  | Query handler                                   | Free tier                          |
| API Gateway (HTTP API)                    | iOS → Lambda endpoint                           | Free tier                          |
| ECR                                       | Container image registry                        | 500MB free/month                   |
| CloudWatch                                | Logs                                            | Free tier                          |

**No OpenSearch, no RDS, no Pinecone.** Vector store is a FAISS index file in S3, loaded into Lambda memory at runtime.

---

## Repository Structure

```
simpsons-episode-finder/
├── CLAUDE.md
├── backend/
│   ├── ingest/
│   │   ├── ingest.py          # One-time script: fetch API → embed → build FAISS index → upload to S3
│   │   └── requirements.txt
│   ├── lambda/
│   │   ├── handler.py         # Lambda entry point
│   │   ├── search.py          # FAISS load + query logic
│   │   ├── bedrock.py         # Titan embed + Haiku call wrappers
│   │   ├── simpsons_api.py    # Simpsons API client
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── infra/
│       └── (CDK or manual setup notes — TBD)
├── ios/
│   └── SimpsonsFinder/
│       └── (SwiftUI project)
└── .env.example
```

---

## Simpsons Episode API

- **Base URL:** `https://thesimpsonsapi.com/api`
- **Episodes endpoint:** `https://thesimpsonsapi.com/api/episodes`
- No authentication required
- Current count: 768 episodes across 39 pages
- **Pagination:** fixed at 20 items per page, cannot be customized
  - Envelope fields: `count`, `next` (url or null), `prev` (url or null), `pages`, `results`
  - Must iterate all 39 pages to retrieve full dataset during ingest

### Episode object shape

```json
{
  "id": 1,
  "airdate": "1989-12-17",
  "episode_number": 1,
  "image_path": "/episode/1.webp",
  "name": "Simpsons Roasting on an Open Fire",
  "season": 1,
  "synopsis": "..."
}
```

**Field notes:**

- `airdate` — ISO date string; may be an **empty string** for some episodes
- `synopsis` — may be an **empty string** for some episodes; handle gracefully in ingest (skip or flag)
- `image_path` — relative path; full CDN URL is `https://cdn.thesimpsonsapi.com/500{image_path}`
- `name` — episode title field (not `title`)

### Ingest strategy

- Paginate through all 39 pages, collecting `results` arrays
- Cache the full episode array as JSON in S3 — avoids re-fetching at query time and removes runtime dependency on the external API
- Episodes with empty `synopsis` should still be embedded using `name` alone, but flag them — match quality will be lower

---

## Ingest Script (`backend/ingest/ingest.py`)

**Responsibilities:**

1. GET all episodes from the Simpsons API
2. For each episode, construct an embeddable text string (e.g. `"{name}. {synopsis}"`) — use `name` alone if `synopsis` is empty
3. Call Bedrock Titan Embeddings in batches (respect API rate limits)
4. Build a FAISS `IndexFlatIP` (inner product / cosine similarity) index
5. Serialize index with `faiss.write_index`
6. Upload FAISS index file to S3
7. Upload episode JSON array to S3 (keyed by FAISS index position)

**Run locally** with appropriate AWS credentials before deploying Lambda.

---

## Lambda (`backend/lambda/`)

### Runtime

- Python 3.12
- Deployed as a **container image** via ECR (avoids FAISS package size issues with zip deploys)

### Dockerfile notes

- Base image: `public.ecr.aws/lambda/python:3.12`
- Install FAISS: `pip install faiss-cpu`
- Copy handler and supporting modules
- `CMD ["handler.lambda_handler"]`

### handler.py

- Entry point: `lambda_handler(event, context)`
- Parses query string from API Gateway event
- Calls `search.find_episodes(query, top_k=3)`
- Calls `bedrock.format_response(query, matched_episodes)`
- Returns HTTP 200 with JSON body

### search.py

- On cold start: download FAISS index from S3 to `/tmp`, load into memory, download episode JSON
- Cache both in module-level globals (warm Lambda reuse)
- Embed incoming query via Titan Embeddings
- Run FAISS search, return top-k episode objects

### bedrock.py

- `embed(text: str) -> list[float]` — calls `amazon.titan-embed-text-v2:0`
- `format_response(query: str, episodes: list[dict]) -> str` — calls `anthropic.claude-haiku-4-5` with a prompt that includes the matched episode data and instructs Haiku to return a helpful, conversational response

### Prompt design (Haiku call)

```
System: You are a Simpsons episode assistant. Given a user's description and one or more
matching episode objects, return a concise response identifying the episode(s) and why
they match. Include season, episode number, title, and a brief synopsis. Be conversational.

User: Query: "{user_query}"

Matched episodes:
{json.dumps(episodes, indent=2)}
```

---

## API Gateway

- **Type:** HTTP API (not REST API — simpler, cheaper)
- Single route: `GET /search?q={query}`
- Lambda integration
- No auth for now (add API key header later if desired)
- CORS enabled (required for any future web client; good habit)

---

## iOS App (`ios/SimpsonsFinder/`)

- **Framework:** SwiftUI
- **Target:** iOS 17+
- **Structure:**
  - `ContentView` — search input + results display
  - `EpisodeViewModel` — `@Observable`, handles API call to API Gateway, holds result state
  - `APIClient` — URLSession wrapper for the API Gateway endpoint
- **No third-party dependencies** — vanilla URLSession, no Alamofire
- Store the API Gateway base URL in a `Config.swift` or `.xcconfig` (not hardcoded)

---

## Environment / Configuration

```.env.example
AWS_REGION=us-east-1
S3_BUCKET=simpsons-finder-assets
FAISS_INDEX_KEY=faiss/episodes.index
EPISODES_JSON_KEY=faiss/episodes.json
BEDROCK_EMBED_MODEL=amazon.titan-embed-text-v2:0
BEDROCK_CHAT_MODEL=anthropic.claude-haiku-4-5-20251001
```

Lambda receives these as environment variables set at deploy time.

---

## IAM

Lambda execution role needs:

- `bedrock:InvokeModel` on the two model ARNs
- `s3:GetObject` on the S3 bucket/keys
- Standard Lambda logging policy (`AWSLambdaBasicExecutionRole`)

Ingest script (local) needs the same S3 and Bedrock permissions on your dev IAM user/profile.

---

## Interaction Conventions

- **Do not generate code unless explicitly asked.** Provide architecture, design decisions, and explanations only.
- **Do not over-explain.** Assume strong AWS + TypeScript background; Python is being actively learned so Python-specific patterns can be briefly noted when non-obvious.
- **Code-first when code is requested.** Minimal prose around it.
- **Ask before making structural changes** to the architecture or file layout.
- **Flag costs** any time a suggested service or approach has non-trivial AWS billing implications.
- **Response style** responses should be clear and concise and avoid sycophancy and unnecessary conversation
