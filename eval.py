"""How accurate is the triager?

Scores classify() against labels.json and prints an accuracy figure.

    python3 eval.py
"""

from __future__ import annotations

import json
import pathlib

import triage

HERE = pathlib.Path(__file__).parent
LABELS = {
    k: v
    for k, v in json.loads((HERE / "labels.json").read_text()).items()
    if not k.startswith("_")
}


def main() -> None:
    correct = 0
    print(f"{'log':20} {'expected':13} {'got':13} ok")
    print("-" * 54)
    for name, expected in sorted(LABELS.items()):
        got = triage.classify((HERE / "logs" / name).read_text())["category"]
        hit = got == expected
        correct += hit
        print(f"{name:20} {expected:13} {got:13} {'ok' if hit else 'XX'}")
    print("-" * 54)
    total = len(LABELS)
    print(f"accuracy: {correct}/{total} ({correct / total:.0%})")


if __name__ == "__main__":
    main()
