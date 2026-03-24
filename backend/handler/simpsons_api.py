"""Simpsons API client — unused at query time if episode JSON is cached in S3."""

import json
from urllib import request

BASE_URL = "https://thesimpsonsapi.com/api"


def get_episode(episode_id: int) -> dict:
    """Fetch a single episode by ID from the Simpsons API."""
    url = f"{BASE_URL}/episodes/{episode_id}"
    response = request.urlopen(url)
    return json.loads(response.read())
