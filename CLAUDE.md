# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**VAROL HUKUK** — A Turkish law firm website built as a FastAPI file-based CMS MVP. No database; all content persists to the filesystem under `./data/` (Docker bind mount). Language is Turkish throughout.

- Public site: `http://localhost:8000`
- Admin panel: `http://localhost:8000/admin/login`

---

## Development Commands

All commands must be run from the `app/` directory:

```bash
cd app

# Setup (Python 3.12+)
python -m venv .venv
. .venv/Scripts/Activate.ps1   # Windows PowerShell
# source .venv/bin/activate    # Linux/Mac

pip install -r requirements.txt

# Seed demo content (Turkish placeholders)
python scripts/seed_demo.py

# Run dev server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests
pytest -q

# Run a single test file
pytest tests/test_auth_login.py -q
```

**Docker (preferred for full deployment):**

```bash
# From repo root
cp .env.example .env   # fill in SMTP and firm details
docker compose up --build
```

---

## Architecture

### Key Constraint: No Database
All mutable data lives in `./data/` (bind-mounted into Docker as `/app/data`). To back up the site, copy only `./data/`. Content is stored as:
- **Markdown with YAML frontmatter** — services (`data/services/<slug>.md`) and blog posts (`data/blog/<slug>.md`)
- **JSON** — `site_settings.json`, `categories.json`, `team.json`, `users/admin.json`
- **JSONL (append-only)** — `leads/leads-YYYY-MM.jsonl` (contact form submissions)
- **Uploaded images** — `data/media/uploads/`

### Module Responsibilities

| File | Responsibility |
|------|---------------|
| `app/main.py` | FastAPI app creation, middleware, startup hooks, router includes |
| `app/config.py` | Pydantic `Settings` from `.env`; defines `DATA_DIR`, `TEMPLATE_DIR`, `STATIC_DIR` |
| `app/storage.py` | All file I/O — atomic writes (write-temp-then-rename), JSON read/write, Markdown+frontmatter read/write, `slugify()`, `_safe_path()` |
| `app/cms.py` | Business logic over storage — `list_posts()`, `get_post()`, `save_post()`, `list_services()`, `append_lead()`, etc. |
| `app/models.py` | Pydantic models: `BlogMeta`, `ServiceMeta`, `SiteSettings`, `LeadEntry`, `TeamItem`, `CategoryItem`, `UserRecord` |
| `app/auth.py` | Session-based admin auth (Argon2 hash in `admin.json`), CSRF tokens, `get_current_admin` FastAPI dependency |
| `app/routes_public.py` | All public-facing routes (`/`, `/hizmetler`, `/makale`, `/iletisim`, etc.) |
| `app/routes_admin.py` | Protected admin CRUD routes (all require `get_current_admin` dependency + CSRF) |
| `app/views.py` | `templates` (Jinja2Templates instance) + `base_context()` for shared template data |
| `app/seo.py` | `build_seo()` — generates title/description/canonical/OpenGraph meta |
| `app/emailer.py` | SMTP contact notification via STARTTLS port 587 (Gmail/Outlook) |
| `app/media.py` | Image upload validation (jpg/png/webp, max 5MB) + Pillow resize to max 1600px |
| `app/rate_limit.py` | `IPRateLimiter` — in-memory sliding window (5 hits / 300s per IP) on contact form |

### Request Flow
Public request → `routes_public.py` → `cms.py` → `storage.py` → file read → `views.py`/`seo.py` → Jinja2 template → response

Admin request → `routes_admin.py` → `get_current_admin` dependency (checks session) → CSRF check → `cms.py` → `storage.py` → atomic file write → redirect

### Template Structure
- `templates/base.html` — master layout (lang="tr", Tailwind CDN, Google Fonts: Cormorant Garamond + Source Sans 3)
- `templates/public/` — public pages
- `templates/admin/` — admin panel pages
- `templates/partials/` — reusable components (`_card_post.html`, `_card_service.html`, `_cta.html`, `_footer.html`)

---

## Data Schema

**Blog post frontmatter** (`data/blog/<slug>.md`):
```yaml
title, slug, excerpt, category_slug, published_at (ISO8601), status (draft|published), seo_title, seo_description, cover_image (optional)
```

**Service frontmatter** (`data/services/<slug>.md`):
```yaml
title, slug, summary, order (int), is_active (bool), seo_title, seo_description
```

Blog posts with `status: published` only appear if `published_at` is in the past.

---

## Security Patterns

- **CSRF**: Every admin POST must include a `csrf_token` field matching the session token. Generated in `auth.py`, validated in each admin route.
- **Path traversal**: `storage._safe_path()` rejects any path resolving outside `DATA_DIR`.
- **Argon2**: Admin password stored as `$argon2id$...` hash in `data/users/admin.json`. First-run seeding uses `ADMIN_USERNAME`/`ADMIN_PASSWORD` env vars.
- **Session**: Starlette `SessionMiddleware` with `SESSION_SECRET`. In production (`APP_ENV=prod`), cookies are `secure=True`.
- **Honeypot**: Contact form includes a hidden field; non-empty submissions are silently rejected.

---

## Environment Variables

Key vars in `.env` (see `.env.example` for full list):

| Variable | Purpose |
|----------|---------|
| `APP_ENV` | `dev` or `prod` (affects secure cookies) |
| `BASE_URL` | Used for SEO canonical URLs and sitemap |
| `SESSION_SECRET` | Starlette session cookie signing key |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Used only on first run to seed `admin.json` |
| `SMTP_HOST/PORT/USER/PASS/FROM/TO` | SMTP for contact form notifications |
| `OPENROUTER_API_KEY` | (Present in `.env`, unused by current app code) |

---

## Testing

Tests live in `app/tests/`. They use `tmp_path` fixtures with monkeypatching to isolate the file system — no real `./data/` is touched during tests.

Test files:
- `test_auth_login.py` — login/logout/session
- `test_routes_auth.py` — admin route protection
- `test_cms_publish.py` — publish status/timestamp filtering
- `test_storage.py` — atomic writes, JSON/Markdown parsing, slugify
- `test_leads.py` — JSONL lead append
