from io import BytesIO
from pathlib import Path
import sys
import os
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

import shutil
from pathlib import Path
from io import BytesIO
import pytest
from fastapi import UploadFile
from services.file_upload_service import FileUploadService


def test_upload_file_正常系(tmp_path: Path):
    # Arrange: create a temporary base directory for uploads
    base_dir = tmp_path / "hoge"
    service = FileUploadService(base_dir)
    
    # Prepare an in-memory file using BytesIO
    file_content = b"sample file content"
    filename = "testfile.txt"
    file_stream = BytesIO(file_content)
    upload_file = UploadFile(filename=filename, file=file_stream)
    
    # Act: call upload_file with a sub-directory "data"
    returned_filename = service.upload_file(upload_file, "data")
    
    # Assert: verify the filename is returned correctly
    assert returned_filename == filename
    
    # Verify that the file was written in the expected location
    target_file_path = base_dir / "data" / filename
    assert target_file_path.exists()
    
    # Verify the content of the written file
    with open(target_file_path, "rb") as f:
        assert f.read() == file_content


def test_upload_file_異常系(tmp_path: Path):
    # Arrange: create a temporary base directory for uploads
    base_dir = tmp_path / "hoge"
    service = FileUploadService(base_dir)
    
    file_content = b"sample file content"
    filename = "testfile.txt"
    file_stream = BytesIO(file_content)
    upload_file = UploadFile(filename=filename, file=file_stream)

    # Act & Assert: patching shutil.copyfileobj to raise an exception simulating a failure during file copy
    with patch("services.file_upload_service.shutil.copyfileobj", side_effect=Exception("Copy failed")):
        with pytest.raises(Exception) as exc_info:
            service.upload_file(upload_file, "data")
    
    assert "Copy failed" in str(exc_info.value)