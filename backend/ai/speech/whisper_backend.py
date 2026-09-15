"""
VoxShield — Whisper ASR Backend
Uses faster-whisper (CTranslate2 backend) which is compatible with Python 3.13
and significantly faster on CPU than openai-whisper.

Model: faster-whisper (wraps OpenAI Whisper weights)
Supports: English, Hindi, Hinglish, and 99+ languages.
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TranscriptResult:
    model_available: bool
    text: str
    language: Optional[str]              # ISO 639-1 language code
    language_probability: Optional[float]
    latency_ms: float
    model_id: str
    segments: list[dict]
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "model_available": self.model_available,
            "text": self.text,
            "language": self.language,
            "language_probability": round(self.language_probability, 3) if self.language_probability else None,
            "latency_ms": round(self.latency_ms, 1),
            "model_id": self.model_id,
            "segments": self.segments,
            "error": self.error,
        }


class WhisperBackend:
    """
    Faster-Whisper ASR backend (CTranslate2-accelerated Whisper).
    Supports English, Hindi, Hinglish, and multilingual speech.
    Runs efficiently on CPU, compatible with Python 3.13.
    """

    def __init__(self, model_size: str = "tiny", device: str = "cpu", language: Optional[str] = None):
        self.model_size = model_size
        self.device = device
        self.language = language  # None = auto-detect
        self.model_id = f"faster-whisper/{model_size}"
        self._model = None
        self._is_loaded = False
        self._load_error: Optional[str] = None

    def load(self) -> bool:
        logger.info(f"Loading faster-whisper {self.model_size} on {self.device}...")
        start = time.perf_counter()
        try:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type="int8",  # int8 reduces RAM on CPU
            )
            load_ms = (time.perf_counter() - start) * 1000
            logger.info(f"✅ faster-whisper {self.model_size} loaded in {load_ms:.0f}ms")
            self._is_loaded = True
            return True
        except ImportError:
            # Try falling back to openai-whisper
            logger.warning("faster-whisper not installed, trying openai-whisper...")
            return self._load_openai_whisper()
        except Exception as e:
            self._load_error = str(e)
            logger.error(f"❌ Failed to load Whisper: {e}")
            return False

    def _load_openai_whisper(self) -> bool:
        """Fallback to original openai-whisper."""
        try:
            import whisper
            self._model = whisper.load_model(self.model_size)
            self._model_type = "openai"
            self.model_id = f"openai/whisper-{self.model_size}"
            logger.info(f"✅ openai-whisper {self.model_size} loaded (fallback)")
            self._is_loaded = True
            return True
        except Exception as e:
            self._load_error = str(e)
            logger.error(f"❌ No Whisper backend available: {e}")
            return False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def transcribe(self, waveform: np.ndarray, sample_rate: int = 16000) -> TranscriptResult:
        """Transcribe audio waveform."""
        if not self._is_loaded:
            return TranscriptResult(
                model_available=False,
                text="",
                language=None,
                language_probability=None,
                latency_ms=0.0,
                model_id=self.model_id,
                segments=[],
                error=self._load_error or "Whisper model not loaded",
            )

        start = time.perf_counter()
        try:
            # Check if using faster-whisper or openai-whisper
            if hasattr(self._model, "transcribe") and "faster" in str(type(self._model)):
                return self._transcribe_faster_whisper(waveform, sample_rate, start)
            else:
                return self._transcribe_openai_whisper(waveform, sample_rate, start)

        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            logger.error(f"Whisper transcription error: {e}")
            return TranscriptResult(
                model_available=True,
                text="",
                language=None,
                language_probability=None,
                latency_ms=latency_ms,
                model_id=self.model_id,
                segments=[],
                error=str(e),
            )

    def _transcribe_faster_whisper(self, waveform: np.ndarray, sample_rate: int, start: float) -> TranscriptResult:
        """Transcribe using faster-whisper."""
        import librosa
        if sample_rate != 16000:
            waveform = librosa.resample(waveform, orig_sr=sample_rate, target_sr=16000)

        segments_gen, info = self._model.transcribe(
            waveform.astype(np.float32),
            language=self.language,
            beam_size=3,
            best_of=3,
            vad_filter=True,
        )

        segments = list(segments_gen)
        full_text = " ".join(s.text.strip() for s in segments)
        latency_ms = (time.perf_counter() - start) * 1000

        logger.info(
            f"faster-whisper: lang={info.language}({info.language_probability:.2f}), "
            f"text='{full_text[:60]}', latency={latency_ms:.0f}ms"
        )

        return TranscriptResult(
            model_available=True,
            text=full_text.strip(),
            language=info.language,
            language_probability=info.language_probability,
            latency_ms=latency_ms,
            model_id=self.model_id,
            segments=[
                {"start": s.start, "end": s.end, "text": s.text.strip()}
                for s in segments
            ],
        )

    def _transcribe_openai_whisper(self, waveform: np.ndarray, sample_rate: int, start: float) -> TranscriptResult:
        """Transcribe using openai-whisper (fallback)."""
        import whisper
        import librosa
        if sample_rate != 16000:
            waveform = librosa.resample(waveform, orig_sr=sample_rate, target_sr=16000)

        waveform_padded = whisper.pad_or_trim(waveform.astype(np.float32))
        mel = whisper.log_mel_spectrogram(waveform_padded).to(self._model.device)
        _, probs = self._model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        lang_prob = float(probs[detected_lang])

        result = self._model.transcribe(
            waveform.astype(np.float32),
            language=self.language or detected_lang,
            fp16=False,
            verbose=False,
        )

        latency_ms = (time.perf_counter() - start) * 1000
        return TranscriptResult(
            model_available=True,
            text=result["text"].strip(),
            language=detected_lang,
            language_probability=lang_prob,
            latency_ms=latency_ms,
            model_id=self.model_id,
            segments=[
                {"start": s["start"], "end": s["end"], "text": s["text"]}
                for s in result.get("segments", [])
            ],
        )
