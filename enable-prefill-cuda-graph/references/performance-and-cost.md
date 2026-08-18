# Performance, Coverage, Startup, and Memory Qualification

## 1. Use the right comparison

Compare graph disabled vs graph enabled with all other settings fixed.

Prefer the same code revision for both arms.

If the adopter itself adds meaningful model-side code, use:

```text
A = before adopter, eager
B = adopter present, graph disabled
C = adopter present, graph enabled
```

Use A→B to detect adapter/model-code overhead.
Use B→C as the primary graph-performance comparison.

Qwen3-Omni is the canonical merged precedent for this A/B/C design.

## 2. Required concurrencies

Run:

- low concurrency, normally c1;
- at least one representative loaded/saturated concurrency;
- standard model benchmark concurrencies when inexpensive.

Use the repository's established benchmark for that model.

## 3. Control noise

For performance claims:

- keep code/config/data fixed between arms;
- warm the workload consistently;
- use fresh servers where startup state matters;
- run at least 3 measured repeats for noisy throughput tests;
- measure or estimate eager A/A variance;
- rotate arm order when practical;
- do not claim an improvement smaller than run-to-run noise.

A faster isolated prefill is useful attribution, but end-to-end serving decides promotion.

## 4. Report serving metrics

Normally include:

```text
throughput
mean latency
p95/p99 latency
TTFT / TTFA / first-token metric where applicable
RTF where applicable
prefill host-wall latency when instrumented
request failures
```

For a throughput improvement, also check whether an important first-token latency metric regresses under realistic concurrency.

Qwen3-Omni is the key precedent: throughput improved substantially, but pure-text TTFT regressed at higher concurrency, so the feature remained opt-in rather than becoming universal default-on.

## 5. Report graph coverage on the measured workload

For every performance arm that claims a graph benefit, report:

```text
graph replays or graph batches
eager fallbacks
fallback reasons
largest replayed shape
```

Without coverage, a benchmark can accidentally measure mostly eager traffic.

## 6. Separate startup cost from steady state

Measure separately:

```text
Prefill CUDA Graph capture time
cold pipeline startup delta
allocated GPU-memory delta
reserved GPU-memory delta
remaining GPU headroom
```

Do not include one-time capture in steady-state request throughput.

Do not infer “no memory cost” from unchanged KV token capacity. Check actual headroom.

## 7. Promotion-oriented interpretation

### Strong default-on signal

- repeatable end-to-end throughput/latency benefit beyond noise;
- no important supported latency regression;
- good replay coverage on representative workloads;
- acceptable capture/startup/memory cost.

### Opt-in signal

- meaningful throughput benefit but workload-dependent latency tradeoff;
- significant startup/VRAM cost;
- only a subset of modalities/output paths qualified;
- benefit is clear for some deployments but not universally desirable.

### No-go signal

- end-to-end regression;
- gain inside noise while capture/memory cost is meaningful;
- low real replay coverage makes the optimization ineffective;
- correctness requires disproportionate infrastructure.
