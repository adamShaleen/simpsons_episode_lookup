"""Lambda entry point. Expects API Gateway HTTP API GET /search?q={query}."""

import json

from backend.handler import bedrock, search


def lambda_handler(event: dict, _context: object) -> dict:
    """Parse query, find matching episodes, format response, return HTTP 200."""
    params = event.get("queryStringParameters") or {}
    query = params.get("q")

    if not query:
        return {"statusCode": 400, "body": json.dumps({"error": "missing query parameter 'q'"})}

    episodes = search.find_episodes(query)

    return {"statusCode": 200, "body": json.dumps({"response": bedrock.format_response(query, episodes)})}
