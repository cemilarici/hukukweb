from pathlib import Path

from app.models import ServiceMeta
from app.storage import read_md_frontmatter, write_md_frontmatter_atomic


def test_frontmatter_roundtrip(isolated_data):
    target = isolated_data / "services" / "example.md"
    meta = ServiceMeta(
        title="Baslik",
        slug="example",
        summary="ozet",
        order=1,
        is_active=True,
        seo_title="",
        seo_description="",
    )

    write_md_frontmatter_atomic(target, meta.model_dump(mode="json"), "icerik")
    loaded_meta, body = read_md_frontmatter(target)

    assert loaded_meta["slug"] == "example"
    assert body == "icerik"
