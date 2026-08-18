# Phase 3b — Adopter patterns

Read this when writing the actual change, or when judging whether a PR's diff is the right size.

Three cases. Most models are case A. Case B needs justification. Case C is a legitimate answer.

## A. Direct adopter

Use when the model already reaches shared Prefill CUDA Graph correctly (proved in phase 1).

The production change should be approximately:

```python
class ModelEngineBuilder(...):
    supports_breakable_prefill_cuda_graph = True

    def generation_defaults(...):
        return {
            ...
            "cuda_graph_backend_prefill": CudaGraphBackend.BREAKABLE,
            "cuda_graph_bs_prefill":
                build_default_prefill_cuda_graph_bs(QUALIFIED_CAP),
        }
```

Add focused tests for:

- support declaration;
- resolved backend;
- bucket policy;
- `disable_cuda_graph=True` or explicit prefill-disable rollback;
- relevant deployment overrides.

The rollback test matters as much as the enablement test — it is the operator's escape hatch when something regresses in production.

**Do not add a model runner merely to enable graphs.**

## B. Input-adapter adopter

Use **only** when prefill embeddings or other supported inputs are composed by the Omni model runner and cannot be placed directly on `ForwardBatch.input_embeds` before graph admission.

Reuse the existing `OmniPrefillInputs` contract. Requirements:

- leave upstream graph-owned fields in their expected admission state;
- attach only the data the model requires;
- validate the whole batch before opting in;
- fail closed to the inherited eager path for unsupported or ambiguous state;
- do not split a batch merely to force graph eligibility;
- do not implement shape-based fallback locally — SGLang already owns that.

Keep the supported modality/output scope explicit. Qwen3-Omni is the reference: a bounded adapter, an explicitly stated scope, and opt-in rather than default-on.

Validating the whole batch before opting in is what keeps failure closed. Per-request opt-in inside a mixed batch produces a batch that is partly graph-shaped and partly not, which is far harder to debug than a clean fallback.

## C. Incompatible for now

If correct replay would require a large scheduler redesign, a second graph runner, unsafe state reconstruction, or broad model surgery — stop.

Report the blocking reason. Do not build infrastructure around it. Record the model as NO-GO or NOT YET QUALIFIED per `decision.md`.

## Minimal implementation check

Before finishing, inspect the diff and ask:

```text
Could this model use the shared implementation with fewer changes?
```

For a straightforward adopter, expect changes confined to:

```text
model engine_builder/config
focused model tests
documentation only if users need an override or scope explanation
```

Anything beyond that needs a concrete, reproduced justification in the PR — the incompatibility you actually hit, not the one you anticipate. Do not generalize a one-model workaround into shared code.
