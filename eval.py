"""Evaluate the triager against the small legacy benchmark.

This reports *agreement with labels.json*, not proven production accuracy. The
README notes that those labels came from an earlier LLM prompt and spot checks.

    python3 eval.py
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
import math
import pathlib
import statistics
import sys
import time
from typing import Callable

import triage

HERE = pathlib.Path(__file__).parent
LABELS = {
    k: v
    for k, v in json.loads((HERE / "labels.json").read_text()).items()
    if not k.startswith("_")
}


@dataclass(frozen=True)
class CaseResult:
    name: str
    expected: str
    predicted: str | None
    latency_ms: float
    error: str | None = None

    @property
    def matched(self) -> bool:
        return self.error is None and self.predicted == self.expected


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Return a Wilson score interval for a binomial proportion."""
    if total <= 0:
        return (0.0, 0.0)
    proportion = successes / total
    denominator = 1 + z**2 / total
    centre = (proportion + z**2 / (2 * total)) / denominator
    margin = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / total + z**2 / (4 * total**2)
        )
        / denominator
    )
    return max(0.0, centre - margin), min(1.0, centre + margin)


def nearest_rank_percentile(values: list[float], percentile: float) -> float:
    """Nearest-rank percentile, which is easy to explain for a tiny sample."""
    if not values:
        raise ValueError("percentile requires at least one value")
    if not 0 < percentile <= 1:
        raise ValueError("percentile must be in (0, 1]")
    ordered = sorted(values)
    rank = math.ceil(percentile * len(ordered))
    return ordered[rank - 1]


def evaluate(
    labels: dict[str, str] | None = None,
    *,
    logs_dir: pathlib.Path | None = None,
    classifier: Callable[[str], dict[str, str]] | None = None,
) -> list[CaseResult]:
    """Run the benchmark while keeping classifier failures distinct from misses."""
    labels = LABELS if labels is None else labels
    logs_dir = HERE / "logs" if logs_dir is None else logs_dir
    classifier = triage.classify if classifier is None else classifier

    results: list[CaseResult] = []
    for name, expected in sorted(labels.items()):
        started = time.perf_counter()
        predicted: str | None = None
        error: str | None = None
        try:
            log_text = (logs_dir / name).read_text(
                encoding="utf-8",
                errors="replace",
            )
            predicted = classifier(log_text)["category"]
        except (OSError, triage.TriageError, KeyError, TypeError) as exc:
            error = str(exc)
        latency_ms = (time.perf_counter() - started) * 1000
        results.append(
            CaseResult(
                name=name,
                expected=expected,
                predicted=predicted,
                latency_ms=latency_ms,
                error=error,
            )
        )
    return results


def _print_results(results: list[CaseResult]) -> None:
    print(f"{'log':20} {'expected':13} {'got':13} {'ms':>8} result")
    print("-" * 70)
    for result in results:
        got = result.predicted if result.error is None else "ERROR"
        status = "ok" if result.matched else ("ERR" if result.error else "XX")
        print(
            f"{result.name:20} {result.expected:13} {got:13} "
            f"{result.latency_ms:8.1f} {status}"
        )
        if result.error:
            first_line = result.error.splitlines()[0]
            print(f"  error: {first_line}")


def _print_summary(results: list[CaseResult]) -> None:
    total = len(results)
    correct = sum(result.matched for result in results)
    errors = sum(result.error is not None for result in results)
    completed = total - errors

    print("-" * 70)
    if completed:
        low, high = wilson_interval(correct, completed)
        print(
            "legacy-label agreement (completed classifications): "
            f"{correct}/{completed} ({correct / completed:.0%})"
        )
        print(f"95% Wilson interval on that agreement: {low:.0%} to {high:.0%}")
    else:
        print("legacy-label agreement (completed classifications): n/a (0 completed)")
        print("95% Wilson interval on that agreement: n/a")
    print(f"end-to-end benchmark successes: {correct}/{total}")
    print(f"classifier/system errors: {errors}/{total}")
    print(
        "benchmark warning: only 10 examples; labels were produced by an earlier "
        "LLM prompt and spot-checked, so agreement is not production accuracy."
    )

    latencies = [result.latency_ms for result in results]
    if latencies:
        print(
            "latency: "
            f"total={sum(latencies):.1f} ms, "
            f"median={statistics.median(latencies):.1f} ms, "
            f"p95(nearest-rank)={nearest_rank_percentile(latencies, 0.95):.1f} ms, "
            f"max={max(latencies):.1f} ms"
        )

    print("\ncategory agreement:")
    for category in triage.CATEGORIES:
        cases = [result for result in results if result.expected == category]
        matched = sum(result.matched for result in cases)
        print(f"  {category:12} {matched}/{len(cases)}")

    print("\nconfusion / outcomes:")
    outcomes = Counter(
        (result.expected, result.predicted if result.error is None else "__error__")
        for result in results
    )
    for (expected, predicted), count in sorted(outcomes.items()):
        print(f"  {expected:12} -> {predicted:12} {count}")


def main() -> int:
    results = evaluate()
    _print_results(results)
    _print_summary(results)
    return int(any(result.error is not None for result in results))


if __name__ == "__main__":
    sys.exit(main())
