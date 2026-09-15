"""
VoxShield — Speaker Verification Service (Stub)

Status: Not implemented for MVP.
Architecture ready for SpeechBrain ECAPA-TDNN integration.

When implemented, this service will:
  1. Enroll a user's trusted contacts' voice samples
  2. Compare incoming caller voice against enrolled voiceprints
  3. Return similarity score and identity risk

Currently shows: "Identity verification — Not configured"
This is intentional — we do NOT fake speaker similarity scores.
"""

import logging

logger = logging.getLogger(__name__)


class SpeakerVerificationService:
    """Speaker verification service — not configured for this deployment."""

    def __init__(self):
        self._is_available = False
        logger.info(
            "SpeakerVerificationService: Not configured. "
            "Enable in Phase 2 after trusted contact voice enrollment is implemented."
        )

    @property
    def is_available(self) -> bool:
        return self._is_available

    def verify(self, waveform, enrolled_voiceprint) -> dict:
        """Returns unavailable status — never fakes a similarity score."""
        return {
            "available": False,
            "similarity": None,
            "identity_risk": None,
            "message": "Identity verification — Not configured",
        }
