from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ask, debug, digest, health, sources
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="dispatch", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(ask.router, prefix="/api")
    app.include_router(digest.router, prefix="/api")
    app.include_router(sources.router, prefix="/api")
    app.include_router(debug.router, prefix="/api")

    return app


app = create_app()
