from __future__ import annotations

from app.config import settings
from app.models import SeoMeta, SiteSettings


def build_seo(
    path: str,
    page_title: str,
    page_description: str,
    site_settings: SiteSettings,
) -> SeoMeta:
    title = page_title or site_settings.default_seo_title
    description = page_description or site_settings.default_seo_description
    canonical = f"{settings.base_url.rstrip('/')}{path}"
    return SeoMeta(
        title=title,
        description=description,
        canonical=canonical,
        og_title=title,
        og_description=description,
    )
