# Bucket Policy, Replay Proof, and Boundary Routing

## 1. Measure the real scheduled prefill shape

Do not choose buckets from raw prompt length, audio duration, processor estimates, or theoretical context length.

Collect actual prefill token counts after:

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

Also report enough distribution detail to explain important clusters and the selected capture budget.

## 2. Choose a qualified capture budget

Prefer the shared ladder:

```python
build_default_prefill_cuda_graph_bs(qualified_capture_budget)
```

The capture budget does not need to equal the maximum legal prefill. Larger shapes may remain eager.

Use a custom bucket list only when measured workload evidence shows the shared ladder is materially worse. Include that evidence in the PR.

A custom ladder is not justified merely because it captures faster or uses slightly less memory if end-to-end performance is indistinguishable within run variance. MOSS-TD is the merged precedent for favoring the shared policy when a smaller custom ladder showed no material serving benefit.

## 3. Respect effective deployment caps

Bucket policy must remain coherent with effective values such as:

- `chunked_prefill_size`;
- `max_prefill_tokens`;
- `cuda_graph_max_bs_prefill`;
- `max_total_tokens`;
- resolved context length.

Qwen3-ASR is the precedent for deriving/adjusting the ladder after deployment overrides merge, rather than assuming static defaults are always the effective caps.

Do not silently override an operator-supplied explicit bucket list unless shared policy explicitly defines that precedence.

## 4. Prove real replay

For at least one real request/workload, capture evidence of:

```text
capture success
admission reached
can_run_cuda_graph == true (or equivalent)
actual replay count > 0
request success
```

Do not report “all buckets captured” as graph coverage. The workload must actually use them.

## 5. Boundary correctness

Test the qualified capture budget around graph/eager routing.

At minimum cover:

```text
inside a normal bucket
largest validated graph shape
just above the graph cap
an eager fallback shape
```

Verify both expected route and successful output.

If radix caching or chunked prefill is part of the supported deployment, include representative cache-hit/chunked shapes.

A fallback is not a failure. It is part of the contract.

Fun-ASR is a good precedent: shapes at and below the qualified cap replayed, shapes immediately above it fell back eagerly, and transcript correctness remained intact.

## 6. Coverage report

For measured workloads report:

```text
eligible prefill forwards or graph batches
graph replays
eager fallbacks
fallback reasons
largest replayed shape
```

If significant traffic falls back because of a padding-factor guard, unsupported state, or capture cap, state it explicitly.

## 7. Configuration safety

When an explicitly named breakable backend bypasses upstream automatic compatibility checks, the shared Omni policy must enforce the missing rules centrally. Do not duplicate those rules inside individual models.

Deployment combinations that were not qualified should remain disabled or be called out explicitly.
