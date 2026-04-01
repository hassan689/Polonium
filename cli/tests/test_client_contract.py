from unittest.mock import Mock, patch

import pytest

from polonium_cli.client import APIError, PoloniumClient


def _response(status_code=200, payload=None, text=""):
    resp = Mock()
    resp.status_code = status_code
    resp.text = text
    resp.json.return_value = payload if payload is not None else {}
    return resp


@patch("polonium_cli.client.requests.Session.request")
def test_client_success_contract(mock_request):
    mock_request.return_value = _response(
        200,
        payload={"id": 1, "github_full_name": "owner/repo"},
    )
    client = PoloniumClient(base_url="http://localhost:8000/api/v1")
    result = client.connect_repo("owner", "repo")
    assert result["id"] == 1


@patch("polonium_cli.client.requests.Session.request")
def test_client_error_contract(mock_request):
    mock_request.return_value = _response(
        404,
        payload={"detail": "Repository not found"},
        text="Repository not found",
    )
    client = PoloniumClient(base_url="http://localhost:8000/api/v1")
    with pytest.raises(APIError) as exc:
        client.repo_overview(999)
    assert exc.value.status_code == 404
    assert "Repository not found" in str(exc.value)

