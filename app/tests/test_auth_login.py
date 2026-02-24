from app.auth import ensure_admin_user, verify_login
from app.config import settings


def test_login_ok_and_wrong_password(isolated_data):
    settings.admin_username = "admin"
    settings.admin_password = "change_me_initial"

    ensure_admin_user()

    assert verify_login("admin", "change_me_initial") is True
    assert verify_login("admin", "wrong-pass") is False
