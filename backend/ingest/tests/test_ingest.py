import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from backend.ingest.ingest import build_embed_text, build_faiss_index, embed_texts, fetch_all_episodes, upload_to_s3
from backend.models import Episode


def test_fetch_all_episodes_raises_on_non_200():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Client Error")

    with patch("backend.ingest.ingest.requests.get", return_value=mock_response):
        with pytest.raises(requests.HTTPError):
            fetch_all_episodes()


def test_fetch_all_episodes_paginates_all_pages():
    page_1 = MagicMock()
    page_1.json.return_value = {
        "count": 2,
        "next": "https://thesimpsonsapi.com/api/episodes?page=2",
        "prev": None,
        "pages": 2,
        "results": [
            {
                "id": 1,
                "name": "Episode 1",
                "synopsis": "Test synopsis",
                "season": 1,
                "episode_number": 1,
                "airdate": "",
                "image_path": "",
            }
        ],
    }

    page_2 = MagicMock()
    page_2.json.return_value = {
        "count": 2,
        "next": None,
        "prev": "https://thesimpsonsapi.com/api/episodes",
        "pages": 2,
        "results": [
            {
                "id": 2,
                "name": "Episode 2",
                "synopsis": "Test synopsis",
                "season": 1,
                "episode_number": 2,
                "airdate": "",
                "image_path": "",
            }
        ],
    }

    with patch("backend.ingest.ingest.requests.get", side_effect=[page_1, page_2]) as mock_get:
        episodes = fetch_all_episodes()

    assert mock_get.call_count == 2
    assert len(episodes) == 2
    assert episodes[0]["id"] == 1
    assert episodes[1]["id"] == 2


mock_episode: Episode = {
    "id": 1,
    "airdate": "mock_air_date",
    "episode_number": 1,
    "image_path": "mock_image_path",
    "name": "mock_name",
    "season": 1,
    "synopsis": "",
}


@pytest.mark.parametrize(
    "episode, expected",
    [(mock_episode, "mock_name"), ({**mock_episode, "synopsis": "mock_synopsis"}, "mock_name. mock_synopsis")],
)
def test_build_embed_text(episode, expected):
    assert build_embed_text(episode) == expected


def test_embed_texts():
    mock_response_1 = MagicMock()
    mock_response_1["body"].read.return_value = json.dumps({"embedding": [0.1, 0.2, 0.3]})

    mock_response_2 = MagicMock()
    mock_response_2["body"].read.return_value = json.dumps({"embedding": [0.4, 0.5, 0.6]})

    with patch(
        "backend.ingest.ingest._bedrock.invoke_model", side_effect=[mock_response_1, mock_response_2]
    ) as mock_invoke_model:
        texts = embed_texts(["text one", "text two"])

    assert mock_invoke_model.call_count == 2
    assert texts == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]


def test_build_faiss_index():
    embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    result = build_faiss_index(embeddings)

    assert result.ntotal == 2
    assert result.d == 3


def test_upload_to_s3():
    index = build_faiss_index([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

    episode_1: Episode = {
        "id": 1,
        "airdate": "mock_air_date_1",
        "episode_number": 1,
        "image_path": "mock_image_path_1",
        "name": "mock_name_1",
        "season": 1,
        "synopsis": "mock synopsis 1",
    }

    episode_2: Episode = {
        "id": 2,
        "airdate": "mock_air_date_2",
        "episode_number": 2,
        "image_path": "mock_image_path_2",
        "name": "mock_name_2",
        "season": 1,
        "synopsis": "mock synopsis 2",
    }

    with patch("backend.ingest.ingest._s3.upload_file") as mock_s3_upload_file:
        with patch("backend.ingest.ingest._s3.put_object") as mock_s3_put_object:
            upload_to_s3(index, [episode_1, episode_2])

    assert mock_s3_upload_file.call_count == 1
    assert mock_s3_upload_file.call_args.args[0].endswith("episodes.index")
    assert mock_s3_upload_file.call_args.args[1] == "test-bucket"
    assert mock_s3_upload_file.call_args.args[2] == "test/index"

    assert mock_s3_put_object.call_count == 1
    assert mock_s3_put_object.call_args.kwargs["Bucket"] == "test-bucket"
    assert mock_s3_put_object.call_args.kwargs["Key"] == "test/episodes.json"
    assert mock_s3_put_object.call_args.kwargs["ContentType"] == "application/json"
    assert json.loads(mock_s3_put_object.call_args.kwargs["Body"]) == [episode_1, episode_2]
