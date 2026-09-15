"""
VoxShield — Risk Engine
Combines voice authenticity, scam intelligence, caller history, and conversation
signals into a single 0–100 risk score with a categorical label.

All weights are loaded from risk_config.yaml — no hardcoded scoring.
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

RISK_CONFIG_PATH = Path(__file__).parent.parent.parent / "risk_config.yaml"


@dataclass
class RiskResult:
    risk_score: int                    # 0–100
    risk_level: str                    # LOW | CAUTION | HIGH | CRITICAL
    component_scores: dict             # Individual signal scores before weighting
    weighted_scores: dict              # Weighted contribution of each signal
    reasons: list[str]                 # Human-readable explanations
    recommended_actions: list[str]     # What user should do
    latency_ms: float

    def to_dict(self) -> dict:
        return {
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "component_scores": {k: round(v, 3) for k, v in self.component_scores.items()},
            "weighted_scores": {k: round(v, 3) for k, v in self.weighted_scores.items()},
            "reasons": self.reasons,
            "recommended_actions": self.recommended_actions,
            "latency_ms": round(self.latency_ms, 2),
        }


class RiskEngine:
    """
    Computes the final VoxShield risk score from multiple signals.

    Inputs:
      - voice_fake_probability: 0.0–1.0 from deepfake detector
      - scam_probability: 0.0–1.0 from scam classifier
      - financial_request: bool
      - urgency_level: 0.0–1.0 (derived from scam analysis)
      - identity_claim: bool
      - caller_history: dict with previous_alerts, is_unknown, is_trusted

    All weights loaded from risk_config.yaml.
    """

    def __init__(self, config_path: Path = RISK_CONFIG_PATH):
        with open(config_path, encoding="utf-8") as f:
            self._cfg = yaml.safe_load(f)

        self._weights = self._cfg["weights"]
        self._caller_modifiers = self._cfg["caller_reputation"]
        self._category_multipliers = self._cfg["category_multipliers"]
        self._thresholds = self._cfg["thresholds"]
        self._explanation_labels = self._cfg["explanations"]

        logger.info("RiskEngine initialized with config from risk_config.yaml")

    def compute(
        self,
        voice_fake_probability: Optional[float],
        scam_result: dict,
        caller_history: Optional[dict] = None,
    ) -> RiskResult:
        """
        Compute risk score.

        Args:
            voice_fake_probability: 0.0–1.0 or None if model unavailable.
            scam_result: Output from ScamIntelligenceService.analyze().
            caller_history: Dict with keys:
                - is_unknown (bool)
                - is_trusted (bool)
                - previous_alerts (int)
                - total_calls (int)

        Returns:
            RiskResult with score, level, components, and explanations.
        """
        start = time.perf_counter()
        caller_history = caller_history or {}

        # --- Extract inputs ---
        scam_prob = scam_result.get("scam_probability", 0.0)
        financial_req = scam_result.get("financial_request", False)
        urgency = scam_result.get("urgency_detected", False)
        identity_claim = scam_result.get("identity_claim", False)
        scam_category = scam_result.get("category", "UNKNOWN")
        is_unknown = caller_history.get("is_unknown", True)
        is_trusted = caller_history.get("is_trusted", False)
        prev_alerts = caller_history.get("previous_alerts", 0)

        # --- Apply category severity multiplier to scam_prob ---
        multiplier = self._category_multipliers.get(scam_category, 1.0)
        adjusted_scam = min(1.0, scam_prob * multiplier)

        # --- Voice fake handling ---
        if voice_fake_probability is None:
            # Model unavailable — don't penalize but don't boost either
            voice_component = 0.3  # Neutral-conservative value
            voice_available = False
        else:
            voice_component = voice_fake_probability
            voice_available = True

        # --- Compute component scores (all 0–1) ---
        components = {
            "voice_authenticity": voice_component,
            "scam_probability": adjusted_scam,
            "financial_request": 1.0 if financial_req else 0.0,
            "urgency_level": 0.85 if urgency else 0.0,
            "identity_claim": 0.65 if identity_claim else 0.0,
            "caller_reputation": self._compute_caller_reputation(
                is_unknown, is_trusted, prev_alerts
            ),
        }

        # --- Apply weights ---
        weighted = {
            k: components[k] * self._weights[k]
            for k in self._weights
        }
        raw_score = sum(weighted.values())  # 0.0–1.0

        # --- Convert to 0–100 integer ---
        score = int(round(raw_score * 100))

        # --- Caller modifier bonuses (post-weight additive) ---
        if is_unknown:
            score += self._caller_modifiers["unknown_number_penalty"]
        if is_trusted:
            score += self._caller_modifiers["trusted_contact_bonus"]
        score += min(prev_alerts, 3) * self._caller_modifiers["repeat_alert_penalty"]

        score = max(0, min(100, score))

        # --- Determine level ---
        risk_level = self._score_to_level(score)

        # --- Generate explanations ---
        reasons = self._generate_reasons(
            voice_component, voice_available, adjusted_scam,
            financial_req, urgency, identity_claim,
            is_unknown, is_trusted, prev_alerts,
        )

        actions = self._generate_actions(risk_level, scam_result)

        latency_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"Risk computed: score={score}, level={risk_level}, "
            f"voice={voice_component:.2f}, scam={adjusted_scam:.2f}, "
            f"latency={latency_ms:.1f}ms"
        )

        return RiskResult(
            risk_score=score,
            risk_level=risk_level,
            component_scores=components,
            weighted_scores=weighted,
            reasons=reasons,
            recommended_actions=actions,
            latency_ms=latency_ms,
        )

    def _compute_caller_reputation(
        self, is_unknown: bool, is_trusted: bool, prev_alerts: int
    ) -> float:
        """Return 0–1 reputation risk score."""
        if is_trusted:
            return 0.05
        if is_unknown and prev_alerts == 0:
            return 0.5
        if prev_alerts > 0:
            return min(1.0, 0.5 + prev_alerts * 0.15)
        return 0.3

    def _score_to_level(self, score: int) -> str:
        if score <= self._thresholds["low_max"]:
            return "LOW"
        elif score <= self._thresholds["caution_max"]:
            return "CAUTION"
        elif score <= self._thresholds["high_max"]:
            return "HIGH"
        else:
            return "CRITICAL"

    def _generate_reasons(
        self,
        voice_prob: float,
        voice_available: bool,
        scam_prob: float,
        financial_req: bool,
        urgency: bool,
        identity_claim: bool,
        is_unknown: bool,
        is_trusted: bool,
        prev_alerts: int,
    ) -> list[str]:
        reasons = []
        labels = self._explanation_labels

        if not voice_available:
            reasons.append("🟡 Voice authenticity model unavailable")
        elif voice_prob >= 0.75:
            reasons.append(f"🔴 {labels['high_voice_fake']} ({voice_prob:.0%} probability)")
        elif voice_prob >= 0.45:
            reasons.append(f"🟠 {labels['medium_voice_fake']} ({voice_prob:.0%} probability)")

        if scam_prob >= 0.70:
            reasons.append(f"🔴 {labels['high_scam']} ({scam_prob:.0%})")
        elif scam_prob >= 0.40:
            reasons.append(f"🟠 {labels['medium_scam']} ({scam_prob:.0%})")

        if financial_req:
            reasons.append(f"🔴 {labels['financial_request']}")
        if urgency:
            reasons.append(f"🟠 {labels['urgency']}")
        if identity_claim:
            reasons.append(f"🟠 {labels['identity_claim']}")
        if is_unknown:
            reasons.append(f"🟡 {labels['unknown_caller']}")
        if prev_alerts > 0:
            reasons.append(f"🔴 {labels['repeat_offender']} ({prev_alerts} previous alert{'s' if prev_alerts > 1 else ''})")
        if is_trusted:
            reasons.append(f"🟢 {labels['trusted_contact']}")

        if not reasons:
            reasons.append("🟢 No significant risk signals detected")

        return reasons

    def _generate_actions(self, risk_level: str, scam_result: dict) -> list[str]:
        base_action = scam_result.get("recommended_action", "")
        actions = []

        if risk_level == "CRITICAL":
            actions += [
                "Do NOT share OTP, PIN, or passwords",
                "Do NOT transfer any money",
                "Hang up immediately",
                "Verify caller through an independent channel",
            ]
        elif risk_level == "HIGH":
            actions += [
                "Do not share personal or financial information",
                "Verify the caller's identity before proceeding",
                "Call back on a known official number",
            ]
        elif risk_level == "CAUTION":
            actions += [
                "Proceed carefully — verify caller identity",
                "Do not share sensitive information on this call",
            ]
        else:
            actions.append("Call appears low risk — remain vigilant")

        if base_action and base_action not in actions:
            actions.append(base_action)

        return actions
