# Phase 4b — Performance, coverage, and cost

Read this when measuring whether enablement is worth it, or when checking a PR's performance claim.

Three measurements, all required before promotion: end-to-end performance, graph coverage, startup/memory cost.

## Performance qualification

Compare graph disabled vs graph enabled with all other settings fixed, preferring the same code revision for both arms.

If the adopter itself adds meaningful model-side code, use three arms:

```text
A = before adopter, eager
B = adopter present, graph disabled
C = adopter present, graph enabled
```

A→B detects adopter overhead. B→C is the primary graph-performance comparison. Skipping A→B lets adopter overhead hide inside an apparent graph win, or make a real graph win look like a wash.

Run at minimum:

- a low-concurrency case, normally c1;
- at least one representative loaded/saturated concurrency;
- additional standard model benchmark concurrencies when inexpensive.

Use the repository's existing benchmark for that model rather than a bespoke harness.

For any performance claim:

- warm the workload consistently;
- use fresh servers where startup state matters;
- run at least 3 measured repeats for noisy throughput measurements;
- measure or estimate eager A/A variance;
- **do not claim an improvement smaller than observed run-to-run noise.**

The A/A number is what makes the delta interpretable. Without it, a 3% improvement is indistinguishable from a quiet machine.

Report model-relevant metrics, normally including:

```text
throughput
mean/p95/p99 latency
TTFT / TTFA / first-token metric where applicable
RTF where applicable
prefill host-wall latency if instrumentation exists
request failures
```

End-to-end performance decides promotion. A faster isolated prefill is useful attribution, but does not by itself justify default-on — prefill can get faster while the end-to-end picture is unchanged because the bottleneck is elsewhere.

## Graph coverage

For each measured workload, report:

```text
eligible prefill forwards
graph replays
eager fallbacks
fallback reasons
largest replayed shape
```

Do not report only that all configured buckets captured. The workload must actually use the graph. Compare observed replay counts against the eligibility you predicted from the phase 2 distribution; a large gap means admission is refusing batches you expected to qualify, and the fallback reasons will say why.

If significant traffic falls back because of the padding-factor guard or the capture cap, state that explicitly. That is a tuning signal, and it also bounds how much of the measured performance delta the graph can possibly explain.

## Startup and memory cost

Measure separately from steady-state request performance:

```text
Prefill CUDA Graph capture time
cold pipeline startup delta
allocated GPU-memory delta
reserved GPU-memory delta
remaining GPU headroom
```

Do not fold capture time into steady-state request throughput — they are different budgets with different operators caring about them.

Check memory **headroom** rather than assuming unchanged KV-token capacity means zero memory cost. Capacity can be unchanged right up until the moment a longer request or a larger batch needs the headroom the graphs consumed.

## Gate

You may proceed to the decision when you have: a performance delta with an A/A noise estimate, coverage counts showing the workload uses the graph, and separately-measured capture time and memory deltas.
