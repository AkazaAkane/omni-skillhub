# PR qualification record

Copy the block below into the PR description and fill it from measurements taken during phases 1–4. Keep raw experimental detail out of production code — the record lives in the PR, not in the repository.

```markdown
## Prefill CUDA Graph qualification

Model:
Model revision:
SGLang-Omni revision:
SGLang version:
GPU:
Backend: breakable
Capture budget / buckets:

### Runtime path
- capture:
- real replay:
- eager fallback:

### Prefill token distribution
- min / median / p95 / max:
- fraction above capture budget:

### Correctness
- deterministic comparison:
- established quality metric:
- boundary cases:

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
- startup delta:
- allocated/reserved delta:
- remaining headroom:

### Decision
DEFAULT ON / OPT-IN / NO-GO

Reason:
Rollback:
```

For a NO-GO or NOT YET QUALIFIED result, fill in whatever was measured and state the blocker under Reason. A partial record still saves the next person the phases you already ran.
