"""
Ingest pipeline: fetch all Simpsons episodes, embed via Bedrock Titan,
build a FAISS index, and upload both the index and episode JSON to S3.

Run once (or on-demand) with valid AWS credentials.
"""

import json
import os
import tempfile

import boto3
import faiss
import numpy as np
import requests
from dotenv import load_dotenv

load_dotenv()

EPISODES_URL = "https://thesimpsonsapi.com/api/episodes"
S3_BUCKET = os.environ["S3_BUCKET"]
FAISS_INDEX_KEY = os.environ["FAISS_INDEX_KEY"]
EPISODES_JSON_KEY = os.environ["EPISODES_JSON_KEY"]
BEDROCK_EMBED_MODEL = os.environ["BEDROCK_EMBED_MODEL"]
AWS_REGION = os.environ["AWS_REGION"]


def fetch_all_episodes() -> list[dict]:
    """Paginate through all pages of the Simpsons API and return every episode."""
    pass


def build_embed_text(episode: dict) -> str:
    """Return embeddable text for an episode; falls back to name if synopsis is empty."""
    pass


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings via Bedrock Titan and return a list of vectors."""
    pass


def build_faiss_index(embeddings: list[list[float]]) -> faiss.IndexFlatIP:
    """Build and return a FAISS IndexFlatIP (cosine similarity) from embeddings."""
    pass


def upload_to_s3(index: faiss.IndexFlatIP, episodes: list[dict]) -> None:
    """Serialize the FAISS index and episode JSON, then upload both to S3."""
    pass


def main() -> None:
    episodes = fetch_all_episodes()
    texts = [build_embed_text(ep) for ep in episodes]
    embeddings = embed_texts(texts)
    index = build_faiss_index(embeddings)
    upload_to_s3(index, episodes)


if __name__ == "__main__":
    main()
