"""
VoxShield — Audio Preprocessing Utility
Handles loading, resampling, and normalization of audio for all AI backends.
"""

import time
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

TARGET_SAMPLE_RATE = 16000  # Required by Whisper and most speech models


def load_audio(
    file_path: str | Path,
    target_sr: int = TARGET_SAMPLE_RATE,
    mono: bool = True,
    normalize: bool = True,
) -> Tuple[np.ndarray, int]:
    """
    Load audio from file, resample to target_sr, optionally normalize.

    Returns:
        (waveform: np.ndarray shape [samples], sample_rate: int)
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    waveform, sr = librosa.load(str(file_path), sr=target_sr, mono=mono)

    if normalize:
        max_val = np.abs(waveform).max()
        if max_val > 0:
            waveform = waveform / max_val

    logger.debug(
        f"Loaded audio: {file_path.name}, sr={sr}, "
        f"duration={len(waveform)/sr:.2f}s, shape={waveform.shape}"
    )
    return waveform, sr


def load_audio_bytes(
    audio_bytes: bytes,
    target_sr: int = TARGET_SAMPLE_RATE,
    mono: bool = True,
    normalize: bool = True,
) -> Tuple[np.ndarray, int]:
    """
    Load audio from raw bytes (e.g., uploaded file or WebSocket chunk).
    Writes to a temporary buffer and loads via librosa.
    """
    import io
    import tempfile
    import os

    # soundfile can read many formats directly from bytes
    try:
        with io.BytesIO(audio_bytes) as buf:
            waveform, sr = sf.read(buf, dtype="float32", always_2d=False)
        # Resample if needed
        if sr != target_sr:
            waveform = librosa.resample(waveform, orig_sr=sr, target_sr=target_sr)
            sr = target_sr
    except Exception:
        # Fallback: write to temp file and use librosa
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            waveform, sr = librosa.load(tmp_path, sr=target_sr, mono=mono)
        finally:
            os.unlink(tmp_path)

    if normalize:
        max_val = np.abs(waveform).max()
        if max_val > 0:
            waveform = waveform / max_val

    return waveform, sr


def split_into_chunks(
    waveform: np.ndarray,
    sample_rate: int,
    chunk_duration_seconds: float = 5.0,
    overlap_seconds: float = 0.5,
) -> list[np.ndarray]:
    """
    Split a long waveform into overlapping chunks for streaming analysis.
    """
    chunk_size = int(chunk_duration_seconds * sample_rate)
    step_size = int((chunk_duration_seconds - overlap_seconds) * sample_rate)

    chunks = []
    start = 0
    while start < len(waveform):
        end = min(start + chunk_size, len(waveform))
        chunk = waveform[start:end]
        if len(chunk) > sample_rate // 2:  # Skip chunks < 0.5s
            chunks.append(chunk)
        start += step_size

    return chunks


def get_audio_duration(waveform: np.ndarray, sample_rate: int) -> float:
    """Return duration in seconds."""
    return len(waveform) / sample_rate


def audio_info(file_path: str | Path) -> dict:
    """Return basic metadata about an audio file without full loading."""
    file_path = Path(file_path)
    info = sf.info(str(file_path))
    return {
        "file": file_path.name,
        "duration_seconds": info.duration,
        "sample_rate": info.samplerate,
        "channels": info.channels,
        "format": info.format,
        "subtype": info.subtype,
    }
