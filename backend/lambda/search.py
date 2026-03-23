"""FAISS index loader and episode search. Index and episodes are cached in module globals
after the first load (warm Lambda reuse)."""

import json
import os

import boto3
import faiss

S3_BUCKET = os.environ["S3_BUCKET"]
FAISS_INDEX_KEY = os.environ["FAISS_INDEX_KEY"]
EPISODES_JSON_KEY = os.environ["EPISODES_JSON_KEY"]
AWS_REGION = os.environ["AWS_REGION"]

_s3 = boto3.client("s3", region_name=AWS_REGION)

# Module-level cache — populated on first invocation
_index: faiss.IndexFlatIP | None = None
_episodes: list[dict] | None = None


def _load_assets() -> None:
    """Download FAISS index and episode JSON from S3 into /tmp; populate module cache."""
    pass


def find_episodes(query: str, top_k: int = 3) -> list[dict]:
    """Embed the query, run FAISS search, and return the top-k matched episode dicts."""
    pass
