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

from backend.ingest.models import EpisodeResponse
from backend.models import Episode

load_dotenv()

EPISODES_URL = "https://thesimpsonsapi.com/api/episodes"
S3_BUCKET = os.environ["S3_BUCKET"]
FAISS_INDEX_KEY = os.environ["FAISS_INDEX_KEY"]
EPISODES_JSON_KEY = os.environ["EPISODES_JSON_KEY"]
BEDROCK_EMBED_MODEL = os.environ["BEDROCK_EMBED_MODEL"]
AWS_REGION = os.environ["AWS_REGION"]

_bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)
_s3 = boto3.client("s3", region_name=AWS_REGION)


def fetch_all_episodes() -> list[Episode]:
    """Paginate through all pages of the Simpsons API and return every episode."""
    episodes: list[Episode] = []
    url = EPISODES_URL

    while url:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data: EpisodeResponse = response.json()
        episodes.extend(data["results"])
        url = data["next"]

    return episodes


def build_embed_text(episode: Episode) -> str:
    """Return embeddable text for an episode; falls back to name if synopsis is empty."""
    name = episode["name"]
    synopsis = episode["synopsis"]

    return f"{name}. {synopsis}" if synopsis else name


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings via Bedrock Titan and return a list of vectors."""
    result = []

    for text in texts:
        response = _bedrock.invoke_model(modelId=BEDROCK_EMBED_MODEL, body=json.dumps({"inputText": text}))
        data = json.loads(response["body"].read())

        embedding = data["embedding"]
        result.append(embedding)

    return result


def build_faiss_index(embeddings: list[list[float]]) -> faiss.IndexFlatIP:
    """Build and return a FAISS IndexFlatIP (cosine similarity) from embeddings."""
    vectors = np.array(embeddings, dtype="float32")
    faiss.normalize_L2(vectors)

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)  # type: ignore

    return index


def upload_to_s3(index: faiss.IndexFlatIP, episodes: list[Episode]) -> None:
    """Serialize the FAISS index and episode JSON, then upload both to S3."""
    with tempfile.TemporaryDirectory() as temp_dir:
        index_path = os.path.join(temp_dir, "episodes.index")
        faiss.write_index(index, index_path)
        _s3.upload_file(index_path, S3_BUCKET, FAISS_INDEX_KEY)

    _s3.put_object(Bucket=S3_BUCKET, Key=EPISODES_JSON_KEY, Body=json.dumps(episodes), ContentType="application/json")


def main() -> None:
    episodes = fetch_all_episodes()
    texts = [build_embed_text(ep) for ep in episodes]
    embeddings = embed_texts(texts)
    index = build_faiss_index(embeddings)
    upload_to_s3(index, episodes)


if __name__ == "__main__":
    main()
