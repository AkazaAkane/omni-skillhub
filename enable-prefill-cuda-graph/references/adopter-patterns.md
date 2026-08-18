# Adopter Patterns

Read this file after route selection.

## A. Direct adopter

Use when the model already reaches shared Prefill CUDA Graph correctly.

Typical production shape:

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

Depending on the model and current shared policy, the bucket ladder may instead be derived after deployment overrides are merged from effective caps. Do not cargo-cult one exact builder implementation; preserve the shared policy's current precedence rules.

Focused tests should cover:

- compatibility/capability declaration;
- resolved prefill backend;
- bucket policy;
- global rollback (`disable_cuda_graph=True`) and/or explicit prefill disable;
- relevant deployment overrides;
- any model-specific semantic fix.

Do **not** add a model runner merely to enable graphs.

### Direct-adopter precedent: Fun-ASR

Fun-ASR already reached the upstream multimodal prefill path. The merged enablement was mostly builder/capability policy plus tests. This is the preferred shape when no model-side seam exists.

### Direct-adopter precedent: MOSS-Transcribe-Diarize

MOSS-TD reused the shared contract and default bucket helper. Its PR is a useful example of accepting padded-shape numerical differences only after they were localized and aggregate quality was shown stable.

### Direct adopter with a narrow semantic repair: Qwen3-ASR

Qwen3-ASR remained a shared-runner adopter. The graph path bypassed a position cast in `forward()`, so the fix was placed immediately before the fused kernel that requires `int32` positions. This is the preferred response to a graph/eager seam: repair the invariant where both execution paths converge.

## B. Input-adapter adopter

Use only when the model's required prefill input is assembled in Omni/model-runner code and cannot safely be placed on the official graph-owned field before graph admission.

Reuse `OmniPrefillInputs`.

Adapter requirements:

- validate the **whole batch** before opting in;
- attach only data required by the model;
- keep upstream graph-owned fields in their expected admission state;
- fail closed to the inherited eager path for unsupported or ambiguous state;
- preserve request-owned metadata such as M-RoPE state;
- never split a batch merely to force graph eligibility;
- never implement shape-based graph/eager fallback locally;
- keep supported modality/output scope explicit.

### Qwen3-Omni precedent

Qwen3-Omni's text-output Thinker needed a bounded adopter because prefill embeddings were composed in the Omni runner. Its adopter:

1. validates whole-batch eligibility;
2. composes the existing normal prefill embeddings;
3. attaches them through `OmniPrefillInputs`;
4. deliberately leaves the official admission-sensitive `input_embeds` field unset until the shared path is ready to consume it;
5. delegates graph mechanics back to SGLang.

Unsupported image/video/deepstack/speech-output/ambiguous-state cases fail closed to eager. The PR did not add its own graph runner, bucket manager, or model-specific shape fallback.

## C. When an adapter is too large

An adapter has crossed into design smell if it starts owning:

- graph capture lifecycle;
- bucket selection;
- padding decisions;
- replay dispatch;
- shape fallback;
- scheduler admission policy.

Those belong to shared infrastructure. If the model cannot fit the existing contract with a bounded adapter, classify it as incompatible for now or first demonstrate a reusable missing abstraction across multiple models.

## Minimal implementation rule

Before finalizing the diff, ask:

```text
Could this model use the shared implementation with fewer changes?
```

For a straightforward adopter, expect changes mostly in:

```text
model engine_builder/config
focused model tests
small semantic fix only if reproduced
user documentation only if an override/scope needs explanation
```
