"""Zorva / GigShield — FastAPI application entry point."""

from contextlib import asynccontextmanager
import logging
import socket
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.db.database import engine, Base
from app.api import income, gigscore, insurance, sos, schemes, earnings_optimizer


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hooks."""
    db_initialized = False

    # ── Startup: create tables (dev only) ─────────────────────
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        db_initialized = True
    except (socket.gaierror, OSError, SQLAlchemyError) as exc:
        if settings.db_required_on_startup:
            raise
        logger.warning(
            "Database unavailable during startup; continuing without DB initialization. "
            "Set DB_REQUIRED_ON_STARTUP=true to fail fast. Error: %s",
            exc,
        )

    yield

    # ── Shutdown: dispose engine ──────────────────────────────
    await engine.dispose()


settings = get_settings()

app = FastAPI(
    title="Zorva — GigShield API",
    description=(
        "AI-powered financial identity & protection platform for gig workers. "
        "Provides GigScore, income aggregation, micro-insurance, SOS routing, "
        "and government scheme matching."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Route registration ───────────────────────────────────────
app.include_router(income.router,              prefix="/api/v1/income",     tags=["Income"])
app.include_router(gigscore.router,            prefix="/api/v1/gigscore",   tags=["GigScore"])
app.include_router(insurance.router,           prefix="/api/v1/insurance",  tags=["Insurance"])
app.include_router(sos.router,                 prefix="/api/v1/sos",        tags=["SOS"])
app.include_router(schemes.router,             prefix="/api/v1/schemes",    tags=["Schemes"])
app.include_router(earnings_optimizer.router,  prefix="/api/v1/earnings",   tags=["Earnings"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Zorva GigShield API",
        "version": "0.1.0",
        "status": "operational",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "env": settings.app_env}
