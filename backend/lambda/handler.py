"""Lambda entry point. Expects API Gateway HTTP API GET /search?q={query}."""

import json

import bedrock
import search


def lambda_handler(event: dict, context: object) -> dict:
    """Parse query, find matching episodes, format response, return HTTP 200."""
    pass
