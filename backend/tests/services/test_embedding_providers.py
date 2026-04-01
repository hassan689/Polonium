import unittest
from unittest.mock import patch

from app.services.embeddings.openai_embedding import OpenAIEmbeddingProvider


class TestOpenAIEmbeddingProvider(unittest.TestCase):
    def test_embed_rejects_empty_text(self):
        provider = OpenAIEmbeddingProvider()
        with self.assertRaises(ValueError):
            provider.embed("   ")

    @patch("app.services.embeddings.openai_embedding.requests.post")
    def test_embed_returns_vector(self, mock_post):
        provider = OpenAIEmbeddingProvider()
        mock_post.return_value.json.return_value = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}
        mock_post.return_value.raise_for_status.return_value = None

        vector = provider.embed("hello world")

        self.assertEqual(vector, [0.1, 0.2, 0.3])
        self.assertEqual(provider.get_dimension(), 3)

    @patch("app.services.embeddings.openai_embedding.requests.post")
    def test_embed_batch_contract(self, mock_post):
        provider = OpenAIEmbeddingProvider()
        mock_post.return_value.json.return_value = {
            "data": [{"embedding": [0.1, 0.2]}, {"embedding": [0.3, 0.4]}]
        }
        mock_post.return_value.raise_for_status.return_value = None

        vectors = provider.embed_batch(["a", "b"])

        self.assertEqual(len(vectors), 2)
        self.assertTrue(all(len(v) == 2 for v in vectors))


if __name__ == "__main__":
    unittest.main()

