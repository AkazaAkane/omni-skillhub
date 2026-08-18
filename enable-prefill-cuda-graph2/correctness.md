# Phase 4a — Correctness qualification

Read this when validating a change, or when a PR reports "output looks the same."

Two parts: boundary routing, then output comparison.

## Boundary routing test

Test the chosen capture budget around its graph/eager boundary. At minimum cover:

```text
inside a normal bucket
largest validated graph shape
just above the graph cap
an eager fallback shape
```

Verify both expected routing **and** successful output for each. If radix caching or chunked prefill is part of the supported deployment, include representative cache-hit and chunked shapes — those produce prefill shapes the naive distribution never shows.

A fallback is not a failure. It is part of the contract. What you are testing is that the boundary routes as designed and that both sides produce correct output.

## Output comparison

Use deterministic decoding where the model supports it. Start with serial c1 comparisons — concurrency-dependent batch composition otherwise obscures whether a difference came from the graph or from batching.

Prefer the strongest stable comparison the model offers:

```text
generated token IDs
codec/action tokens
transcript
waveform bytes / PCM
model-specific quality metric
```

## When padded replay is not bit-identical

Do not universally require bit identity. Bucket padding changes GEMM shapes and therefore floating-point numerics; MOSS-Transcribe-Diarize is the reference case for a correct adopter with padded-shape numerical differences.

When output differs, work through this in order:

1. verify repeated runs within each arm are stable where expected;
2. check exact-shape graph replay against eager, when useful for attribution;
3. identify whether the difference comes from padding/batch shape rather than incorrect graph state;
4. run the model's established full quality evaluation;
5. require the existing quality regression threshold to pass.

Step 3 is the load-bearing one. A padding-induced numerical difference is stable and explicable by shape; a graph state bug is reproducible, shape-independent, and usually gets worse with request count as stale captured state accumulates.

**Never accept an aggregate quality metric to hide a reproducible semantic bug in the graph path.** A WER or MOS that stays within threshold does not mean the graph is correct — it means the metric is not sensitive to the bug you have. If step 1 or 2 shows something reproducible, go back to `graph-semantics.md`.

## Gate

You may leave correctness when boundary routing is verified in all four regions, and output differences are either absent or attributed to padding with the model's established quality gate passing.
