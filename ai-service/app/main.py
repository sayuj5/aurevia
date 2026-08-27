from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import health, nlp, audio
from app.core.exceptions import AIException, ai_exception_handler, generic_exception_handler

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add exception handlers
    app.add_exception_handler(AIException, ai_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Include routers
    app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
    app.include_router(nlp.router, prefix=settings.API_V1_STR, tags=["nlp"])
    app.include_router(audio.router, prefix=settings.API_V1_STR, tags=["audio"])

    return app

app = create_app()
