# Architecture, Inspection, and Route Selection

Use this file first when enabling Prefill CUDA Graph for a model or reviewing an enablement PR.

## 1. Establish the ownership boundary

The shared path should own graph mechanics. Model code should only express compatibility or supply narrowly scoped data/semantic adaptation.

```text
model-specific code
  ├─ capability declaration
  ├─ default/opt-in policy
  └─ only necessary semantic/input adaptation
        ↓
SGLang-Omni shared policy/bootstrap
        ↓
SGLang PrefillCudaGraphRunner
  ├─ admission
  ├─ static buffers
  ├─ padding
  ├─ replay
  └─ eager fallback
```

A PR is suspicious if it introduces model-local code for behavior already owned by the shared runner.

## 2. Inspect the model before changing code

Identify:

- generation engine builder;
- model/model runner used during prefill;
- `forward()` and the lower-level module actually captured;
- `max_prefill_tokens`;
- `chunked_prefill_size`;
- multimodal embedding construction;
- position/M-RoPE preparation;
- hidden-state or auxiliary-output side channels;
- request-local mutable state;
- model-local encoder/decode/vocoder CUDA Graph or `torch.compile` paths.

Then compare the eager call path with the captured/replayed call path. The critical question is not merely “does capture work?” but **what eager wrapper behavior is bypassed during replay?**

## 3. Prove the shared path before implementation

Start with configuration-only qualification if possible.

Enable the upstream breakable prefill backend with a small explicit bucket set that covers a real request. Verify from runtime evidence:

- capture completes;
- graph admission is reached;
- `can_run_cuda_graph` or equivalent returns true for a real prefill;
- at least one real request executes via replay;
- the request completes;
- disabling Prefill CUDA Graph returns to eager execution.

**Successful capture alone is not sufficient. Prove replay.**

If the model already replays correctly, do not modify its forward/model-runner path.

## 4. Audit semantic seams

Look for behavior that exists in eager wrappers but may be skipped by graph replay:

- dtype casts;
- position/M-RoPE preparation;
- multimodal embedding composition;
- hidden-state capture;
- host/device synchronization;
- `.item()`, `.any()`, `nonzero()`, or data-dependent Python branches;
- request-local state mutation;
- dynamically created tensors whose addresses must remain stable;
- auxiliary inputs absent from the graph batch.

If a required invariant is skipped, fix it at the **narrowest common boundary** used by eager and graph execution.

Example:

```text
bad:
    add a special case in an Omni graph runner

preferred:
    normalize the input immediately before the kernel/module that requires it
```

Qwen3-ASR is the canonical precedent: replay bypassed a `forward()` position dtype cast, so the fix moved the normalization to the fused-kernel preparation boundary rather than adding a model-specific graph path.

## 5. Route the model

### Route A — Direct adopter

Choose this when the model already reaches the shared graph path correctly and all required inputs are already represented in upstream-compatible graph fields.

Expected production diff is small: capability declaration, backend default/opt-in, bucket policy, and focused tests.

Examples: Fun-ASR, MOSS-Transcribe-Diarize. Qwen3-ASR is also fundamentally direct, with one narrow semantic fix.

### Route B — Input-adapter adopter

Choose this only when model/Omni runner-composed prefill inputs cannot be represented in the fields available at graph admission without a small adapter.

Use the existing `OmniPrefillInputs` contract rather than inventing another side channel.

Example: Qwen3-Omni text-output Thinker.

### Route C — Incompatible for now

Stop if correct replay requires any of the following without an already established shared abstraction:

- a second generic Prefill CUDA Graph runner;
- scheduler redesign solely for one model;
- unsafe reconstruction of request-local state;
- broad model surgery;
- forced batch splitting only to obtain graph eligibility;
- disabling shared eager fallback.

Report the blocking reason instead of creating infrastructure around it.

## 6. New-model completion rule

A newly supported SGLang-backed model should eventually be classified as one of:

- `DEFAULT ON`;
- `OPT-IN`;
- `NO-GO`;
- `NOT YET QUALIFIED`.

Do not set `supports_breakable_prefill_cuda_graph=True` merely because the model boots with the backend enabled.
