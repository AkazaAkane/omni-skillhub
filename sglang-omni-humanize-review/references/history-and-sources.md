# Episode data, retrieval, and evidence protocol

## Coverage and provenance

Workflow inspiration: [BBuf's sglang-humanize-review](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/tree/2dd7b5d4d0d0813ba2639826386d73ae81e30809/skills/sglang-humanize-review), inspected 2026-10-30. The user's existing `sglang-omni-review-pr` supplies revision discipline, invariant tracing, scoped claims and discriminating validation. This independently written skill does not vendor the upstream scripts/corpus or private transcript material. The previous Omni architecture/style pointers remain historical navigation aids.

The initial offline snapshot contains **9 whole-discussion envelopes**: PRs #779, #1090, #1104, #1356, #1441, #3173 and #3338; issues #188 and #661. Selection starts from prior Zhao-related sources, includes a linked fix and a few supplemental recent/model/backend examples. It is not all discussions involving Zhao, a statistically representative sample, or a repository-wide crawl. Participant discovery is optional; the schema is independent of reviewer identity. Exact capture times, event range, endpoint pagination/counts, source hashes, selection and missing coverage are in [omni-review-corpus.metadata.json](omni-review-corpus.metadata.json).

## Raw evidence and interpretations are separate

- [omni-review-corpus.jsonl.gz](omni-review-corpus.jsonl.gz) stores one JSON object per complete selected PR/issue envelope. `raw.metadata` preserves its title/body and captured PR head/base; `raw.conversation`, `raw.inline`, `raw.reviews`, `raw.commits` and `raw.files` preserve original REST objects where applicable. Bodies, languages, people/bots, empty review summaries, timestamps, URLs, diff context and comment/review commit IDs are retained without interpretation. This broad envelope avoids losing author replies or treating one comment as a resolved problem.
- [omni-review-corpus.annotations.jsonl](omni-review-corpus.annotations.jsonl) contains separate concern-level interpretations keyed by `episode_id` and `annotation_id`. Multiple concerns can share one raw envelope. Each explanatory field uses `{value, status, source_urls}`; statuses distinguish `observed`, `inferred`, `author_report`, and `unknown`. Tags are explicitly inferred search aids. Unannotated envelopes remain searchable through raw text; annotations are not required for code-grounded findings.
- `sources` records each API endpoint, pagination/counts and capture window. `completeness.endpoint_pagination=complete` certifies only the listed endpoint reads. It does not prove that GitHub exposed deleted/private material, that linked PRs were expanded, or that an individual concern was resolved. Reads are not an atomic snapshot. REST does not certify thread resolved/outdated state; published inline replies retain `in_reply_to_id`.

A concern interpretation should answer these questions, using unknown instead of inventing answers:

| Field | Meaning / evidence boundary |
| --- | --- |
| `background` | What change/problem was under discussion? Cite PR/issue metadata. |
| `code_revision` | Which implementation did the concern address? Use inline `commit_id`/`original_commit_id` and review `commit_id`; top-level comments can have unknown revision. Never assign today's captured head retroactively. |
| `concern` | What failure/cost was alleged, by whom, and supported by which original text? |
| `trigger_invariant` | Trigger and violated contract. Mark a derived mechanism as inferred. |
| `requested_evidence` | Actual reproduction/experiment requested; unknown if none is established. |
| `response` | Author/reviewer rebuttal, modification, experiment or lack of response. Distinguish reports from verified code. |
| `outcome` | Accepted, withdrawn, reported fixed, unresolved or unknown, with supporting replies. Approval/merge is PR disposition, not proof that this concern was resolved. |
| `applicability` | Model/backend/topology/version/architecture assumptions and exceptions; these still need checking against the new target. |
| Provenance | Raw source URLs, annotation version/author/date, and envelope capture/completeness. Interpretations never overwrite raw evidence. |

## Collection, refresh and interruption

The [collector](../scripts/collect_omni_review_corpus.py) uses authenticated `gh api` GETs and Python's standard library. This gives a reusable CLI outside a connected session. In an interactive review, prefer available connected GitHub reads for small live checks; use paginated reads when a connector truncates.

From the skill directory, an explicit bounded refresh is:

```bash
python3 scripts/collect_omni_review_corpus.py \
  --pr 779 --pr 1090 --pr 1104 --pr 1356 --pr 1441 --pr 3173 --pr 3338 \
  --issue 188 --issue 661 --state-dir /tmp/omni-review-refresh-unique
```

Use a new empty state directory for each refresh. Each completed endpoint page is checkpointed; rerun the identical selection with `--resume` after interruption. A resumed attempt reuses its completed pages, so it is not a fresh live check. Do not resume an old attempt to certify new remote state.

A successful refresh replaces selected whole envelopes and retains unselected envelopes. It refetches every selected endpoint from page 1, capturing current edited text and newly visible/deleted comments rather than skipping old comments by creation date. It does not reconstruct a pre-edit version GitHub no longer exposes or keep all earlier published snapshots in the corpus. Preserve a prior corpus externally when comparing versions. Original checkpoint responses remain in that attempt's state directory.

On failure/rate limiting, stop with a nonzero exit and record the incomplete attempt/error in metadata; completed pages remain resumable and the prior published corpus is retained. Do not silently publish partial selected discussions or retry indefinitely. Publication uses a temporary file and rename; corpus/hash metadata can be inconsistent after a process crash between their renames, so verify the recorded hash before use and rerun/resume if mismatched. Changed-file count mismatches fail capture rather than hiding API caps/concurrent changes.

Optional participant discovery selects the union of `commenter` and `reviewed-by` PR queries, then retains **every participant's context**:

```bash
python3 scripts/collect_omni_review_corpus.py --participant zhaochenyang20 \
  --since 2026-10-01 --state-dir /tmp/omni-review-participant-unique
```

This is bounded candidate discovery, not proof of all participation: PR search may miss discussions, edited comments may not update search as expected, and issue discussions need explicit selection. Search pagination/incomplete-results/1,000-result caps are checked; narrow the date window or explicitly select PRs if capped. The initial bundled snapshot used explicit selection, not this discovery mode. Refresh selected older envelopes periodically or when a finding depends on their present state. A capture records visible published state, not all prior comment edits or private/pending/deleted material.

## Three-route retrieval

First record current-code hypotheses, then search the offline corpus using the [search helper](../scripts/search_omni_review_corpus.py):

```bash
python3 scripts/search_omni_review_corpus.py \
  --path sglang_omni/scheduling --symbol SessionRuntime \
  --mechanism 'late arrival' --mechanism 'slot reuse' \
  --mechanism 'exactly-once release' --condition MLX --condition 'CUDA Graph'
```

All routes are OR-unioned: component paths/symbols (including inline/file diff context), failure mechanisms/invariants (raw bodies and separate annotations), and backend/config/experiment conditions. A matching top-level discussion needs no path. Resolve renamed owners from target history, for example `git log --follow -- path/to/file`, instead of copying SGLang path aliases. Use vocabulary from [review-surfaces.md](review-surfaces.md#mechanism-vocabulary-and-candidate-invariants) as prompts, then actual current symbols and synonyms. There are no embeddings or reviewer-identity/recency boosts.

The helper scans the whole supplied snapshot, deduplicates by envelope, and reports scanned/eligible/matched counts and routes. Ranking is lexical mechanism-hit count, then condition-hit count, then component-hit count, with stable ID ties. These scores do not determine semantic applicability or prove a bug. `--limit` bounds navigation results only; inspect further candidates or alternate words when recall is weak. An annotation match remains an inference with provenance, not raw testimony.

Expand any candidate used in a finding, without truncating replies:

```bash
python3 scripts/search_omni_review_corpus.py --expand sgl-project/sglang-omni:pr:1090
```

This prints the entire raw envelope and separate interpretations. Reconstruct relevant inline threads through `in_reply_to_id`, inspect review bodies/states and top-level author responses, and follow linked fixes/rebuttals/counterexamples needed for that concern. A summary, first four comments, empty approval, or merged state cannot establish its outcome. Source rules/invariants outrank timestamp or reviewer identity. Newer exceptions should be considered, not automatically accepted.

## Applicability, evidence gates and degradation

For each historical concern considered, record shared mechanism, current corresponding code at the target SHA, reachable trigger, concrete consequence, material differences/counterexamples, and the minimum fix/check. Classify `applicable`, `inapplicable`, or `unknown`. Only the chain in `SKILL.md` permits a historical concern to support a finding. An applicable mechanism can still be guarded correctly in current code; search for that refutation. Unknown trigger/context stays a hypothesis or a narrowly stated evidence gap. Independently proven current bugs need no historical precedent.

Daily review uses offline evidence with capture dates; perform live checks only for material stale/missing replies, linked resolutions, target-specific newer exceptions, or recent subsystem changes. Report missing access/pagination/context. If the snapshot is absent/corrupt, the hash differs, no candidates match, or live history is unavailable, continue current-code analysis and disclose the relevant limit. Widen synonyms/routes before assuming no precedent. Do not manufacture a historical synthesis or block a useful review solely on missing history.

## Evaluate judgment, not report richness

No review-quality improvement has been measured for this version. Mechanical tests validate capture/retrieval behavior, not finding precision. A later equal-time-budget comparison should hold out target PRs from raw data, interpretations, linked fixes and retrieval results; `--exclude-pr` prevents direct target retrieval/expansion but does not detect indirect answer leakage. Remove future fix/review references in other envelopes too. Use an archived pre-review target/code snapshot: today's PR body/edited comments cannot reliably reconstruct an earlier review state.

Compare the previous skill against this one on both consequential-bug and clean PRs. Record independently confirmed findings and consequences, false positives/irrelevant test requests/style disputes, obsolete-contract applications, whether proposed validation discriminates the hypothesis, and total review time. Keep budgets and available target artifacts equal. Count citations/report length only as cost, never success. Do not claim success from the included seeds or known historical outcomes, and do not build embeddings or expand the corpus until observed recall/decision failures justify them.
