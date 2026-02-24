import shutil

import pytest

from app import auth
from app import cms
from app import config
from app import main as app_main
from app import storage


@pytest.fixture
def isolated_data(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(config, "DATA_DIR", data_dir)
    monkeypatch.setattr(storage, "DATA_DIR", data_dir)
    monkeypatch.setattr(auth, "DATA_DIR", data_dir)
    monkeypatch.setattr(cms, "DATA_DIR", data_dir)
    monkeypatch.setattr(app_main, "DATA_DIR", data_dir)

    monkeypatch.setattr(cms, "SITE_SETTINGS_PATH", data_dir / "site_settings.json")
    monkeypatch.setattr(cms, "CATEGORIES_PATH", data_dir / "categories.json")
    monkeypatch.setattr(cms, "TEAM_PATH", data_dir / "team.json")
    monkeypatch.setattr(cms, "SERVICES_DIR", data_dir / "services")
    monkeypatch.setattr(cms, "BLOG_DIR", data_dir / "blog")
    monkeypatch.setattr(cms, "LEADS_DIR", data_dir / "leads")

    yield data_dir

    shutil.rmtree(data_dir, ignore_errors=True)
