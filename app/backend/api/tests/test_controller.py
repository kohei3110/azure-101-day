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
from services.code_interpreter_service import CodeInterpreterService
from services.sidecar_service import SidecarService
from dependency_injector.wiring import Provide, inject
from di.containers import Container


# テスト用のダミー実装
class DummySidecarService:
    def post_slm(self, prompt: str) -> dict:
        return {"message": "dummy response"}

# DIのオーバーライドを行うフィクスチャ
@pytest.fixture(autouse=True)
def override_sidecar_service():
    Container.sidecar_service.override(DummySidecarService())
    yield
    Container.sidecar_service.reset_override()


app = create_app()
client = TestClient(app)


@pytest.fixture
def mock_file_upload_service():
    base_dir = Path("/mock/base/dir")
    return FileUploadService(base_dir)


@pytest.fixture
def tmp_result_file(tmp_path: Path) -> Path:
    file_path = tmp_path / "result.txt"
    file_path.write_text("Result content")
    return file_path


def test_upload_data_正常系(mock_file_upload_service):
    file_content = b"test content"
    file = UploadFile(filename="testfile.txt", file=file_content)

    response = client.post(
        "/data",
        files={"file": ("testfile.txt", file_content, "text/plain")}
    )

    assert response.status_code == 200
    assert response.json() == {"filename": "testfile.txt"}


def test_upload_data_ファイルがない(mock_file_upload_service):
    response = client.post(
        "/data",
        files={"file": ("", b"", "text/plain")}
    )

    assert response.status_code == 422


def test_upload_data_サービス層で例外(mock_file_upload_service):
    file_content = b"test content"
    file = UploadFile(filename="testfile.txt", file=BytesIO(file_content))

    with patch.object(FileUploadService, 'upload_file', side_effect=Exception("Upload failed")):
        response = client.post(
            "/data",
            files={"file": ("testfile.txt", file_content, "text/plain")}
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to upload file"}


def test_upload_files_正常系(mock_file_upload_service):
    file_content = b"test content"
    file = UploadFile(filename="testfile.txt", file=file_content)

    response = client.post(
        "/files",
        files={"file": ("testfile.txt", file_content, "text/plain")}
    )

    assert response.status_code == 200
    assert response.json() == {"filename": "testfile.txt"}


def test_upload_files_ファイルがない(mock_file_upload_service):
    response = client.post(
        "/files",
        files={"file": ("", b"", "text/plain")}
    )

    assert response.status_code == 422


def test_upload_files_サービス層で例外(mock_file_upload_service):
    file_content = b"test content"
    file = UploadFile(filename="testfile.txt", file=BytesIO(file_content))

    with patch.object(FileUploadService, 'upload_file', side_effect=Exception("Upload failed")):
        response = client.post(
            "/files",
            files={"file": ("testfile.txt", file_content, "text/plain")}
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to upload file"}


def test_post_code_interpreter_正常系(tmp_result_file: Path):
    message = "test message"
    file_content = b"test content"
    
    with patch.object(CodeInterpreterService, "process_file_and_message", new_callable=AsyncMock) as mock_process:
        mock_process.return_value = str(tmp_result_file)
        
        response = client.post(
            "/code_interpreter",
            files={"file": ("testfile.txt", BytesIO(file_content), "text/plain")},
            data={"message": message}
        )
    
    assert response.status_code == 200
    disposition = response.headers.get("content-disposition", "")
    assert "result.txt" in disposition


def test_post_code_interpreter_異常系(tmp_result_file: Path):
    message = "test message"
    file_content = b"test content"
    
    with patch.object(
        CodeInterpreterService, 
        "process_file_and_message", 
        new_callable=AsyncMock, 
        side_effect=Exception("Interpretation failed")
    ):
        response = client.post(
            "/code_interpreter",
            files={"file": ("testfile.txt", BytesIO(file_content), "text/plain")},
            data={"message": message}
        )
    
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to interpret code"}


def test_post_slm():
    with patch.object(SidecarService, "post_slm", new_callable=AsyncMock) as mock_process:
        response = client.post(
            "/slm",
            json= {"prompt": "今日は寒いですね。"}
        )
        
        assert response.status_code == 200
        assert response.json() == {"message": "test message"}