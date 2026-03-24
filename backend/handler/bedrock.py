"""Bedrock wrappers: Titan embeddings and Claude Haiku response formatting."""

import json
import os

import boto3

from backend.models import Episode

EMBED_MODEL = os.environ["BEDROCK_EMBED_MODEL"]
CHAT_MODEL = os.environ["BEDROCK_CHAT_MODEL"]
AWS_REGION = os.environ["AWS_REGION"]

_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)


SYSTEM_PROMPT = (
    "You are a Simpsons episode assistant. Given a user's description and one or more "
    "matching episode objects, return a concise response identifying the episode(s) and "
    "why they match. Include season, episode number, title, and a brief synopsis. "
    "Be conversational."
)


def embed(text: str) -> list[float]:
    """Embed a string via Titan Text Embeddings v2 and return the vector."""
    response = _client.invoke_model(modelId=EMBED_MODEL, body=json.dumps({"inputText": text}))
    data = json.loads(response["body"].read())
    return data["embedding"]


def format_response(query: str, episodes: list[Episode]) -> str:
    """Call Claude Haiku with the user query and matched episodes; return formatted text."""
    content = f'Query: "{query}"\n\nMatched episodes:\n{json.dumps(episodes, indent=2)}'

    request_body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": content}],
        }
    )

    response = _client.invoke_model(
        modelId=CHAT_MODEL,
        body=request_body,
    )

    data = json.loads(response["body"].read())
    return data["content"][0]["text"]
