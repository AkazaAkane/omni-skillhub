# Omni maintainer standards

Read this for every review. This combines the user's existing `sglang-omni-review-pr` doctrine with the linked public Omni sources, checked on 2026-10-30, rather than claiming to speak for every maintainer. The severity/verdict and experiment-design guidance below are adopted review conventions, not quotations attributed to a particular maintainer. Resolve current rules from the reviewed revision's `AGENTS.md` and its referenced coding-style document. If source locations move, follow the target tree.

## Keep the request path coherent

[Issue #188](https://github.com/sgl-project/sglang-omni/issues/188) challenges overlapping delegation layers, dynamic interface adaptation, duplicated mechanics, and confusing ownership. Its refactor goals include preserving functionality/performance and reducing new-model onboarding cost. Its old layer names and code-volume targets describe that proposal, not today's required architecture.

Review implication: trace the actual request and find the nearest existing implementation before asking for a new interface. A new layer needs a distinct responsibility; fewer lines alone do not prove a safe refactor.

[Issue #661](https://github.com/sgl-project/sglang-omni/issues/661) identifies duplicated per-model serving optimizations, benchmark lifecycle glue, filler comments, and tests that repeat accuracy CI. It places reusable mechanics in shared runtime code and model semantics in model directories.

Review implication: check existing helpers and shared contracts first. Preserve regression tests that catch lifecycle, concurrency, and boundary failures which accuracy CI does not cover. Do not turn this issue into a blanket ban on unit tests or a mandate to abstract every similarity.

## Configuration has an owner

[The review on #779](https://github.com/sgl-project/sglang-omni/pull/779#issuecomment-4712162612) asks for server arguments instead of environment arguments for serving tuning. This supports using the existing discoverable configuration route. It does not establish a universal ban on environment variables or new flags.

Trace ownership from public input to the executing component. Defaults should be owned once and forwarded through existing typed surfaces. Separate an omitted parameter from an explicit override when a model has different defaults. Bootstrap/CI environment variables may already be the repository convention; verify their role before criticizing them.

## Validate the right model at the right boundary

[The reference-input thread on #1090](https://github.com/sgl-project/sglang-omni/pull/1090#discussion_r3610997291) calls for public request checks before backend dispatch. [The language thread](https://github.com/sgl-project/sglang-omni/pull/1090#discussion_r3611005830) shows how a global enum expansion can admit inputs that another TTS model cannot handle. Follow the replies: the author reports fixes in #1104, including model-scoped language support.

Review implication: public validation must reflect the selected model's actual capabilities. Do not silently ignore, rewrite, or fall back from unsupported semantics. Distinguish recoverable external failures from broken internal invariants; a fallback must have a valid, documented outcome.

## Every retained surface needs a reason

[The artifact thread on #1090](https://github.com/sgl-project/sglang-omni/pull/1090#discussion_r3610888803) questions a model-specific benchmark harness and generated artifacts; the author removes them. [The config thread](https://github.com/sgl-project/sglang-omni/pull/1090#discussion_r3610889749) questions a trivial config; the author keeps required architecture fields and removes a redundant default.

Review implication: ask what durable behavior a file owns. The outcome supports removing unnecessary surfaces while retaining required configuration, rather than deleting all small configs.

## Claims must fit the experiment

[PR #1441](https://github.com/sgl-project/sglang-omni/pull/1441) reports numerical parity and an isolated optimization measurement while explicitly limiting the performance claim to that local operation. It is an author-reported example approved by a maintainer, not independent replication or a universal benchmark protocol.

Review implication: separate local speedups from request latency/throughput, and numerical parity from model quality. For audio, count failed/empty requests, skipped samples, and actual output durations; report distributions when means hide stalls. A single boot does not establish backend/model support.

## Current style and test instructions

At the checked [coding-style snapshot](https://github.com/sgl-project/sglang-omni/blob/a91bcac9d550c41491746de7773efa9432ee2c00/.claude/skills/code-review/coding-style.md), relevant rules include small concrete abstractions, explicit units in names, concrete typing, module-scope imports, sparse useful comments, one configuration owner, shared runtime outside sibling model packages, and tests of public contracts. The document also contains specific formatting/control-flow requirements; read the complete target-branch version instead of reconstructing it from this summary.

Use the target repository's configured checks. When a test needs an accelerator or optional backend, verify its marker and actual CI lane selection; a test that never runs does not provide coverage. Check existing suites before proposing a new test module.

## Comment and severity discipline

Make a comment explain a reachable failure or a demonstrated repository cost. Cite the target code and use history only when it applies. Ask a short question if intent is unclear; otherwise state the issue directly and request a minimal fix. An unresolved question is not automatically a blocker.

Do not infer a current requirement from an old unmerged proposal, an author reply, a bot's review, or an approval with no explanation. Distinguish an absent benchmark from a demonstrated regression. Missing material evidence can justify withholding approval, but must not be described as a reproduced runtime failure.

## Severity and verdict

Use the smallest severity that describes the actual consequence, following the existing review skill:

- **BLOCKER:** reachable wrong output, hang/deadlock, resource leak/corruption, silent semantic fallback, or a realistic invariant violation; also evidence invalidating a headline claim or duplication that defeats the stated refactor purpose.
- **MAJOR:** material architecture/maintenance regression, an important changed production path without sufficient validation, inconsistent serving configuration, or an evidence gap undermining a significant claim. Explain whether it blocks merging and why.
- **MINOR:** localized maintainability, diagnostics, documentation, or test-quality concern that does not undermine the core change.
- **NIT:** local style/naming preference; use sparingly and do not block without an applicable repository rule.

Recommend `REQUEST_CHANGES` for a blocker or blocking major concern, `COMMENT` for actionable nonblocking findings, and `APPROVE` when no actionable merge concern remains within the reviewed scope. An approval recommendation must still disclose untested paths and residual uncertainty. If the user/interface requires priority labels, use its definitions; do not equate this skill's BLOCKER category automatically with P0.

A useful comment states the failure or concrete inconsistency, explains its consequence, cites the relevant code/precedent, and asks for the smallest sufficient fix or evidence. Keep experimental requests discriminating: hypothesis, controlled variables, metric, and the outcome that resolves the concern. Do not demand an unrelated qualification matrix or penalize a concise PR whose narrow change already has sufficient evidence.
