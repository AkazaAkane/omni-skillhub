# Phase 3a — Graph-path semantic audit

Read this when replay happens but output is wrong or suspicious, when admission refuses batches you expected to be eligible, or before writing any model-side fix.

## What to compare

Compare eager execution against the region **actually entered during replay** — not against `forward()`. The captured module is often below `forward()`, so anything the wrapper does on the way in is skipped at replay time.

Look for behavior in wrappers or `forward()` that graph replay may bypass:

- dtype casts;
- position or M-RoPE preparation;
- multimodal embedding composition;
- hidden-state capture;
- host/device synchronization;
- `.item()`, `.any()`, `nonzero()`, or data-dependent Python branches;
- mutation of request-local state;
- dynamically created tensors whose addresses must be stable;
- auxiliary inputs not represented in the graph batch.

The last three are the ones that produce intermittent rather than deterministic wrongness. A tensor allocated fresh each call has a new address the graph will not see; state mutated per request is frozen at capture; an auxiliary input outside the graph batch silently keeps its captured value.

Qwen3-ASR is the worked example of this failure: the captured path bypassed logic that `forward()` performed, so replay ran on inputs that had never been normalized.

## Where to fix it

Fix at the **narrowest common execution boundary** shared by eager and graph execution:

```text
bad:
    special case in an Omni graph runner

preferred:
    normalize the input immediately before the kernel that requires it
```

Fixing at the narrow boundary means eager and graph converge on the same prepared input, so the two paths cannot drift again later. Fixing in a graph runner means the invariant holds only while someone remembers to maintain a second dispatch path.

Do not modify shared infrastructure for a model-specific problem unless the same missing contract is demonstrated in **multiple** models. One model's missing dtype cast is a model fix; three models missing the same cast is a contract gap worth raising upstream.

## Gate

You may leave this audit when each semantic difference is either fixed at a shared boundary, or documented as an accepted numerical difference to be justified in `correctness.md`.

Then continue to `adopter-patterns.md` to choose how the model declares support.
