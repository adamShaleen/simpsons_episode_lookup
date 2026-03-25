"""Bedrock wrappers: Titan embeddings and Claude Haiku response formatting."""

import json
import os

import boto3

from backend.models import Episode, EpisodeResult

EMBED_MODEL = os.environ["BEDROCK_EMBED_MODEL"]
CHAT_MODEL = os.environ["BEDROCK_CHAT_MODEL"]
AWS_REGION = os.environ["AWS_REGION"]

_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)


SYSTEM_PROMPT = (
    "You are a Simpsons episode assistant. Given a user's description or keywords, return a raw JSON array of matching "
    "episode data. No prose, no markdown, no code fences — only the JSON array. "
    "Each object must have exactly these fields: title, season, episode_number, airdate, synopsis (1 to 2 sentences). "
    "Always return a JSON array, even if there is only one match. "
    "If one episode is an obvious match, return only that episode. If the query is ambiguous, return up to 3 results. "
    "Order results by relevance to the user's query, most relevant first."
)


def embed(text: str) -> list[float]:
    """Embed a string via Titan Text Embeddings v2 and return the vector."""
    response = _client.invoke_model(modelId=EMBED_MODEL, body=json.dumps({"inputText": text}))
    data = json.loads(response["body"].read())
    return data["embedding"]


def format_response(query: str, episodes: list[Episode]) -> list[EpisodeResult]:
    """Call Claude Haiku with the user query and matched episodes; return structured episode list."""
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
    text = data["content"][0]["text"].strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1]  # drop the opening ```json line
        text = text.rsplit("```", 1)[0]  # drop the closing ```

    return json.loads(text.strip())
