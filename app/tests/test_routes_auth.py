from fastapi.testclient import TestClient

from app.main import create_app


def test_smoke_routes():
    client = TestClient(create_app())

    assert client.get("/healthz").status_code == 200
    assert client.get("/").status_code == 200
    assert client.get("/iletisim/").status_code == 200


def test_admin_guard_redirects_to_login():
    client = TestClient(create_app())
    response = client.get("/admin/dashboard", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"
