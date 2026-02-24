from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="dev", alias="APP_ENV")
    base_url: str = Field(default="http://localhost:8000", alias="BASE_URL")
    session_secret: str = Field(default="change_me", alias="SESSION_SECRET")
    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="change_me_initial", alias="ADMIN_PASSWORD")

    smtp_host: str = Field(default="", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_pass: str = Field(default="", alias="SMTP_PASS")
    smtp_from: str = Field(default="", alias="SMTP_FROM")
    smtp_to: str = Field(default="", alias="SMTP_TO")

    firm_name: str = Field(default="VAROL HUKUK", alias="FIRM_NAME")
    phone: str = Field(default="", alias="PHONE")
    whatsapp: str = Field(default="", alias="WHATSAPP")
    email: str = Field(default="", alias="EMAIL")
    address: str = Field(default="", alias="ADDRESS")
    map_iframe_url: str = Field(default="", alias="MAP_IFRAME_URL")


APP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
TEMPLATE_DIR = APP_ROOT / "app" / "templates"
STATIC_DIR = APP_ROOT / "app" / "static"

settings = Settings()
