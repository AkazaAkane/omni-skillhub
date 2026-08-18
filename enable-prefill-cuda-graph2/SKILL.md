---
name: enable-prefill-cuda-graph
description: Qualify and enable SGLang-Omni breakable Prefill CUDA Graph for one model. Use whenever prefill CUDA graphs come up for an Omni model — enabling or capturing them, picking capture buckets or a capture budget, debugging eager fallback or replay, judging whether a model should be default-on/opt-in/no-go, or reviewing a PR that sets supports_breakable_prefill_cuda_graph. Reuse the shared SGLang/Omni graph path, make only model-specific fixes demonstrated necessary, and validate correctness, end-to-end performance, and startup/memory cost before promoting.
---

# enable-prefill-cuda-graph

Qualifying one model for the shared breakable Prefill CUDA Graph path.

The goal is **not** to make every model use Prefill CUDA Graph. The goal is to answer six questions with evidence:

1. Can the model use the shared breakable prefill graph path correctly?
2. What is the smallest model-specific change required?
3. What token range should be captured?
4. Does it improve end-to-end serving beyond run-to-run noise?
5. Are capture time and GPU-memory cost acceptable?
6. Should it be default-on, opt-in, or no-go?

A no-go is a valid result. So is "not yet qualified."

## Ground rules

Reuse the existing shared implementation. Start with configuration-only qualification; add code only after reproducing a concrete incompatibility.

Do not add:

- another Prefill CUDA Graph runner;
- another generic bucket policy;
- model-specific graph/eager dispatch;
- model-specific shape fallback already handled by SGLang;
- a new configuration abstraction around existing `ServerArgs`;
- speculative hooks for models that do not need them.

The ownership boundary this skill works within:

```text
model
  └─ declares whether its prefill semantics are compatible
       ↓
SGLang-Omni shared policy
  └─ validates configuration and model capability
       ↓
SGLang PrefillCudaGraphRunner
  ├─ capture
  ├─ admission
  ├─ padding
  ├─ replay
  └─ eager fallback
```

Anything the runner already owns is not a model concern. Most incorrect enablement work comes from re-implementing one of those five boxes per model.

## Workflow

Five phases, each gated. Read the phase reference when you enter that phase — not before, and don't read them all upfront. Do not proceed past a gate you cannot answer from runtime evidence.

| Phase | Do | Gate | Read |
|---|---|---|---|
| 1. Qualify | Inspect the model, run it with the breakable backend, prove real replay | Graph replay demonstrated, eager rollback demonstrated | `references/qualify.md` |
| 2. Size | Measure the scheduled prefill token distribution, choose a capture budget | Budget justified by measured shapes, not prompt length | `references/capture-budget.md` |
| 3. Implement | Audit graph-path semantics, pick the adopter type, make the minimal change | Diff is model config + tests unless a fix is demonstrated necessary | `references/graph-semantics.md`, then `references/adopter-patterns.md` |
| 4. Validate | Boundary routing, correctness comparison, performance, coverage, startup/memory | Every claim in the PR traceable to a measurement | `references/correctness.md`, `references/performance.md` |
| 5. Decide | Choose DEFAULT ON / OPT-IN / NO-GO, record the qualification | Exactly one outcome, with reason and rollback | `references/decision.md` |

Phase 1 is often the whole task. If configuration alone gives correct replay, skip straight from phase 2 to a config-only adopter in phase 3.

If you are **reviewing** a PR rather than doing the work, read `references/decision.md` first — it lists what evidence the PR must contain — then consult the phase reference for whichever claim looks weakest.

## PR evidence

Every enablement or rejection carries a compact qualification record in the PR description. Copy the template from `assets/pr-qualification-record.md` and fill it from measurements taken during phases 1–4. Keep raw experimental detail out of production code.

## Hard rules

These hold across all phases:

- **Capture success is not replay.** A model that captures buckets and then falls back on every request has gained nothing. Prove replay from runtime evidence.
- **Never infer buckets from raw input length**, audio duration, processor estimates, or theoretical context length. Only the scheduled prefill shape counts.
- **Never enable by default from a microbenchmark.** End-to-end serving decides promotion; faster isolated prefill is attribution, not justification.
- **Never claim an improvement smaller than measured run-to-run noise.**
- **Do not require bit-identical padded numerics** when the model's established correctness contract does not require them — but never let an aggregate quality metric paper over a reproducible semantic bug in the graph path.
- **Never disable eager fallback.** Fallback is part of the contract, not a failure.
- **Do not conflate LM Prefill CUDA Graph** with model-local encoder, decoder, vocoder, or `torch.compile` paths. They are separate mechanisms with separate qualification.
- **Do not generalize a one-model workaround** into shared infrastructure, and do not turn a no-go result into extra infrastructure.
- **Do not set `supports_breakable_prefill_cuda_graph=True` merely because the model boots** with the backend enabled.
