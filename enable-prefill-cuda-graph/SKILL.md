---
name: enable-prefill-cuda-graph
description: Qualify, implement, review, and promote SGLang-Omni breakable Prefill CUDA Graph support for one model. Reuse the shared SGLang/Omni graph path, choose the smallest adopter pattern, validate real replay/correctness/performance/startup cost, and decide DEFAULT ON, OPT-IN, or NO-GO.
---

# Enable Prefill CUDA Graph

Use this skill when:

- enabling Prefill CUDA Graph for an existing SGLang-Omni model;
- qualifying a newly added model for Prefill CUDA Graph;
- reviewing a PR that enables or changes Prefill CUDA Graph;
- deciding DEFAULT ON vs OPT-IN vs NO-GO;
- diagnosing why a model captures but does not replay correctly.

The goal is **not** to make every model use Prefill CUDA Graph. The goal is to determine whether one model can safely and profitably use the existing shared breakable prefill graph path.

## Core rule

Reuse the existing ownership boundary:

```text
model
  └─ declares compatibility or supplies the smallest model-specific adaptation
      ↓
SGLang-Omni shared policy
  └─ validates capability/configuration and wires Omni-specific inputs when needed
      ↓
SGLang PrefillCudaGraphRunner
  ├─ capture
  ├─ admission
  ├─ padding
  ├─ replay
  └─ eager fallback
```

Do not add another generic graph runner, bucket policy, graph/eager dispatcher, or model-local fallback mechanism unless a concrete shared-contract gap has been demonstrated across multiple models.

## How to use this skill

Read only the files needed for the task. Do **not** load every reference by default.

| Task | Read |
|---|---|
| Understand ownership, inspect a model, choose a route | [architecture-and-routing.md](references/architecture-and-routing.md) |
| Implement/review a direct adopter or input adapter | [adopter-patterns.md](references/adopter-patterns.md) |
| Choose buckets, prove capture/replay/fallback | [bucket-and-runtime.md](references/bucket-and-runtime.md) |
| Validate semantic/output correctness | [correctness.md](references/correctness.md) |
| Benchmark throughput/latency/coverage/startup/memory | [performance-and-cost.md](references/performance-and-cost.md) |
| Decide default-on/opt-in/no-go or prepare PR evidence | [promotion-and-pr-evidence.md](references/promotion-and-pr-evidence.md) |
| Compare against merged precedents | [merged-pr-casebook.md](references/merged-pr-casebook.md) |

## Default workflow

1. Read [architecture-and-routing.md](references/architecture-and-routing.md).
2. Prove the existing shared path can capture **and actually replay** before changing model code.
3. Classify the model as:
   - **direct adopter**;
   - **input-adapter adopter**;
   - **incompatible for now**.
4. Make the smallest model-specific change supported by a reproduced incompatibility.
5. Qualify token/bucket coverage using real scheduled prefill shapes.
6. Run correctness qualification.
7. Run end-to-end performance plus startup/memory qualification.
8. Choose exactly one outcome: **DEFAULT ON**, **OPT-IN**, or **NO-GO**.
9. Before finishing, ask: **Could this model use the shared implementation with fewer changes?**

## Non-negotiable evidence

A qualification is incomplete without all of the following:

- actual graph replay, not only successful capture;
- expected eager fallback at the graph boundary;
- deterministic or strongest-stable correctness comparison;
- established model quality gate where exact identity is not the contract;
- end-to-end benchmark against graph-disabled control;
- graph replay/eager fallback coverage on the measured workload;
- capture time and GPU-memory cost measured separately;
- explicit rollback path;
- a promotion decision with scope and tradeoffs.

## Important distinctions

Do not conflate LM Prefill CUDA Graph with model-local encoder, decoder, vocoder, or decode CUDA Graph implementations.

Do not infer graph buckets from raw prompt length or audio duration. Use the actual scheduled prefill token shape after preprocessing, multimodal expansion, radix-cache effects, chunking, and scheduler batching.

Do not universally require bit identity. Padding can change GEMM shapes and floating-point numerics. Investigate reproducible differences, attribute them, and then apply the model's established quality contract.

## Historical anchor

The reusable integration is tracked in [sglang-omni issue #1357](https://github.com/sgl-project/sglang-omni/issues/1357). Merged precedents and the specific lessons to reuse are summarized in [merged-pr-casebook.md](references/merged-pr-casebook.md).
