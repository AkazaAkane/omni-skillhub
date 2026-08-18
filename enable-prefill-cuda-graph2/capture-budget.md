# Phase 2 — Capture budget and buckets

Read this when choosing what shapes to capture, or when reviewing a hand-written bucket ladder.

## Measure the scheduled prefill shape

Bucket selection is driven by the actual scheduled prefill shape. It is **not** driven by raw prompt length, audio duration, processor estimates, or theoretical context length — every one of those diverges from what the scheduler hands to the graph runner.

Collect actual prefill token counts *after* all of:

- preprocessing;
- Omni request construction;
- multimodal expansion;
- radix-cache effects;
- chunking;
- scheduler batching.

Report at least:

```text
min
median
p95
max
```

plus enough distribution detail to see important clusters. Multi-modal and ASR workloads are frequently multi-modal in the statistical sense too — a single p95 hides a bimodal shape, and a ladder tuned to the mean can miss both peaks.

## Choose a qualified capture budget

Prefer the shared ladder:

```python
build_default_prefill_cuda_graph_bs(qualified_capture_budget)
```

The capture budget does not need to equal the model's maximum legal prefill. Prefills above the qualified budget may remain eager — that is a supported outcome, not a gap to close. Capturing shapes the workload never produces costs startup time and GPU memory for nothing.

Use a custom bucket list **only** when measured workload evidence shows the shared ladder is materially worse for this model, and include that evidence in the PR. A hand-maintained ladder is a recurring maintenance cost that someone else inherits.

## Gate

You may leave phase 2 when the capture budget traces to a measured distribution, and you can say which fraction of real traffic falls above it.

Carry the distribution numbers forward — phase 4 coverage (`performance.md`) compares predicted eligibility against observed replay counts, and a large gap between them means admission is refusing batches you expected to be eligible.
