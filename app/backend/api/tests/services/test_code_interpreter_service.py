import os
import sys
import logging
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from services.code_interpreter_service import CodeInterpreterService

class DummyTracerSpan:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def set_attributes(self, attrs):
        pass

class TestCodeInterpreterServiceHandleRunCompletion(unittest.TestCase):
    def setUp(self):
        # Setup dummy dependencies
        self.project_client = MagicMock()
        self.project_client.agents.delete_file = MagicMock()
        self.file_repository = MagicMock()
        self.message_repository = MagicMock()
        self.service = CodeInterpreterService(self.project_client,
                                                self.file_repository,
                                                self.message_repository)

    @patch("services.code_interpreter_service.tracer")
    def test_handle_run_completion_normal(self, mock_tracer):
        # Patch tracer to return a dummy context manager
        mock_tracer.start_as_current_span.return_value = DummyTracerSpan()
        
        # Create a dummy run object with non-failed status.
        dummy_run = MagicMock()
        dummy_run.status = "success"  # Normal case, not failed.
        dummy_run.last_error = None

        file_id = "dummy-file-id"
        thread_id = "dummy-thread-id"

        self.service.handle_run_completion(dummy_run, thread_id, file_id)
        
        # Verify that delete_file was called once with the correct file_id.
        self.project_client.agents.delete_file.assert_called_once_with(file_id)

if __name__ == "__main__":
    unittest.main()