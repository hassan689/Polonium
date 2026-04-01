from app.services.embeddings.factory import EmbeddingFactory


def test_embedding_factory_openai(monkeypatch):
    monkeypatch.setattr("app.services.embeddings.factory.settings.EMBEDDING_PROVIDER", "openai")
    provider = EmbeddingFactory.create()
    assert provider.__class__.__name__ == "OpenAIEmbeddingProvider"


def test_embedding_factory_sentence_transformer(monkeypatch):
    monkeypatch.setattr(
        "app.services.embeddings.factory.settings.EMBEDDING_PROVIDER",
        "sentence_transformer",
    )

    class _FakeSentenceProvider:
        def __init__(self):
            pass

    monkeypatch.setattr(
        "app.services.embeddings.factory.SentenceTransformerProvider",
        _FakeSentenceProvider,
    )
    provider = EmbeddingFactory.create()
    assert provider.__class__.__name__ == "_FakeSentenceProvider"

