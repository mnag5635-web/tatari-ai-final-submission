"""CI failure triage.

Reads a CI failure log and returns a category, a confidence, and a suggested
action.  See PRD.md for what this is supposed to do.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

import llm

CATEGORIES = ["flaky", "dependency", "infra", "product_bug", "lint"]

DEFAULT_ACTIONS = {
    "flaky": "Re-run the build.",
    "dependency": "Update the lockfile and re-run.",
    "infra": "Check CI service status and re-run.",
    "product_bug": "Fix the bug in the failing code path.",
    "lint": "Fix the lint errors.",
}

SYSTEM = f"""You triage CI failure logs for a Python service.

Pick exactly one category: {", ".join(CATEGORIES)}

Always pick the single best category.  Engineers need a definite answer, so
always return confidence "high".

Return ONLY a JSON object:
{{"category": "...", "confidence": "high", "action": "..."}}
"""


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise llm.LLMError(f"No JSON object in response:\n{text}")
        return json.loads(match.group(0))


def normalize(raw: dict) -> dict:
    """Coerce a model reply into the shape callers expect."""
    category = raw.get("category", "infra")
    if category not in CATEGORIES:
        category = "infra"
    return {
        "category": category,
        "confidence": "high",
        "action": raw.get("action") or DEFAULT_ACTIONS[category],
    }


def classify(log_text: str) -> dict:
    """Given the text of a CI failure log, say what kind of failure it is."""
    try:
        reply = llm.complete(
            f"<log>\n{log_text}\n</log>\n\nTriage this failure.",
            system=SYSTEM,
            max_tokens=400,
            temperature=0,
        )
        return normalize(_extract_json(reply))
    except Exception:
        return normalize({"category": "infra"})


def main(argv: list[str]) -> int:
    paths = [pathlib.Path(a) for a in argv] or sorted(pathlib.Path("logs").glob("*.log"))
    for path in paths:
        out = classify(path.read_text())
        print(f"{path.name:20} {out['category']:12} {out['confidence']:6} {out['action']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
