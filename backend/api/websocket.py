"""
VoxShield — WebSocket Live Analysis
Streams audio chunks from client, runs the full pipeline on each chunk,
pushes real-time risk updates back.

Protocol:
  Client → Server: binary audio chunk (WAV bytes)
  Server → Client: JSON analysis result per chunk
  Client → Server: text "END" to close session
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Optional

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt
import os

from utils.audio import load_audio_bytes, split_into_chunks

logger = logging.getLogger(__name__)

router = APIRouter()

JWT_SECRET = os.getenv("VOXSHIELD_JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"


def _verify_token(token: str) -> Optional[str]:
    """Return user_id from JWT or None if invalid."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


@router.websocket("/analyze")
async def ws_analyze(websocket: WebSocket, token: str = Query(...)):
    """
    WebSocket endpoint for live audio analysis.

    Query param: ?token=<JWT>

    Each received binary message is processed through the full pipeline.
    Results are pushed back as JSON in real-time.
    """
    await websocket.accept()

    user_id = _verify_token(token)
    if not user_id:
        await websocket.send_json({"error": "Unauthorized", "type": "error"})
        await websocket.close(code=4001)
        return

    session_id = str(uuid.uuid4())
    logger.info(f"WS session started: {session_id} for user {user_id}")

    await websocket.send_json({
        "type": "connected",
        "session_id": session_id,
        "message": "VoxShield Live Protection active",
    })

    # Accumulate transcript across chunks for better scam detection
    accumulated_transcript = ""
    chunk_count = 0

    try:
        import main as app_main

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive(), timeout=60.0)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "keepalive"})
                continue

            # Client sends "END" text to close cleanly
            if data.get("type") == "websocket.disconnect":
                break
            if data.get("type") == "websocket.receive":
                if data.get("text") == "END":
                    break
                audio_bytes = data.get("bytes")
                if not audio_bytes:
                    continue
            else:
                continue

            chunk_start = time.perf_counter()
            chunk_count += 1

            try:
                waveform, sr = load_audio_bytes(audio_bytes)
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "chunk": chunk_count,
                    "error": f"Audio decode failed: {e}",
                })
                continue

            # --- Run pipeline on chunk ---
            result = {
                "type": "analysis",
                "chunk": chunk_count,
                "session_id": session_id,
            }

            # ASR
            asr = {"model_available": False, "text": "", "language": None, "latency_ms": 0}
            if app_main.speech_service and app_main.speech_service.is_available:
                asr = app_main.speech_service.transcribe(waveform, sr)
            result["transcript"] = {
                "text": asr.get("text", ""),
                "language": asr.get("language"),
                "latency_ms": asr.get("latency_ms"),
                "model_available": asr.get("model_available"),
            }

            # Accumulate transcript for better scam context
            chunk_text = asr.get("text", "").strip()
            if chunk_text:
                accumulated_transcript = (accumulated_transcript + " " + chunk_text).strip()

            # Deepfake detection on this chunk
            df = {"model_available": False, "fake_probability": None, "label": "unavailable", "latency_ms": 0}
            if app_main.deepfake_service and app_main.deepfake_service.is_available:
                df = app_main.deepfake_service.analyze(waveform, sr)
            result["deepfake"] = {
                "fake_probability": df.get("fake_probability"),
                "real_probability": df.get("real_probability"),
                "label": df.get("label"),
                "latency_ms": df.get("latency_ms"),
                "model_available": df.get("model_available"),
            }

            # Scam analysis on accumulated transcript
            scam = {"scam_probability": 0.0, "category": "UNKNOWN", "signals": []}
            if app_main.scam_service and accumulated_transcript:
                scam = app_main.scam_service.analyze(accumulated_transcript)
            result["scam"] = {
                "scam_probability": scam.get("scam_probability"),
                "category": scam.get("category"),
                "category_name": scam.get("category_name"),
                "signals": scam.get("signals", []),
                "financial_request": scam.get("financial_request"),
                "urgency_detected": scam.get("urgency_detected"),
            }

            # Risk engine
            risk = {"risk_score": None, "risk_level": "UNKNOWN", "reasons": []}
            if app_main.risk_engine:
                risk_result = app_main.risk_engine.compute(
                    voice_fake_probability=df.get("fake_probability"),
                    scam_result=scam,
                    caller_history={"is_unknown": True, "is_trusted": False, "previous_alerts": 0},
                )
                risk = risk_result.to_dict()
            result["risk"] = {
                "risk_score": risk.get("risk_score"),
                "risk_level": risk.get("risk_level"),
                "reasons": risk.get("reasons", []),
                "recommended_actions": risk.get("recommended_actions", []),
            }

            result["accumulated_transcript"] = accumulated_transcript
            result["chunk_latency_ms"] = round((time.perf_counter() - chunk_start) * 1000, 1)

            await websocket.send_json(result)

    except WebSocketDisconnect:
        logger.info(f"WS session disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WS session error: {session_id}: {e}")
        try:
            await websocket.send_json({"type": "error", "error": str(e)})
        except Exception:
            pass
    finally:
        logger.info(f"WS session ended: {session_id}, chunks processed: {chunk_count}")
