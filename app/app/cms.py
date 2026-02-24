from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from app.config import DATA_DIR, settings
from app.models import (
    BlogDocument,
    BlogMeta,
    CategoryItem,
    LeadEntry,
    ServiceDocument,
    ServiceMeta,
    SiteSettings,
    TeamItem,
)
from app.storage import (
    ensure_data_dirs,
    list_markdown_files,
    parse_doc,
    read_json,
    slugify,
    write_json_atomic,
    write_md_frontmatter_atomic,
)

ModelT = TypeVar("ModelT", bound=BaseModel)


SITE_SETTINGS_PATH = DATA_DIR / "site_settings.json"
CATEGORIES_PATH = DATA_DIR / "categories.json"
TEAM_PATH = DATA_DIR / "team.json"
SERVICES_DIR = DATA_DIR / "services"
BLOG_DIR = DATA_DIR / "blog"
LEADS_DIR = DATA_DIR / "leads"


def _default_site_settings() -> SiteSettings:
    return SiteSettings(
        firm_name=settings.firm_name,
        phone=settings.phone,
        whatsapp=settings.whatsapp,
        email=settings.email,
        address=settings.address,
        map_iframe_url=settings.map_iframe_url,
        default_seo_title=settings.firm_name,
    )


def load_site_settings() -> SiteSettings:
    ensure_data_dirs()
    raw = read_json(SITE_SETTINGS_PATH, default=None)
    if not raw:
        current = _default_site_settings()
        save_site_settings(current)
        return current
    return SiteSettings(**raw)


def save_site_settings(payload: SiteSettings) -> None:
    write_json_atomic(SITE_SETTINGS_PATH, payload.model_dump(mode="json"))


def load_categories() -> list[CategoryItem]:
    ensure_data_dirs()
    raw = read_json(CATEGORIES_PATH, default=[])
    return [CategoryItem(**item) for item in raw]


def save_categories(items: list[CategoryItem]) -> None:
    write_json_atomic(CATEGORIES_PATH, [item.model_dump(mode="json") for item in items])


def load_team() -> list[TeamItem]:
    ensure_data_dirs()
    raw = read_json(TEAM_PATH, default=[])
    return [TeamItem(**item) for item in raw]


def save_team(items: list[TeamItem]) -> None:
    write_json_atomic(TEAM_PATH, [item.model_dump(mode="json") for item in items])


def list_services(active_only: bool = False) -> list[ServiceDocument]:
    ensure_data_dirs()
    docs: list[ServiceDocument] = []
    for path in list_markdown_files(SERVICES_DIR):
        meta, markdown, html = parse_doc(path, ServiceMeta)
        if active_only and not meta.is_active:
            continue
        docs.append(ServiceDocument(meta=meta, content_markdown=markdown, content_html=html))
    return sorted(docs, key=lambda x: (x.meta.order, x.meta.title.lower()))


def get_service(slug: str) -> ServiceDocument | None:
    safe_slug = slugify(slug)
    path = SERVICES_DIR / f"{safe_slug}.md"
    if not path.exists():
        return None
    meta, markdown, html = parse_doc(path, ServiceMeta)
    return ServiceDocument(meta=meta, content_markdown=markdown, content_html=html)


def save_service(meta: ServiceMeta, content_markdown: str) -> None:
    path = SERVICES_DIR / f"{meta.slug}.md"
    write_md_frontmatter_atomic(path, meta.model_dump(mode="json"), content_markdown)


def delete_service(slug: str) -> None:
    path = SERVICES_DIR / f"{slugify(slug)}.md"
    if path.exists():
        path.unlink()


def list_posts(include_drafts: bool = False) -> list[BlogDocument]:
    ensure_data_dirs()
    docs: list[BlogDocument] = []
    now = datetime.now(UTC)
    for path in list_markdown_files(BLOG_DIR):
        meta, markdown, html = parse_doc(path, BlogMeta)
        if not include_drafts:
            if meta.status != "published":
                continue
            if meta.published_at.astimezone(UTC) > now:
                continue
        docs.append(BlogDocument(meta=meta, content_markdown=markdown, content_html=html))
    return sorted(docs, key=lambda x: x.meta.published_at, reverse=True)


def get_post(slug: str) -> BlogDocument | None:
    safe_slug = slugify(slug)
    path = BLOG_DIR / f"{safe_slug}.md"
    if not path.exists():
        return None
    meta, markdown, html = parse_doc(path, BlogMeta)
    return BlogDocument(meta=meta, content_markdown=markdown, content_html=html)


def save_post(meta: BlogMeta, content_markdown: str) -> None:
    path = BLOG_DIR / f"{meta.slug}.md"
    write_md_frontmatter_atomic(path, meta.model_dump(mode="json"), content_markdown)


def delete_post(slug: str) -> None:
    path = BLOG_DIR / f"{slugify(slug)}.md"
    if path.exists():
        path.unlink()


def append_lead(entry: LeadEntry) -> Path:
    ensure_data_dirs()
    filename = f"leads-{entry.timestamp.strftime('%Y-%m')}.jsonl"
    path = LEADS_DIR / filename
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry.model_dump(mode="json"), ensure_ascii=False) + "\n")
    return path
