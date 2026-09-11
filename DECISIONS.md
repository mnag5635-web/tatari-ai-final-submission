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
- I did not rewrite `llm.py`; its API-key validation, timeout, and transient retry behavior are adequate for this time box.
- I did not add a rules engine, second model/provider, SDK dependency, web UI, Slack integration, database, or Docker layer. Those would add surface area without addressing the highest-risk failure mode first.
- I did not claim confidence calibration or production accuracy from ten weakly adjudicated examples.

## How I know it is better

- Baseline deterministic suite: **5/5 passing**.
- Final deterministic suite: **26/26 passing**, covering validation, JSON parsing, provider failures, malformed replies, unsupported categories, adversarial log serialization, deterministic safe actions, invalid UTF-8 input, CLI exit behavior, and evaluation error accounting.
- A real CLI run with no API key now exits **1** with an understandable configuration error; the previous code would have returned `infra / high`.
- The benchmark is now explicit about provenance and uncertainty, and manual review identifies the `build-4928` label disagreement instead of hiding it.
- A live Anthropic key is not available in this isolated environment, so I do not claim a new model-agreement or API-latency number.

## What did not work

- Live model evaluation/latency measurement could not run because `ANTHROPIC_API_KEY` is not available here. The controlled no-key evaluation reported **10/10 classifier/configuration errors** rather than fabricated classifications.
- My first README patch accidentally left a stray Markdown code fence. Immediate diff inspection caught it and I removed it before committing; I am recording it here rather than presenting a perfectly cleaned-up process.
- One patch-interface attempt appeared successful but did not persist across tool calls. The failing tests exposed the rollback; I repeated the red/green cycle using the persistent patch command.

## What I would do next

1. Build a substantially larger human-adjudicated dataset with written annotation guidance and inter-rater agreement.
2. Run this version against that set repeatedly to measure category-specific errors, real latency/cost, and action usefulness; then establish explicit rollout thresholds.
3. Shadow-deploy predictions as non-blocking CI metadata, collect engineer feedback, and adjudicate disagreements before any automated action.
4. Add adversarial log/prompt-injection cases and monitor drift from real CI traffic.
5. Establish an input budget plus organization-approved secret/PII redaction before sending real CI logs to an external provider.

**Rollout recommendation:** do not roll this out organization-wide as an authoritative classifier next week. The implementation is materially safer and more testable, but the evidence base is too small and weakly labeled. Shadow deployment or a limited pilot is justified; full rollout is not yet justified.
