from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import ensure_admin_user
from app.cms import save_categories, save_post, save_service, save_site_settings, save_team
from app.models import BlogMeta, CategoryItem, ServiceMeta, SiteSettings, TeamItem
from app.storage import ensure_data_dirs


def run() -> None:
    ensure_data_dirs()
    ensure_admin_user()

    save_site_settings(
        SiteSettings(
            firm_name="VAROL HUKUK",
            phone="+90 212 000 00 00",
            whatsapp="+905550000000",
            email="info@varolhukuk.com",
            address="Istanbul, Turkiye",
            map_iframe_url="",
            about_text="VAROL HUKUK, ticari hukuk ve uyusmazlik cozumunde muvekkillerine stratejik destek sunar.",
            founder_text="Kurucu avukatimiz, sirketler hukuku ve dava yonetimi alaninda calismaktadir.",
            default_seo_title="VAROL HUKUK",
            default_seo_description="Ticari hukuk ve danismanlik hizmetleri",
            social={"linkedin": "", "instagram": "", "x": ""},
        )
    )

    save_categories(
        [
            CategoryItem(name="Ticaret Hukuku", slug="ticaret-hukuku", is_active=True),
            CategoryItem(name="Sozlesmeler", slug="sozlesmeler", is_active=True),
        ]
    )

    save_team(
        [
            TeamItem(name="Av. Ornek Varol", title="Kurucu Avukat", bio="Ticari uyusmazliklar ve sozlesme yonetimi.", order=1, is_active=True)
        ]
    )

    save_service(
        ServiceMeta(
            title="Ticari Dava Takibi",
            slug="ticari-dava-takibi",
            summary="Sirketler arasi uyusmazliklarda temsil ve surec yonetimi.",
            order=1,
            is_active=True,
            seo_title="Ticari Dava Takibi",
            seo_description="Ticari dava sureclerinde uzman hukuki destek.",
        ),
        "Ticari alacak, tazminat ve sozlesme kaynakli uyusmazliklarda dava sureclerini uctan uca yonetiyoruz.",
    )

    save_service(
        ServiceMeta(
            title="Sozlesme Danismanligi",
            slug="sozlesme-danismanligi",
            summary="Sozlesme hazirligi, inceleme ve risk azaltma.",
            order=2,
            is_active=True,
            seo_title="Sozlesme Danismanligi",
            seo_description="Sozlesme sureclerinde riskleri azaltan hukuki danismanlik.",
        ),
        "Satin alma, hizmet ve dagitim sozlesmelerinde muzakere, revizyon ve risk analizi destegi sagliyoruz.",
    )

    save_post(
        BlogMeta(
            title="Ticari Sozlesmelerde Ceza Kosulu",
            slug="ticari-sozlesmelerde-ceza-kosulu",
            excerpt="Ceza kosulu duzenlemelerinde dikkat edilmesi gereken temel noktalar.",
            category_slug="sozlesmeler",
            published_at=datetime.now(UTC),
            status="published",
            seo_title="Ticari Sozlesmelerde Ceza Kosulu",
            seo_description="Ceza kosulu maddelerinin uygulamadaki etkileri.",
        ),
        "Ceza kosulu maddeleri, sozlesme ihlali halinde caydiricilik saglarken olcululuk ilkesine uygun olmalidir.",
    )


if __name__ == "__main__":
    run()
    print("Demo icerik olusturuldu.")
