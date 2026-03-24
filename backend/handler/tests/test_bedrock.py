import json
from unittest.mock import MagicMock, patch

from backend.handler.bedrock import embed, format_response
from backend.handler import bedrock


def test_embed():
    mock_body = MagicMock()
    mock_body.read.return_value = json.dumps({"embedding": [0.1, 0.2, 0.3]})

    with patch("backend.handler.bedrock._client.invoke_model") as mock_invoke_model:
        mock_invoke_model.return_value = {"body": mock_body}
        result = embed("The time that Marge went to jail")

    assert result == [0.1, 0.2, 0.3]
    assert mock_invoke_model.call_count == 1
    assert json.loads(mock_invoke_model.call_args.kwargs["body"]) == {"inputText": "The time that Marge went to jail"}


def test_format_response():
    mock_body = MagicMock()
    mock_body.read.return_value = json.dumps({"content": [{"text": "mock text"}]})

    episodes = [{"name": "episode 1", "synopsis": "synopsis 1"}, {"name": "episode 2", "synopsis": "synopsis 2"}]
    expected_content = f'Query: "mock query"\n\nMatched episodes:\n{json.dumps(episodes, indent=2)}'

    with patch("backend.handler.bedrock._client.invoke_model") as mock_invoke_model:
        mock_invoke_model.return_value = {"body": mock_body}
        result = format_response(
            "mock query", [{"name": "episode 1", "synopsis": "synopsis 1"}, {"name": "episode 2", "synopsis": "synopsis 2"}]
        )

    assert result == "mock text"
    assert mock_invoke_model.call_count == 1
    assert "modelId" in mock_invoke_model.call_args.kwargs
    assert json.loads(mock_invoke_model.call_args.kwargs["body"]) == {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "system": bedrock.SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": expected_content}],
    }
