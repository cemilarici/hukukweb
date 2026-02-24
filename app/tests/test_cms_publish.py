from datetime import UTC, datetime

from app.cms import list_posts, save_post
from app.models import BlogMeta


def test_publish_filter(isolated_data):
    save_post(
        BlogMeta(
            title="Taslak",
            slug="taslak",
            excerpt="",
            category_slug="",
            published_at=datetime.now(UTC),
            status="draft",
            seo_title="",
            seo_description="",
        ),
        "test",
    )
    save_post(
        BlogMeta(
            title="Yayin",
            slug="yayin",
            excerpt="",
            category_slug="",
            published_at=datetime.now(UTC),
            status="published",
            seo_title="",
            seo_description="",
        ),
        "test",
    )

    published = list_posts(include_drafts=False)
    all_posts = list_posts(include_drafts=True)

    assert len(all_posts) == 2
    assert len(published) == 1
    assert published[0].meta.slug == "yayin"
