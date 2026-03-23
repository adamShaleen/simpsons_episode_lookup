"""Bedrock wrappers: Titan embeddings and Claude Haiku response formatting."""

import json
import os

import boto3

EMBED_MODEL = os.environ["BEDROCK_EMBED_MODEL"]
CHAT_MODEL = os.environ["BEDROCK_CHAT_MODEL"]
AWS_REGION = os.environ["AWS_REGION"]

_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def embed(text: str) -> list[float]:
    """Embed a string via Titan Text Embeddings v2 and return the vector."""
    pass


def format_response(query: str, episodes: list[dict]) -> str:
    """Call Claude Haiku with the user query and matched episodes; return formatted text."""
    pass
