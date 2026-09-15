"""
VoxShield — Deepfake Detection Service
High-level service that wraps the active deepfake backend.
Backend is selected via config.yaml (deepfake.backend).
"""

import logging
import os
from pathlib import Path
from typing import Optional

import numpy as np
import yaml

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"


class DeepfakeDetectionService:
    """
    Unified interface for deepfake audio detection.
    Selects and manages the configured backend (Spectra-0, pipeline, or wav2vec2).
    """

    def __init__(self, config_path: Path = CONFIG_PATH):
        self._backend_name = "spectra"
        self._device = "cpu"

        if config_path.exists():
            try:
                with open(config_path) as f:
                    cfg = yaml.safe_load(f) or {}
                self._backend_name = cfg.get("deepfake", {}).get("backend", "spectra")
                self._backend_cfg = cfg.get("deepfake", {}).get(self._backend_name, {})
                self._device = self._backend_cfg.get("device", "cpu")
            except Exception as e:
                logger.warning(f"Could not load config.yaml: {e}. Defaulting to CPU.")

        self._backend = None
        self._pipe = None

    def initialize(self) -> bool:
        """Load the configured backend model. Falls back to public pipeline if gated."""
        if self._backend_name == "disabled":
            logger.info("Deepfake detection is disabled via config.")
            return False

        # Attempt primary Spectra backend
        try:
            from .spectra_backend import SpectraBackend
            self._backend = SpectraBackend(device=self._device)
            if self._backend.load():
                logger.info("✅ Spectra-0 backend loaded successfully.")
                return True
        except Exception as e:
            logger.warning(f"Spectra backend initialization failed: {e}. Attempting public HF pipeline fallback...")

        # Fallback: Load public open-source audio classification pipeline
        try:
            from transformers import pipeline
            import torch

            device = 0 if self._device == "cuda" and torch.cuda.is_available() else -1
            token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")

            self._pipe = pipeline(
                "audio-classification",
                model="mo-thecreator/Deepfake-audio-detection",
                device=device,
                token=token,
            )
            logger.info("✅ Public deepfake audio classification pipeline loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Fallback audio classifier failed to load: {e}")
            return False

    @property
    def is_available(self) -> bool:
        backend_ready = self._backend is not None and getattr(self._backend, "is_loaded", False)
        pipe_ready = self._pipe is not None
        return backend_ready or pipe_ready

    def analyze(self, waveform: np.ndarray, sample_rate: int = 16000) -> dict:
        """Analyze audio for deepfake characteristics."""
        if not self.is_available:
            return {
                "model_available": False,
                "fake_probability": None,
                "real_probability": None,
                "label": "Model unavailable",
                "confidence": None,
                "latency_ms": 0.0,
                "model_id": self._backend_name,
                "error": "Deepfake detection model not loaded",
            }

        # If Spectra backend loaded
        if self._backend and getattr(self._backend, "is_loaded", False):
            result = self._backend.predict(waveform, sample_rate)
            return result.to_dict()

        # If Fallback Transformers pipeline loaded
        try:
            import time
            t0 = time.perf_counter()

            # Ensure waveform is 1D float32 numpy array
            if waveform.ndim > 1:
                waveform = np.mean(waveform, axis=0)
            waveform = waveform.astype(np.float32)

            # Normalization check
            if np.max(np.abs(waveform)) > 1.0:
                waveform = waveform / np.max(np.abs(waveform))

            preds = self._pipe({"raw": waveform, "sampling_rate": sample_rate})
            latency = (time.perf_counter() - t0) * 1000

            fake_score = 0.0
            real_score = 0.0
            for p in preds:
                lbl = p["label"].lower()
                if "fake" in lbl or "spoof" in lbl or "synthetic" in lbl:
                    fake_score = max(fake_score, float(p["score"]))
                else:
                    real_score = max(real_score, float(p["score"]))

            if real_score == 0.0 and fake_score > 0.0:
                real_score = max(0.0, 1.0 - fake_score)
            elif fake_score == 0.0 and real_score > 0.0:
                fake_score = max(0.0, 1.0 - real_score)

            is_fake = fake_score > 0.5
            return {
                "model_available": True,
                "fake_probability": round(fake_score, 4),
                "real_probability": round(real_score, 4),
                "label": "Synthetic / AI Voice" if is_fake else "Authentic Human Voice",
                "confidence": round(fake_score if is_fake else real_score, 4),
                "latency_ms": round(latency, 1),
                "model_id": "transformers/deepfake-audio-fallback",
                "error": None,
            }
        except Exception as e:
            logger.error(f"Prediction inference error: {e}")
            return {
                "model_available": False,
                "fake_probability": None,
                "real_probability": None,
                "label": "Inference Error",
                "confidence": None,
                "latency_ms": 0.0,
                "model_id": "fallback",
                "error": str(e),
            }