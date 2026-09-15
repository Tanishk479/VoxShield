"""
VoxShield — Dashboard API
Aggregated stats, analytics, and insights from real database records.
All numbers come from stored call/analysis data — never hardcoded.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import get_current_user
from db.database import get_db
from db.models import Call, CallAnalysis, User

router = APIRouter()


@router.get("/stats")
async def dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return key stats for the dashboard header cards.
    All values computed from DB records for this user.
    """
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    # Total calls analyzed
    total_calls = await db.scalar(
        select(func.count(Call.id)).where(Call.user_id == current_user.id)
    )

    # Total scam attempts (risk >= CAUTION)
    scam_attempts = await db.scalar(
        select(func.count(CallAnalysis.id))
        .join(Call, CallAnalysis.call_id == Call.id)
        .where(
            Call.user_id == current_user.id,
            CallAnalysis.risk_level.in_(["CAUTION", "HIGH", "CRITICAL"]),
        )
    )

    # High risk calls
    high_risk = await db.scalar(
        select(func.count(CallAnalysis.id))
        .join(Call, CallAnalysis.call_id == Call.id)
        .where(
            Call.user_id == current_user.id,
            CallAnalysis.risk_level.in_(["HIGH", "CRITICAL"]),
        )
    )

    # Calls blocked
    calls_blocked = await db.scalar(
        select(func.count(Call.id)).where(
            Call.user_id == current_user.id,
            Call.action_taken == "BLOCKED",
        )
    )

    # Average risk this week vs last week
    this_week_avg = await db.scalar(
        select(func.avg(CallAnalysis.risk_score))
        .join(Call, CallAnalysis.call_id == Call.id)
        .where(
            Call.user_id == current_user.id,
            Call.timestamp >= week_ago,
        )
    )
    last_week_start = week_ago - timedelta(days=7)
    last_week_avg = await db.scalar(
        select(func.avg(CallAnalysis.risk_score))
        .join(Call, CallAnalysis.call_id == Call.id)
        .where(
            Call.user_id == current_user.id,
            Call.timestamp >= last_week_start,
            Call.timestamp < week_ago,
        )
    )

    risk_trend = None
    if this_week_avg is not None and last_week_avg and last_week_avg > 0:
        change_pct = ((this_week_avg - last_week_avg) / last_week_avg) * 100
        risk_trend = {
            "this_week": round(this_week_avg, 1),
            "last_week": round(last_week_avg, 1),
            "change_percent": round(change_pct, 1),
            "direction": "up" if change_pct > 0 else "down",
        }

    return {
        "calls_analyzed": total_calls or 0,
        "scam_attempts": scam_attempts or 0,
        "high_risk_calls": high_risk or 0,
        "calls_blocked": calls_blocked or 0,
        "risk_trend": risk_trend,
    }


@router.get("/weekly-activity")
async def weekly_activity(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return daily call counts and scam attempt counts for the last N days.
    Used for the weekly chart.
    """
    if days not in (7, 30, 90):
        days = 7

    now = datetime.utcnow()
    start = now - timedelta(days=days)

    result = await db.execute(
        select(Call.timestamp, CallAnalysis.risk_level, CallAnalysis.scam_category)
        .join(CallAnalysis, Call.id == CallAnalysis.call_id, isouter=True)
        .where(Call.user_id == current_user.id, Call.timestamp >= start)
        .order_by(Call.timestamp)
    )
    rows = result.all()

    # Build day buckets
    data = {}
    for i in range(days):
        day = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        data[day] = {"date": day, "total": 0, "scam": 0, "high_risk": 0}

    for ts, risk_level, _ in rows:
        if ts:
            day = ts.strftime("%Y-%m-%d")
            if day in data:
                data[day]["total"] += 1
                if risk_level in ("CAUTION", "HIGH", "CRITICAL"):
                    data[day]["scam"] += 1
                if risk_level in ("HIGH", "CRITICAL"):
                    data[day]["high_risk"] += 1

    return {"days": days, "data": list(data.values())}


@router.get("/scam-categories")
async def scam_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return scam category breakdown for pie/donut chart."""
    result = await db.execute(
        select(CallAnalysis.scam_category, func.count(CallAnalysis.id).label("count"))
        .join(Call, CallAnalysis.call_id == Call.id)
        .where(
            Call.user_id == current_user.id,
            CallAnalysis.scam_category != "UNKNOWN",
            CallAnalysis.scam_probability >= 0.4,
        )
        .group_by(CallAnalysis.scam_category)
        .order_by(desc("count"))
    )
    rows = result.all()

    total = sum(r.count for r in rows)
    categories = [
        {
            "category": r.scam_category,
            "count": r.count,
            "percentage": round((r.count / total * 100), 1) if total > 0 else 0,
        }
        for r in rows
    ]

    return {"categories": categories, "total": total}


@router.get("/language-breakdown")
async def language_breakdown(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return language distribution of analyzed calls."""
    result = await db.execute(
        select(Call.language, func.count(Call.id).label("count"))
        .where(Call.user_id == current_user.id, Call.language.isnot(None))
        .group_by(Call.language)
        .order_by(desc("count"))
    )
    rows = result.all()

    lang_names = {
        "en": "English", "hi": "Hindi", "pa": "Punjabi",
        "ta": "Tamil", "te": "Telugu", "bn": "Bengali",
        "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada",
    }

    total = sum(r.count for r in rows)
    return {
        "languages": [
            {
                "code": r.language,
                "name": lang_names.get(r.language, r.language.upper()),
                "count": r.count,
                "percentage": round(r.count / total * 100, 1) if total > 0 else 0,
            }
            for r in rows
        ],
        "total": total,
    }


@router.get("/time-heatmap")
async def time_heatmap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return call counts by time of day for heatmap visualization."""
    result = await db.execute(
        select(Call.timestamp, CallAnalysis.risk_level)
        .join(CallAnalysis, Call.id == CallAnalysis.call_id, isouter=True)
        .where(
            Call.user_id == current_user.id,
            Call.timestamp.isnot(None),
        )
    )
    rows = result.all()

    # Bucket into 4 time periods
    periods = {"Morning": 0, "Afternoon": 0, "Evening": 0, "Night": 0}
    scam_periods = {"Morning": 0, "Afternoon": 0, "Evening": 0, "Night": 0}

    for ts, risk_level in rows:
        if ts:
            hour = ts.hour
            if 6 <= hour < 12:
                period = "Morning"
            elif 12 <= hour < 17:
                period = "Afternoon"
            elif 17 <= hour < 21:
                period = "Evening"
            else:
                period = "Night"
            periods[period] += 1
            if risk_level in ("CAUTION", "HIGH", "CRITICAL"):
                scam_periods[period] += 1

    return {
        "periods": [
            {"period": k, "total": v, "scam": scam_periods[k]}
            for k, v in periods.items()
        ]
    }


@router.get("/safety-score")
async def safety_score(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Compute VoxShield Safety Score for this user.
    Based on actual interactions — not a hardcoded value.
    """
    total = await db.scalar(
        select(func.count(Call.id)).where(Call.user_id == current_user.id)
    )
    if not total:
        return {"score": None, "factors": [], "message": "No calls analyzed yet"}

    blocked = await db.scalar(
        select(func.count(Call.id)).where(
            Call.user_id == current_user.id, Call.action_taken == "BLOCKED"
        )
    )
    critical_continued = await db.scalar(
        select(func.count(Call.id))
        .join(CallAnalysis, Call.id == CallAnalysis.call_id)
        .where(
            Call.user_id == current_user.id,
            CallAnalysis.risk_level == "CRITICAL",
            Call.action_taken == "CONTINUED",
        )
    )
    verified = await db.scalar(
        select(func.count(Call.id)).where(
            Call.user_id == current_user.id, Call.action_taken == "VERIFIED"
        )
    )

    # Score formula (0–100)
    score = 70  # base
    if total > 0:
        block_rate = (blocked or 0) / total
        score += int(block_rate * 15)
    if verified:
        score += min(10, verified * 2)
    if critical_continued:
        score -= min(20, (critical_continued or 0) * 5)
    score = max(0, min(100, score))

    factors = []
    if blocked:
        factors.append(f"Blocked {blocked} suspicious caller{'s' if blocked > 1 else ''}")
    if verified:
        factors.append(f"Verified {verified} caller{'s' if verified > 1 else ''} before proceeding")
    if not critical_continued:
        factors.append("No critical-risk calls continued unverified")

    return {
        "score": score,
        "factors": factors,
        "total_calls": total,
    }
