from __future__ import annotations

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.cms import load_site_settings
from app.config import TEMPLATE_DIR
from app.seo import build_seo


templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def base_context(request: Request, path: str, title: str, description: str) -> dict:
    site_settings = load_site_settings()
    seo = build_seo(path=path, page_title=title, page_description=description, site_settings=site_settings)
    return {
        "request": request,
        "site_settings": site_settings,
        "seo": seo,
    }
