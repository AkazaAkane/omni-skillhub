# Historical evidence and source coverage

## Provenance and limits

Workflow inspiration: [BBuf/AI-Infra-Auto-Driven-SKILLS, sglang-humanize-review](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/tree/2dd7b5d4d0d0813ba2639826386d73ae81e30809/skills/sglang-humanize-review), revision `2dd7b5d4d0d0813ba2639826386d73ae81e30809`, inspected 2026-10-30. This adaptation is independently authored; it does not vendor the upstream scripts, prose, SGLang corpus, or BBuf supplement.

The Omni evidence below was retrieved on 2026-10-30. It is a curated index of two issues and three PRs, not a downloadable episode dataset, repository-wide sweep, or statistical account of maintainer behavior. Current architecture/style pointers use Omni revision `a91bcac9d550c41491746de7773efa9432ee2c00`; actual reviews must resolve the reviewed revision.

The user's existing `sglang-omni-review-pr/SKILL.md` supplies the review doctrine: reuse/deletion, invariant tracing, fail-fast versus diagnostic completeness, support-claim scope, PR-type evidence, outlier/calibration handling, severity/verdict conventions, and minimum discriminating validation. Its `REFERENCES.md` helped identify the public sources below, which were checked directly. Relevant rules are incorporated into this skill so the sibling is not a runtime dependency. Its private transcript-based rationale is not included as public historical evidence. The new output preserves comprehension and historical synthesis before the prior skill's verdict/findings/evidence/validation/comment structure.

## Seed sources

Select only sources relevant to the changed mechanism. Read linked threads and their replies live when using them as evidence; the summaries are navigation aids.

| Source | Evidence type / attribution | Relevant concern and observed outcome |
| --- | --- | --- |
| [Issue #188](https://github.com/sgl-project/sglang-omni/issues/188) | Refactor proposal by `zhaochenyang20`, created 2026-03-24. | Overlapping layers, duplicate concepts/mechanics, preservation of behavior/performance. Treat its architecture as historical, not today's call graph. |
| [Issue #661](https://github.com/sgl-project/sglang-omni/issues/661) | Refactor epic by `zhaochenyang20`, created 2026-06-02. | Shared mechanics versus model semantics; reusable benchmark lifecycle; filler comments and redundant tests. Its task table is historical, not proof of current implementation status. |
| [PR #779 config comment](https://github.com/sgl-project/sglang-omni/pull/779#issuecomment-4712162612) | Top-level review concern from `zhaochenyang20`. | Requests serving arguments rather than environment arguments. Read author follow-ups/config changes before asserting the final resolution. |
| [PR #1090 artifact thread](https://github.com/sgl-project/sglang-omni/pull/1090#discussion_r3610888803) and [config thread](https://github.com/sgl-project/sglang-omni/pull/1090#discussion_r3610889749) | Inline review by `zhaochenyang20`, 2026-07-19; author replies; request-changes and later approval. | Author removes benchmark harness/artifacts, retains required config fields, removes redundant default. Final disposition matters: this was not a ban on small config files. |
| [PR #1090 validation thread](https://github.com/sgl-project/sglang-omni/pull/1090#discussion_r3610997291) and [language thread](https://github.com/sgl-project/sglang-omni/pull/1090#discussion_r3611005830) | Inline review by `SandyLuXY`, 2026-07-19; subsequent author replies. | Pre-backend reference validation and model-specific language support; replies report fixes in #1104. A reply is a reported resolution; check code before claiming that fix exists at another revision. |
| [PR #1441](https://github.com/sgl-project/sglang-omni/pull/1441) | Author-reported optimization/parity experiment; approved by `zhaochenyang20` on 2026-08-10. | Local measurement explicitly scoped away from E2E RTF. Approval alone does not turn every implementation/test detail into a general rule. |

## Retrieve evidence for a review

Use connected GitHub tools when available: search PRs/issues, then fetch the selected PR, changed files, and its combined conversation/inline/review timeline. Check whether the returned timeline is complete. If a connector truncates, use paginated GitHub API reads. Repository files must be read at the target head SHA.

With an authenticated `gh` CLI, these read-only examples retrieve the three episode types for one seed PR; replace the number for the selected candidate. `--paginate --slurp` keeps every returned page. Store temporary output outside the reviewed working tree when useful.

```bash
gh api --paginate --slurp 'repos/sgl-project/sglang-omni/pulls/1090/comments?per_page=100'
gh api --paginate --slurp 'repos/sgl-project/sglang-omni/issues/1090/comments?per_page=100'
gh api --paginate --slurp 'repos/sgl-project/sglang-omni/pulls/1090/reviews?per_page=100'
```

For inline threads group by `in_reply_to_id`, retaining path, hunk, line/original line, reviewer, timestamps, original body and URL. Read all replies in the relevant group. Conversations may refer to several topics; review submissions may be empty but still record request-changes/approval state. An empty approval provides disposition, not rationale.

Find more recent or more specific candidates by combining model/helper/scheduler names with risk terms. Example searches:

```bash
gh search prs --repo sgl-project/sglang-omni 'vocoder abort' --sort updated --limit 30
gh search prs --repo sgl-project/sglang-omni 'MLX cancellation' --sort updated --limit 30
gh search issues --repo sgl-project/sglang-omni 'reference encoding' --sort updated --limit 30
```

These searches return bounded candidate lists and do not exhaustively search every review comment. Use file history to find same-path changes when keyword search misses them, and inspect discussion bodies before accepting a match. When paths were renamed, resolve historical owners using target-tree history, for example `git log --follow -- path/to/file`; do not reuse SGLang's path aliases for Omni.

Search a relevant subsystem plus its demonstrated failure mechanism, then retrieve the selected discussions in full. If nothing relevant appears, widen once to the shared component or model family. Stop when the relevant discussions and newer counterexamples have been assessed, or explain the access/search limit; do not recrawl the whole repository for every small patch. A complete read of selected PRs is still bounded repository coverage.

## Synthesis to include in the review

Report the search date and terms, selected PR/issue numbers, number/type of episodes actually read when countable, date range, and whether pagination was complete. Do not report corpus-wide `scanned/matched` statistics without a real corpus scan. Never claim completeness just because a search result hit its configured limit.

Summarize recurring concerns, requested fixes/experiments, author responses, and final disposition. Include newer disagreements instead of treating age or reviewer identity as automatic precedence. Current target-branch rules and executable contracts determine applicability.

If GitHub is inaccessible, report that live history was unavailable. Use the seed summaries as historical context with that limitation and perform the available code review. Never block a useful correctness review solely because a historical sweep cannot run, and never present summarized or unseen comments as freshly retrieved quotations.
