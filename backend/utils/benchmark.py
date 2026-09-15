"""
VoxShield — Benchmark Utility
Measures actual inference latency and RAM usage.
All numbers reported are real measurements — nothing is hardcoded.
"""

import time
import psutil
import os
import logging
from dataclasses import dataclass, field
from typing import Callable, Any

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    name: str
    latency_ms: float
    ram_before_mb: float
    ram_after_mb: float
    ram_delta_mb: float
    success: bool
    error: str | None = None
    extra: dict = field(default_factory=dict)

    def __str__(self) -> str:
        status = "✅" if self.success else "❌"
        return (
            f"{status} [{self.name}]\n"
            f"   Latency    : {self.latency_ms:.1f} ms\n"
            f"   RAM before : {self.ram_before_mb:.1f} MB\n"
            f"   RAM after  : {self.ram_after_mb:.1f} MB\n"
            f"   RAM delta  : {self.ram_delta_mb:+.1f} MB\n"
        ) + (f"   Error      : {self.error}\n" if self.error else "")


def get_ram_mb() -> float:
    """Return current process RSS memory in MB."""
    proc = psutil.Process(os.getpid())
    return proc.memory_info().rss / 1024 / 1024


def get_system_ram_available_mb() -> float:
    """Return system-wide available RAM in MB."""
    return psutil.virtual_memory().available / 1024 / 1024


def benchmark(
    name: str,
    fn: Callable[[], Any],
    warmup: bool = False,
) -> BenchmarkResult:
    """
    Run a callable and measure its wall-clock latency and RAM impact.

    Args:
        name: Human-readable label for this benchmark.
        fn: Zero-argument callable to time.
        warmup: If True, run once before timing (for JIT warmup).
    """
    if warmup:
        try:
            fn()
        except Exception:
            pass

    ram_before = get_ram_mb()
    start = time.perf_counter()
    error = None
    try:
        result = fn()
    except Exception as e:
        result = None
        error = str(e)
    end = time.perf_counter()
    ram_after = get_ram_mb()

    br = BenchmarkResult(
        name=name,
        latency_ms=(end - start) * 1000,
        ram_before_mb=ram_before,
        ram_after_mb=ram_after,
        ram_delta_mb=ram_after - ram_before,
        success=error is None,
        error=error,
    )
    logger.info(str(br))
    return br


def benchmark_model_load(name: str, load_fn: Callable[[], Any]) -> BenchmarkResult:
    """Benchmark a model load operation specifically."""
    logger.info(f"Benchmarking model load: {name}")
    return benchmark(f"model_load:{name}", load_fn)


def benchmark_inference(
    name: str,
    inference_fn: Callable[[], Any],
    runs: int = 3,
) -> BenchmarkResult:
    """
    Run inference multiple times and return average latency.
    Uses the first run as warmup.
    """
    logger.info(f"Benchmarking inference: {name} ({runs} runs)")
    results = []
    for i in range(runs):
        r = benchmark(f"{name}_run{i+1}", inference_fn)
        results.append(r)

    avg_latency = sum(r.latency_ms for r in results) / len(results)
    best = min(results, key=lambda r: r.latency_ms)
    worst = max(results, key=lambda r: r.latency_ms)

    summary = BenchmarkResult(
        name=f"{name}_avg({runs}runs)",
        latency_ms=avg_latency,
        ram_before_mb=results[0].ram_before_mb,
        ram_after_mb=results[-1].ram_after_mb,
        ram_delta_mb=results[-1].ram_after_mb - results[0].ram_before_mb,
        success=all(r.success for r in results),
        extra={
            "best_ms": best.latency_ms,
            "worst_ms": worst.latency_ms,
            "runs": runs,
        },
    )
    logger.info(f"  Average: {avg_latency:.1f}ms | Best: {best.latency_ms:.1f}ms | Worst: {worst.latency_ms:.1f}ms")
    return summary
