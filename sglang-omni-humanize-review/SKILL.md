---
name: sglang-omni-humanize-review
description: "Review SGLang-Omni PRs, diffs, patches, or local changes using public Omni maintainer discussions and current repository contracts. Explain the changed execution path with a Mermaid diagram, synthesize relevant historical review evidence, then assess correctness, shared-runtime reuse, streaming audio, lifecycle, API compatibility, backend coverage, and performance claims. Use for human-style maintainer review or PR preparation; for the upstream sgl-project/sglang runtime itself, use its own review guidance."
---

# SGLang-Omni Humanize Review

Review the behavior a contributor is changing, with the concrete concerns and evidence standards seen in SGLang-Omni maintainer discussions. Ground findings in the target revision; history helps identify risks but does not prove a current defect.

This is an independently written Omni adaptation of [BBuf's sglang-humanize-review](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/tree/2dd7b5d4d0d0813ba2639826386d73ae81e30809/skills/sglang-humanize-review). It retains the comprehension-first and historical-evidence workflow. Its evidence is a curated Omni source index plus live discussion retrieval, with no bundled full-history corpus. Do not claim the upstream SGLang corpus or BBuf's review rules describe Omni.

It also incorporates the user's existing `sglang-omni-review-pr` standards: repository coherence, deletion/reuse, explicit invariants, fail-fast behavior, scoped support claims, and reproducible evidence. The applicable rules are included here and in the references; installing or loading that sibling skill is not required. Passing CI alone does not establish a sound architecture or sufficient evidence. Apply the same responsibility and review bar to human- and AI-written changes.

## Read and resolve the target

1. Read [maintainer-standards.md](references/maintainer-standards.md) and the target revision's applicable `AGENTS.md` and coding-style instructions. Current target instructions take precedence over this historical synthesis, subject to the user's instructions.
2. Record repository, base/head SHA and merge base, changed paths, PR motivation, linked issues, unresolved discussions, and available CI results. For local work, distinguish committed changes, staged/unstaged edits, and untracked files. For re-review, identify the previously reviewed SHA and the intervening diff.
3. Read the diff and enough callers, callees, configuration, and neighboring implementations to explain the actual behavior. Fetch surrounding code at the PR head SHA; a local checkout on another revision cannot establish a finding about that head.
4. Read only the relevant sections of [review-surfaces.md](references/review-surfaces.md). Classify both the changed mechanism and PR type before choosing validation. For a benchmark-plan review, assess whether the proposed experiment can resolve its hypothesis; do not treat planned measurements as completed evidence.

Treat review as read-only. Draft comments in the response; publish reviews/comments, resolve threads, or change code only when the user asks for those actions. A requested review does not authorize deploying or running a costly benchmark campaign.

## Historical evidence pass

Before writing findings, follow [history-and-sources.md](references/history-and-sources.md): select relevant Omni precedents, retrieve their complete review episodes, and search for newer same-subsystem discussions when available. Read replies and subsequent review states, rather than extracting a maintainer's first objection in isolation.

- Distinguish inline threads, top-level conversations, review submissions, issue proposals, and author-reported measurements. An approved PR body is evidence of the author's experiment, not a quotation of maintainer policy.
- Preserve original comment language when quoting, and link the exact comment. Exclude known bot/agent feedback from claims about human maintainer opinions; a `User` account alone does not establish human authorship.
- Summarize what was challenged, the requested evidence, and how the discussion ended. Treat a finding as independent code reasoning unless a retrieved precedent actually supports it.
- Report retrieved PRs/episodes, dates, queries, pagination completeness, and gaps. This is a bounded search, not an exhaustive repository census. If no relevant precedent is found or access is unavailable, say so and continue a code-grounded review without invented historical support.

## Explain execution before judgment

Open the review with a short problem → mechanism → observable outcome summary, including the root cause, success condition, and main regression risks where established. Flag underspecified motivation rather than inventing it. Name the real entrypoint and the changed files/symbols. Include a compact Mermaid flowchart before findings, and follow it immediately with a prose walkthrough.

- Trace only the changed execution path: request/config entry → validation/lowering → stage/scheduler/runner or native backend → output/cleanup, as applicable. This is an orientation aid, not a mandatory architecture shared by every model.
- Use real symbols verified at the reviewed revision. Quote labels, annotate meaningful branch conditions, and mark modified/added nodes with `:::changed` plus a legend. Define `classDef changed stroke-dasharray:5 5,stroke-width:2px;` once per diagram.
- Prefer a small top-down diagram; use separate diagrams for independent paths. Show the relevant error/abort branch when that is the change's purpose.
- For a refactor, explain whether routing or ownership changes while external behavior stays equivalent. For docs/config/CI-only diffs, diagram the actual load/validation/job path; if there is no execution change, state that and use a small dependency diagram. Do not invent runtime edges to fill a diagram.
- If the available patch lacks enough context, explicitly mark the missing edge as unknown and state what source is needed to complete it.

## Review in this order

### Scope and ownership

Establish the concrete problem and smallest sufficient change. Compare with the nearest working model or shared implementation. Look for repeated server lifecycle, scheduling, reference encoding, pipeline state, cache, serialization, vocoder, and benchmark mechanics. Identify why each new helper or layer is needed now. Keep model semantics in model code and shared serving mechanics in the existing framework surfaces.

For each new class/helper/config/harness, ask whether it can disappear or reuse an existing surface. Cite a concrete repository precedent when flagging inconsistency; personal taste is insufficient. Check that every changed file contributes to the stated goal and that unrelated cleanup, generated artifacts, and speculative follow-ups are kept outside the change.

Do not import SGLang-specific kernel namespaces, test layouts, flag bans, or diffusion conventions into Omni without target-branch evidence. Do not require a generic abstraction merely because multiple models might need it later.

### Configuration and API contract

Trace each changed public parameter through CLI/YAML/API, typed configuration, factory, request builder, and backend as applicable. Check omitted values versus explicit user values, preserved defaults, model-specific validation, and unsupported combinations. A global schema change must not make another model accept an input it cannot execute. Reject invalid requests before expensive work where the actual boundary permits it.

### Correctness and lifecycle

Follow request/session state through admission, execution, completion, error, and abort. Verify ownership and release of slots, KV/cache state, references, relay tensors, and codec/vocoder state. Inspect late arrivals after cancellation, repeated requests, and concurrent rows only where the changed mechanism can affect them. Apply the relevant audio, distributed, and backend checks from the surface reference.

For each new or relied-upon invariant, identify its validation site, whether validation occurs early enough, the violation outcome, any fallback that can mask it, and the regression coverage at the right boundary. Examples include engine-wide parameters versus per-request overrides, admission/compile/batch limits, graph replay state, leader/follower lifetime, and exactly-once resource release. Check that failed validation cannot leave partially mutated config or initialized runtime state.

Inspect broad exceptions, forgiving attribute defaults, and silent semantic fallback for broken internal contracts, especially OOM/init failures that leave a partially alive service. These are semantic checks, not token bans: optional external fields and expected recoverable failures can justify defensive handling. Runtime failure should remain visible while CI preserves all available failed metrics and useful diagnostics.

For an optimized/kernel/native path, prove that the real request dispatch selects it. A green E2E test that executes a fallback does not cover the candidate. Do not turn empty intermediate audio chunks into an error unless the stream contract forbids them; distinguish them from a whole request completing without required audio.

### Tests, measurements, and claim scope

Check whether tests actually reach the changed branch and assert the public contract or a meaningful invariant. Prefer a focused regression in an existing suite over another mock pipeline or duplicated accuracy suite. Passing unit tests does not establish streaming, concurrency, device execution, or production support.

For performance claims, require baseline/candidate revisions, identical hardware/model/checkpoint/workload/configuration, warmup/cache state, relevant latency and throughput, failures/skips and sample counts, and repetitions when variance matters. Use quality evidence appropriate to the output. Keep microbenchmarks, dispatch coverage, E2E gains, and quality parity distinct. Report numerical results as author-reported unless independently reproduced.

Assess evidence against the PR-type table in [review-surfaces.md](references/review-surfaces.md#evidence-by-pr-type). Keep claimed support limited to measured model/backend/config/topology combinations. Treat outliers as evidence: record the invalidation reason, contamination rule, replacement run, and provenance before excluding a result. An intermittent quality failure may be a defect. CI calibration must reproduce the gated condition, distinguish raw references from tolerance/slack, and validate the result after applying the calibration.

Request only validation that discriminates a real concern in the changed path. A docs-only change need not run model inference; a scheduler race may need an abort/recovery test rather than a full quality benchmark. State exact commands/results and whether they were run locally, observed in CI at a specific SHA, or merely proposed.

## Output

Use the user's language for the review. Suggested GitHub comments should normally be concise English unless the user requests otherwise. Keep quoted historical comments in their original language.

Return these in order, scaling length to the diff:

1. **Comprehension:** concise change summary, Mermaid path, immediate walkthrough.
2. **Historical synthesis:** relevant recurring concerns with exact links, observed resolutions, and bounded coverage or access limitations.
3. **Verdict:** `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`, with a short reason using the severity guidance in [maintainer-standards.md](references/maintainer-standards.md#severity-and-verdict). This is a recommendation, not a submitted GitHub review.
4. **Findings:** actionable issues ordered by severity. Default to the existing review skill's `BLOCKER`/`MAJOR`/`MINOR`/`NIT` labels unless the user or review interface requires another convention. For each, give verified file/line or hunk, triggering condition, concrete consequence, evidence, and the smallest fix or discriminating test. Separate optional nits from blockers; do not manufacture findings. If none exist, say so.
5. **Evidence assessment:** what was run/observed, what it proves, and what was not validated. For performance changes, distinguish local/micro, E2E, quality, repeat/noise, and production-condition coverage. Do not imply untested hardware or modes are qualified.
6. **Minimum additional validation:** only checks needed to resolve material concerns. State the hypothesis, controlled variables, metrics, and result that would resolve each concern. For a narrow change, N/A with a reason is sufficient.
7. **Ready-to-post comments:** concise comments worth posting, with exact placement when available; omit duplicated analysis and state clearly if no comment is needed.

For PR preparation, use the same comprehension and evidence pass, then give likely reviewer concerns, missing evidence, and minimal patch cleanup instead of a formal merge verdict. When preparing ready-to-post comments, write the failure first and a short concrete ask; avoid repeating the entire review in each comment.
