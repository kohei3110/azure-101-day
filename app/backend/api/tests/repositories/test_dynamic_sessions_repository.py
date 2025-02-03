import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from repositories.dynamic_sessions_repository import DynamicSessionsRepository


class TestDynamicSessionsRepository(unittest.TestCase):
    def setUp(self):
        self.repo = DynamicSessionsRepository()
        self.session_id = "test-session-id"
        self.file = MagicMock()
        self.file.filename = "test.txt"
        self.file.file = BytesIO(b"test content")
        self.code = "print('Hello, World!')"


    @patch("dynamic_sessions_repository.requests.post")
    def test_upload_file(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        self.repo.upload_file(self.session_id, self.file)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("Authorization", kwargs["headers"])
        self.assertIn("file", kwargs["files"])


    @patch("dynamic_sessions_repository.requests.post")
    def test_execute_code(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        self.repo.execute_code(self.session_id, self.code)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("Authorization", kwargs["headers"])
        self.assertIn("Content-Type", kwargs["headers"])
        self.assertIn("code", kwargs["json"]["properties"])

if __name__ == "__main__":
    unittest.main()
