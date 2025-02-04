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
    def test_handle_run_completion_正常系(self, mock_tracer):
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


    @patch("services.code_interpreter_service.logging")
    @patch("services.code_interpreter_service.tracer")
    def test_handle_run_completion_異常系(self, mock_tracer, mock_logging):
        # Setup the tracer context manager
        # Create a dummy run with failed status and an error message
        dummy_run = MagicMock()
        dummy_run.status = "failed"  # Normal case, not failed.
        dummy_run.last_error = "Simulated failure"
        thread_id = "dummy-thread-id"
        file_id = "dummy-file-id"

        # Call the method under test
        self.service.handle_run_completion(dummy_run, thread_id, file_id)

        # Assert that the error is logged
        mock_logging.error.assert_called_with("Run failed: Simulated failure")
        # Assert that delete_file is called even in failure case
        self.project_client.agents.delete_file.assert_called_once_with(file_id)


    def test_save_generated_images_normal(self):
        # Call the method with a dummy thread id.
        result = self.service.save_generated_images("dummy-thread-id")
        # Assert that the result is the expected file name.
        self.assertEqual(result, "generated_image.png")


if __name__ == "__main__":
    unittest.main()