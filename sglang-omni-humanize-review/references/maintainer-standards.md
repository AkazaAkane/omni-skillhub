# Contracts, review methods, and historical observations

Keep these layers separate. Only the target revision establishes the current repository contract. Review methods describe how to reason; historical observations generate hypotheses and may include obsolete architecture or accepted exceptions.

## Current contracts: resolve before history

Read the reviewed revision's applicable `AGENTS.md`, referenced coding-style instructions, public interfaces, ownership boundaries and closest working implementations. Subject to the user's instructions, those current sources determine whether a change violates a rule. Cite that actual source when asserting a design inconsistency. Do not substitute a historical style snapshot or a maintainer's identity for a current rule.

The previously checked [coding-style snapshot](https://github.com/sgl-project/sglang-omni/blob/a91bcac9d550c41491746de7773efa9432ee2c00/.claude/skills/code-review/coding-style.md) is a navigation pointer, not certification of today's rules. Resolve its current location through the target's instructions. Likewise, shared runtime ownership must be established from current interfaces/callers before treating model-local implementation as duplication.

## Review methods: stable execution discipline

These methods incorporate the user's existing `sglang-omni-review-pr`; they are adopted review practice, not historical quotations:

- Fix the exact target and trace callers, config and real dispatch before consulting episodes. Record independent invariants and risk hypotheses first. Inspect the whole changed path; green CI and a persuasive PR description do not establish correctness.
- For each invariant, locate validation, reachable violations, fallback semantics, mutation/initialization timing and regression coverage. Trace lifecycle and resource ownership where changed. Interpret exceptions, attribute defaults and environment settings by their actual contract; do not ban tokens or demand universal defensive handling.
- Search actual existing helpers before alleging duplication or asking for abstractions. Establish distinct responsibility and material maintenance cost; neither a small file nor low reuse count alone proves a finding. Keep changes and requested validation causally tied to the stated problem.
- Separate code-derived facts, observed results, author reports, inference, unknowns and proposals. Test the actual candidate, not an unverified fallback. One boot is not qualification; parity is not speedup; local speedup is not E2E improvement; projection is not measurement.
- Check controls, sample/failure counts, variance, quality and claim scope when a measurement matters. Preserve outliers unless a documented invalidation reason justifies exclusion. Reproduce the CI gate's actual conditions and distinguish raw references from slack. Fast runtime failure should preserve available diagnostic metrics.
- Require the applicability and evidence chain in `SKILL.md` before promoting a historical concern. Current-code findings need no precedent. Unknown triggers remain hypotheses; missing proof may challenge a significant claim but is not evidence that a runtime bug occurred.

## Historical observations: read after the independent pass

The following are bounded navigation summaries. Expand the raw episode and relevant linked discussion before using an observation in a finding. The source index and raw/interpretation protocol are in [history-and-sources.md](history-and-sources.md).

| Observation | Source | Scope and exception to check |
| --- | --- | --- |
| Overlapping delegation and repeated mechanics increased onboarding cost in an older architecture. | [Issue #188](https://github.com/sgl-project/sglang-omni/issues/188) | Its layer names and code-volume targets are historical. Establish today's ownership and actual redundant responsibility first. |
| TTS implementations repeated framework mechanics; some tests/comments and benchmark lifecycle glue carried redundant cost. | [Issue #661](https://github.com/sgl-project/sglang-omni/issues/661) | Not a ban on unit tests, model-specific semantics or small helpers. Contract/race regressions may be absent from accuracy CI. |
| A reviewer requested server arguments for serving tuning instead of environment arguments. | [PR #779 comment](https://github.com/sgl-project/sglang-omni/pull/779#issuecomment-4712162612) | Verify the current config owner and author response; bootstrap/process/CI environment conventions may differ. |
| Benchmark artifacts were removed, while required fields of a small config were retained. | [PR #1090 artifact](https://github.com/sgl-project/sglang-omni/pull/1090#discussion_r3610888803), [config](https://github.com/sgl-project/sglang-omni/pull/1090#discussion_r3610889749) | The resolution supports retaining necessary configuration. Small config size is not a deletion rule. |
| A global language enum admitted values another model could not execute; reference checks occurred too late. | [PR #1090 language](https://github.com/sgl-project/sglang-omni/pull/1090#discussion_r3611005830), [validation](https://github.com/sgl-project/sglang-omni/pull/1090#discussion_r3610997291) | Replies report #1104 fixes. Neither a reply nor a merge proves a fix exists at the currently reviewed revision. |
| An author explicitly scoped a local parity/performance experiment away from an E2E RTF claim. | [PR #1441](https://github.com/sgl-project/sglang-omni/pull/1441) | Author-reported evidence, not independent replication or a universal benchmark protocol endorsed by an approval. |

Do not turn repeated reviewer concerns into doctrine. Reviewer identity explains provenance; recency can motivate checking drift but does not automatically overrule an older still-applicable contract. An approval, merge or author saying “fixed” is not a concern-level verified outcome.

## Severity and verdict

Use the smallest severity that describes the actual consequence, following the existing review skill:

- **BLOCKER:** reachable wrong output, hang/deadlock, resource leak/corruption, silent semantic fallback, or a realistic invariant violation; also evidence invalidating a headline claim or duplication that defeats the stated refactor purpose.
- **MAJOR:** material architecture/maintenance regression, an important changed production path without sufficient validation, inconsistent serving configuration, or an evidence gap undermining a significant claim. Explain whether it blocks merging and why.
- **MINOR:** localized maintainability, diagnostics, documentation, or test-quality concern that does not undermine the core change.
- **NIT:** local style/naming preference; use sparingly and do not block without an applicable repository rule.

Recommend `REQUEST_CHANGES` for a blocker or blocking major concern, `COMMENT` for actionable nonblocking findings, and `APPROVE` when no actionable merge concern remains within the reviewed scope. An approval recommendation must still disclose untested paths and residual uncertainty. If the user/interface requires priority labels, use its definitions; do not equate this skill's BLOCKER category automatically with P0.

A useful comment states the failure or concrete inconsistency, explains its consequence, cites the relevant code/precedent, and asks for the smallest sufficient fix or evidence. Keep experimental requests discriminating: hypothesis, controlled variables, metric, and the outcome that resolves the concern. Do not demand an unrelated qualification matrix or penalize a concise PR whose narrow change already has sufficient evidence.
