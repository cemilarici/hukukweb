# VAROL HUKUK - FastAPI File CMS MVP

TR odakli, SSR FastAPI tabanli hukuk burosu sitesi. Veritabani yoktur; tum icerik `./data/` altinda dosya olarak saklanir.

## Ozellikler
- Public site: `/`, `/hizmetler`, `/makale`, `/iletisim`, `/kvkk`, `/yasal-uyari`
- Admin panel: `/admin` (login + CRUD)
- Dosya tabanli CMS:
  - `data/services/*.md`
  - `data/blog/*.md`
  - `data/categories.json`
  - `data/team.json`
  - `data/site_settings.json`
  - `data/leads/leads-YYYY-MM.jsonl`
- SMTP bildirim (Gmail/Outlook STARTTLS 587)
- Medya yukleme (jpg/png/webp, max 5MB, Pillow resize)
- CSRF korumasi, session tabanli admin auth, Argon2 hash

## Hizli Baslangic (Docker)
1. `.env.example` dosyasini `.env` olarak kopyalayin ve degiskenleri doldurun.
2. Koku dizinde calistirin:
   ```bash
   docker compose up --build
   ```
3. Acilis:
   - Public: `http://localhost:8000`
   - Admin: `http://localhost:8000/admin/login`

## Lokal Gelistirme
```bash
cd app
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python scripts/seed_demo.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Test
```bash
cd app
pytest -q
```

## Seed
Ornek veri olusturmak icin:
```bash
cd app
python scripts/seed_demo.py
```

## Operasyon Notu
Yedekleme icin `./data` klasorunu kopyalamaniz yeterlidir.
