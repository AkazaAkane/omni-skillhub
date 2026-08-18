# Promotion Decision and Required PR Evidence

Choose exactly one outcome after correctness and performance qualification.

## DEFAULT ON

Use when:

- replay is correct for the declared scope;
- established quality gates pass;
- end-to-end performance improves materially and repeatably beyond measured noise;
- no important supported workload has an unacceptable latency regression;
- capture/startup/memory cost is acceptable;
- eager rollback works.

## OPT-IN

Use when correctness is established but the tradeoff is deployment-dependent, for example:

- throughput improves but an important latency metric regresses;
- startup or graph memory cost is large;
- only some modalities/output paths are qualified;
- evidence is promising but insufficient for a universal default.

Keep eager as default and document the qualified scope.

## NO-GO

Use when:

- correctness fails;
- end-to-end performance regresses;
- apparent gains are inside measurement noise with meaningful cost;
- startup/memory cost is disproportionate;
- required implementation would duplicate shared graph infrastructure.

A no-go is a valid result. Record the reason instead of adding complexity to force adoption.

## Required PR evidence

Use a compact qualification record like this:

```markdown
## Prefill CUDA Graph qualification

Model:
Model revision:
SGLang-Omni revision:
SGLang version:
GPU:
Backend: breakable
Capture budget / buckets:
Qualified scope:

### Runtime path
- capture:
- real replay:
- eager fallback:

### Correctness
- deterministic comparison:
- exact mismatches and attribution:
- established quality metric:
- boundary cases:
- unsupported-scope fallback:

### Performance
| Concurrency | Eager | Graph | Delta |
|---|---:|---:|---:|
| ... | ... | ... | ... |

A/A noise or repeat spread:

### Coverage
- graph replay:
- eager fallback:
- fallback reasons:
- largest replayed shape:

### Startup / memory
- capture time:
- cold startup delta:
- allocated/reserved delta:
- remaining headroom:

### Decision
DEFAULT ON / OPT-IN / NO-GO

Reason:
Rollback:
```

## Review checklist

A reviewer should reject or request more evidence when any of these are missing:

- capture is shown but replay is not;
- bucket choice is based on raw input length instead of scheduled prefill shape;
- graph/eager boundary is untested;
- a mismatch is waved away without attribution;
- only a microbenchmark is provided for a default-on claim;
- no A/A noise/repeat information for a small performance gain;
- graph coverage is omitted;
- startup/memory cost is omitted;
- model code duplicates shared graph admission/fallback/bucket logic;
- rollback is not demonstrated;
- qualified modality/output scope is ambiguous.

## Final minimality check

Before merging, inspect the diff and ask:

```text
Could this model use the shared implementation with fewer changes?
```

Keep raw experiment machinery out of production code unless it is reusable runtime observability or a focused regression test.
