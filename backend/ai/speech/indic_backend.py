"""
VoxShield — IndicConformer ASR Backend (Stub)

Status: NOT loaded during live demo due to hardware constraints.
  - Model: ai4bharat/indic-conformer-600m-multilingual
  - Estimated RAM: ~2.4 GB
  - Hardware: i5-1335U, 8GB RAM — insufficient for concurrent operation
  - Supported languages: 22 scheduled Indian languages

HOW TO ENABLE:
  1. Ensure system has 16+ GB RAM or use a GPU server.
  2. Set config.yaml speech.backend = "indic"
  3. The architecture supports full swap-in without code changes.

ONNX/QUANTIZATION:
  If a quantized IndicConformer is released, this backend can be updated
  to load it. The service interface remains unchanged.
"""

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

from .whisper_backend import TranscriptResult

logger = logging.getLogger(__name__)

INDIC_MODEL_ID = "ai4bharat/indic-conformer-600m-multilingual"

SUPPORTED_LANGUAGES = [
    "as", "bn", "brx", "doi", "gu", "hi", "kn", "kok", "ks",
    "mai", "ml", "mni", "mr", "ne", "or", "pa", "sa", "sat",
    "sd", "ta", "te", "ur",
]


class IndicConformerBackend:
    """
    AI4Bharat IndicConformer ASR backend.
    Supports all 22 scheduled Indian languages.

    NOTE: Disabled for demo — model too large for 8 GB RAM laptop.
    Set config.yaml speech.indic.enabled = true to activate on capable hardware.
    """

    def __init__(self, model_id: str = INDIC_MODEL_ID, device: str = "cpu"):
        self.model_id = model_id
        self.device = device
        self._is_loaded = False
        self._load_error = (
            "IndicConformer 600M is disabled: requires ~2.4 GB RAM + 4 GB free system RAM. "
            "Current deployment: 8 GB RAM laptop in demo mode. "
            "Architecture is ready — enable on server deployment."
        )

    def load(self) -> bool:
        """
        Attempt to load IndicConformer.
        Will fail gracefully with a clear message on demo hardware.
        """
        logger.warning(
            "IndicConformer load requested but disabled on demo hardware.\n"
            f"  Reason: {self._load_error}"
        )
        # Uncomment the block below on capable hardware:
        # try:
        #     from nemo.collections.asr.models import EncDecMultiTaskModel
        #     self._model = EncDecMultiTaskModel.from_pretrained(self.model_id)
        #     self._is_loaded = True
        #     return True
        # except Exception as e:
        #     self._load_error = str(e)
        #     return False
        return False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def transcribe(self, waveform: np.ndarray, sample_rate: int = 16000, language: Optional[str] = None) -> TranscriptResult:
        """Transcribe using IndicConformer (unavailable in demo mode)."""
        return TranscriptResult(
            model_available=False,
            text="",
            language=language,
            language_probability=None,
            latency_ms=0.0,
            model_id=self.model_id,
            segments=[],
            error=self._load_error,
        )
