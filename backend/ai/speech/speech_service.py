"""
VoxShield — Speech Recognition Service
Routes transcription to the configured ASR backend (Whisper or IndicConformer).
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import yaml

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"


class SpeechRecognitionService:
    """
    Unified ASR interface. Backend is selected via config.yaml.

    Routing logic:
      - English, Hindi, Hinglish → Whisper (reliable, fast on CPU)
      - Regional Indian languages → IndicConformer (disabled on demo hardware)
      - Auto-detect mode: Whisper detects language first, then routes if needed
    """

    INDIC_LANGUAGES = {
        "as", "bn", "brx", "doi", "gu", "kn", "kok", "ks",
        "mai", "ml", "mni", "mr", "ne", "or", "pa", "sa", "sat",
        "sd", "ta", "te", "ur",
    }

    def __init__(self, config_path: Path = CONFIG_PATH):
        with open(config_path) as f:
            cfg = yaml.safe_load(f)

        speech_cfg = cfg["speech"]
        self._primary_backend_name = speech_cfg["backend"]
        self._whisper_cfg = speech_cfg.get("whisper", {})
        self._indic_cfg = speech_cfg.get("indic", {})

        self._whisper_backend = None
        self._indic_backend = None

    def initialize(self) -> dict:
        """
        Load configured backends. Returns status dict.
        """
        status = {}

        # Always load Whisper — it's the primary/fallback
        from .whisper_backend import WhisperBackend
        self._whisper_backend = WhisperBackend(
            model_size=self._whisper_cfg.get("model_size", "tiny"),
            device=self._whisper_cfg.get("device", "cpu"),
            language=self._whisper_cfg.get("language"),
        )
        whisper_ok = self._whisper_backend.load()
        status["whisper"] = "loaded" if whisper_ok else "failed"

        # Load IndicConformer only if explicitly enabled in config
        if self._indic_cfg.get("enabled", False):
            from .indic_backend import IndicConformerBackend
            self._indic_backend = IndicConformerBackend(
                model_id=self._indic_cfg.get("model_id", "ai4bharat/indic-conformer-600m-multilingual"),
                device=self._indic_cfg.get("device", "cpu"),
            )
            indic_ok = self._indic_backend.load()
            status["indic"] = "loaded" if indic_ok else "disabled (hardware constraint)"
        else:
            status["indic"] = "disabled (config)"

        return status

    @property
    def is_available(self) -> bool:
        return (
            self._whisper_backend is not None and self._whisper_backend.is_loaded
        ) or (
            self._indic_backend is not None and self._indic_backend.is_loaded
        )

    def transcribe(
        self,
        waveform: np.ndarray,
        sample_rate: int = 16000,
        language_hint: Optional[str] = None,
    ) -> dict:
        """
        Transcribe audio, routing to the appropriate backend.

        Args:
            waveform: Float32 numpy array at 16kHz.
            sample_rate: Audio sample rate.
            language_hint: Optional ISO 639-1 code to skip auto-detection.

        Returns:
            TranscriptResult as dict.
        """
        # Route to IndicConformer for regional languages if available
        if (
            language_hint in self.INDIC_LANGUAGES
            and self._indic_backend is not None
            and self._indic_backend.is_loaded
        ):
            logger.info(f"Routing to IndicConformer for language: {language_hint}")
            result = self._indic_backend.transcribe(waveform, sample_rate, language_hint)
            if result.model_available:
                return result.to_dict()
            logger.warning("IndicConformer unavailable, falling back to Whisper")

        # Primary: Whisper
        if self._whisper_backend and self._whisper_backend.is_loaded:
            result = self._whisper_backend.transcribe(waveform, sample_rate)
            return result.to_dict()

        # Nothing available
        return {
            "model_available": False,
            "text": "",
            "language": None,
            "language_probability": None,
            "latency_ms": 0.0,
            "model_id": "none",
            "segments": [],
            "error": "No ASR backend available",
        }
