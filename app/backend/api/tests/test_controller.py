from pathlib import Path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from fastapi.testclient import TestClient
from fastapi import UploadFile, FastAPI, Depends, HTTPException
from unittest.mock import AsyncMock, MagicMock, patch
from startup import create_app
from controller import upload_data
from services.file_upload_service import FileUploadService
from dependency_injector.wiring import Provide, inject
from di.containers import Container

app = create_app()
client = TestClient(app)


@pytest.fixture
def mock_file_upload_service():
    with patch("services.file_upload_service.FileUploadService") as MockService:
        mock_service = MockService.return_value
        mock_service.base_dir = Path("/mock/base/dir")
        mock_service.upload_file = AsyncMock(return_value="testfile.txt")
        yield mock_service


def test_upload_data_success(mock_file_upload_service):
    file_content = b"test content"
    file = UploadFile(filename="testfile.txt", file=file_content)

    response = client.post(
        "/data",
        files={"file": ("testfile.txt", file_content, "text/plain")}
    )

    assert response.status_code == 200
    assert response.json() == {"filename": "testfile.txt"}


def test_upload_data_invalid_file(mock_file_upload_service):
    response = client.post(
        "/data",
        files={"file": ("", b"", "text/plain")}
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_upload_file_creates_target_dir(mock_file_upload_service):
    # Arrange
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.txt"
    mock_file.file = MagicMock()
    sub_dir = "subdir"
    target_dir = mock_file_upload_service.base_dir / sub_dir

    # Act
    await mock_file_upload_service.upload_file(mock_file, sub_dir)

    # Assert
    target_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)