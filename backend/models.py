from typing import TypedDict


class Episode(TypedDict):
    id: int
    airdate: str
    episode_number: int
    image_path: str
    name: str
    season: int
    synopsis: str
