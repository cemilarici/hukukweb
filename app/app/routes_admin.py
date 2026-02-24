from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse

from app.auth import (
    csrf_form_token,
    ensure_admin_user,
    get_current_admin,
    issue_csrf,
    login_admin,
    logout_admin,
    validate_csrf,
)
from app.cms import (
    delete_post,
    delete_service,
    get_post,
    get_service,
    list_posts,
    list_services,
    load_categories,
    load_site_settings,
    load_team,
    save_categories,
    save_post,
    save_service,
    save_site_settings,
    save_team,
)
from app.media import validate_and_save_image
from app.models import BlogMeta, CategoryItem, ServiceMeta, SiteSettings, TeamItem
from app.storage import slugify
from app.views import base_context, templates

router = APIRouter(prefix="/admin", tags=["admin"])


def _is_checked(value: str | None) -> bool:
    return value in {"on", "true", "1", "yes"}


@router.get("/")
def admin_index(request: Request, _: str = Depends(get_current_admin)):
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.get("/login")
def admin_login_page(request: Request):
    ensure_admin_user()
    ctx = {"request": request, "error": "", "csrf_token": issue_csrf(request)}
    return templates.TemplateResponse(request, "admin/login.html", ctx)


@router.post("/login")
def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Depends(csrf_form_token),
):
    validate_csrf(request, csrf_token)
    from app.auth import verify_login

    if not verify_login(username, password):
        ctx = {"request": request, "error": "Hatalı kullanıcı adı veya şifre.", "csrf_token": issue_csrf(request)}
        return templates.TemplateResponse(request, "admin/login.html", ctx, status_code=401)

    login_admin(request, username)
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.post("/logout")
def admin_logout(request: Request, _: str = Depends(get_current_admin), csrf_token: str = Depends(csrf_form_token)):
    validate_csrf(request, csrf_token)
    logout_admin(request)
    return RedirectResponse(url="/admin/login", status_code=303)


@router.get("/dashboard")
def dashboard(request: Request, _: str = Depends(get_current_admin)):
    ctx = base_context(request, "/admin/dashboard", "Admin Panel", "")
    ctx.update(
        {
            "csrf_token": issue_csrf(request),
            "services_count": len(list_services(active_only=False)),
            "posts_count": len(list_posts(include_drafts=True)),
            "categories_count": len(load_categories()),
            "team_count": len(load_team()),
        }
    )
    return templates.TemplateResponse(request, "admin/dashboard.html", ctx)


@router.get("/services")
def services_list(request: Request, _: str = Depends(get_current_admin)):
    ctx = base_context(request, "/admin/services", "Hizmet Yönetimi", "")
    ctx.update({"items": list_services(active_only=False), "csrf_token": issue_csrf(request)})
    return templates.TemplateResponse(request, "admin/services_list.html", ctx)


@router.get("/services/new")
def service_new_form(request: Request, _: str = Depends(get_current_admin)):
    ctx = base_context(request, "/admin/services/new", "Yeni Hizmet", "")
    ctx.update({"item": None, "csrf_token": issue_csrf(request)})
    return templates.TemplateResponse(request, "admin/service_form.html", ctx)


@router.get("/services/{slug}/edit")
def service_edit_form(slug: str, request: Request, _: str = Depends(get_current_admin)):
    item = get_service(slug)
    if not item:
        raise HTTPException(status_code=404)
    ctx = base_context(request, f"/admin/services/{slug}/edit", "Hizmet Düzenle", "")
    ctx.update({"item": item, "csrf_token": issue_csrf(request)})
    return templates.TemplateResponse(request, "admin/service_form.html", ctx)


@router.post("/services/save")
def service_save(
    request: Request,
    _: str = Depends(get_current_admin),
    csrf_token: str = Depends(csrf_form_token),
    slug_original: str = Form(default=""),
    title: str = Form(...),
    slug: str = Form(...),
    summary: str = Form(default=""),
    order: int = Form(default=0),
    is_active: str | None = Form(default=None),
    seo_title: str = Form(default=""),
    seo_description: str = Form(default=""),
    content_markdown: str = Form(default=""),
):
    validate_csrf(request, csrf_token)
    clean_slug = slugify(slug)
    meta = ServiceMeta(
        title=title,
        slug=clean_slug,
        summary=summary,
        order=order,
        is_active=_is_checked(is_active),
        seo_title=seo_title,
        seo_description=seo_description,
    )
    save_service(meta, content_markdown)
    if slug_original and slug_original != clean_slug:
        delete_service(slug_original)
    return RedirectResponse(url="/admin/services", status_code=303)


@router.post("/services/{slug}/delete")
def service_delete(slug: str, request: Request, _: str = Depends(get_current_admin), csrf_token: str = Depends(csrf_form_token)):
    validate_csrf(request, csrf_token)
    delete_service(slug)
    return RedirectResponse(url="/admin/services", status_code=303)


@router.get("/posts")
def posts_list(request: Request, _: str = Depends(get_current_admin)):
    ctx = base_context(request, "/admin/posts", "Makale Yönetimi", "")
    ctx.update({"items": list_posts(include_drafts=True), "csrf_token": issue_csrf(request)})
    return templates.TemplateResponse(request, "admin/posts_list.html", ctx)


@router.get("/posts/new")
def post_new_form(request: Request, _: str = Depends(get_current_admin)):
    ctx = base_context(request, "/admin/posts/new", "Yeni Makale", "")
    ctx.update({"item": None, "categories": load_categories(), "csrf_token": issue_csrf(request)})
    return templates.TemplateResponse(request, "admin/post_form.html", ctx)


@router.get("/posts/{slug}/edit")
def post_edit_form(slug: str, request: Request, _: str = Depends(get_current_admin)):
    item = get_post(slug)
    if not item:
        raise HTTPException(status_code=404)
    ctx = base_context(request, f"/admin/posts/{slug}/edit", "Makale Düzenle", "")
    ctx.update({"item": item, "categories": load_categories(), "csrf_token": issue_csrf(request)})
    return templates.TemplateResponse(request, "admin/post_form.html", ctx)


@router.post("/posts/save")
def post_save(
    request: Request,
    _: str = Depends(get_current_admin),
    csrf_token: str = Depends(csrf_form_token),
    slug_original: str = Form(default=""),
    title: str = Form(...),
    slug: str = Form(...),
    excerpt: str = Form(default=""),
    category_slug: str = Form(default=""),
    published_at: str = Form(...),
    status: str = Form(default="draft"),
    seo_title: str = Form(default=""),
    seo_description: str = Form(default=""),
    content_markdown: str = Form(default=""),
    cover_image: UploadFile | None = None,
):
    validate_csrf(request, csrf_token)

    clean_slug = slugify(slug)
    parsed_published = datetime.fromisoformat(published_at)
    if parsed_published.tzinfo is None:
        parsed_published = parsed_published.replace(tzinfo=UTC)

    previous = get_post(slug_original) if slug_original else None
    cover_path = previous.meta.cover_image if previous else None
    if cover_image and cover_image.filename:
        cover_path = validate_and_save_image(cover_image, f"post-{clean_slug}")

    meta = BlogMeta(
        title=title,
        slug=clean_slug,
        excerpt=excerpt,
        category_slug=slugify(category_slug) if category_slug else "",
        published_at=parsed_published,
        status="published" if status == "published" else "draft",
        seo_title=seo_title,
        seo_description=seo_description,
        cover_image=cover_path,
    )
    save_post(meta, content_markdown)
    if slug_original and slug_original != clean_slug:
        delete_post(slug_original)
    return RedirectResponse(url="/admin/posts", status_code=303)


@router.post("/posts/{slug}/delete")
def post_delete(slug: str, request: Request, _: str = Depends(get_current_admin), csrf_token: str = Depends(csrf_form_token)):
    validate_csrf(request, csrf_token)
    delete_post(slug)
    return RedirectResponse(url="/admin/posts", status_code=303)


@router.get("/categories")
def categories_list(request: Request, _: str = Depends(get_current_admin)):
    ctx = base_context(request, "/admin/categories", "Kategori Yönetimi", "")
    ctx.update({"items": load_categories(), "csrf_token": issue_csrf(request)})
    return templates.TemplateResponse(request, "admin/categories.html", ctx)


@router.post("/categories/save")
def categories_save(
    request: Request,
    _: str = Depends(get_current_admin),
    csrf_token: str = Depends(csrf_form_token),
    name: str = Form(...),
    slug: str = Form(...),
    is_active: str | None = Form(default="on"),
):
    validate_csrf(request, csrf_token)
    items = load_categories()
    clean_slug = slugify(slug)
    existing = [i for i in items if i.slug == clean_slug]
    item = CategoryItem(name=name, slug=clean_slug, is_active=_is_checked(is_active))
    if existing:
        items = [item if i.slug == clean_slug else i for i in items]
    else:
        items.append(item)
    save_categories(items)
    return RedirectResponse(url="/admin/categories", status_code=303)


@router.post("/categories/{slug}/delete")
def categories_delete(slug: str, request: Request, _: str = Depends(get_current_admin), csrf_token: str = Depends(csrf_form_token)):
    validate_csrf(request, csrf_token)
    items = [i for i in load_categories() if i.slug != slugify(slug)]
    save_categories(items)
    return RedirectResponse(url="/admin/categories", status_code=303)


@router.get("/team")
def team_list(request: Request, _: str = Depends(get_current_admin)):
    ctx = base_context(request, "/admin/team", "Ekip Yönetimi", "")
    ctx.update({"items": sorted(load_team(), key=lambda x: x.order), "csrf_token": issue_csrf(request)})
    return templates.TemplateResponse(request, "admin/team.html", ctx)


@router.post("/team/save")
def team_save(
    request: Request,
    _: str = Depends(get_current_admin),
    csrf_token: str = Depends(csrf_form_token),
    name: str = Form(...),
    title: str = Form(default=""),
    bio: str = Form(default=""),
    order: int = Form(default=0),
    is_active: str | None = Form(default="on"),
):
    validate_csrf(request, csrf_token)
    items = load_team()
    key = slugify(name)
    candidate = TeamItem(name=name, title=title, bio=bio, order=order, is_active=_is_checked(is_active))
    found = False
    updated: list[TeamItem] = []
    for item in items:
        if slugify(item.name) == key:
            updated.append(candidate)
            found = True
        else:
            updated.append(item)
    if not found:
        updated.append(candidate)
    save_team(updated)
    return RedirectResponse(url="/admin/team", status_code=303)


@router.post("/team/{name_slug}/delete")
def team_delete(name_slug: str, request: Request, _: str = Depends(get_current_admin), csrf_token: str = Depends(csrf_form_token)):
    validate_csrf(request, csrf_token)
    items = [i for i in load_team() if slugify(i.name) != slugify(name_slug)]
    save_team(items)
    return RedirectResponse(url="/admin/team", status_code=303)


@router.get("/settings")
def settings_form(request: Request, _: str = Depends(get_current_admin), saved: int = 0, error: str = ""):
    ctx = base_context(request, "/admin/settings", "Site Ayarları", "")
    ctx.update(
        {
            "item": load_site_settings(),
            "csrf_token": issue_csrf(request),
            "saved": bool(saved),
            "error": error,
        }
    )
    return templates.TemplateResponse(request, "admin/settings.html", ctx)


@router.post("/settings")
def settings_save(
    request: Request,
    _: str = Depends(get_current_admin),
    csrf_token: str = Depends(csrf_form_token),
    firm_name: str = Form(default=""),
    phone: str = Form(default=""),
    whatsapp: str = Form(default=""),
    email: str = Form(default=""),
    address: str = Form(default=""),
    map_iframe_url: str = Form(default=""),
    about_text: str = Form(default=""),
    founder_text: str = Form(default=""),
    default_seo_title: str = Form(default=""),
    default_seo_description: str = Form(default=""),
    linkedin: str = Form(default=""),
    instagram: str = Form(default=""),
    x: str = Form(default=""),
    remove_background: str | None = Form(default=None),
    background_image_file: UploadFile | None = File(default=None),
):
    validate_csrf(request, csrf_token)
    current = load_site_settings()
    background_image = current.background_image
    if _is_checked(remove_background):
        background_image = None
    if background_image_file and background_image_file.filename:
        background_image = validate_and_save_image(background_image_file, "site-background")

    final_firm_name = (firm_name or current.firm_name or "VAROL HUKUK").strip()
    try:
        payload = SiteSettings(
            firm_name=final_firm_name,
            phone=phone,
            whatsapp=whatsapp,
            email=email,
            address=address,
            map_iframe_url=map_iframe_url,
            about_text=about_text,
            founder_text=founder_text,
            background_image=background_image,
            default_seo_title=default_seo_title or final_firm_name,
            default_seo_description=default_seo_description,
            social={"linkedin": linkedin, "instagram": instagram, "x": x},
        )
        save_site_settings(payload)
        return RedirectResponse(url="/admin/settings?saved=1", status_code=303)
    except Exception:
        return RedirectResponse(url="/admin/settings?error=Kayit%20sirasinda%20hata%20olustu", status_code=303)
