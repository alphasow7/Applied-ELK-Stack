from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.logging import logger
from app.models.database import init_db
from app.routes import auth, farmers, market, weather, ussd, analytics

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Plateforme de données prédictives pour l'agriculture — "
        "USSD/SMS pour les agriculteurs, Web & API pour les coopératives et acheteurs."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = round((time.time() - start) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} → {response.status_code} ({elapsed}ms)",
    )
    return response


@app.on_event("startup")
async def startup():
    await init_db()
    # Seed demo data
    from app.models.database import AsyncSessionLocal
    from app.services.seed_service import seed_database
    async with AsyncSessionLocal() as db:
        await seed_database(db)
    logger.info("AgriTech Platform started ✓")


# Routes
app.include_router(auth.router, prefix="/api")
app.include_router(farmers.router, prefix="/api")
app.include_router(market.router, prefix="/api")
app.include_router(weather.router, prefix="/api")
app.include_router(ussd.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}


@app.get("/")
async def root():
    return {
        "message": "AgriTech Platform API",
        "docs": "/api/docs",
        "ussd_demo": "/api/ussd/demo",
        "health": "/api/health",
    }
