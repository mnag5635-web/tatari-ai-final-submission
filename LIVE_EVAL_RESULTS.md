# Live evaluation results

Credential-free evidence from the Anthropic evaluation performed on
2026-09-11. The model was `claude-haiku-4-5`; each run invoked `eval.py` over
the ten unchanged `logs/*.log` fixtures in sorted order. The supplied API key
required a workspace header, which was injected only in the evaluation process.
Neither credential nor workspace metadata was written to this repository.

Per-case latency is printed by `eval.py` to the nearest 0.1 ms. Per-run
summaries were calculated by the evaluator from the original unrounded timers,
so recomputing a run median from these rounded rows can differ by 0.1 ms.

## Run 1

| Log | Expected | Predicted | Latency | Outcome |
| --- | --- | --- | ---: | --- |
| `build-4817.log` | `flaky` | `flaky` | 8,462.0 ms | match |
| `build-4823.log` | `dependency` | `dependency` | 7,672.6 ms | match |
| `build-4831.log` | `infra` | `infra` | 7,405.6 ms | match |
| `build-4840.log` | `lint` | `lint` | 7,830.0 ms | match |
| `build-4852.log` | `product_bug` | `product_bug` | 9,297.1 ms | match |
| `build-4866.log` | `flaky` | `flaky` | 15,023.2 ms | match |
| `build-4871.log` | `product_bug` | `product_bug` | 9,906.0 ms | match |
| `build-4902.log` | `product_bug` | `product_bug` | 7,885.8 ms | match |
| `build-4915.log` | `infra` | `infra` | 8,221.1 ms | match |
| `build-4928.log` | `flaky` | `product_bug` | 8,660.0 ms | disagreement |

Summary: 9/10 legacy-label agreement, 0/10 system errors; median 8,341.6
ms, p95 15,023.2 ms, max 15,023.2 ms.

## Run 2

| Log | Expected | Predicted | Latency | Outcome |
| --- | --- | --- | ---: | --- |
| `build-4817.log` | `flaky` | `flaky` | 8,487.0 ms | match |
| `build-4823.log` | `dependency` | `dependency` | 8,023.3 ms | match |
| `build-4831.log` | `infra` | `infra` | 7,817.0 ms | match |
| `build-4840.log` | `lint` | `lint` | 7,945.0 ms | match |
| `build-4852.log` | `product_bug` | `product_bug` | 9,273.3 ms | match |
| `build-4866.log` | `flaky` | `flaky` | 12,480.1 ms | match |
| `build-4871.log` | `product_bug` | `product_bug` | 10,432.4 ms | match |
| `build-4902.log` | `product_bug` | `product_bug` | 7,304.6 ms | match |
| `build-4915.log` | `infra` | `infra` | 9,495.4 ms | match |
| `build-4928.log` | `flaky` | `product_bug` | 8,874.9 ms | disagreement |

Summary: 9/10 legacy-label agreement, 0/10 system errors; median 8,680.9
ms, p95 12,480.1 ms, max 12,480.1 ms.

## Run 3

| Log | Expected | Predicted | Latency | Outcome |
| --- | --- | --- | ---: | --- |
| `build-4817.log` | `flaky` | `flaky` | 7,691.3 ms | match |
| `build-4823.log` | `dependency` | `dependency` | 9,507.2 ms | match |
| `build-4831.log` | `infra` | `infra` | 9,035.8 ms | match |
| `build-4840.log` | `lint` | `lint` | 29,921.5 ms | match |
| `build-4852.log` | `product_bug` | `product_bug` | 14,223.8 ms | match |
| `build-4866.log` | `flaky` | `flaky` | 13,093.7 ms | match |
| `build-4871.log` | `product_bug` | `product_bug` | 10,063.3 ms | match |
| `build-4902.log` | `product_bug` | `product_bug` | 7,703.0 ms | match |
| `build-4915.log` | `infra` | `infra` | 8,152.3 ms | match |
| `build-4928.log` | `flaky` | `product_bug` | 8,454.0 ms | disagreement |

Summary: 9/10 legacy-label agreement, 0/10 system errors; median 9,271.5
ms, p95 29,921.5 ms, max 29,921.5 ms.

## Aggregate

- 27/30 legacy-label matches; 0/30 classifier/system errors.
- All ten predictions were identical across the three runs.
- `build-4928.log` was the sole disagreement in every run.
- From the 30 published rounded observations: median 8,573.5 ms, nearest-rank
  p95 15,023.2 ms, max 29,921.5 ms.
