import sys
import os
import random
import asyncio
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import async_sessionmaker, engine
import db.models as models

User = getattr(models, "User", None)
Call = getattr(models, "Call", None)
TrustedContact = getattr(models, "TrustedContact", None)

try:
    from utils.auth import get_password_hash
except ImportError:
    try:
        from api.auth import get_password_hash
    except ImportError:
        import hashlib
        def get_password_hash(password: str) -> str:
            return hashlib.sha256(password.encode()).hexdigest()

from sqlalchemy import select

async def seed_rich_demo_account():
    DEMO_EMAIL = "demo@voxshield.in"
    DEMO_PASSWORD = "VoxShieldDemo2026!"

    if not User or not Call:
        print("[!] Critical: User or Call model missing in db.models.")
        return

    print(f"[*] Connecting session to populate demo operator: {DEMO_EMAIL}")

    # expire_on_commit=False prevents MissingGreenlet on async reloads
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as db:
        # 1. Fetch or Create Demo User
        stmt = select(User).where(User.email == DEMO_EMAIL)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            user = User(
                email=DEMO_EMAIL,
                hashed_password=get_password_hash(DEMO_PASSWORD),
                full_name="Tanishk",
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"[+] Created user: {DEMO_EMAIL} (ID: {user.id})")
        else:
            print(f"[i] Using existing user: {DEMO_EMAIL} (ID: {user.id})")

        # Capture user_id directly into a plain variable
        saved_user_id = user.id

        # 2. Seed Trusted Contacts if the model exists
        if TrustedContact:
            trusted_seeds = [
                {"name": "Papa", "phone": "+91 98140 12345", "relationship": "father"},
                {"name": "Mummy", "phone": "+91 98140 54321", "relationship": "mother"},
                {"name": "HDFC Fraud Desk", "phone": "+91 1800 202 6161", "relationship": "bank"},
                {"name": "Sister", "phone": "+91 98765 43210", "relationship": "sister"},
            ]
            for tc in trusted_seeds:
                try:
                    contact = TrustedContact(
                        user_id=saved_user_id,
                        name=tc["name"],
                        phone_number=tc["phone"],
                        relationship=tc["relationship"]
                    )
                    db.add(contact)
                except Exception:
                    pass
            await db.commit()
            print("[+] Seeded trusted contacts.")

        # 3. Call telemetry templates
        scam_templates = [
            {
                "num": "+91 98765 01234",
                "caller_name": "CBI Cyber Cell Impersonator",
                "category": "digital_arrest",
                "risk_level": "CRITICAL",
                "score": 96,
                "lang": "hi",
                "transcript": "Aapka naam illegal narcotics parcel mein aaya hai. Supreme court ke orders par aap digital arrest mein hain. Turant security deposit bhejiye.",
                "fake_prob": 0.32,
                "scam_prob": 0.98,
                "action": "BLOCKED"
            },
            {
                "num": "+91 82345 67890",
                "caller_name": "Unknown Suspect",
                "category": "ai_voice",
                "risk_level": "CRITICAL",
                "score": 94,
                "lang": "hi",
                "transcript": "Beta main hospital mein hoon, accident ho gaya hai. Doctor ko 50,000 turant UPI kar do, jaldi karo phone kat raha hai.",
                "fake_prob": 0.95,
                "scam_prob": 0.92,
                "action": "BLOCKED"
            },
            {
                "num": "+91 94567 89012",
                "caller_name": "Electricity KYC Extortion",
                "category": "kyc",
                "risk_level": "HIGH",
                "score": 82,
                "lang": "en",
                "transcript": "Dear customer, your electricity bill is unpaid and power will be disconnected tonight. Call verification officer immediately.",
                "fake_prob": 0.12,
                "scam_prob": 0.88,
                "action": "BLOCKED"
            },
            {
                "num": "+91 91234 56789",
                "caller_name": "Courier Customs Trap",
                "category": "courier",
                "risk_level": "HIGH",
                "score": 79,
                "lang": "hi",
                "transcript": "FedEx Mumbai hub se baat kar rahe hain. Aapka parcel custom ne intercept kiya hai jisme illegal items hain.",
                "fake_prob": 0.20,
                "scam_prob": 0.82,
                "action": "BLOCKED"
            },
            {
                "num": "+91 99999 11111",
                "caller_name": "UPI Refund Scam",
                "category": "upi",
                "risk_level": "CAUTION",
                "score": 62,
                "lang": "en",
                "transcript": "I am sending a collect request of 20,000 on your PhonePe for refund approval. Please enter your UPI PIN to receive money.",
                "fake_prob": 0.05,
                "scam_prob": 0.69,
                "action": "ANALYZED"
            },
            {
                "num": "+91 98140 12345",
                "caller_name": "Papa",
                "category": "safe",
                "risk_level": "LOW",
                "score": 12,
                "lang": "pa",
                "transcript": "Haan beta, train vich baith gaye si? Ghar aake phone kari.",
                "fake_prob": 0.03,
                "scam_prob": 0.04,
                "action": "VERIFIED"
            },
            {
                "num": "+91 98140 54321",
                "caller_name": "Mummy",
                "category": "safe",
                "risk_level": "LOW",
                "score": 8,
                "lang": "hi",
                "transcript": "Beta lunch kar liya tune? Sham ko time se room par aa jana.",
                "fake_prob": 0.02,
                "scam_prob": 0.02,
                "action": "VERIFIED"
            },
        ]

        now = datetime.now(timezone.utc)
        call_columns = {col.name for col in Call.__table__.columns}

        # 4. Generate 32 Intercepted Threat Streams
        for _ in range(32):
            template = random.choice(scam_templates)
            call_time = now - timedelta(
                days=random.randint(0, 28),
                hours=random.randint(1, 23),
                minutes=random.randint(0, 59)
            )

            call_kwargs = {}
            if "user_id" in call_columns:
                call_kwargs["user_id"] = saved_user_id
            if "caller_number" in call_columns:
                call_kwargs["caller_number"] = template["num"]
            if "caller_name" in call_columns:
                call_kwargs["caller_name"] = template.get("caller_name")
            if "duration_seconds" in call_columns:
                call_kwargs["duration_seconds"] = random.randint(14, 210)
            if "language" in call_columns:
                call_kwargs["language"] = template["lang"]
            if "final_risk_score" in call_columns:
                call_kwargs["final_risk_score"] = template["score"] + random.randint(-4, 3)
            if "risk_level" in call_columns:
                call_kwargs["risk_level"] = template["risk_level"]
            if "scam_category" in call_columns:
                call_kwargs["scam_category"] = template["category"]
            if "action_taken" in call_columns:
                call_kwargs["action_taken"] = template["action"]
            if "transcript" in call_columns:
                call_kwargs["transcript"] = template["transcript"]
            if "deepfake_probability" in call_columns:
                call_kwargs["deepfake_probability"] = template["fake_prob"]
            if "scam_probability" in call_columns:
                call_kwargs["scam_probability"] = template["scam_prob"]
            if "timestamp" in call_columns:
                call_kwargs["timestamp"] = call_time
            if "created_at" in call_columns:
                call_kwargs["created_at"] = call_time
            if "is_demo" in call_columns:
                call_kwargs["is_demo"] = True

            try:
                db.add(Call(**call_kwargs))
            except Exception:
                pass

        await db.commit()
        print("[✓] Successfully seeded 32 rich telemetry calls!")

if __name__ == "__main__":
    asyncio.run(seed_rich_demo_account())