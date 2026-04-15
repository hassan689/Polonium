from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import pytest


class MockGitHubAPI:
    async def get_repository(self, owner: str, name: str) -> Dict[str, Any]:
        return {
            "full_name": f"{owner}/{name}",
            "html_url": f"https://github.com/{owner}/{name}",
            "description": "mock repository",
            "default_branch": "main",
        }

    async def get_repository_contents(self, owner: str, name: str, path: str = "", recursive: bool = True) -> List[Dict[str, Any]]:
        return [{"path": "README.md", "type": "blob", "size": 100}]

    async def get_file_content(self, owner: str, name: str, path: str) -> str:
        return "# mock content"


class MockLLMProvider:
    def chat(self, messages, temperature=0.7) -> str:
        if any("JSON" in m.get("content", "") for m in messages):
            return '{"overview":"mock","architecture":"mock","tech_stack":["python"],"key_files":["README.md"]}'
        return "mock llm response"


@dataclass
class TestDataFactory:
    def repository_payload(self, repo_id: int = 1) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "id": repo_id,
            "github_owner": "owner",
            "github_name": "repo",
            "github_full_name": "owner/repo",
            "github_url": "https://github.com/owner/repo",
            "github_description": "demo",
            "status": "completed",
            "total_files": 1,
            "total_size_bytes": 100,
            "created_at": now,
            "updated_at": now,
        }

    def chat_message_payload(self, content: str = "hello") -> Dict[str, Any]:
        return {
            "id": 1,
            "repository_id": 1,
            "user_id": None,
            "role": "assistant",
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }


@pytest.fixture
def mock_github_api():
    return MockGitHubAPI()


@pytest.fixture
def mock_llm_provider():
    return MockLLMProvider()


@pytest.fixture
def test_data_factory():
    return TestDataFactory()

