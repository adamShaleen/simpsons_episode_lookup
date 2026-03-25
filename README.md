# The Simpsons Episode Lookup

A web app that accepts a description or keywords and returns a matching Simpsons episode using semantic search.

---

## Architecture

### Ingest Pipeline _(run once / on-demand)_

```
Simpsons Episode API → Bedrock Titan Embeddings → FAISS index → S3
```

### Query Path _(per user request)_

```
Browser → API Gateway → Lambda → Titan Embeddings → FAISS search → Claude Haiku → Browser
```

---

## Stack

| Layer        | Technology                                |
| ------------ | ----------------------------------------- |
| Frontend     | React / TypeScript / Vite (hosted on S3)  |
| API          | AWS API Gateway (HTTP API)                |
| Compute      | AWS Lambda (container image)              |
| Embeddings   | Amazon Bedrock — Titan Text Embeddings v2 |
| LLM          | Amazon Bedrock — Claude Haiku             |
| Vector store | FAISS index file in S3                    |

---

## Project Status

| Component  
| ------------------------------ |
| Project scaffolding |
| Python tooling (ruff + pytest) |
| Backend — ingest script |
| Backend — Lambda handler |
| AWS infrastructure |
| Frontend — web app |

---

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -r backend/ingest/requirements.txt
pip install -r backend/handler/requirements.txt
```

Copy `.env.example` to `.env` and fill in your AWS values before running the ingest script.

---

## Deploying the Backend

Requires Docker Desktop running and AWS credentials with ECR and Lambda permissions.

Set these variables from your `.env` before running the steps below:

```bash
export AWS_ACCOUNT_ID=your_account_id
export AWS_REGION=us-west-2
```

**0. Start Docker Desktop**

Ensure Docker Desktop is running before proceeding.

**1. Authenticate Docker with ECR**

```bash
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
```

**2. Build the image**

```bash
docker build --platform linux/amd64 --provenance=false -t simpsons-episode-lookup -f backend/handler/Dockerfile .
```

**3. Tag the image**

```bash
docker tag simpsons-episode-lookup:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/simpsons-episode-lookup:latest
```

**4. Push to ECR**

```bash
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/simpsons-episode-lookup:latest
```

**5. Update the Lambda function**

```bash
aws lambda update-function-code --function-name simpsons-episode-lookup --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/simpsons-episode-lookup:latest --region $AWS_REGION
```

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
