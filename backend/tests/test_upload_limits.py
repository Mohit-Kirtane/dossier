import io
import uuid

import pytest
from fastapi.testclient import TestClient

from app.ingestion.loaders import FileTooLarge, ensure_within_upload_size_limit
from app.main import app

client = TestClient(app)


def test_ensure_within_upload_size_limit_allows_small_file():
    ensure_within_upload_size_limit(b"x" * 1024)  # should not raise


def test_ensure_within_upload_size_limit_rejects_oversized_file():
    with pytest.raises(FileTooLarge):
        ensure_within_upload_size_limit(b"x" * (5 * 1024 * 1024 + 1))


def _login_new_user():
    email = f"upload-test-{uuid.uuid4().hex[:10]}@example.com"
    client.post("/api/auth/register", json={"email": email, "password": "hunter22", "name": "X"})


def test_document_upload_rejects_file_over_5mb():
    _login_new_user()
    oversized = io.BytesIO(b"a" * (5 * 1024 * 1024 + 1))
    res = client.post(
        "/api/documents/upload",
        files={"file": ("big.txt", oversized, "text/plain")},
    )
    assert res.status_code == 413
    client.post("/api/auth/logout")


def test_document_upload_accepts_file_under_5mb():
    _login_new_user()
    small = io.BytesIO(b"Vacation policy: 18 days per year.")
    res = client.post(
        "/api/documents/upload",
        files={"file": ("small.txt", small, "text/plain")},
    )
    assert res.status_code == 200
    client.post("/api/auth/logout")
