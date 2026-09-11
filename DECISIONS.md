# Decisions

## What I assumed

- The five categories are fixed for this exercise. I improved their boundaries instead of inventing a new taxonomy.
- `confidence: "high"` is a product/API contract, not calibrated probability. I preserved it for successful classifications rather than silently adding medium/low values.
- The requirement that every CI log receive one category applies to a valid, successfully processed log; provider/configuration/parser/program failures are triage-system failures and must not be disguised as build classifications.
- “Fast enough” has no numerical SLA in the PRD. I therefore report observed latency when a real model can be called rather than inventing a threshold.
- `labels.json` is a regression artifact, not perfect ground truth, because the README says its labels came from an earlier LLM prompt plus spot checks.

## What I changed

1. **Fail closed instead of manufacturing `infra`.** Provider failures, malformed model output, unsupported categories, and invalid confidence now raise an explicit `TriageError`. The CLI writes the failure to stderr and exits non-zero.
2. **Separated untrusted evidence from instructions.** CI logs are JSON-serialized in a `ci_log` field, including delimiter-like text. The prompt explicitly treats every character in that field as evidence rather than instructions.
3. **Kept remediation application-owned.** The model returns only category and contract confidence. After strict validation, the application selects a concise category-specific action, so arbitrary model-generated commands are never exposed as trusted guidance.
4. **Made evaluation decision-useful.** `eval.py` reports per-case outcomes, classifier errors separately from disagreements, latency, category outcomes, and a Wilson interval for completed legacy-label agreement. `BENCHMARK_REVIEW.md` records my manual read of all ten fixtures without changing labels.

## What I deliberately did not change

- I did **not** edit `labels.json` to chase 100%. In particular, I think `build-4928.log` is better described as `product_bug`: the API promises sorted output while the SQL explicitly has no `ORDER BY`.
- I did not commit workspace-specific credentials or headers to `llm.py`; the live evaluation supplied its required workspace header only in the evaluation process.
- I did not add a rules engine, second model/provider, SDK dependency, web UI, Slack integration, database, or Docker layer. Those would add surface area without addressing the highest-risk failure mode first.
- I did not claim confidence calibration or production accuracy from ten weakly adjudicated examples.

## How I know it is better

- Baseline deterministic suite: **5/5 passing**.
- Final deterministic suite: **26/26 passing**, covering validation, JSON parsing, provider failures, malformed replies, unsupported categories, adversarial log serialization, deterministic safe actions, invalid UTF-8 input, CLI exit behavior, and evaluation error accounting.
- A real CLI run with no API key now exits **1** with an understandable configuration error; the previous code would have returned `infra / high`.
- The benchmark is now explicit about provenance and uncertainty, and manual review identifies the `build-4928` label disagreement instead of hiding it.
- Three live `claude-haiku-4-5` runs completed with **9/10 legacy-label agreement and 0/10 system errors each**. All ten predictions were identical across runs; `build-4928` was consistently the sole disagreement.
- Across 30 live calls, observed latency was **8,573.5 ms median, 15,023.2 ms p95, and 29,921.5 ms max**. This is measured evidence, not an invented SLA.

## What did not work

- The first live smoke request failed with HTTP 400 because the supplied API key required a workspace header. No fixture log was sent in that attempt.
- An authorized read-only workspace-list request then failed with HTTP 403 because the key lacked administrative listing permission. The evaluation proceeded only after the user supplied the workspace ID; the header was injected in memory and no credential was committed.
- My first README patch accidentally left a stray Markdown code fence. Immediate diff inspection caught it and I removed it before committing; I am recording it here rather than presenting a perfectly cleaned-up process.
- One patch-interface attempt appeared successful but did not persist across tool calls. The failing tests exposed the rollback; I repeated the red/green cycle using the persistent patch command.

## What I would do next

1. Build a substantially larger human-adjudicated dataset with written annotation guidance and inter-rater agreement.
2. Run this version against that set repeatedly to measure category-specific errors, real latency/cost, and action usefulness; then establish explicit rollout thresholds.
3. Shadow-deploy predictions as non-blocking CI metadata, collect engineer feedback, and adjudicate disagreements before any automated action.
4. Add adversarial log/prompt-injection cases and monitor drift from real CI traffic.
5. Establish an input budget plus organization-approved secret/PII redaction before sending real CI logs to an external provider.

**Rollout recommendation:** do not roll this out organization-wide as an authoritative classifier next week. The implementation is materially safer and more testable, but the evidence base is too small and weakly labeled. Shadow deployment or a limited pilot is justified; full rollout is not yet justified.
