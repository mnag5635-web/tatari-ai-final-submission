"""Minimal Anthropic Messages API client.

Standard library only, so there is nothing to install. It is a thin wrapper
around one HTTP POST -- if you would rather use the official `anthropic` SDK or
anything else, go ahead. Nothing here is precious.

Requires your own ANTHROPIC_API_KEY in the environment. If you would rather use
a different provider, replacing this module is expected rather than discouraged.
"""

from __future__ import annotations

import json
import math
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"

# A burst of requests can come back as a 429. These retries take care of the
# ordinary case for you.
MAX_ATTEMPTS = 3
MAX_RETRY_WAIT = 30.0
# Rate limits and request timeouts, plus every 5xx (the API sends 529 when it
# is overloaded). Anything else is a real error and retrying only hides it.
RETRY_STATUSES = frozenset({408, 429, 529})

# Haiku 4.5 is fast and cheap, which matters when you are iterating in a
# two-hour time box. Swap this for "claude-sonnet-5" or "claude-opus-5" if you
# want a more capable model; the request shape is identical.
DEFAULT_MODEL = "claude-haiku-4-5"


class LLMError(RuntimeError):
    """Raised when the API call fails or returns something unusable."""


def complete(
    prompt: str,
    *,
    system: str | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
    **extra: object,
) -> str:
    """Send `prompt` to the model and return its text response.

    Args:
        prompt: The user message.
        system: Optional system prompt.
        model: Model id. See DEFAULT_MODEL above.
        max_tokens: Hard cap on response length.
        **extra: Any other top-level request field, passed through untouched
            (for example output_config=... or tools=...). See
            https://platform.claude.com/docs/en/api/messages

    Returns:
        The concatenated text of the response.

    Raises:
        LLMError: on a missing key, an HTTP error, or a response with no text.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMError(
            "ANTHROPIC_API_KEY is not set.\n"
            "This module needs your own Anthropic key. Export it and try again:\n"
            "    export ANTHROPIC_API_KEY='...'\n"
            "Or replace this module with a client for whatever you already use."
        )

    payload: dict[str, object] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system is not None:
        payload["system"] = system
    payload.update(extra)

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": API_VERSION,
            "content-type": "application/json",
        },
        method="POST",
    )

    body = _send(request)

    if body.get("stop_reason") == "refusal":
        raise LLMError("The model declined to answer this request.")

    text = "".join(
        block.get("text", "")
        for block in body.get("content", [])
        if block.get("type") == "text"
    )
    if not text:
        raise LLMError(f"No text in response. Full body:\n{json.dumps(body, indent=2)}")
    return text


def _send(request: urllib.request.Request) -> dict:
    """POST the request, retrying the transient failures. Returns the parsed body."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                if not _is_retryable(exc.code) or attempt == MAX_ATTEMPTS:
                    detail = exc.read().decode("utf-8", errors="replace")
                    raise LLMError(f"API returned HTTP {exc.code}: {detail}") from exc
                delay = _retry_after(exc, attempt)
            finally:
                exc.close()
            time.sleep(delay)
        except urllib.error.URLError as exc:
            raise LLMError(f"Could not reach the API: {exc.reason}") from exc
    raise LLMError("Ran out of retries.")  # unreachable, here to satisfy the reader


def _is_retryable(status: int) -> bool:
    """Whether an HTTP status is worth trying again."""
    return status in RETRY_STATUSES or 500 <= status < 600


def _retry_after(exc: urllib.error.HTTPError, attempt: int) -> float:
    """How long to wait before retrying. The server's advice wins if it gave any.

    Retry-After is either a number of seconds or an HTTP date, and it can also
    be nonsense. Anything we cannot read as a sane delay falls back to the
    usual backoff.
    """
    header = exc.headers.get("retry-after") if exc.headers else None
    if header:
        try:
            seconds = float(header)
        except (TypeError, ValueError):
            seconds = _seconds_until(header)
        if seconds is not None and math.isfinite(seconds) and seconds >= 0:
            return min(seconds, MAX_RETRY_WAIT)
    return min(2.0**attempt, MAX_RETRY_WAIT)


def _seconds_until(http_date: str) -> float | None:
    """Turn an HTTP-date Retry-After into a delay, or None if it is not one."""
    try:
        when = parsedate_to_datetime(http_date)
    except (TypeError, ValueError):
        return None
    if when is None:
        return None
    if when.tzinfo is None:  # a date with no zone is GMT, per the spec
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())


if __name__ == "__main__":
    # Smoke test: python3 llm.py
    print(complete("Reply with exactly: ok", max_tokens=16))
