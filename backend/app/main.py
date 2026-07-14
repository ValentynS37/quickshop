from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import build_router
from .config import Settings, get_settings
from .database import Base, build_engine, build_session_factory


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.2.0",
        description="Human-in-the-loop agent workflow and Evidence Engine for BADS TrustOS.",
    )
    app.state.settings = settings
    app.state.engine = build_engine(settings.database_url)
    app.state.session_factory = build_session_factory(app.state.engine)
    Base.metadata.create_all(app.state.engine)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-BADS-API-Key"],
    )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name, "version": "0.2.0"}

    app.include_router(build_router(settings), prefix=settings.api_prefix, tags=["BADS OS"])
    return app


app = create_app()
