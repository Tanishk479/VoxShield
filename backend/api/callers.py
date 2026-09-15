"""
VoxShield — Caller Intelligence API
Per-number risk profiles aggregated from call history.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import get_current_user
from db.database import get_db
from db.models import Call, CallAnalysis, CallerProfile, TrustedContact, User

router = APIRouter()


@router.get("/")
async def list_callers(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return caller profiles for numbers that have called this user."""
    result = await db.execute(
        select(
            Call.caller_number,
            func.count(Call.id).label("total_calls"),
            func.max(Call.timestamp).label("last_seen"),
            func.avg(CallAnalysis.risk_score).label("avg_risk"),
            func.sum(
                (CallAnalysis.risk_level.in_(["HIGH", "CRITICAL"])).cast(int)
            ).label("alert_count"),
        )
        .join(CallAnalysis, Call.id == CallAnalysis.call_id, isouter=True)
        .where(Call.user_id == current_user.id, Call.caller_number.isnot(None))
        .group_by(Call.caller_number)
        .order_by(desc("avg_risk"))
        .limit(limit)
    )
    rows = result.all()

    # Check trusted contacts
    trusted_result = await db.execute(
        select(TrustedContact.phone_number).where(TrustedContact.user_id == current_user.id)
    )
    trusted_numbers = {r[0] for r in trusted_result.all()}

    callers = []
    for row in rows:
        callers.append({
            "caller_number": row.caller_number,
            "total_calls": row.total_calls,
            "last_seen": row.last_seen.isoformat() if row.last_seen else None,
            "avg_risk_score": round(row.avg_risk or 0, 1),
            "alert_count": int(row.alert_count or 0),
            "is_trusted": row.caller_number in trusted_numbers,
            "risk_status": (
                "TRUSTED" if row.caller_number in trusted_numbers
                else "HIGH_RISK" if (row.avg_risk or 0) >= 70
                else "CAUTION" if (row.avg_risk or 0) >= 45
                else "NORMAL"
            ),
        })

    return {"callers": callers}


@router.get("/{phone_number}")
async def caller_detail(
    phone_number: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full profile for a specific caller number."""
    calls_result = await db.execute(
        select(Call, CallAnalysis)
        .join(CallAnalysis, Call.id == CallAnalysis.call_id, isouter=True)
        .where(Call.user_id == current_user.id, Call.caller_number == phone_number)
        .order_by(desc(Call.timestamp))
        .limit(10)
    )
    rows = calls_result.all()

    if not rows:
        raise HTTPException(status_code=404, detail="No calls found for this number")

    risk_scores = [a.risk_score for _, a in rows if a and a.risk_score is not None]
    categories = [a.scam_category for _, a in rows if a and a.scam_category and a.scam_category != "UNKNOWN"]

    most_common_category = None
    if categories:
        most_common_category = max(set(categories), key=categories.count)

    return {
        "phone_number": phone_number,
        "total_calls": len(rows),
        "alert_count": sum(1 for _, a in rows if a and a.risk_level in ("HIGH", "CRITICAL")),
        "avg_risk_score": round(sum(risk_scores) / len(risk_scores), 1) if risk_scores else None,
        "most_common_category": most_common_category,
        "calls": [
            {
                "id": c.id,
                "timestamp": c.timestamp.isoformat() if c.timestamp else None,
                "duration_seconds": c.duration_seconds,
                "language": c.language,
                "action_taken": c.action_taken,
                "risk_score": a.risk_score if a else None,
                "risk_level": a.risk_level if a else None,
                "scam_category": a.scam_category if a else None,
            }
            for c, a in rows
        ],
    }
