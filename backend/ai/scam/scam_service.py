"""
VoxShield — Scam Intelligence Service
High-level interface for scam analysis.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ScamIntelligenceService:
    """Wraps the scam classifier for use in the analysis pipeline."""

    def __init__(self):
        from .scam_classifier import ScamClassifier
        self._classifier = ScamClassifier()
        self._is_available = True

    @property
    def is_available(self) -> bool:
        return self._is_available

    def analyze(self, transcript: str) -> dict:
        """
        Analyze transcript for scam intent.

        Args:
            transcript: Full text from ASR output.

        Returns:
            Scam analysis dict.
        """
        if not transcript or not transcript.strip():
            return {
                "scam_probability": 0.0,
                "category": "UNKNOWN",
                "category_name": "No transcript",
                "severity": "LOW",
                "signals": [],
                "urgency_detected": False,
                "financial_request": False,
                "identity_claim": False,
                "matched_indicators": [],
                "recommended_action": "Unable to analyze — no transcript available.",
                "latency_ms": 0.0,
            }

        return self._classifier.classify(transcript)
