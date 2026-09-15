"""
VoxShield — Deepfake Detection Service
Wraps the spectra_0 model (lab260/spectra_0) for voice authenticity analysis.

IMPORTANT: No values are hardcoded. All probabilities come directly from model inference.
If the model fails to load, the service reports model_available=False — it does NOT
return fake scores to keep the UI looking good.
"""

import logging
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

logger = logging.getLogger(__name__)

SPECTRA_MODEL_ID = "lab260/spectra_0"
CACHE_DIR = Path(__file__).parent.parent.parent / "model_cache"


@dataclass
class DeepfakeResult:
    """Result from deepfake detection inference."""
    model_available: bool
    fake_probability: Optional[float]          # 0.0 = real, 1.0 = fake
    real_probability: Optional[float]
    label: Optional[str]                       # "real" | "spoof" | "uncertain"
    confidence: Optional[float]               # max(fake_prob, real_prob)
    latency_ms: float
    model_id: str
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "model_available": self.model_available,
            "fake_probability": round(self.fake_probability, 4) if self.fake_probability is not None else None,
            "real_probability": round(self.real_probability, 4) if self.real_probability is not None else None,
            "label": self.label,
            "confidence": round(self.confidence, 4) if self.confidence is not None else None,
            "latency_ms": round(self.latency_ms, 1),
            "model_id": self.model_id,
            "error": self.error,
        }

    @property
    def unavailable_result(self) -> dict:
        return {
            "model_available": False,
            "fake_probability": None,
            "real_probability": None,
            "label": "Model unavailable",
            "confidence": None,
            "latency_ms": self.latency_ms,
            "model_id": self.model_id,
            "error": self.error,
        }


class SpectraBackend:
    """
    Deepfake detection using lab260/spectra_0.

    spectra_0 is an audio classification model that distinguishes
    between genuine (real/bonafide) and spoofed (synthetic/deepfake) speech.
    """

    def __init__(self, device: str = "cpu", cache_dir: Optional[Path] = None):
        self.device = device
        self.cache_dir = cache_dir or CACHE_DIR
        self.model_id = SPECTRA_MODEL_ID
        self._model = None
        self._feature_extractor = None
        self._is_loaded = False
        self._load_error: Optional[str] = None
        self._label_map: dict[str, str] = {}

    def load(self) -> bool:
        """
        Load model from HuggingFace Hub (downloads on first run, cached after).
        Returns True if successful, False otherwise.
        """
        logger.info(f"Loading deepfake model: {self.model_id}")
        load_start = time.perf_counter()

        try:
            self._feature_extractor = AutoFeatureExtractor.from_pretrained(
                self.model_id,
                cache_dir=str(self.cache_dir),
            )
            self._model = AutoModelForAudioClassification.from_pretrained(
                self.model_id,
                cache_dir=str(self.cache_dir),
            )
            self._model.eval()
            self._model.to(self.device)

            # Build label map from model config
            self._label_map = {
                str(i): label
                for i, label in self._model.config.id2label.items()
            }
            logger.info(f"Model labels: {self._label_map}")

            load_ms = (time.perf_counter() - load_start) * 1000
            logger.info(f"✅ spectra_0 loaded in {load_ms:.0f}ms on {self.device}")
            self._is_loaded = True
            return True

        except Exception as e:
            self._load_error = str(e)
            logger.error(f"❌ Failed to load spectra_0: {e}")
            self._is_loaded = False
            return False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def predict(self, waveform: np.ndarray, sample_rate: int = 16000) -> DeepfakeResult:
        """
        Run deepfake detection on a waveform.

        Args:
            waveform: Float32 numpy array, shape [samples], normalized to [-1, 1].
            sample_rate: Sample rate of the waveform (model expects 16kHz).

        Returns:
            DeepfakeResult with real probabilities from model inference.
        """
        if not self._is_loaded:
            return DeepfakeResult(
                model_available=False,
                fake_probability=None,
                real_probability=None,
                label="Model unavailable",
                confidence=None,
                latency_ms=0.0,
                model_id=self.model_id,
                error=self._load_error or "Model not loaded",
            )

        start = time.perf_counter()
        try:
            # Prepare inputs
            inputs = self._feature_extractor(
                waveform,
                sampling_rate=sample_rate,
                return_tensors="pt",
                padding=True,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=-1).squeeze().cpu().numpy()

            latency_ms = (time.perf_counter() - start) * 1000

            # Map label indices to probabilities
            # spectra_0 uses "bonafide" (real) and "spoof" (fake) labels
            id2label = self._model.config.id2label
            fake_prob = 0.0
            real_prob = 0.0

            for idx, prob in enumerate(probs):
                label_name = id2label[idx].lower()
                if any(term in label_name for term in ["spoof", "fake", "synthetic", "generated"]):
                    fake_prob += float(prob)
                elif any(term in label_name for term in ["real", "bonafide", "genuine", "human"]):
                    real_prob += float(prob)

            # If we can't parse labels, use index 0=real, 1=fake as common default
            if fake_prob == 0.0 and real_prob == 0.0:
                logger.warning("Could not parse label names; falling back to index mapping")
                if len(probs) >= 2:
                    real_prob = float(probs[0])
                    fake_prob = float(probs[1])
                else:
                    real_prob = 1.0 - float(probs[0])
                    fake_prob = float(probs[0])

            # Normalize in case of rounding
            total = fake_prob + real_prob
            if total > 0:
                fake_prob /= total
                real_prob /= total

            confidence = max(fake_prob, real_prob)

            # Determine label
            if fake_prob >= 0.75:
                label = "spoof"
            elif fake_prob >= 0.45:
                label = "uncertain"
            else:
                label = "real"

            logger.info(
                f"Deepfake inference: fake={fake_prob:.3f}, real={real_prob:.3f}, "
                f"label={label}, latency={latency_ms:.1f}ms"
            )

            return DeepfakeResult(
                model_available=True,
                fake_probability=fake_prob,
                real_probability=real_prob,
                label=label,
                confidence=confidence,
                latency_ms=latency_ms,
                model_id=self.model_id,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            logger.error(f"Inference error: {e}")
            return DeepfakeResult(
                model_available=True,
                fake_probability=None,
                real_probability=None,
                label="error",
                confidence=None,
                latency_ms=latency_ms,
                model_id=self.model_id,
                error=str(e),
            )
