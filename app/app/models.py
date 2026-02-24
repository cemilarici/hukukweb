from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


SLUG_PATTERN = r"^[a-z0-9-]+$"


class ServiceMeta(BaseModel):
    title: str = Field(min_length=2)
    slug: str = Field(pattern=SLUG_PATTERN)
    summary: str = Field(default="")
    order: int = 0
    is_active: bool = True
    seo_title: str = ""
    seo_description: str = ""
    background_image: str | None = None


class BlogMeta(BaseModel):
    title: str = Field(min_length=2)
    slug: str = Field(pattern=SLUG_PATTERN)
    excerpt: str = ""
    category_slug: str = Field(default="", pattern=r"^$|^[a-z0-9-]+$")
    published_at: datetime
    status: Literal["draft", "published"] = "draft"
    seo_title: str = ""
    seo_description: str = ""
    cover_image: str | None = None
    background_image: str | None = None


class CategoryItem(BaseModel):
    name: str = Field(min_length=2)
    slug: str = Field(pattern=SLUG_PATTERN)
    is_active: bool = True


class TeamItem(BaseModel):
    name: str = Field(min_length=2)
    title: str = ""
    bio: str = ""
    image: str | None = None
    order: int = 0
    is_active: bool = True


class SocialLinks(BaseModel):
    linkedin: str = ""
    instagram: str = ""
    x: str = ""


class SiteSettings(BaseModel):
    firm_name: str = "VAROL HUKUK"
    phone: str = ""
    whatsapp: str = ""
    email: str = ""
    address: str = ""
    map_iframe_url: str = ""
    about_text: str = ""
    founder_text: str = ""
    background_image: str | None = None
    default_seo_title: str = "VAROL HUKUK"
    default_seo_description: str = ""
    social: SocialLinks = Field(default_factory=SocialLinks)


class UserRecord(BaseModel):
    username: str = Field(min_length=3)
    password_hash: str = Field(min_length=20)
    created_at: datetime
    updated_at: datetime


class LeadEntry(BaseModel):
    timestamp: datetime
    ip: str
    user_agent: str = ""
    name: str = Field(min_length=2)
    email: EmailStr
    phone: str = ""
    message: str = Field(min_length=5)


class ContactFormData(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(default="", max_length=60)
    message: str = Field(min_length=5, max_length=3000)
    website: str = ""

    @field_validator("website")
    @classmethod
    def honeypot_must_be_empty(cls, value: str) -> str:
        if value.strip():
            raise ValueError("spam_detected")
        return value


class SeoMeta(BaseModel):
    title: str
    description: str
    canonical: str
    og_title: str
    og_description: str


class Document(BaseModel):
    meta: ServiceMeta | BlogMeta
    content_markdown: str
    content_html: str


class BlogDocument(BaseModel):
    meta: BlogMeta
    content_markdown: str
    content_html: str


class ServiceDocument(BaseModel):
    meta: ServiceMeta
    content_markdown: str
    content_html: str


class JsonEnvelope(BaseModel):
    data: Any
