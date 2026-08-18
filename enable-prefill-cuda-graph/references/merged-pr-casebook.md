# Merged PR Casebook

These are precedents, not templates to copy line-for-line. Reuse the lesson that matches the current model.

## PR #1364 — Higgs-TTS: establish the shared integration

Link: https://github.com/sgl-project/sglang-omni/pull/1364

Role in the architecture:

- established the model-agnostic breakable Prefill CUDA Graph enablement layer;
- introduced capability gating and shared bucket policy;
- provided an Omni prefill input transport for runner-composed embeddings;
- added startup attestation and eager rollback/fallback behavior;
- made Higgs-TTS the first default-on adopter.

Validation lessons:

- successful capture is not enough; prove real replay;
- padded replay may be numerically different without being semantically wrong;
- localize the difference, then run the full model quality gate;
- test shape edges and over-cap eager fallback;
- measure capture time and memory separately.

Do not repeat #1364's shared infrastructure in later model PRs. Later adopters should reuse it.

## PR #1379 — MOSS-Transcribe-Diarize: thin direct adopter

Link: https://github.com/sgl-project/sglang-omni/pull/1379

Pattern:

- declare compatibility;
- enable breakable backend;
- use shared bucket helper;
- reuse the existing graph path without model-runner surgery.

Validation lessons:

- exact transcript identity can fail because padded capture shape changes numerics;
- exact-shape replay can be used to attribute the difference;
- repeated stability within each arm plus paired CER/cpCER/DER gates can justify acceptance when exact identity is not the model contract;
- a smaller custom ladder is not worth keeping if serving benefit is inside run variance; favor the common policy for consistency.

## PR #1398 — Fun-ASR: minimal direct adopter with explicit boundary evidence

Link: https://github.com/sgl-project/sglang-omni/pull/1398

Pattern:

- the model already reached the upstream-compatible prefill graph path;
- enablement was primarily builder/capability policy plus tests;
- qualified a bounded capture budget while allowing larger prefills to remain eager.

Validation lessons:

- test tokens immediately below/at/above the graph cap;
- report graph vs eager routing and transcript mismatches;
- report actual graph/eager coverage on end-to-end benchmarks;
- distinguish a large host-wall prefill improvement from end-to-end QPS changes that may be within noise.

This is the preferred target shape for a simple new adopter.

## PR #1458 — Qwen3-ASR: direct adopter plus one semantic seam repair

Link: https://github.com/sgl-project/sglang-omni/pull/1458

Pattern:

- the LM body could use the shared graph directly;
- graph replay bypassed `forward()` logic that cast positions to the dtype required by a fused kernel;
- the repair moved the dtype normalization to the fused-kernel preparation boundary shared by eager and graph execution;
- bucket policy was derived from effective post-override limits;
- shared policy enforced incompatibility checks that an explicitly selected backend would otherwise skip.

Validation lessons:

- audit exactly what the captured module bypasses;
- fix missing invariants at the narrowest common execution boundary;
- keep generic compatibility validation in shared policy, not model code;
- deployment overrides must not create an impossible bucket/cap configuration.

## PR #1381 — Qwen3-Omni: bounded input adapter, opt-in

Link: https://github.com/sgl-project/sglang-omni/pull/1381

Pattern:

- runner-composed embeddings required `OmniPrefillInputs`;
- whole-batch eligibility was validated before opting into the sidecar path;
- unsupported/ambiguous modality and state combinations failed closed to inherited eager execution;
- SGLang retained graph admission, buckets, padding, replay, and shape fallback;
- support scope was limited to qualified text-output paths.

Benchmark design lesson:

```text
A = pre-adopter eager
B = adopter present, graph disabled
C = same adopter code, graph enabled
```

A→B isolates adopter overhead; B→C isolates graph benefit.

Promotion lesson:

Substantial throughput gains do not automatically imply default-on. Qwen3-Omni kept the feature opt-in because high-concurrency text TTFT could regress and startup/VRAM cost was significant. This is the key precedent for treating promotion as a workload tradeoff rather than a binary correctness question.

## How to use the casebook

When reviewing a new PR, identify the closest precedent:

```text
Already upstream-compatible?        -> Fun-ASR / MOSS-TD
One eager-vs-replay semantic seam?  -> Qwen3-ASR
Runner-composed bounded inputs?     -> Qwen3-Omni
Need new shared infrastructure?     -> first prove #1364 has a real reusable gap
```

A new model PR should normally look **smaller** than the foundational #1364 PR.
