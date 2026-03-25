import json
from unittest.mock import MagicMock, patch

from backend.handler import bedrock
from backend.handler.bedrock import embed, format_response
from backend.models import Episode, EpisodeResult


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
    input_episodes: list[Episode] = [
        {
            "id": 1,
            "name": "episode 1",
            "season": 1,
            "episode_number": 1,
            "airdate": "1989-12-17",
            "image_path": "/episode/1.webp",
            "synopsis": "synopsis 1",
        }
    ]

    expected_output: list[EpisodeResult] = [
        {"title": "episode 1", "season": 1, "episode_number": 1, "airdate": "1989-12-17", "synopsis": "synopsis 1"}
    ]

    mock_body = MagicMock()
    mock_body.read.return_value = json.dumps({"content": [{"text": json.dumps(expected_output)}]})

    expected_content = f'Query: "mock query"\n\nMatched episodes:\n{json.dumps(input_episodes, indent=2)}'

    with patch("backend.handler.bedrock._client.invoke_model") as mock_invoke_model:
        mock_invoke_model.return_value = {"body": mock_body}
        result = format_response("mock query", input_episodes)

    assert result == expected_output
    assert mock_invoke_model.call_count == 1
    assert "modelId" in mock_invoke_model.call_args.kwargs
    assert json.loads(mock_invoke_model.call_args.kwargs["body"]) == {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "system": bedrock.SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": expected_content}],
    }


def test_format_response_strips_markdown_fences():
    expected_output: list[EpisodeResult] = [
        {"title": "episode 1", "season": 1, "episode_number": 1, "airdate": "1989-12-17", "synopsis": "synopsis 1"}
    ]
    fenced_text = f"```json\n{json.dumps(expected_output)}\n```"

    mock_body = MagicMock()
    mock_body.read.return_value = json.dumps({"content": [{"text": fenced_text}]})

    with patch("backend.handler.bedrock._client.invoke_model") as mock_invoke_model:
        mock_invoke_model.return_value = {"body": mock_body}
        result = format_response("mock query", [])

    assert result == expected_output
