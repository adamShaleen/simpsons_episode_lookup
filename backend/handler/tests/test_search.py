import json
from unittest.mock import MagicMock, patch

import numpy

from backend.handler import search


def test_load_assets():
    search._index = None
    search._episodes = None

    with patch("backend.handler.search._s3.download_file") as download_file_mock:
        with patch("backend.handler.search.faiss.read_index") as read_index_mock:
            with patch("backend.handler.search._s3.get_object") as get_object_mock:
                download_file_mock.return_value = None
                read_index_mock.return_value = MagicMock()
                return_mock = MagicMock()
                return_mock.read.return_value = json.dumps([])
                get_object_mock.return_value = {"Body": return_mock}

                search._load_assets()

                assert search._index is not None
                assert search._episodes == []


def test_find_episodes():
    episodes = [
        {"id": 1, "name": "episode 0"},
        {"id": 2, "name": "episode 1"},
        {"id": 3, "name": "episode 2"},
    ]

    mock_index = MagicMock()
    mock_index.search.return_value = (None, numpy.array([[0, 2]]))

    search._index = mock_index
    search._episodes = episodes

    with patch("backend.handler.search._load_assets"):
        with patch("backend.handler.search.bedrock.embed") as mock_embed:
            mock_embed.return_value = [0.1, 0.2, 0.3]
            result = search.find_episodes("Marge goes to jail", top_k=2)

    assert result == [episodes[0], episodes[2]]
    assert mock_embed.call_count == 1
    assert mock_embed.call_args.args[0] == "Marge goes to jail"
