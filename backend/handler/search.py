"""FAISS index loader and episode search. Index and episodes are cached in module globals
after the first load (warm Lambda reuse)."""

import json
import os

import boto3
import faiss
import numpy

from backend.handler import bedrock
from backend.models import Episode

S3_BUCKET = os.environ["S3_BUCKET"]
FAISS_INDEX_KEY = os.environ["FAISS_INDEX_KEY"]
EPISODES_JSON_KEY = os.environ["EPISODES_JSON_KEY"]
AWS_REGION = os.environ["AWS_REGION"]

_s3 = boto3.client("s3", region_name=AWS_REGION)

# Module-level cache — populated on first invocation
_index: faiss.IndexFlatIP | None = None
_episodes: list[Episode] | None = None


def _load_assets() -> None:
    """Download FAISS index and episode JSON from S3 into /tmp; populate module cache."""
    global _index, _episodes

    if _index is not None:
        return

    local_path = "/tmp/episodes.index"
    _s3.download_file(Bucket=S3_BUCKET, Key=FAISS_INDEX_KEY, Filename=local_path)
    _index = faiss.read_index(local_path)

    get_object_response = _s3.get_object(Bucket=S3_BUCKET, Key=EPISODES_JSON_KEY)
    _episodes = json.loads(get_object_response["Body"].read())


def find_episodes(query: str, top_k: int = 3) -> list[Episode]:
    """Embed the query, run FAISS search, and return the top-k matched episode dicts."""
    _load_assets()
    embedding = bedrock.embed(query)
    vector = numpy.array([embedding], dtype=numpy.float32)

    assert _index is not None and _episodes is not None
    _, indices = _index.search(vector, top_k)  # type: ignore
    return [_episodes[int(i)] for i in indices[0]]
