"""
General API client for Polonium backend communication.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class APIError(Exception):
    status_code: int
    message: str
    details: Optional[Any] = None

    def __str__(self) -> str:
        base = f"[{self.status_code}] {self.message}"
        if self.details:
            return f"{base} | details={self.details}"
        return base


class PoloniumClient:
    """Reusable HTTP client with retries and auth support."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        token: Optional[str] = None,
        timeout_seconds: int = 60,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self._configure_retries()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.session.headers.update({"Content-Type": "application/json"})

    def _configure_retries(self) -> None:
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.request(method, url, timeout=self.timeout_seconds, **kwargs)
            if response.status_code >= 400:
                payload = self._safe_json(response)
                message = payload.get("detail", response.text) if isinstance(payload, dict) else response.text
                raise APIError(response.status_code, message, payload)
            payload = self._safe_json(response)
            return payload if isinstance(payload, dict) else {"data": payload}
        except requests.RequestException as exc:
            raise APIError(0, f"Network error calling {url}", str(exc)) from exc

    @staticmethod
    def _safe_json(response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return {"raw": response.text}

    def connect_repo(self, owner: str, name: str) -> Dict[str, Any]:
        return self._request("POST", "repositories", json={"owner": owner, "name": name})

    def list_repos(self) -> Dict[str, Any]:
        return self._request("GET", "repositories")

    def repo_overview(self, repo_id: int) -> Dict[str, Any]:
        return self._request("GET", f"repositories/{repo_id}/overview")

    def explain_file(self, repo_id: int, file_path: str) -> Dict[str, Any]:
        return self._request("GET", f"repositories/{repo_id}/files/{file_path}/explain")

    def send_chat(self, repo_id: int, content: str) -> Dict[str, Any]:
        return self._request("POST", f"repositories/{repo_id}/chat", json={"content": content})

    def chat_history(self, repo_id: int) -> Dict[str, Any]:
        return self._request("GET", f"repositories/{repo_id}/chat")

