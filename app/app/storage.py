from __future__ import annotations

import json
import os
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable, TypeVar

import frontmatter
from markdown_it import MarkdownIt
from pydantic import BaseModel

from app.config import DATA_DIR

T = TypeVar("T", bound=BaseModel)

_slug_re = re.compile(r"[^a-z0-9-]+")
_md = MarkdownIt("commonmark", {"html": False, "linkify": True})


def ensure_data_dirs() -> None:
    for directory in [
        DATA_DIR,
        DATA_DIR / "users",
        DATA_DIR / "services",
        DATA_DIR / "blog",
        DATA_DIR / "leads",
        DATA_DIR / "media",
        DATA_DIR / "media" / "uploads",
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def slugify(value: str) -> str:
    val = value.strip().lower().replace("_", "-").replace(" ", "-")
    val = _slug_re.sub("-", val)
    val = re.sub(r"-+", "-", val).strip("-")
    if not re.fullmatch(r"[a-z0-9-]+", val or ""):
        raise ValueError("invalid_slug")
    return val


def _safe_path(path: Path) -> Path:
    resolved = path.resolve()
    base = DATA_DIR.resolve()
    if base not in [resolved, *resolved.parents]:
        raise ValueError("path_outside_data")
    return resolved


def read_json(path: Path, default: Any = None) -> Any:
    safe = _safe_path(path)
    if not safe.exists():
        return default
    with safe.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_atomic(path: Path, data: Any) -> None:
    safe = _safe_path(path)
    safe.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(safe.parent)) as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2)
        temp_name = tmp.name
    os.replace(temp_name, safe)


def read_md_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    safe = _safe_path(path)
    if not safe.exists():
        raise FileNotFoundError(str(safe))
    with safe.open("r", encoding="utf-8") as handle:
        post = frontmatter.load(handle)
    return dict(post.metadata), post.content


def write_md_frontmatter_atomic(path: Path, metadata: dict[str, Any], content: str) -> None:
    safe = _safe_path(path)
    safe.parent.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post(content, **metadata)
    rendered = frontmatter.dumps(post)
    with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(safe.parent)) as tmp:
        tmp.write(rendered)
        temp_name = tmp.name
    os.replace(temp_name, safe)


def parse_doc(path: Path, model_factory: Callable[..., T]) -> tuple[T, str, str]:
    meta_raw, markdown = read_md_frontmatter(path)
    model = model_factory(**meta_raw)
    html = _md.render(markdown)
    return model, markdown, html


def list_markdown_files(directory: Path) -> list[Path]:
    safe = _safe_path(directory)
    if not safe.exists():
        return []
    return sorted([item for item in safe.glob("*.md") if item.is_file()])
