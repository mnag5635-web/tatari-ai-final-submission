# Decisions

## What I assumed

- The five categories are fixed. `confidence: "high"` is an API contract for successful classifications, not calibrated probability.
- Provider, configuration, parsing, and program failures are triage-system failures; they must not be mislabeled as CI failures.
- “Fast enough” has no SLA, so I report measured latency rather than inventing a threshold.
- `labels.json` is a regression artifact, not perfect ground truth: its labels came from an earlier prompt plus spot checks.

## What I changed

- **Fail closed:** invalid model output and provider failures now raise `TriageError`; the CLI explains the error on stderr and exits non-zero instead of manufacturing `infra / high`.
- **Protect the trust boundary:** the log is JSON-serialized as untrusted evidence, while strict parsing rejects wrappers, arrays, duplicate keys, extra values, unsupported categories, and invalid confidence.
- **Own remediation in code:** the model selects only category and confidence; the application supplies a deterministic, category-specific action rather than exposing model-generated commands.
- **Make evaluation useful:** `eval.py` separates system errors from label disagreements and reports per-case results, latency, category outcomes, and a Wilson interval. `BENCHMARK_REVIEW.md` documents manual review without rewriting labels.

## What I deliberately did not change

I did not edit `labels.json` to force 100%. I consider `build-4928.log` a plausible `product_bug`: the API promises sorted output while the SQL omits `ORDER BY`. I also avoided a rules engine, second provider, SDK, UI, Slack integration, database, and Docker layer; none addresses the highest-risk failure mode. Credentials and workspace headers remained runtime-only.

## How I know it is better

The deterministic suite grew from **5/5 to 30/30 passing**, covering strict parsing, provider failures, adversarial log serialization, safe actions, bad input, CLI exits, and evaluation error accounting. Without an API key, the CLI now exits **1** with a clear configuration error; previously it returned `infra / high`.

Three live `claude-haiku-4-5` runs produced identical predictions, **9/10 legacy-label agreement**, and **0/30 system errors**; `build-4928` was the sole disagreement. Across 30 calls, latency was **8.57 s median, 15.02 s p95, and 29.92 s max**. This supports repeatability, not production accuracy or an unspecified latency SLA.

## What did not work

The first smoke call failed HTTP 400 because the key required a workspace header; an authorized workspace-list request then failed HTTP 403 because the key lacked admin permission. No fixture was sent until the user supplied the workspace ID. Later review exposed permissive wrapper and duplicate-key parsing; failing regression tests reproduced both gaps before the parser was fixed. Diff inspection also caught a stray README fence, and the test suite caught one patch that had not persisted.

## What I would do next

Create a larger human-adjudicated dataset with annotation guidance and inter-rater agreement; define accuracy, latency, cost, and action-quality thresholds; add input budgets, approved secret/PII redaction, and adversarial cases; then shadow-deploy and adjudicate real disagreements before automation.

**Recommendation:** limited shadow pilot, not authoritative organization-wide rollout next week. The implementation is safer and repeatable, but ten weakly adjudicated examples are insufficient evidence.
