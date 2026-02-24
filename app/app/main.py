from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.auth import ensure_admin_user
from app.config import DATA_DIR, STATIC_DIR, settings
from app.routes_admin import router as admin_router
from app.routes_public import router as public_router
from app.storage import ensure_data_dirs


def create_app() -> FastAPI:
    app = FastAPI(title=settings.firm_name)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        same_site="lax",
        https_only=settings.app_env == "prod",
    )

    ensure_data_dirs()
    ensure_admin_user()

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

    app.include_router(public_router)
    app.include_router(admin_router)
    return app


app = create_app()
