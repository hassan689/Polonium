import pytest

from app.services.ai_service import AIService


class _Provider:
    def chat(self, messages, temperature=0.7):
        if any("Format your response as JSON" in m.get("content", "") for m in messages):
            return '{"overview":"ok","architecture":"layered","tech_stack":["python"],"key_files":["app/main.py"]}'
        return "hello from provider"


@pytest.mark.asyncio
async def test_generate_chat_response(monkeypatch):
    monkeypatch.setattr("app.services.ai_service.LLMFactory.create", lambda: _Provider())
    service = AIService()
    response = await service.generate_chat_response("hello")
    assert "hello" in response.lower()


@pytest.mark.asyncio
async def test_generate_repository_overview(monkeypatch):
    monkeypatch.setattr("app.services.ai_service.LLMFactory.create", lambda: _Provider())
    service = AIService()
    result = await service.generate_repository_overview(
        repository_name="owner/repo",
        file_summaries=[{"path": "app/main.py", "summary": "entry"}],
    )
    assert result["overview"] == "ok"
    assert "python" in result["tech_stack"]

