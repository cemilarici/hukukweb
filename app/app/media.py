from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image

from app.config import DATA_DIR
from app.storage import slugify

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_BYTES = 5 * 1024 * 1024
MAX_WIDTH = 1600


def _extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()


def validate_and_save_image(upload: UploadFile, slug_hint: str) -> str:
    ext = _extension(upload.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Sadece jpg, png veya webp yüklenebilir")

    payload = upload.file.read()
    if len(payload) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="Maksimum yükleme boyutu 5MB")

    try:
        image = Image.open(BytesIO(payload))
        image.load()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Geçersiz resim dosyası") from exc

    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")

    if image.width > MAX_WIDTH:
        ratio = MAX_WIDTH / float(image.width)
        image = image.resize((MAX_WIDTH, int(image.height * ratio)))

    safe_slug = slugify(slug_hint)
    file_name = f"{safe_slug}.{ 'jpg' if ext == 'jpeg' else ext }"
    dest: Path = DATA_DIR / "media" / "uploads" / file_name
    dest.parent.mkdir(parents=True, exist_ok=True)

    save_format = "JPEG" if file_name.endswith(".jpg") else file_name.rsplit(".", 1)[1].upper()
    image.save(dest, format=save_format, optimize=True)
    return f"/data/media/uploads/{file_name}"
