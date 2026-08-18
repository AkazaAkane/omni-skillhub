# Research grounding for `sglang-omni-review-pr`

This file records why the skill uses its review heuristics. It is reference material, not a checklist that must be loaded for every review.

## Direct SGLang-Omni evidence

### Issue #188 — SGLang-Omni Refactoring Proposal

https://github.com/sgl-project/sglang-omni/issues/188

Zhao Chenyang identifies:

- excessive request-path abstraction layers;
- Stage -> Worker -> Executor -> Engine as overlapping delegation layers;
- confusing duplicate concepts/names;
- dynamic attribute delegation as a sign of unclear interface design;
- near-isomorphic Engine/Executor interfaces;
- repeated relay/test/embedding glue;
- large-file/code-volume concentration;
- goals to remove layers, reduce total code, preserve functionality/performance, and lower new-model onboarding cost.

This supports: coherence, deletion, explicit ownership, skepticism toward pass-through abstraction, and refactor evidence that preserves behavior/performance.

### Issue #661 — Large-scale refactor epic

https://github.com/sgl-project/sglang-omni/issues/661

Zhao calls out three recurring agent-written PR problems:

1. filler comments that carry no information;
2. failure to reuse existing benchmark/server abstractions;
3. redundant unit tests for behavior already covered by per-model accuracy CI.

The issue also notes that TTS models repeatedly reimplemented the same serving optimizations and states the intended split: reusable mechanics in framework/shared code, model semantics/math in model directories.

This supports: reuse-before-new-glue, comment quality, contract-focused tests, and framework-owned mechanics.

### PR #530 — Report all CI metric threshold failures

https://github.com/sgl-project/sglang-omni/pull/530

The PR explicitly says that although CI should fail fast, it still needs to report all available numbers and identify every unmet threshold.

This supports the distinction between fail-fast execution semantics and diagnostic completeness.

### PR #641 — Resolve Text Only Qwen3 Omni TP Issue

https://github.com/sgl-project/sglang-omni/pull/641

The PR:

- links the originating issue;
- states a concrete root cause;
- aligns text-only behavior with the existing speech configuration instead of inventing a separate fix path;
- provides a reproduction command;
- adds focused regression coverage.

This supports root-cause review, repository precedent, and focused bugfix evidence.

### PR #1356 — dots.tts-mf support

https://github.com/sgl-project/sglang-omni/pull/1356

The PR:

- explains the pipeline and why its tail needs per-request KV state;
- calls out two non-obvious forced settings and explains the architectural reason;
- rejects incompatible per-request values instead of silently reinterpreting them;
- reports full Seed-TTS EN 1088 results, quality, latency, throughput, memory, and failures;
- distinguishes aggregate throughput from per-request latency;
- includes a large explicit `Not in this PR` section with unsupported/unmeasured items and suggested follow-ups.

This supports explicit invariants, evidence scope, disclosures, and follow-up boundaries.

### Review on PR #779 — ZONOS2

https://github.com/sgl-project/sglang-omni/pull/779

Direct review comment from Zhao:

> Use server args, do not use ENV Args

The contributor then moved tuning toggles to typed factory/server args consistent with other models.

This supports discoverable config through normal serving surfaces. The skill intentionally treats this as a strong preference, not a universal ban on environment variables.

### Review on PR #1090 — Audar-TTS

https://github.com/sgl-project/sglang-omni/pull/1090

Direct Zhao review comments include:

- questioning why generated benchmark artifacts/harness content should remain in the PR;
- asking whether a very simple config file should exist at all.

He requested changes, and the contributor removed the benchmark artifacts and reduced redundant config content.

This supports deletion/scope review and skepticism toward extra maintained surfaces.

### PR #1441 — dots.tts CFG null projection

https://github.com/sgl-project/sglang-omni/pull/1441

This reviewed/approved PR is useful as an evidence-quality example:

- it provides a local microbenchmark;
- verifies exact numerical parity;
- explicitly says the benchmark is isolated and **not** an end-to-end RTF claim.

This supports keeping claims no broader than the measurement.

## Podcast transcript supplied by the user — 2026-08-14

The transcript reinforces four engineering principles used by the skill:

### Consistency/coherence is more actionable than subjective taste

Zhao describes coding “taste” as subjective but says a maintainable project should converge on consistent choices. He describes keeping a personal/team list of coding preferences and using it to make contributions more coherent.

Implication for the skill: review against repository precedent before personal aesthetics.

### Over-protective programming can hide real failures

He gives an example in which AI-generated defensive exception handling caught an OOM during training and allowed the job to remain alive for hours instead of failing. He describes this as “over protective programming” and argues that when a field/state is guaranteed by the system, missing state should fail fast rather than be hidden by permissive attribute access/defaults.

Implication: distinguish recoverable boundaries from broken internal invariants.

### AI makes strict review more important

He notes that submitting code is easy while reviewing it is hard, and argues that collaborative projects need strict reviewers and responsible contributors because the old assumption that a PR necessarily represented substantial author effort no longer holds in the agent era.

Implication: passing tests does not substitute for architecture/failure-mode review.

### Responsibility does not transfer to the agent

The contributor/reviewer remains responsible for the code even when an agent generated it.

Implication: do not excuse duplication, speculative abstraction, or weak evidence because the change was AI-generated.

## Deliberate non-rules

The research does not justify making these universal hard requirements:

- every PR must begin with an issue;
- one mandatory conventional-commit format;
- a fixed maximum PR line count;
- all comments must only explain “why”;
- never use `getattr`;
- never use `try/except`;
- never use environment variables.

Apply repository precedent and semantics instead of token-level bans.
