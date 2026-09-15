"""
VoxShield — Scam Classifier
Hybrid rule-based scam intelligence engine.

Features:
- English / Hindi / Hinglish support
- Taxonomy-based category matching
- Weighted contextual signals
- Combination / social-engineering detection
- Family / friend impersonation detection
- Police / authority / digital-arrest detection
- Financial + urgency + secrecy correlation
- Explainable scoring
- Backward-compatible response fields

IMPORTANT:
This is a rule-based intelligence layer. It does not claim
machine-learning accuracy or training on Indian scam calls.
"""

import json
import logging
import re
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

TAXONOMY_PATH = Path(__file__).parent / "scam_taxonomy.json"


class ScamClassifier:
    """
    Explainable scam-intelligence classifier.

    The classifier does NOT treat one keyword as proof of a scam.

    Instead it combines multiple signals:

        identity + urgency + financial request + secrecy
                         ↓
                    higher risk

    This is particularly useful for:
        - Family impersonation
        - UPI/payment scams
        - Police impersonation
        - Digital arrest scams
        - KYC scams
        - OTP scams
        - Courier scams
        - Banking scams
    """

    def __init__(self, taxonomy_path: Path = TAXONOMY_PATH):
        self._taxonomy = self._load_taxonomy(taxonomy_path)
        self._categories = {
            c["id"]: c for c in self._taxonomy["categories"]
        }

        # ---------------------------------------------------------
        # Urgency / pressure
        # ---------------------------------------------------------
        self._urgency_patterns = [
            r"\babhi\b",
            r"\babhi\s+(?:bhejo|karo|do|chahiye)\b",
            r"\bturant\b",
            r"\bjaldi\b",
            r"\bfauran\b",
            r"\burgent(?:ly)?\b",
            r"\bimmediately\b",
            r"\bright\s+now\b",
            r"\bright\s+away\b",
            r"\bhurry\b",
            r"\bhurry\s+up\b",
            r"\bno\s+time\b",
            r"\bvery\s+urgent\b",
            r"\bemergency\b",
            r"\bemergency\s+hai\b",
            r"\blast\s+chance\b",
            r"\btoday\s+only\b",
            r"\bdeadline\b",
            r"\bwithin\s+\d+\s*(?:minutes?|hours?)\b",
            r"\bjaldi\s+se\b",
            r"\babhi\s+ke\s+abhi\b",
        ]

        # ---------------------------------------------------------
        # Financial / payment
        # ---------------------------------------------------------
        self._financial_patterns = [
            r"\bpaise\b",
            r"\bpaise\s+(?:bhej|chahiye|do)\b",
            r"\bpaisa\b",
            r"\brup(?:a|i)ye?\b",
            r"\brupees?\b",
            r"₹",
            r"\b\d+\s*(?:rupees?|rs|₹)\b",
            r"\bupi\b",
            r"\bupi\s+(?:kar|bhej|se|payment)\b",
            r"\bpaytm\b",
            r"\bphonepe\b",
            r"\bgoogle\s+pay\b",
            r"\bgpay\b",
            r"\btransfer\b",
            r"\btransfer\s+(?:money|paise)\b",
            r"\bsend\s+money\b",
            r"\bsend\s+(?:me\s+)?(?:money|paise)\b",
            r"\bbhej(?:o|na)?\b",
            r"\bpayment\b",
            r"\bpay\b",
            r"\bamount\b",
            r"\bmoney\b",
            r"\bfund\b",
            r"\bcash\b",
            r"\bimps\b",
            r"\bneft\b",
            r"\baccount\s+mein\s+(?:dal|bhej)\b",
            r"\baccount\s+mein\s+transfer\b",
        ]

        # ---------------------------------------------------------
        # Identity / authority claims
        # ---------------------------------------------------------
        self._identity_patterns = [
            r"\bmain\s+.*\s*hoon\b",
            r"\bi\s+am\b",
            r"\bi'm\b",
            r"\bim\b",
            r"\bspeaking\b",
            r"\bcalling\s+from\b",
            r"\bcall(?:ing)?\s+from\b",
            r"\bofficial\b",
            r"\bofficer\b",
            r"\binspector\b",
            r"\bcommissioner\b",
            r"\bdepartment\s+se\b",
            r"\bdepartment\s+from\b",
            r"\bgovernment\s+officer\b",
            r"\bpolice\s+officer\b",
            r"\bbank\s+se\s+bol\b",
            r"\bbank\s+se\s+bol\s+raha\b",
            r"\bbeta\b",
            r"\bpapa\b",
            r"\bmummy\b",
            r"\bmom\b",
            r"\bdad\b",
            r"\bdaddy\b",
            r"\bbhai\b",
            r"\bbehen\b",
            r"\bsister\b",
            r"\bbrother\b",
            r"\bcousin\b",
            r"\bdidi\b",
            r"\bbhabhi\b",
        ]

        # ---------------------------------------------------------
        # Family relationship indicators
        # ---------------------------------------------------------
        self._family_patterns = [
            r"\bbhai\b",
            r"\bbrother\b",
            r"\bbehen\b",
            r"\bsister\b",
            r"\bcousin\b",
            r"\bbeta\b",
            r"\bbeti\b",
            r"\bpapa\b",
            r"\bpapaji\b",
            r"\bdad\b",
            r"\bdaddy\b",
            r"\bmummy\b",
            r"\bmom\b",
            r"\bmama\b",
            r"\bchacha\b",
            r"\bchachi\b",
            r"\buncle\b",
            r"\baunty\b",
            r"\bdidi\b",
            r"\bbhabhi\b",
        ]

        # ---------------------------------------------------------
        # Emergency / distress story
        # ---------------------------------------------------------
        self._emergency_patterns = [
            r"\bhospital\b",
            r"\baccident\b",
            r"\baccident\s+ho\s+gaya\b",
            r"\bmushkil\s+mein\s+hoon\b",
            r"\bproblem\s+mein\s+hoon\b",
            r"\bphas\s+gaya\b",
            r"\bphas\s+gayi\b",
            r"\btrouble\s+mein\s+hoon\b",
            r"\bjail\s+mein\s+hoon\b",
            r"\bemergency\b",
            r"\bmedical\s+emergency\b",
            r"\bphone\s+(?:kharab|damage|toot)\b",
            r"\bphone\s+kho\s+gaya\b",
            r"\bphone\s+lost\b",
            r"\bnew\s+number\s+se\b",
            r"\bnew\s+number\b",
        ]

        # ---------------------------------------------------------
        # Secrecy / isolation manipulation
        # ---------------------------------------------------------
        self._secrecy_patterns = [
            r"\bkisi\s+ko\s+mat\s+batana\b",
            r"\bkisi\s+se\s+mat\s+batana\b",
            r"\bmat\s+batana\b",
            r"\bghar\s+pe\s+mat\s+batana\b",
            r"\bmummy\s+papa\s+ko\s+mat\s+batana\b",
            r"\bmom\s+dad\s+ko\s+mat\s+batana\b",
            r"\bdon't\s+tell\s+anyone\b",
            r"\bdont\s+tell\s+anyone\b",
            r"\bdon't\s+tell\s+my\s+parents\b",
            r"\bdont\s+tell\s+my\s+parents\b",
            r"\bkeep\s+this\s+secret\b",
            r"\bsecret\s+rakhna\b",
            r"\bkisi\s+ko\s+mat\s+bolna\b",
            r"\bparents\s+ko\s+mat\s+batana\b",
        ]

        # ---------------------------------------------------------
        # Police / government authority
        # ---------------------------------------------------------
        self._authority_patterns = [
            r"\bpolice\b",
            r"\bpolice\s+officer\b",
            r"\binspector\b",
            r"\bcommissioner\b",
            r"\bcbi\b",
            r"\bed\s+department\b",
            r"\bincome\s+tax\b",
            r"\bgovernment\s+officer\b",
            r"\bgovernment\s+department\b",
            r"\bcyber\s*crime\b",
            r"\bcyber\s*crime\s+department\b",
            r"\bcyber\s+cell\b",
            r"\bthana\s+se\b",
            r"\bpolice\s+station\s+se\b",
            r"\bauthorit(?:y|ies)\b",
            r"\bcustoms\s+officer\b",
        ]

        # ---------------------------------------------------------
        # Threat / intimidation
        # ---------------------------------------------------------
        self._threat_patterns = [
            r"\blegal\s+action\b",
            r"\blegal\s+action\s+liya\s+jayega\b",
            r"\barrest\b",
            r"\barrest\s+kar\b",
            r"\barrest\s+kar\s+liya\b",
            r"\barrest\s+warrant\b",
            r"\bwarrant\b",
            r"\bjail\b",
            r"\bcase\s+hai\b",
            r"\bcase\s+filed\b",
            r"\bfir\b",
            r"\bfir\s+filed\b",
            r"\binvestigation\b",
            r"\bunder\s+investigation\b",
            r"\byou\s+will\s+be\s+arrested\b",
            r"\baction\s+will\s+be\s+taken\b",
            r"\baccount\s+will\s+be\s+blocked\b",
            r"\baccount\s+blocked\b",
            r"\bnumber\s+blocked\b",
            r"\bsim\s+blocked\b",
        ]

        # ---------------------------------------------------------
        # Verification / sensitive information
        # ---------------------------------------------------------
        self._verification_patterns = [
            r"\bverification\b",
            r"\bverify\b",
            r"\bverify\s+your\b",
            r"\bverification\s+ke\s+liye\b",
            r"\bverify\s+karna\b",
            r"\bverify\s+karo\b",
            r"\bkyc\b",
            r"\baadhaar\b",
            r"\baadhaar\s+verification\b",
            r"\bpan\b",
            r"\bpan\s+card\b",
            r"\bdate\s+of\s+birth\b",
            r"\bdob\b",
            r"\bidentity\s+verification\b",
            r"\bdocuments?\s+verify\b",
        ]

        # ---------------------------------------------------------
        # OTP / credential requests
        # ---------------------------------------------------------
        self._credential_patterns = [
            r"\botp\b",
            r"\bone\s+time\s+password\b",
            r"\bverification\s+code\b",
            r"\btell\s+me\s+the\s+code\b",
            r"\bcode\s+batao\b",
            r"\botp\s+batao\b",
            r"\botp\s+share\b",
            r"\bshare\s+your\s+otp\b",
            r"\bshare\s+the\s+otp\b",
            r"\bupi\s+pin\b",
            r"\bpin\s+batao\b",
            r"\bpassword\b",
            r"\bnet\s+banking\s+password\b",
        ]

        # ---------------------------------------------------------
        # Independent channel / caller verification
        # ---------------------------------------------------------
        self._caller_verification_patterns = [
            r"\bverify\s+caller\b",
            r"\bverify\s+identity\b",
            r"\bknown\s+number\b",
            r"\bsaved\s+number\b",
            r"\bcall\s+back\b",
            r"\bcall\s+me\s+back\b",
            r"\bknown\s+contact\b",
        ]

        logger.info(
            "ScamClassifier initialized with %d categories",
            len(self._categories),
        )

    # =============================================================
    # Helpers
    # =============================================================

    def _load_taxonomy(self, path: Path) -> dict:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize ASR text while preserving Hindi/Hinglish words.

        Examples:
            "  UPI   KAR DE!!! "
            -> "upi kar de"

        Also handles common ASR punctuation noise.
        """
        text = text.lower()

        # Normalize common currency / punctuation spacing
        text = text.replace("₹", " ₹ ")

        # Keep Unicode letters/numbers and basic punctuation
        text = re.sub(r"[^\w\s₹']", " ", text, flags=re.UNICODE)

        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    @staticmethod
    def _match_patterns(
        text: str,
        patterns: list[str],
    ) -> list[str]:
        """Return matched regex patterns without duplicates."""
        matches = []

        for pattern in patterns:
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append(pattern)
            except re.error:
                logger.warning("Invalid regex pattern: %s", pattern)

        return matches

    @staticmethod
    def _probability_to_severity(probability: float) -> str:
        """
        Convert scam probability to an explainable severity.

        0.00–0.29  SAFE
        0.30–0.59  SUSPICIOUS
        0.60–0.79  HIGH
        0.80–1.00  CRITICAL
        """
        if probability >= 0.80:
            return "CRITICAL"
        if probability >= 0.60:
            return "HIGH"
        if probability >= 0.30:
            return "SUSPICIOUS"
        return "SAFE"

    # =============================================================
    # Main classifier
    # =============================================================

    def classify(self, transcript: str) -> dict:
        """
        Analyze transcript for scam intent.

        Returns:
            {
                scam_probability,
                category,
                category_name,
                severity,
                signals,
                urgency_detected,
                financial_request,
                identity_claim,
                matched_indicators,
                recommended_action,
                explanation,
                risk_factors,
                latency_ms
            }
        """

        start = time.perf_counter()

        if not transcript or not transcript.strip():
            return {
                "scam_probability": 0.0,
                "category": "UNKNOWN",
                "category_name": "No transcript",
                "severity": "SAFE",
                "signals": [],
                "urgency_detected": False,
                "financial_request": False,
                "identity_claim": False,
                "matched_indicators": [],
                "recommended_action": (
                    "Unable to analyze — no transcript available."
                ),
                "explanation": "No speech transcript was available.",
                "risk_factors": [],
                "latency_ms": 0.0,
            }

        text = self._normalize_text(transcript)

        # =========================================================
        # STEP 1 — Taxonomy category matching
        # =========================================================

        category_scores: dict[str, float] = {}
        category_matches: dict[str, list[str]] = {}

        severity_weight = {
            "CRITICAL": 1.30,
            "HIGH": 1.10,
            "MEDIUM": 0.90,
            "LOW": 0.70,
        }

        for cat_id, cat in self._categories.items():

            if cat_id == "UNKNOWN":
                continue

            matched = []

            for indicator in cat.get("indicators", []):
                indicator_lower = indicator.lower().strip()

                if not indicator_lower:
                    continue

                if indicator_lower in text:
                    matched.append(indicator)

            if matched:
                weight = severity_weight.get(
                    cat.get("severity", "MEDIUM"),
                    1.0,
                )

                indicator_count = len(cat.get("indicators", []))

                raw_score = (
                    len(matched)
                    / max(1, indicator_count)
                ) * 3.0 * weight

                category_scores[cat_id] = min(
                    1.0,
                    raw_score,
                )

                category_matches[cat_id] = matched

        # =========================================================
        # STEP 2 — Cross-cutting intelligence signals
        # =========================================================

        urgency_matches = self._match_patterns(
            text,
            self._urgency_patterns,
        )

        financial_matches = self._match_patterns(
            text,
            self._financial_patterns,
        )

        identity_matches = self._match_patterns(
            text,
            self._identity_patterns,
        )

        family_matches = self._match_patterns(
            text,
            self._family_patterns,
        )

        emergency_matches = self._match_patterns(
            text,
            self._emergency_patterns,
        )

        secrecy_matches = self._match_patterns(
            text,
            self._secrecy_patterns,
        )

        authority_matches = self._match_patterns(
            text,
            self._authority_patterns,
        )

        threat_matches = self._match_patterns(
            text,
            self._threat_patterns,
        )

        verification_matches = self._match_patterns(
            text,
            self._verification_patterns,
        )

        credential_matches = self._match_patterns(
            text,
            self._credential_patterns,
        )

        # =========================================================
        # STEP 3 — Boolean signals
        # =========================================================

        urgency_detected = bool(urgency_matches)
        financial_request = bool(financial_matches)
        identity_claim = bool(identity_matches)

        family_detected = bool(family_matches)
        emergency_detected = bool(emergency_matches)
        secrecy_detected = bool(secrecy_matches)
        authority_detected = bool(authority_matches)
        threat_detected = bool(threat_matches)
        verification_detected = bool(verification_matches)
        credential_request_detected = bool(credential_matches)

        # =========================================================
        # STEP 4 — Base category
        # =========================================================

        if category_scores:

            best_cat_id = max(
                category_scores,
                key=category_scores.get,
            )

            base_score = category_scores[best_cat_id]

            matched_indicators = category_matches[
                best_cat_id
            ]

        else:

            best_cat_id = "UNKNOWN"
            base_score = 0.0
            matched_indicators = []

        # =========================================================
        # STEP 5 — Contextual scoring
        # =========================================================

        score = base_score

        risk_factors: list[str] = []

        # Individual signals
        if urgency_detected:
            score += 0.08
            risk_factors.append(
                "Urgent or pressure-based language"
            )

        if financial_request:
            score += 0.12
            risk_factors.append(
                "Financial/payment request"
            )

        if identity_claim:
            score += 0.04
            risk_factors.append(
                "Caller identity claim detected"
            )

        if emergency_detected:
            score += 0.06
            risk_factors.append(
                "Emergency/distress scenario detected"
            )

        if secrecy_detected:
            score += 0.10
            risk_factors.append(
                "Secrecy/isolation manipulation detected"
            )

        if authority_detected:
            score += 0.12
            risk_factors.append(
                "Government/police authority claim detected"
            )

        if threat_detected:
            score += 0.12
            risk_factors.append(
                "Threat/intimidation language detected"
            )

        if verification_detected:
            score += 0.07
            risk_factors.append(
                "Identity/KYC verification request detected"
            )

        if credential_request_detected:
            score += 0.15
            risk_factors.append(
                "OTP/password/PIN request detected"
            )

        # =========================================================
        # STEP 6 — High-value combinations
        #
        # This is the most important improvement.
        # A single "bhai" isn't dangerous.
        #
        # But:
        #
        # family + emergency + money + urgency + secrecy
        #
        # is a strong social-engineering pattern.
        # =========================================================

        # ---------------------------------------------------------
        # FAMILY IMPERSONATION COMBINATION
        # ---------------------------------------------------------

        family_combo_count = sum([
            family_detected,
            emergency_detected,
            financial_request,
            urgency_detected,
            secrecy_detected,
        ])

        if family_detected and financial_request:
            score += 0.15
            risk_factors.append(
                "Family relationship combined with financial request"
            )

        if family_detected and emergency_detected:
            score += 0.10
            risk_factors.append(
                "Family relationship combined with emergency story"
            )

        if financial_request and urgency_detected:
            score += 0.12
            risk_factors.append(
                "Urgent financial request"
            )

        if financial_request and secrecy_detected:
            score += 0.10
            risk_factors.append(
                "Financial request combined with secrecy"
            )

        if family_combo_count >= 4:
            score += 0.20
            risk_factors.append(
                "Strong family-impersonation social-engineering pattern"
            )

        # ---------------------------------------------------------
        # POLICE / DIGITAL ARREST COMBINATION
        # ---------------------------------------------------------

        authority_combo_count = sum([
            authority_detected,
            threat_detected,
            verification_detected,
            urgency_detected,
        ])

        if authority_detected and threat_detected:
            score += 0.15
            risk_factors.append(
                "Authority claim combined with intimidation"
            )

        if authority_detected and verification_detected:
            score += 0.10
            risk_factors.append(
                "Authority claim combined with identity verification"
            )

        if authority_combo_count >= 3:
            score += 0.18
            risk_factors.append(
                "Strong authority-impersonation pattern"
            )

        # ---------------------------------------------------------
        # OTP / CREDENTIAL COMBINATION
        # ---------------------------------------------------------

        if credential_request_detected and urgency_detected:
            score += 0.12
            risk_factors.append(
                "Urgent request for authentication credentials"
            )

        # ---------------------------------------------------------
        # FINANCIAL + IDENTITY COMBINATION
        # ---------------------------------------------------------

        if financial_request and verification_detected:
            score += 0.10
            risk_factors.append(
                "Financial request combined with identity verification"
            )

        # =========================================================
        # STEP 7 — Prevent accidental over-scoring
        # =========================================================

        score = min(1.0, score)

        # =========================================================
        # STEP 8 — If category is UNKNOWN but strong signals exist
        # =========================================================

        if best_cat_id == "UNKNOWN":

            if (
                family_combo_count >= 3
                or authority_combo_count >= 3
                or (
                    financial_request
                    and urgency_detected
                )
                or (
                    credential_request_detected
                    and urgency_detected
                )
            ):
                score = max(score, 0.60)

            elif urgency_detected or financial_request:
                score = max(score, 0.35)

        # =========================================================
        # STEP 9 — Override category when contextual pattern
        # is stronger than weak taxonomy matching
        # =========================================================

        # Family pattern
        if family_combo_count >= 3:

            if (
                best_cat_id == "UNKNOWN"
                or best_cat_id in {
                    "UPI",
                    "FAMILY_IMPERSONATION",
                }
            ):
                best_cat_id = "FAMILY_IMPERSONATION"

        # Authority / digital arrest pattern
        if (
            authority_detected
            and threat_detected
            and (
                verification_detected
                or urgency_detected
            )
        ):

            # Prefer DIGITAL_ARREST when strong legal-threat signals
            if any(
                word in text
                for word in [
                    "digital arrest",
                    "arrest warrant",
                    "fir",
                    "under investigation",
                    "you are under investigation",
                    "aapke khilaf case",
                    "legal action",
                ]
            ):
                best_cat_id = "DIGITAL_ARREST"

            else:
                best_cat_id = "POLICE_IMPERSONATION"

        # =========================================================
        # STEP 10 — Determine final severity
        # =========================================================

        final_severity = self._probability_to_severity(score)

        # =========================================================
        # STEP 11 — Human-readable signals
        # =========================================================

        signals: list[str] = []

        # Existing taxonomy indicators
        for indicator in matched_indicators[:5]:
            signals.append(indicator)

        # High-level signals
        if family_detected:
            signals.append("family/friend relationship detected")

        if emergency_detected:
            signals.append("emergency/distress language detected")

        if urgency_detected:
            signals.append("urgent language detected")

        if financial_request:
            signals.append("financial request detected")

        if secrecy_detected:
            signals.append("secrecy manipulation detected")

        if authority_detected:
            signals.append("authority claim detected")

        if threat_detected:
            signals.append("threat/intimidation detected")

        if verification_detected:
            signals.append("identity verification request detected")

        if credential_request_detected:
            signals.append("credential/OTP request detected")

        # Remove duplicates while preserving order
        signals = list(dict.fromkeys(signals))

        # =========================================================
        # STEP 12 — Category information
        # =========================================================

        cat_data = self._categories.get(
            best_cat_id,
            self._categories["UNKNOWN"],
        )

        # =========================================================
        # STEP 13 — Explanation
        # =========================================================

        explanation = self._build_explanation(
            category=best_cat_id,
            family_detected=family_detected,
            emergency_detected=emergency_detected,
            financial_request=financial_request,
            urgency_detected=urgency_detected,
            secrecy_detected=secrecy_detected,
            authority_detected=authority_detected,
            threat_detected=threat_detected,
            verification_detected=verification_detected,
            credential_request_detected=credential_request_detected,
        )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        return {
            "scam_probability": round(score, 4),
            "category": best_cat_id,
            "category_name": cat_data["name"],
            "severity": final_severity,
            "signals": signals,
            "urgency_detected": urgency_detected,
            "financial_request": financial_request,
            "identity_claim": identity_claim,
            "matched_indicators": matched_indicators,
            "recommended_action": cat_data[
                "recommended_action"
            ],
            "explanation": explanation,
            "risk_factors": risk_factors[:12],
            "latency_ms": round(latency_ms, 2),
        }

    # =============================================================
    # Explanation generator
    # =============================================================

    def _build_explanation(
        self,
        category: str,
        family_detected: bool,
        emergency_detected: bool,
        financial_request: bool,
        urgency_detected: bool,
        secrecy_detected: bool,
        authority_detected: bool,
        threat_detected: bool,
        verification_detected: bool,
        credential_request_detected: bool,
    ) -> str:

        # Family impersonation
        if category == "FAMILY_IMPERSONATION":

            parts = []

            if family_detected:
                parts.append("family/friend identity cues")

            if emergency_detected:
                parts.append("an emergency or distress story")

            if financial_request:
                parts.append("a financial request")

            if urgency_detected:
                parts.append("urgent pressure")

            if secrecy_detected:
                parts.append("a request to keep the interaction secret")

            if parts:
                return (
                    "Potential family-impersonation scam detected: "
                    + ", ".join(parts)
                    + "."
                )

        # Digital arrest
        if category == "DIGITAL_ARREST":

            parts = []

            if authority_detected:
                parts.append("authority impersonation")

            if threat_detected:
                parts.append("legal/arrest threats")

            if verification_detected:
                parts.append("identity verification")

            if urgency_detected:
                parts.append("urgent pressure")

            return (
                "Potential digital-arrest/authority scam detected: "
                + ", ".join(parts)
                + "."
            )

        # Police impersonation
        if category == "POLICE_IMPERSONATION":

            return (
                "Potential police/government impersonation detected "
                "based on authority claims and suspicious interaction "
                "patterns."
            )

        # UPI
        if category == "UPI":

            return (
                "Potential payment scam detected because the "
                "conversation contains payment or UPI-related signals."
            )

        # OTP
        if category == "OTP":

            return (
                "Potential credential theft detected because the "
                "conversation contains OTP or authentication-code "
                "requests."
            )

        # Generic
        if financial_request and urgency_detected:

            return (
                "Suspicious interaction detected: an urgent "
                "financial request was identified."
            )

        if credential_request_detected:

            return (
                "Suspicious interaction detected: a request for "
                "sensitive authentication information was identified."
            )

        if authority_detected and threat_detected:

            return (
                "Suspicious authority-impersonation pattern detected "
                "with threatening language."
            )

        return (
            "No strong scam pattern was identified from the "
            "available transcript."
        )