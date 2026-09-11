# Decisions

## What I assumed

The categories are fixed, and `confidence: "high"` is a product-contract value, not calibrated probability. Classifier failures are system failures, not CI `infra`. “Fast enough” has no SLA, so I report latency rather than invent a threshold. I treat the weakly adjudicated `labels.json` as a regression artifact, not unquestionable ground truth.

## What I changed

- **Fail closed:** provider/invalid-output failures raise `TriageError`; the CLI writes to stderr and exits non-zero instead of manufacturing `infra / high`.
- **Protect the boundary:** logs are JSON-serialized as untrusted evidence; strict parsing rejects malformed or ambiguous responses.
- **Own remediation:** the model selects category/confidence; code supplies stable category actions rather than potentially hallucinated commands.
- **Improve evaluation:** system errors are separate from label disagreements; reports include per-case outcomes, latency, category counts, and a Wilson interval. `BENCHMARK_REVIEW.md` records manual review.

## What I deliberately did not change

I did not edit `labels.json` to force 100%. `build-4928.log` is plausibly `product_bug`: the API promises sorted output while SQL omits `ORDER BY`. I avoided a rules engine, second provider, UI, Slack integration, database, and Docker; none addressed the highest risk within the time box. Credentials remained runtime-only.

## How I know it is better

The deterministic suite grew from **5 to 30 passing tests**, covering strict parsing, provider failures, adversarial input, safe actions, CLI exits, and evaluation error accounting. A missing key now exits **1**, not with a false classification.

Three live `claude-haiku-4-5` runs produced identical predictions, **27/30 legacy-label matches**, and **0/30 system errors**; `build-4928` was the sole disagreement. Latency was **8.57 s median, 15.02 s p95, and 29.92 s max**. This supports repeatability, not production accuracy or an undefined latency SLO.

At current Haiku 4.5 [list pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) (**$1/M input, $5/M output**), observed prompt size suggests **~$0.001/build**: roughly **$10/day at 10k builds, $100 at 100k, or $1k at 1M**, before retries/caching. Production budgeting must use recorded token usage and build volume.

## What did not work

The first smoke call failed HTTP 400 because the key required a workspace header; listing workspaces failed HTTP 403. No fixture was sent until the ID was supplied. Regression tests later exposed permissive wrapper/duplicate-key parsing, and verification caught an unpersisted patch.

## What I would do next

Build a larger human-adjudicated dataset with inter-rater agreement; define accuracy, latency, cost, and action-quality gates; add input budgets, approved secret/PII redaction, and adversarial cases; then shadow-deploy and adjudicate disagreements.

**Recommendation:** limited shadow pilot, not authoritative organization-wide rollout next week. The implementation is safer and repeatable, but ten weakly adjudicated examples are insufficient evidence.
