# Phase 5 — Promotion decision

Read this when concluding the work, or first when reviewing someone else's enablement PR.

Choose exactly one outcome. Record the reason and the rollback path in the PR using `assets/pr-qualification-record.md`.

## DEFAULT ON

All of:

- graph replay is correct for the declared scope;
- established quality gates pass;
- end-to-end performance improves materially and repeatably beyond measured noise;
- no important supported workload has an unacceptable latency regression;
- capture/startup/memory cost is acceptable;
- eager rollback works.

## OPT-IN

Correctness is established, but the tradeoff is deployment-dependent. Typical triggers:

- throughput improves but an important latency metric regresses;
- graph memory/startup cost is large;
- only a subset of modalities/output paths is qualified;
- evidence is promising but insufficient for a universal default.

Keep eager as the default and document the qualified scope. Qwen3-Omni is the reference: a correct bounded adapter that stays opt-in because the qualified scope is narrower than the model's full surface.

Opt-in is not a consolation prize. It is the honest answer when the win depends on how the model is deployed.

## NO-GO

Any of:

- correctness fails;
- end-to-end performance regresses;
- apparent gains are inside measurement noise with meaningful cost;
- startup/memory cost is disproportionate;
- the required implementation would duplicate shared graph infrastructure.

Leave the model unsupported or disabled, and record the reason so the next person does not repeat the investigation. A no-go is a valid result — the investigation still produced a distribution, a coverage picture, and a documented blocker.

Do not turn a no-go into extra infrastructure.

## Reviewing an enablement PR

Check, in this order — each is a place where PRs commonly overclaim:

1. Does the evidence show real **replay**, or only capture?
2. Does the capture budget trace to a measured prefill distribution?
3. Is the diff confined to config + tests, or did a model-specific fix leak into shared code?
4. Is the performance delta larger than the reported A/A noise?
5. Do coverage numbers show the workload actually using the graph?
6. Is `supports_breakable_prefill_cuda_graph=True` justified by qualification, or by the model merely booting?

## New-model checklist

When a new SGLang-backed model is added, classify Prefill CUDA Graph explicitly before calling model enablement complete:

- `DEFAULT ON` — qualified and enabled;
- `OPT-IN` — qualified with documented tradeoffs;
- `NO-GO` — tested and rejected with reason;
- `NOT YET QUALIFIED` — follow-up required.

`NOT YET QUALIFIED` is the correct label when nobody has run phase 1 yet. Leaving the question unanswered is what produces silent, untested `supports_breakable_prefill_cuda_graph=True` declarations later.
