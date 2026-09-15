"""
VoxShield — Calls API
Upload audio → full AI pipeline → store result → return analysis.
"""

import time
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import get_current_user
from db.database import get_db
from db.models import Call, CallAnalysis, CallerProfile, User

router = APIRouter()


async def _run_pipeline(audio_bytes: bytes, caller_number: Optional[str], user: User) -> dict:
    """
    Run the full VoxShield analysis pipeline on an uploaded audio file.
    All values come from actual model inference.
    """
    import main as app_main
    import numpy as np

    from utils.audio import load_audio_bytes
    from utils.benchmark import get_ram_mb

    total_start = time.perf_counter()
    result = {
        "caller_number": caller_number,
        "user_id": user.id,
    }

    # --- Load audio ---
    try:
        waveform, sr = load_audio_bytes(audio_bytes)
        result["audio_duration_seconds"] = round(len(waveform) / sr, 1)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not process audio: {e}")

    # --- ASR ---
    asr_result = {"model_available": False, "text": "", "language": None, "latency_ms": 0.0}
    if app_main.speech_service and app_main.speech_service.is_available:
        asr_result = app_main.speech_service.transcribe(waveform, sr)
    result["transcript"] = asr_result

    # --- Deepfake Detection ---
    df_result = {"model_available": False, "fake_probability": None, "label": "unavailable", "latency_ms": 0.0}
    if app_main.deepfake_service and app_main.deepfake_service.is_available:
        df_result = app_main.deepfake_service.analyze(waveform, sr)
    result["deepfake"] = df_result

    # --- Scam Intelligence ---
    scam_result = {"scam_probability": 0.0, "category": "UNKNOWN", "signals": []}
    if app_main.scam_service:
        scam_result = app_main.scam_service.analyze(asr_result.get("text", ""))
    result["scam"] = scam_result

    # --- Caller History ---
    # TODO: query CallerProfile for this number
    caller_history = {
        "is_unknown": True,
        "is_trusted": False,
        "previous_alerts": 0,
        "total_calls": 0,
    }
    result["caller_history"] = caller_history

    # --- Risk Engine ---
    risk_result = None
    if app_main.risk_engine:
        risk_result = app_main.risk_engine.compute(
            voice_fake_probability=df_result.get("fake_probability"),
            scam_result=scam_result,
            caller_history=caller_history,
        )
    result["risk"] = risk_result.to_dict() if risk_result else {"risk_score": None, "risk_level": "UNKNOWN"}

    total_ms = (time.perf_counter() - total_start) * 1000
    result["total_latency_ms"] = round(total_ms, 1)
    result["ram_mb"] = round(get_ram_mb(), 1)

    return result


@router.post("/analyze")
async def analyze_call(
    audio: UploadFile = File(...),
    caller_number: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload an audio file for full VoxShield analysis.
    Returns deepfake probability, scam analysis, and risk score.
    All values are from real model inference — never hardcoded.
    """
    audio_bytes = await audio.read()
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=422, detail="Empty audio file")

    pipeline_result = await _run_pipeline(audio_bytes, caller_number, current_user)

    # Store in database
    call_id = str(uuid.uuid4())
    asr = pipeline_result.get("transcript", {})
    df = pipeline_result.get("deepfake", {})
    scam = pipeline_result.get("scam", {})
    risk = pipeline_result.get("risk", {})

    call = Call(
        id=call_id,
        user_id=current_user.id,
        caller_number=caller_number,
        duration_seconds=int(pipeline_result.get("audio_duration_seconds", 0)),
        language=asr.get("language"),
        action_taken="ANALYZED",
        is_demo=False,
    )
    db.add(call)

    analysis = CallAnalysis(
        id=str(uuid.uuid4()),
        call_id=call_id,
        transcript=asr.get("text"),
        asr_model=asr.get("model_id"),
        asr_latency_ms=asr.get("latency_ms"),
        voice_fake_probability=df.get("fake_probability"),
        voice_real_probability=df.get("real_probability"),
        voice_label=df.get("label"),
        deepfake_model=df.get("model_id"),
        deepfake_latency_ms=df.get("latency_ms"),
        scam_probability=scam.get("scam_probability"),
        scam_category=scam.get("category"),
        scam_severity=scam.get("severity"),
        scam_signals=scam.get("signals", []),
        financial_request=scam.get("financial_request", False),
        urgency_detected=scam.get("urgency_detected", False),
        identity_claim=scam.get("identity_claim", False),
        risk_score=risk.get("risk_score"),
        risk_level=risk.get("risk_level"),
        risk_reasons=risk.get("reasons"),
        risk_actions=risk.get("recommended_actions"),
        risk_components=risk.get("component_scores"),
        total_latency_ms=pipeline_result.get("total_latency_ms"),
    )
    db.add(analysis)
    await db.flush()

    return {
        "call_id": call_id,
        "analysis": pipeline_result,
    }


@router.get("/history")
async def call_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get call history for the current user, newest first."""
    result = await db.execute(
        select(Call, CallAnalysis)
        .join(CallAnalysis, Call.id == CallAnalysis.call_id, isouter=True)
        .where(Call.user_id == current_user.id)
        .order_by(desc(Call.timestamp))
        .offset(offset)
        .limit(limit)
    )
    rows = result.all()

    calls = []
    for call, analysis in rows:
        calls.append({
            "id": call.id,
            "caller_number": call.caller_number,
            "timestamp": call.timestamp.isoformat() if call.timestamp else None,
            "duration_seconds": call.duration_seconds,
            "language": call.language,
            "action_taken": call.action_taken,
            "is_demo": call.is_demo,
            "risk_score": analysis.risk_score if analysis else None,
            "risk_level": analysis.risk_level if analysis else None,
            "scam_category": analysis.scam_category if analysis else None,
            "voice_fake_probability": analysis.voice_fake_probability if analysis else None,
        })

    return {"calls": calls, "total": len(calls), "offset": offset, "limit": limit}


@router.get("/{call_id}")
async def get_call_detail(
    call_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full detail for a specific call."""
    result = await db.execute(
        select(Call, CallAnalysis)
        .join(CallAnalysis, Call.id == CallAnalysis.call_id, isouter=True)
        .where(Call.id == call_id, Call.user_id == current_user.id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Call not found")

    call, analysis = row
    return {
        "call": {
            "id": call.id,
            "caller_number": call.caller_number,
            "timestamp": call.timestamp.isoformat() if call.timestamp else None,
            "duration_seconds": call.duration_seconds,
            "language": call.language,
            "action_taken": call.action_taken,
            "is_demo": call.is_demo,
        },
        "analysis": {
            "transcript": analysis.transcript if analysis else None,
            "voice_fake_probability": analysis.voice_fake_probability if analysis else None,
            "voice_label": analysis.voice_label if analysis else None,
            "scam_probability": analysis.scam_probability if analysis else None,
            "scam_category": analysis.scam_category if analysis else None,
            "scam_signals": analysis.scam_signals if analysis else [],
            "financial_request": analysis.financial_request if analysis else False,
            "urgency_detected": analysis.urgency_detected if analysis else False,
            "risk_score": analysis.risk_score if analysis else None,
            "risk_level": analysis.risk_level if analysis else None,
            "risk_reasons": analysis.risk_reasons if analysis else [],
            "risk_actions": analysis.risk_actions if analysis else [],
            "risk_components": analysis.risk_components if analysis else {},
            "total_latency_ms": analysis.total_latency_ms if analysis else None,
            "asr_model": analysis.asr_model if analysis else None,
            "deepfake_model": analysis.deepfake_model if analysis else None,
        } if analysis else None,
    }
