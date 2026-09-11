# CI Failure Triage Assistant

## Background

When a CI build fails, somebody reads the log and decides what happened before
anything else can proceed. That reading step is repetitive and we would like to
automate it.

## What we want

A command-line tool that takes a CI failure log and returns a category, a
confidence, and a suggested next action.

## Requirements

1. Accepts the text of a CI failure log and returns a structured result.
2. Every log receives exactly one category, at high confidence. Engineers will
   not act on a maybe.
3. Fast enough that we could run it on every build.
4. Someone other than the author should be able to run it and understand the
   output.

## Out of scope

Fixing the failures. Posting to Slack. A web interface.

## Where it stands today

Implemented in `triage.py`. `eval.py` scores it against `labels.json`:
**90% accurate, 9 of 10** on the sample logs in `logs/`.

Ready to roll out to the whole engineering org next week.
