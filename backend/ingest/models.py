from typing import TypedDict

from backend.models import Episode


class EpisodeResponse(TypedDict):
    count: int
    next: str | None
    prev: str | None
    pages: int
    results: list[Episode]
