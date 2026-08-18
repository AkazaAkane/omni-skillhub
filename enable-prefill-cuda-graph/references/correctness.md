# Correctness Qualification

Correctness is a layered investigation, not a single metric.

## 1. Start serial and deterministic

Use deterministic decoding where the model supports it.

Start with c1 comparisons to avoid concurrency-dependent batch composition obscuring graph correctness.

Prefer the strongest stable comparison available:

```text
generated token IDs
codec/action tokens
transcript
waveform bytes / PCM
model-specific quality metric
```

Exact identity is strongest when it is a valid model contract, but it is not universally required.

## 2. Separate semantic bugs from padded-shape numerics

Bucket padding can change GEMM shapes and therefore floating-point kernel selection/numerics.

If padded replay differs from eager:

1. verify repeated runs within each arm are stable where expected;
2. compare exact-shape graph replay with eager if useful for attribution;
3. determine whether the difference comes from padding/batch shape or from missing graph state/semantics;
4. inspect the first divergence when possible;
5. run the model's established full quality evaluation;
6. require the existing quality regression threshold to pass.

Never use an aggregate quality metric to conceal a reproducible semantic bug in the graph path.

## 3. Useful attribution matrix

When output differs, a strong controlled matrix is:

```text
A = eager, exact shape
B = graph, exact shape
C = graph, padded bucket shape
```

Interpretation:

- A != B: likely graph semantic/state bug; investigate before promotion.
- A == B and B != C: likely padded-shape numerical effect; continue attribution and quality qualification.
- all equal: strongest result.

## 4. Merged precedents

### Higgs-TTS

The merged Higgs work showed padded replay was not bit-identical to eager, localized the difference to dense GEMMs, demonstrated exact identity with batch-invariant kernels, and then ran full Seed-TTS quality evaluation. This is the model for proving a numerical difference is benign rather than dismissing it.

### MOSS-Transcribe-Diarize

MOSS-TD observed a small number of exact transcript differences with shared padded buckets. Exact-shape replay matched eager, repeated outputs were stable within arms, and paired CER/cpCER/DER quality checks showed no aggregate regression. This is a valid non-bit-identical qualification because the difference was attributed and the established metrics passed.

### Qwen3-ASR

Qwen3-ASR found a true semantic seam: replay bypassed a required position dtype cast. That was fixed at the common fused-kernel boundary. After the repair, exact transcript comparisons and full WER checks passed.

The lesson: **do not label every mismatch as harmless padding noise; first prove which class of mismatch it is.**

## 5. Scope correctness

For adapters, explicitly test unsupported/ambiguous states and prove they fail closed to eager.

Examples:

- unsupported modalities;
- hidden-state capture paths;
- malformed auxiliary input state;
- official upstream `input_embeds` already present;
- ambiguous cached-prefix state;
- speech-output path when only text-output prefill is qualified.

Whole-batch eligibility should be consistent. Do not partially graph a batch merely to improve coverage.

## 6. Boundary and lifecycle cases

Where relevant, add:

- graph-cap edge cases;
- chunked prefill;
- radix-cache prefix cases;
- abort/disconnect lifecycle;
- fallback then later graph-eligible request;
- rollback to graph-disabled mode.

## 7. Minimum correctness record

A PR should state:

```text
deterministic comparison method
number of samples
exact mismatches, if any
attribution result
established quality metric and threshold
boundary routing results
unsupported-scope fallback results
rollback result
```
