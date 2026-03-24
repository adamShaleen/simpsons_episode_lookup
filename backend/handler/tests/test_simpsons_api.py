import json
from unittest.mock import MagicMock, patch

from backend.handler import simpsons_api


def test_get_episode():
    episode_fields = {"name": "episode name"}
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(episode_fields).encode()

    with patch("backend.handler.simpsons_api.request.urlopen") as mock_url_open:
        mock_url_open.return_value = mock_response
        result = simpsons_api.get_episode(1)

    assert result == episode_fields
    assert mock_url_open.call_count == 1
    assert mock_url_open.call_args.args[0] == "https://thesimpsonsapi.com/api/episodes/1"
