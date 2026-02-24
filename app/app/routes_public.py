from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Form, Request
from fastapi.responses import PlainTextResponse, Response

from app.cms import (
    append_lead,
    load_categories,
    load_site_settings,
    load_team,
    list_posts,
    list_services,
    get_post,
    get_service,
)
from app.config import settings
from app.emailer import send_contact_notification
from app.models import ContactFormData, LeadEntry
from app.rate_limit import IPRateLimiter
from app.views import base_context, templates

router = APIRouter()
_limiter = IPRateLimiter(max_hits=5, window_seconds=300)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "0.0.0.0"


@router.get("/")
def home(request: Request):
    services = list_services(active_only=True)[:6]
    posts = list_posts(include_drafts=False)[:3]
    ctx = base_context(request, "/", "Ana Sayfa | VAROL HUKUK", "Ticari uyuşmazlıklar ve hukuk danışmanlığı.")
    ctx.update({"services": services, "posts": posts})
    return templates.TemplateResponse(request, "public/home.html", ctx)


@router.get("/hakkimizda/biz-kimiz/")
def about_us(request: Request):
    team = [x for x in load_team() if x.is_active]
    ctx = base_context(request, "/hakkimizda/biz-kimiz/", "Biz Kimiz", "VAROL HUKUK hakkında bilgi")
    ctx.update({"team": sorted(team, key=lambda x: x.order)})
    return templates.TemplateResponse(request, "public/about_us.html", ctx)


@router.get("/hakkimizda/kurucumuz/")
def founder(request: Request):
    ctx = base_context(request, "/hakkimizda/kurucumuz/", "Kurucumuz", "Kurucu avukat hakkında")
    return templates.TemplateResponse(request, "public/founder.html", ctx)


@router.get("/hizmetler/")
def service_list(request: Request):
    services = list_services(active_only=True)
    ctx = base_context(request, "/hizmetler/", "Hizmetlerimiz", "Sunulan hukuk hizmetleri")
    ctx.update({"services": services})
    return templates.TemplateResponse(request, "public/services.html", ctx)


@router.get("/hizmetler/{slug}/")
def service_detail(request: Request, slug: str):
    service = get_service(slug)
    if not service or not service.meta.is_active:
        return Response(status_code=404)
    ctx = base_context(
        request,
        f"/hizmetler/{slug}/",
        service.meta.seo_title or service.meta.title,
        service.meta.seo_description or service.meta.summary,
    )
    ctx.update({"service": service})
    return templates.TemplateResponse(request, "public/service_detail.html", ctx)


@router.get("/makale/")
def post_list(request: Request, kategori: str | None = None):
    posts = list_posts(include_drafts=False)
    categories = [c for c in load_categories() if c.is_active]
    if kategori:
        posts = [post for post in posts if post.meta.category_slug == kategori]
    ctx = base_context(request, "/makale/", "Makaleler", "Hukuki makaleler")
    ctx.update({"posts": posts, "categories": categories, "selected_category": kategori or ""})
    return templates.TemplateResponse(request, "public/posts.html", ctx)


@router.get("/makale/{slug}/")
def post_detail(request: Request, slug: str):
    post = get_post(slug)
    if not post:
        return Response(status_code=404)
    now = datetime.now(UTC)
    if post.meta.status != "published" or post.meta.published_at.astimezone(UTC) > now:
        return Response(status_code=404)
    ctx = base_context(
        request,
        f"/makale/{slug}/",
        post.meta.seo_title or post.meta.title,
        post.meta.seo_description or post.meta.excerpt,
    )
    ctx.update({"post": post})
    return templates.TemplateResponse(request, "public/post_detail.html", ctx)


@router.get("/iletisim/")
def contact_get(request: Request):
    ctx = base_context(request, "/iletisim/", "İletişim", "VAROL HUKUK iletişim bilgileri")
    ctx.update({"form_status": None, "errors": []})
    return templates.TemplateResponse(request, "public/contact.html", ctx)


@router.post("/iletisim/")
def contact_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(default=""),
    message: str = Form(...),
    website: str = Form(default=""),
):
    # Honeypot: bot ise sessizce başarı döndür
    if website.strip():
        ctx = base_context(request, "/iletisim/", "İletişim", "VAROL HUKUK iletişim bilgileri")
        ctx.update({"form_status": "success", "errors": []})
        return templates.TemplateResponse(request, "public/contact.html", ctx)

    errors: list[str] = []
    ip = _client_ip(request)
    if not _limiter.allow(ip):
        errors.append("Çok sık deneme yaptınız. Lütfen birkaç dakika sonra tekrar deneyin.")

    try:
        form = ContactFormData(name=name, email=email, phone=phone, message=message, website=website)
    except Exception:
        errors.append("Form alanlarını kontrol edin.")
        form = None

    if not errors and form:
        entry = LeadEntry(
            timestamp=datetime.now(UTC),
            ip=ip,
            user_agent=request.headers.get("user-agent", ""),
            name=form.name,
            email=form.email,
            phone=form.phone,
            message=form.message,
        )
        append_lead(entry)

        body = (
            f"Yeni iletişim formu:\n\n"
            f"Ad Soyad: {entry.name}\n"
            f"E-posta: {entry.email}\n"
            f"Telefon: {entry.phone}\n"
            f"IP: {entry.ip}\n\n"
            f"Mesaj:\n{entry.message}\n"
        )
        send_contact_notification("VAROL HUKUK - Yeni İletişim Formu", body)

        ctx = base_context(request, "/iletisim/", "İletişim", "VAROL HUKUK iletişim bilgileri")
        ctx.update({"form_status": "success", "errors": []})
        return templates.TemplateResponse(request, "public/contact.html", ctx)

    ctx = base_context(request, "/iletisim/", "İletişim", "VAROL HUKUK iletişim bilgileri")
    ctx.update({"form_status": "error", "errors": errors})
    return templates.TemplateResponse(request, "public/contact.html", ctx, status_code=400)


@router.get("/kvkk/")
def kvkk(request: Request):
    ctx = base_context(request, "/kvkk/", "KVKK / Gizlilik", "KVKK ve gizlilik metni")
    return templates.TemplateResponse(request, "public/kvkk.html", ctx)


@router.get("/yasal-uyari/")
def legal_warning(request: Request):
    ctx = base_context(request, "/yasal-uyari/", "Yasal Uyarı", "Yasal uyarı metni")
    return templates.TemplateResponse(request, "public/legal_warning.html", ctx)


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots() -> str:
    return "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"


@router.get("/sitemap.xml")
def sitemap() -> Response:
    urls = [
        "/",
        "/hakkimizda/biz-kimiz/",
        "/hakkimizda/kurucumuz/",
        "/hizmetler/",
        "/makale/",
        "/iletisim/",
        "/kvkk/",
        "/yasal-uyari/",
    ]

    for service in list_services(active_only=True):
        urls.append(f"/hizmetler/{service.meta.slug}/")
    for post in list_posts(include_drafts=False):
        urls.append(f"/makale/{post.meta.slug}/")

    xml_items = "\n".join(
        [f"  <url><loc>{settings.base_url.rstrip('/')}{path}</loc></url>" for path in urls]
    )
    xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n{xml_items}\n</urlset>"
    return Response(content=xml, media_type="application/xml")


@router.get("/healthz")
def healthz() -> dict[str, Any]:
    return {"status": "ok"}
