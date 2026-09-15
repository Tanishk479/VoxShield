"""
VoxShield — FastAPI Application Entry Point
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("voxshield")

CONFIG_PATH = Path(__file__).parent / "config.yaml"

# Global service instances (loaded once at startup)
speech_service = None
deepfake_service = None
scam_service = None
risk_engine = None
startup_status = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models and initialize DB on startup."""
    global speech_service, deepfake_service, scam_service, risk_engine, startup_status

    logger.info("=" * 60)
    logger.info("🚀 VoxShield starting up...")
    logger.info("=" * 60)

    # 1. Initialize database
    from db.database import init_db
    await init_db()
    logger.info("✅ Database initialized")

    # 2. Load Scam Intelligence (fast — no ML model needed)
    from ai.scam.scam_service import ScamIntelligenceService
    scam_service = ScamIntelligenceService()
    startup_status["scam"] = "ready"
    logger.info("✅ Scam Intelligence ready")

    # 3. Load Risk Engine
    from ai.risk.risk_engine import RiskEngine
    risk_engine = RiskEngine()
    startup_status["risk_engine"] = "ready"
    logger.info("✅ Risk Engine ready")

    # 4. Load Speech (Whisper)
    from ai.speech.speech_service import SpeechRecognitionService
    speech_service = SpeechRecognitionService()
    speech_status = speech_service.initialize()
    startup_status["speech"] = speech_status
    logger.info(f"Speech backends: {speech_status}")

    # 5. Load Deepfake detector
    from ai.deepfake.deepfake_service import DeepfakeDetectionService
    deepfake_service = DeepfakeDetectionService()
    df_ok = deepfake_service.initialize()
    startup_status["deepfake"] = "ready" if df_ok else "failed — check logs"
    logger.info(f"Deepfake detector: {'✅' if df_ok else '❌'} {startup_status['deepfake']}")

    logger.info("=" * 60)
    logger.info("✅ VoxShield ready")
    logger.info(f"   Status: {startup_status}")
    logger.info("=" * 60)

    yield  # App is running

    logger.info("VoxShield shutting down...")


app = FastAPI(
    title="VoxShield API",
    description="AI-Powered Real-Time Voice Scam Protection — SIH 2026",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Next.js frontend in dev
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ─── Mount API Routers ────────────────────────────────────────────────────────
from api.auth import router as auth_router
from api.calls import router as calls_router
from api.dashboard import router as dashboard_router
from api.callers import router as callers_router
from api.websocket import router as ws_router

app.include_router(auth_router,      prefix="/api/auth",      tags=["Auth"])
app.include_router(calls_router,     prefix="/api/calls",     tags=["Calls"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(callers_router,   prefix="/api/callers",   tags=["Callers"])
app.include_router(ws_router,        prefix="/ws",            tags=["WebSocket"])


@app.get("/api/health")
async def health():
    """Health check + model status."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "services": startup_status,
    }


@app.get("/")
async def root():
    return {"message": "VoxShield API — SIH 2026. See /docs for API reference."}
