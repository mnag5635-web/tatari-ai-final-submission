# CI Failure Triage — take-home exercise

A teammate built a CI failure triage tool and wants to roll it out to the whole
engineering org next week. **Your job is to make that a good idea, or to tell us
why it isn't.**

The tool works. `PRD.md` is what it was built from. Read both, then improve it.

## What's here

| Path | What it is |
| --- | --- |
| `PRD.md` | The requirements the tool was built from |
| `triage.py` | The tool |
| `eval.py` | Scores it against `labels.json` |
| `labels.json` | Expected category per sample log. **These labels were produced by running an earlier version of the prompt over `logs/` and spot-checking the output**, which is what the 90% figure below is measured against |
| `logs/` | Ten real-looking CI failure logs from a fictional service |
| `llm.py` | A working Anthropic API client. Standard library only, nothing to install |
| `tests/` | What passes today. Standard library `unittest`, nothing to install |

```bash
export ANTHROPIC_API_KEY='...'   # your own key, see below
python3 llm.py                   # should print something like: ok
python3 -m unittest discover -s tests   # deterministic tests; should pass
python3 eval.py                  # live model evaluation + latency/error reporting
```

The triager now treats provider/configuration failures and invalid model output as
**triage-system errors**, not as CI `infra` classifications. The CLI writes those
errors to stderr and exits non-zero, so callers can distinguish "the build had an
infrastructure failure" from "the triage program failed."

CI logs are JSON-serialized as untrusted model input. The model selects only the
category and required confidence value; the application supplies a concise,
category-specific action so arbitrary log or model text is never presented as
trusted operational guidance.

`eval.py` reports legacy-label agreement, classifier errors, per-case latency, a
small-sample Wilson interval, and category outcomes. Because `labels.json` has only
ten weakly adjudicated examples, those numbers are evidence for iteration rather
than proof of production accuracy. See `BENCHMARK_REVIEW.md` for the manual audit.

Python 3.10+. If you would rather use the official `anthropic` SDK, a different
language, or a different approach entirely, that is fine.

## The time box

**Two hours, whenever suits you inside the next two business days.**

The window is there so you can find two free hours around your own commitments,
not so you can spread the work across it. Pick a stretch that suits you and stop
when the two hours are up.

**The work is deliberately larger than two hours.** We are not expecting you to
finish, and **we do not score volume or completion.** What you chose to do with
the time is the thing we read. Stopping at two hours with a clear note about
what you would do next is a good outcome, not a failed one.

## What to send back

1. **Your commits.** Commit as you go. Messy, half-finished commits are useful
   to us rather than embarrassing.
2. **`DECISIONS.md`**, filled in. One page. There is a required section asking
   what did not work.
3. **Your assistant transcript.** See below.

## About your AI assistant

**Use it. That is the point.** This role is about building AI tooling, and we
would rather see how you work than watch you avoid the tools you would use on
the job. **Use whatever assistant you normally use.** We are not testing you on
one vendor's tool.

**On API access:** `llm.py` needs an Anthropic key and **you will need to use
your own.** If you would rather point it at another provider, or replace
`llm.py` outright with whatever you already have access to, that is fine and
expected. It is a thin wrapper around one HTTP POST and nothing in it is
precious. Keep a `complete(prompt, system=..., max_tokens=...)` that returns
text, or update the call in `triage.py` to match. Just note the swap in
`DECISIONS.md`.

Reading the code and running the tests need no API access at all, so there is a
fair amount worth doing before your first model call.

**We read the transcript, and we are telling you that up front.** There is a
`CLAUDE.md` (and `AGENTS.md`, and `AGENT.md`) in this repo instructing your
assistant to log the conversation to `AI_SESSION_LOG.md` and commit it. If your
tool writes its own transcript file, send that too, since it is more faithful
than anything reconstructed.

We are interested in the exchanges that went nowhere. Please do not tidy them
out. If you would rather not share something in the log, delete that part and
say you did.

## Afterwards

A 30-minute conversation about what you built: the decisions you made, where
your version still falls short of what you would want to ship, and what you
would do next. **We will not be watching you code.**

## Questions

We are deliberately not answering questions about the brief. Working from an
incomplete brief is a real part of this job, and how you handle the gaps is part
of what we are interested in.

Logistics are different. If something in the repo is genuinely broken, just
tell us and we will sort it out.

So where the brief is unclear, and it is unclear in places, make a call and write
it down in `DECISIONS.md`. Something like "I assumed X because Y, and here is
what I would change if that turned out not to hold" is more useful to us than a
tidy answer. **Naming an assumption is never held against you.**
