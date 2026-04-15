import unittest
from unittest.mock import patch

from app.services.llm.exceptions import ConfigurationError, InferenceError
from app.services.llm.openai_compatible import OpenAICompatibleProvider


class TestOpenAICompatibleProvider(unittest.TestCase):
    @patch("app.services.llm.openai_compatible.settings")
    def test_configuration_error_on_missing_base_url(self, mock_settings):
        mock_settings.LOCAL_LLM_BASE_URL = ""
        mock_settings.LOCAL_LLM_MODEL = "llama3.1:8b"
        with self.assertRaises(ConfigurationError):
            OpenAICompatibleProvider()

    @patch("app.services.llm.openai_compatible.requests.post")
    def test_chat_returns_content(self, mock_post):
        provider = OpenAICompatibleProvider()
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "hello"}}]
        }
        mock_post.return_value.raise_for_status.return_value = None

        content = provider.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(content, "hello")

    @patch("app.services.llm.openai_compatible.requests.post", side_effect=Exception("boom"))
    def test_chat_wraps_inference_error(self, _mock_post):
        provider = OpenAICompatibleProvider()
        with self.assertRaises(InferenceError):
            provider.chat([{"role": "user", "content": "hi"}])


if __name__ == "__main__":
    unittest.main()

