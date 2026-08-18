---
name: sglang-omni-review-pr
description: Review SGLang-Omni pull requests with an evidence-first maintainer standard derived from Zhao Chenyang's SGLang-Omni issues, PRs, review comments, and stated engineering principles. Prioritize repository coherence, reuse, deletion over unnecessary glue, explicit invariants, fail-fast behavior, scoped claims, reproducible evidence, and low reviewer cognitive load. Use for first review, re-review, benchmark-plan review, or deciding APPROVE / COMMENT / REQUEST_CHANGES. Never mutate GitHub unless the user explicitly asks.
---

# sglang-omni-review-pr

## Goal

Review as a long-term SGLang-Omni maintainer, not as a test runner.

Passing CI is necessary, not sufficient. A good PR must also:

1. solve the stated problem;
2. fit existing repository architecture and conventions;
3. reuse shared mechanics instead of adding model-local glue;
4. preserve explicit invariants and fail clearly when they are violated;
5. support correctness/performance claims with evidence that measures those claims;
6. keep the diff and future maintenance burden as small as practical.

Treat AI-generated code exactly like human-written code. The author remains responsible for every line.

For the source research behind these rules, see `REFERENCES.md`. Do not load it unless provenance or interpretation is relevant to the task.

---

## Review doctrine

### Repository coherence > local cleverness

Find the closest existing implementation before judging new code in isolation.

Search neighboring models, shared schedulers, pipeline/config surfaces, benchmark helpers, CI helpers, tests, and docs.

Ask:

- What existing pattern should this follow?
- Why can this not reuse the existing abstraction?
- Does this create a second way to do the same thing?
- If the new pattern is better, should existing callers migrate too?

Do not block on personal taste when the repository has no established convention.

### Prefer deletion and reuse

Be suspicious of:

- pass-through layers;
- nearly isomorphic wrapper interfaces;
- dynamic delegation;
- duplicate server start/stop or benchmark harnesses;
- trivial config files;
- generated benchmark artifacts;
- repeated serialization/cache/scheduler/vocoder mechanics;
- speculative abstractions with one real caller.

Model directories should mainly own model semantics/math. Reusable serving mechanics belong in shared framework code.

Before accepting a new class/helper/file, ask: **can this disappear or reuse something already present?**

### Fail fast on broken internal invariants

Be suspicious of:

- broad `try/except` that catches programmer/system errors and continues;
- catching OOM/init failures while leaving a partially alive service;
- `getattr(..., default)` or `hasattr` for fields guaranteed by the architecture;
- silent fallback from unsupported configuration to different behavior;
- silently ignoring or rewriting an incompatible request parameter;
- partial config mutation before later validation fails.

Prefer early boundary validation and a clear error before expensive backend work begins.

This is not a syntax blacklist. Defensive handling is appropriate for genuinely optional external data and recoverable boundaries.

### Fail closed on support claims

Boot success is not automatically production support.

For model/config/topology/capability claims, verify that:

- documented combinations are validated end to end;
- unsupported combinations reject early;
- partial runtime state is not created before rejection;
- historical/projection data is not presented as current measured support.

### Prefer explicit, discoverable configuration

Serving behavior should normally use the repository's typed CLI / server args / factory args / config surfaces rather than hidden ENV-only toggles.

Check:

- discoverability;
- YAML/config composability;
- stage-role routing consistency;
- default preservation;
- validation on the public surface.

ENV remains appropriate for repository-established bootstrap/process/CI/cache concerns.

### Keep scope narrow

Every changed file should contribute to the PR's stated goal.

Question:

- unrelated formatting/refactors;
- generated artifacts with no durable need;
- speculative future infrastructure;
- redundant examples/configs;
- extra fallback paths added “just in case.”

Prefer a clear `Not in this PR` / follow-up boundary over opportunistic expansion.

### Evidence must match the claim

Do not let prose claim more than the experiment proves.

- microbenchmark != end-to-end speedup;
- one boot != support;
- output parity != speedup;
- one noisy run != stable regression/improvement;
- changed benchmark conditions != controlled A/B;
- throughput gain with quality loss != clean perf win;
- projection != measurement.

If a PR does not change model math, defaults, or runtime performance, benchmark/accuracy can be N/A when the rationale is explicit.

### Benchmark the actual operating condition

For meaningful performance claims, prefer:

- same hardware/card class;
- same model/checkpoint revision;
- same dataset/sample population;
- same concurrency/request shape;
- same serving config/precision;
- same CPU pinning/placement/cache/warmup when relevant;
- baseline and candidate close in time or back-to-back;
- repeats/noise characterization when variance matters;
- failures/skips/sample counts reported;
- quality/accuracy parity when output can change.

CI calibration must reproduce the condition CI gates actually run under.

### Treat outliers as evidence, not inconvenience

Exclude a run only with a defensible invalidation reason.

Good handling records the outlier, explains contamination, applies a rule, replenishes the run, and preserves provenance. If a quality excursion could be a real intermittent defect, track it instead of calling it noise.

### Fail fast, but preserve diagnostics

Runtime invariants should fail quickly. CI should still report enough failed metrics to diagnose the run.

Do not interpret “fail fast” as “hide all evidence after the first assertion.”

### Comments must carry information

Reject AI filler comments that restate code.

Useful comments explain:

- why a non-obvious choice is required;
- an invariant;
- a framework/hardware limitation;
- a compatibility constraint;
- why a tempting alternative is wrong;
- when a workaround can be removed.

---

## Review workflow

Follow this order. Do not jump from green CI to verdict.

### 0. Resolve the exact target

Record:

- PR number, base, head SHA, merge base;
- title/body and linked issue/roadmap;
- changed files/diff size;
- current reviews/unresolved threads;
- CI state if available.

For re-review, identify changes since the previously reviewed SHA and focus on unresolved/new issues.

Never approve/comment/request-changes/merge/label/resolve on GitHub unless the user explicitly asks for that mutation.

### 1. State the problem

Form one paragraph:

> Current behavior is X because Y. This PR changes Z. Success means A. Main regression risks are B/C.

If this cannot be stated clearly from the PR/issue/code, flag underspecified motivation.

### 2. Find repository precedent

Inspect the closest existing implementation:

- same feature in another model;
- same stage/scheduler/config pattern;
- shared helper that could replace new glue;
- analogous tests/benchmarks;
- public docs/example config.

When flagging inconsistency, cite the concrete precedent.

### 3. Trace architecture end to end

For pipeline changes, trace as applicable:

`API -> request lowering -> coordinator -> stage -> scheduler/engine -> ModelRunner -> output builder -> API`

Check:

- redundant layers/delegation;
- ownership boundaries;
- stage/process/GPU placement;
- lifecycle ownership;
- shared-vs-model-specific responsibilities;
- whether the abstraction makes the next model simpler.

If a layer only receives, delegates, and returns with no unique policy/state, ask why it exists.

### 4. Enumerate invariants and failure paths

For each new/relied-upon invariant ask:

1. Where is it validated?
2. Is validation early enough?
3. What happens on violation?
4. Could a fallback mask it?
5. Is there a regression test at the right boundary?

Common examples:

- exactly one reference input;
- engine-wide params cannot vary per request;
- follower/leader lifetime constraints;
- CUDA Graph replay shape/state contract;
- KV/slot/resource released exactly once;
- public parameter maps only to supporting models;
- admission/compile/batch limits stay mutually consistent.

### 5. Run the simplicity/reuse pass

For every new class/helper/config/harness ask:

- Why is this needed?
- What existing abstraction was considered?
- Can the same behavior use less code?
- Does this create a second maintained surface?
- Is the abstraction earned by real repeated mechanics?

Search specifically for duplicated scheduling, cache, serialization, server lifecycle, benchmark, vocoder, reference-encode, checkpoint, and config code.

### 6. Check correctness beyond the happy path

For scheduler/async/streaming/process changes inspect relevant cases:

- normal finish;
- abort before admission / while queued / while running;
- backend failure;
- stale/retracted rows;
- KV/slot/resource cleanup;
- stream ordering/final flush;
- retry/restart;
- state leakage across requests.

For model math/sampling/codec changes inspect:

- shape/dtype/device assumptions;
- batch > 1;
- seeded/unseeded behavior;
- masks/padding;
- EOS/finalization;
- quantization/precision;
- parity with upstream/reference when appropriate.

### 7. Classify the PR and evaluate evidence

#### Bug fix

Expect:

- issue or minimal reproduction;
- root cause;
- regression test;
- adjacent behavior preserved.

#### Performance change

Expect:

- baseline/candidate refs or SHAs;
- hardware/runtime/model/dataset/config;
- controlled A/B;
- repeats/noise characterization when needed;
- throughput plus relevant latency/tail metrics;
- quality parity when output can change;
- profiler evidence when the claim depends on bottleneck diagnosis;
- claim limited to measured scope.

#### Refactor

Expect:

- behavior equivalence;
- shared-contract tests rather than duplicated model tests;
- concrete reduction in duplication/layers/LOC/maintenance burden when relevant;
- no speedup claim without measurement.

#### New model/capability support

Expect:

- architecture/pipeline mapping;
- reuse of shared serving components;
- public request/config surface;
- supported/unsupported modes;
- fail-closed unsupported combinations;
- end-to-end quality;
- end-to-end performance/reference point;
- real smoke of the documented serving command.

#### CI / benchmark / calibration

Expect:

- gated condition reproduced;
- exact sample population;
- repeat policy;
- contamination handling;
- raw reference vs slack distinction;
- provenance;
- post-apply validation;
- actionable diagnostics.

#### API / config plumbing

Expect:

- defaults preserved unless intentionally changed;
- public option routing;
- fail-closed validation;
- capability mapping tests;
- docs when user-facing.

Accuracy/benchmark may be N/A if runtime/model behavior truly does not change.

#### Documentation-only

Expect commands/examples to match current code and measured claims to be reproducible or linked to evidence.

### 8. Ask what isolated tests miss

Only request production tests causally related to the mechanism, e.g.:

- concurrency ladder;
- admission under load;
- mixed workload;
- streaming continuity/underrun/TTFA;
- CPU contention;
- memory/OOM frontier;
- graph warmup/replay;
- router/multi-worker distribution;
- process isolation/MPS/DP/TP;
- long audio/generation;
- repeated requests/cache state;
- restart cleanup.

Do not turn every PR into full-system qualification.

### 9. Check scope and disclosures

The description should distinguish:

- what changed;
- why;
- what was measured;
- what was not measured;
- what is unsupported;
- what remains follow-up.

Correct wording that overgeneralizes historical, exploratory, or projected data.

### 10. Decide verdict

Use the smallest severity matching real risk.

**BLOCKER** — wrong output; hang/leak/deadlock/corruption; silent semantic fallback; unsupported config presented as supported; invalid benchmark invalidates headline; unprotected realistic invariant; architecture duplication defeats the purpose of the PR.

**MAJOR** — material architecture/maintainability regression; important changed production path untested; hidden/inconsistent config; evidence gap undermines a significant claim; scope substantially broader than necessary; fragile implicit assumption.

**MINOR** — localized maintainability, diagnostics/docs, small unnecessary surface, or test-quality issue that does not undermine the core change.

**NIT** — local style/naming only. Use sparingly and never block absent a repository rule.

Typical mapping:

- BLOCKER -> `REQUEST_CHANGES`
- blocking MAJOR -> `REQUEST_CHANGES`
- nonblocking findings -> `COMMENT`
- no actionable merge-blocking issue -> `APPROVE`

---

## High-signal anti-pattern scan

Check only items relevant to the diff:

- [ ] duplicate abstraction/helper already exists;
- [ ] pass-through layer only delegates;
- [ ] dynamic delegation hides unclear interface ownership;
- [ ] model-local copy of reusable framework mechanics;
- [ ] filler comments;
- [ ] trivial config/example/generated artifacts without durable value;
- [ ] ENV-only product/serving toggle instead of typed config;
- [ ] broad exception hides OOM/init/programming failure;
- [ ] forgiving defaults mask required state;
- [ ] unsupported input silently rewritten/ignored;
- [ ] validation occurs too late;
- [ ] config/state can be partially mutated before validation completes;
- [ ] duplicated unit tests repeat accuracy CI instead of protecting a contract;
- [ ] microbenchmark advertised as E2E gain;
- [ ] single/noisy run advertised as stable delta;
- [ ] baseline/candidate conditions differ;
- [ ] quality omitted for an output-changing optimization;
- [ ] failures/skips/sample counts omitted;
- [ ] outlier removed without defensible rule;
- [ ] projection presented as measurement;
- [ ] unrelated cleanup mixed into the diff;
- [ ] narrow smoke presented as broad support.

---

## Non-rules: do not lint by token

`getattr`/`hasattr` — problematic when hiding required invariants; valid for truly optional compatibility fields.

`try/except` — problematic when broken internal state continues as success; valid for expected recoverable failures.

ENV — problematic as hidden serving feature config when typed surfaces exist; valid for bootstrap/process/CI/cache concerns.

Abstraction — problematic when it adds indirection without reducing duplication; valid when repeated real mechanics move into shared code.

Tests — problematic when they duplicate huge accuracy behavior; valuable for shared contracts, lifecycle/concurrency invariants, and focused regressions.

Fail-fast — does not require CI to stop collecting useful diagnostic metrics.

---

## Writing review comments

A useful comment should:

1. state the concrete failure mode or repository inconsistency;
2. explain why it matters;
3. point to precedent/invariant when applicable;
4. request the smallest sufficient fix or evidence.

Avoid vague design criticism, unsupported taste, long redesigns, or narrating the code.

### Templates

**Unnecessary surface**

> This looks like another maintained surface for behavior already available in `<existing helper/path>`. What semantic difference requires it to be separate? If there isn't one, can we reuse the shared path and remove this file/layer?

**Hidden config**

> This changes serving behavior through an environment variable, while comparable options use typed factory/server args. Can we keep this discoverable/config-driven through the existing config surface instead of adding an ENV-only knob?

**Fail-fast invariant**

> This fallback makes a state that should be impossible look supported. If `<condition>` is required by the pipeline contract, defaulting here pushes the failure deeper into serving. Can we validate it at the boundary and fail there instead?

**Broad exception**

> This catches `<exception>` and continues, so a real backend/system failure can leave a partially alive request/process. What recovery state is valid after this exception? If there isn't one, this should fail fast.

**Claim > evidence**

> The current data shows `<local measurement>`, but the PR claims `<broader claim>`. Can we either add the controlled end-to-end evidence for that claim or narrow the wording to the measured scope?

**Benchmark mismatch**

> Baseline and candidate differ in `<condition>`, so this delta is not attributable to the code change. Please rerun them under the same serving condition, ideally back-to-back, before using this as performance evidence.

**Production-path gap**

> The unit test covers the local mechanism, but the changed failure surface is at `<concurrency/router/streaming/abort>` time. A focused end-to-end regression on that path would protect the actual issue without expanding this into a full benchmark matrix.

**Duplicate model-local mechanics**

> This appears to repeat `<shared mechanism>` inside the model. The repository direction is shared framework mechanics with model-specific semantics/hooks. Can this use the shared implementation instead of carrying another copy?

---

## Required output

Return the review in this order.

### 1. Verdict

Exactly one: `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`.

Explain in 2–5 sentences.

### 2. Problem and proposed solution

Concise problem -> mechanism -> intended outcome summary for a reader who has not read the diff.

### 3. Findings

Only defensible findings. Do not manufacture nits.

For each:

```text
[BLOCKER|MAJOR|MINOR|NIT] <path>:<line or hunk>
Finding: <one sentence>
Why it matters: <concrete failure mode / repository cost>
Evidence: <code path, precedent, experiment, or missing proof>
Suggested comment: <ready-to-post GitHub comment>
```

Sort by severity and causal importance.

### 4. Evidence assessment

State what is proven and what is not.

For performance PRs separate:

- micro/local evidence;
- end-to-end evidence;
- accuracy/quality evidence;
- repeat/noise characterization;
- production-condition coverage.

### 5. Minimum additional validation

Ask only for experiments that discriminate a real concern.

For each state:

- hypothesis;
- controlled variables;
- metrics;
- result that resolves the concern.

### 6. Ready-to-post comments

Repeat only comments worth leaving on GitHub, with exact file/line placement when available.

If there are no actionable comments, state that clearly.

---

## Discipline

- Inspect code around the diff, not only patch lines.
- Verify existing abstractions before asking for new ones.
- Verify suspected bugs with code-path reasoning or focused reproduction when feasible.
- Separate fact from inference.
- Separate correctness from taste.
- Separate measurement from projection.
- Separate “works in this test” from “project-supported.”
- Do not demand unrelated benchmark work.
- Do not reward a huge PR description when the diff is incoherent.
- Do not punish a concise PR when a narrow change has sufficient evidence.
- Prefer one precise blocker over ten speculative comments.
