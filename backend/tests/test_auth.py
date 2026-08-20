import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:10]}@example.com"


def test_register_and_me():
    email = _unique_email()
    res = client.post("/api/auth/register", json={"email": email, "password": "hunter22", "name": "Test User"})
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == email
    assert body["is_admin"] is False

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == email

    client.post("/api/auth/logout")


def test_register_rejects_short_password():
    res = client.post(
        "/api/auth/register", json={"email": _unique_email(), "password": "short", "name": "X"}
    )
    assert res.status_code == 400


def test_register_rejects_duplicate_email():
    email = _unique_email()
    client.post("/api/auth/register", json={"email": email, "password": "hunter22", "name": "X"})
    res = client.post("/api/auth/register", json={"email": email, "password": "hunter22", "name": "X"})
    assert res.status_code == 409
    client.post("/api/auth/logout")


def test_login_wrong_password_rejected():
    email = _unique_email()
    client.post("/api/auth/register", json={"email": email, "password": "hunter22", "name": "X"})
    client.post("/api/auth/logout")

    res = client.post("/api/auth/login", json={"email": email, "password": "wrong-password"})
    assert res.status_code == 401


def test_login_correct_password_succeeds():
    email = _unique_email()
    client.post("/api/auth/register", json={"email": email, "password": "hunter22", "name": "X"})
    client.post("/api/auth/logout")

    res = client.post("/api/auth/login", json={"email": email, "password": "hunter22"})
    assert res.status_code == 200
    assert res.json()["email"] == email
    client.post("/api/auth/logout")


def test_me_requires_auth():
    anon = TestClient(app)
    res = anon.get("/api/auth/me")
    assert res.status_code == 401


def test_workflow_routes_require_auth():
    anon = TestClient(app)
    assert anon.get("/api/documents").status_code == 401
    assert anon.post("/api/chat", json={"question": "hi"}).status_code == 401
    assert anon.post("/api/database-chat", json={"question": "hi"}).status_code == 401
    assert anon.get("/api/policy-chat/personas").status_code == 401


def test_non_admin_cannot_view_admin_activity():
    email = _unique_email()
    client.post("/api/auth/register", json={"email": email, "password": "hunter22", "name": "X"})

    res = client.get("/api/admin/activity")
    assert res.status_code == 403
    client.post("/api/auth/logout")


def test_activity_is_logged_on_register_and_login():
    email = _unique_email()
    client.post("/api/auth/register", json={"email": email, "password": "hunter22", "name": "X"})

    res = client.get("/api/activity/me")
    assert res.status_code == 200
    events = [row["event_type"] for row in res.json()]
    assert "register" in events
    client.post("/api/auth/logout")
