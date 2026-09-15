"""
VoxShield — Demo Data Seeder
Generates clearly labeled synthetic call history for dashboard demonstration.

IMPORTANT:
  - All seeded records have is_demo=True
  - The frontend must display a "DEMO DATA" badge when is_demo records are shown
  - These records represent plausible scenarios, NOT real user activity
  - Never represent this as real-world statistics

Run: python -m db.seed_demo
"""

import asyncio
import json
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add backend dir to path if running standalone
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import AsyncSessionLocal, init_db
from db.models import Call, CallAnalysis, CallerProfile, User, UserSettings
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEMO_USER = {
    "email": "demo@voxshield.in",
    "full_name": "Tanishq (Demo)",
    "phone": "+919876543210",
    "password": "VoxShieldDemo2026!",
}

# Sample scam scenarios for demo
DEMO_SCENARIOS = [
    {
        "caller": "+918800000001",
        "language": "hi",
        "duration": 134,
        "voice_fake": 0.84,
        "scam_prob": 0.91,
        "category": "FAMILY_IMPERSONATION",
        "risk": 92,
        "level": "CRITICAL",
        "signals": ["AI voice suspected", "urgent money request", "identity impersonation"],
        "transcript": "Beta main hospital mein hoon, jaldi se 20000 rupaye bhej de...",
        "action": "BLOCKED",
    },
    {
        "caller": "+918800000002",
        "language": "en",
        "duration": 87,
        "voice_fake": 0.72,
        "scam_prob": 0.88,
        "category": "OTP",
        "risk": 85,
        "level": "CRITICAL",
        "signals": ["OTP request", "bank impersonation", "urgency"],
        "transcript": "This is your bank security team. Please share the OTP received on your phone.",
        "action": "BLOCKED",
    },
    {
        "caller": "+918800000003",
        "language": "hi",
        "duration": 210,
        "voice_fake": 0.61,
        "scam_prob": 0.79,
        "category": "DIGITAL_ARREST",
        "risk": 78,
        "level": "HIGH",
        "signals": ["digital arrest threat", "police impersonation", "financial demand"],
        "transcript": "Main CBI officer bol raha hoon. Aapke khilaf arrest warrant hai...",
        "action": "ENDED",
    },
    {
        "caller": "+918800000004",
        "language": "en",
        "duration": 45,
        "voice_fake": 0.12,
        "scam_prob": 0.82,
        "category": "UPI",
        "risk": 68,
        "level": "HIGH",
        "signals": ["UPI request", "financial request", "urgency"],
        "transcript": "Sir your UPI is blocked. Please verify by sending Re 1 to this number.",
        "action": "BLOCKED",
    },
    {
        "caller": "+918800000005",
        "language": "hi",
        "duration": 55,
        "voice_fake": 0.09,
        "scam_prob": 0.35,
        "category": "KYC",
        "risk": 44,
        "level": "CAUTION",
        "signals": ["KYC claim"],
        "transcript": "Aapka KYC update karna hai warna account band ho jayega.",
        "action": "CONTINUED",
    },
    {
        "caller": "+918800000006",
        "language": "en",
        "duration": 182,
        "voice_fake": 0.05,
        "scam_prob": 0.08,
        "category": "UNKNOWN",
        "risk": 12,
        "level": "LOW",
        "signals": [],
        "transcript": "Hi, calling about the product you ordered last week.",
        "action": "CONTINUED",
    },
    {
        "caller": "+918800000007",
        "language": "hi",
        "duration": 91,
        "voice_fake": 0.78,
        "scam_prob": 0.85,
        "category": "BANKING",
        "risk": 88,
        "level": "CRITICAL",
        "signals": ["AI voice", "account suspension threat", "urgency"],
        "transcript": "Aapka bank account suspicious activity ki wajah se block hone wala hai...",
        "action": "BLOCKED",
    },
    {
        "caller": "+918800000008",
        "language": "en",
        "duration": 67,
        "voice_fake": 0.55,
        "scam_prob": 0.71,
        "category": "INVESTMENT",
        "risk": 65,
        "level": "HIGH",
        "signals": ["guaranteed returns", "investment scam"],
        "transcript": "We guarantee 40% monthly returns on our crypto trading platform.",
        "action": "ENDED",
    },
    {
        "caller": "+918800000009",
        "language": "hi",
        "duration": 128,
        "voice_fake": 0.21,
        "scam_prob": 0.67,
        "category": "COURIER",
        "risk": 57,
        "level": "CAUTION",
        "signals": ["parcel stopped", "customs claim"],
        "transcript": "Aapka parcel customs mein roka gaya hai. Illegal items mile hain.",
        "action": "VERIFIED",
    },
    {
        "caller": "+918800000010",
        "language": "en",
        "duration": 38,
        "voice_fake": 0.03,
        "scam_prob": 0.04,
        "category": "UNKNOWN",
        "risk": 8,
        "level": "LOW",
        "signals": [],
        "transcript": "Hello, this is a reminder about your appointment tomorrow at 3 PM.",
        "action": "CONTINUED",
    },
]

EXTRA_CALLERS = [
    "+919900000011", "+919900000012", "+919900000013",
    "+919900000014", "+919900000015", "+919900000016",
    "+919900000017", "+919900000018", "+919900000019",
    "+919900000020",
]


def _days_ago(n: int, hour_offset: int = 0) -> datetime:
    return datetime.now() - timedelta(days=n, hours=hour_offset)


async def seed():
    print("[*] Initializing database...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # Check if demo user already exists
        from sqlalchemy import select
        existing = await session.execute(
            select(User).where(User.email == DEMO_USER["email"])
        )
        user = existing.scalar_one_or_none()

        if user:
            print(f"[OK] Demo user already exists: {user.email}")
        else:
            print("[*] Creating demo user...")
            user = User(
                id=str(uuid.uuid4()),
                email=DEMO_USER["email"],
                full_name=DEMO_USER["full_name"],
                phone=DEMO_USER["phone"],
                hashed_password=pwd_ctx.hash(DEMO_USER["password"]),
            )
            session.add(user)
            settings = UserSettings(
                id=str(uuid.uuid4()),
                user_id=user.id,
            )
            session.add(settings)
            await session.flush()
            print(f"  [OK] User created: {user.email}")

        # Create 30 demo calls spread over last 30 days
        print("📞 Seeding demo call history...")
        call_count = 0

        for day_offset in range(30):
            # 0–3 calls per day
            n_calls = random.choices([0, 1, 2, 3], weights=[0.3, 0.35, 0.25, 0.10])[0]
            for _ in range(n_calls):
                scenario = random.choice(DEMO_SCENARIOS)
                # Add variance to scores
                fake_var = random.uniform(-0.08, 0.08)
                scam_var = random.uniform(-0.06, 0.06)

                call_id = str(uuid.uuid4())
                call = Call(
                    id=call_id,
                    user_id=user.id,
                    caller_number=scenario["caller"],
                    timestamp=_days_ago(day_offset, random.randint(0, 23)),
                    duration_seconds=scenario["duration"] + random.randint(-20, 40),
                    language=scenario["language"],
                    action_taken=scenario["action"],
                    is_demo=True,  # ← All demo records flagged
                )
                session.add(call)

                fake_prob = max(0.0, min(1.0, scenario["voice_fake"] + fake_var))
                scam_prob = max(0.0, min(1.0, scenario["scam_prob"] + scam_var))

                analysis = CallAnalysis(
                    id=str(uuid.uuid4()),
                    call_id=call_id,
                    transcript=scenario["transcript"],
                    asr_model="openai/whisper-tiny",
                    voice_fake_probability=fake_prob,
                    voice_real_probability=1.0 - fake_prob,
                    voice_label="spoof" if fake_prob > 0.6 else "uncertain" if fake_prob > 0.4 else "real",
                    deepfake_model="lab260/Spectra-0",
                    scam_probability=scam_prob,
                    scam_category=scenario["category"],
                    scam_severity="CRITICAL" if scenario["risk"] >= 88 else "HIGH" if scenario["risk"] >= 65 else "MEDIUM",
                    scam_signals=scenario["signals"],
                    financial_request="financial request" in scenario["signals"] or "money" in scenario["transcript"].lower(),
                    urgency_detected="urgency" in scenario["signals"],
                    identity_claim="impersonation" in " ".join(scenario["signals"]).lower(),
                    risk_score=min(100, scenario["risk"] + random.randint(-5, 5)),
                    risk_level=scenario["level"],
                    risk_reasons=[f"🔴 {s}" for s in scenario["signals"][:3]],
                    risk_actions=["Verify caller through another channel"],
                )
                session.add(analysis)
                call_count += 1

        await session.commit()
        print(f"  ✅ Seeded {call_count} demo calls")

        # Seed caller profiles
        print("👥 Seeding caller profiles...")
        for scenario in DEMO_SCENARIOS[:7]:
            cp = CallerProfile(
                id=str(uuid.uuid4()),
                phone_number=scenario["caller"],
                total_calls=random.randint(2, 8),
                total_alerts=random.randint(1, 5),
                average_risk_score=scenario["risk"] * 0.9,
                most_common_category=scenario["category"],
                is_blocked=scenario["action"] == "BLOCKED",
            )
            session.add(cp)

        await session.commit()

    print("\n✅ Demo data seeded successfully!")
    print(f"   Login: {DEMO_USER['email']}")
    print(f"   Password: {DEMO_USER['password']}")
    print("   ⚠  All records flagged is_demo=True — displayed with DEMO badge in UI")


if __name__ == "__main__":
    asyncio.run(seed())
