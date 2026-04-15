import pytest

from app.services.ai_service import AIService


class _MockProvider:
    def chat(self, messages, temperature=0.7):
        return "chat-response"


@pytest.mark.asyncio
async def test_chat_flow_with_mock_provider(monkeypatch):
    monkeypatch.setattr("app.services.ai_service.LLMFactory.create", lambda: _MockProvider())
    service = AIService()
    response = await service.generate_chat_response(
        user_message="What does this repo do?",
        repository_context="owner/repo",
        chat_history=[{"role": "user", "content": "hello"}],
    )
    assert response == "chat-response"


@pytest.mark.asyncio
@pytest.mark.benchmark(group="chat-latency")
async def test_chat_latency_benchmark(monkeypatch, benchmark):
    monkeypatch.setattr("app.services.ai_service.LLMFactory.create", lambda: _MockProvider())
    service = AIService()
    benchmark(service.provider.chat, [{"role": "user", "content": "ping"}], 0.7)

