from io import BytesIO
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
    base_dir = Path("/mock/base/dir")
    return FileUploadService(base_dir)


def test_upload_data_success_dataディレクトリ(mock_file_upload_service):
    file_content = b"test content"
    file = UploadFile(filename="testfile.txt", file=file_content)

    response = client.post(
        "/data",
        files={"file": ("testfile.txt", file_content, "text/plain")}
    )

    assert response.status_code == 200
    assert response.json() == {"filename": "testfile.txt"}


def test_upload_data_invalid_file_dataディレクトリ(mock_file_upload_service):
    response = client.post(
        "/data",
        files={"file": ("", b"", "text/plain")}
    )

    assert response.status_code == 422


def test_upload_data_failure_dataディレクトリ(mock_file_upload_service):
    file_content = b"test content"
    file = UploadFile(filename="testfile.txt", file=BytesIO(file_content))

    with patch.object(FileUploadService, 'upload_file', side_effect=Exception("Upload failed")):
        response = client.post(
            "/data",
            files={"file": ("testfile.txt", file_content, "text/plain")}
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to upload file"}


def test_upload_data_success_filesディレクトリ(mock_file_upload_service):
    file_content = b"test content"
    file = UploadFile(filename="testfile.txt", file=file_content)

    response = client.post(
        "/files",
        files={"file": ("testfile.txt", file_content, "text/plain")}
    )

    assert response.status_code == 200
    assert response.json() == {"filename": "testfile.txt"}


def test_upload_data_invalid_filesディレクトリ(mock_file_upload_service):
    response = client.post(
        "/files",
        files={"file": ("", b"", "text/plain")}
    )

    assert response.status_code == 422


def test_upload_data_failure_filesディレクトリ(mock_file_upload_service):
    file_content = b"test content"
    file = UploadFile(filename="testfile.txt", file=BytesIO(file_content))

    with patch.object(FileUploadService, 'upload_file', side_effect=Exception("Upload failed")):
        response = client.post(
            "/files",
            files={"file": ("testfile.txt", file_content, "text/plain")}
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to upload file"}