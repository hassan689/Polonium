import pytest

from app.services.embedding_service import EmbeddingService


class _MockEmbeddingProvider:
    def embed(self, text):
        return [0.1, 0.2, 0.3]

    def get_dimension(self):
        return 3


@pytest.mark.benchmark(group="embedding-generation")
def test_embedding_generation_time(benchmark, monkeypatch):
    monkeypatch.setattr("app.services.embedding_service.EmbeddingFactory.create", lambda: _MockEmbeddingProvider())
    service = EmbeddingService()
    benchmark(service.provider.embed, "hello world")

