import json
from unittest.mock import patch

from backend.handler.handler import lambda_handler

MOCK_EPISODES = [{"id": 1, "name": "episode 1", "synopsis": "synopsis 1"}]
MOCK_RESPONSE = "This is a formatted response."


def test_lambda_handler_returns_200():
    with patch("backend.handler.handler.search.find_episodes") as mock_find:
        with patch("backend.handler.handler.bedrock.format_response") as mock_format:
            mock_find.return_value = MOCK_EPISODES
            mock_format.return_value = MOCK_RESPONSE

            result = lambda_handler({"queryStringParameters": {"q": "Marge goes to jail"}}, None)

    assert result["statusCode"] == 200
    assert json.loads(result["body"]) == {"response": MOCK_RESPONSE}
    assert mock_find.call_args.args[0] == "Marge goes to jail"
    assert mock_format.call_args.args == ("Marge goes to jail", MOCK_EPISODES)


def test_lambda_handler_returns_400_when_query_missing():
    result = lambda_handler({"queryStringParameters": {}}, None)
    assert result["statusCode"] == 400

    result = lambda_handler({"queryStringParameters": None}, None)
    assert result["statusCode"] == 400

    result = lambda_handler({}, None)
    assert result["statusCode"] == 400
