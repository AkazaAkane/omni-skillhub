# Evidence Workflow

Use this workflow to convert a release range into a defensible editorial summary.

## Source Priority

Use sources in this order:

1. Target branch or release tag code and metadata.
2. Merged PR final body, final commits, and final review discussion.
3. Attached benchmark artifacts or reproducible final-head results.
4. Related issues and roadmap descriptions.
5. Prior summaries only as discovery aids, never as the final evidence source.

A PR's early benchmark or stale body text must not override later final-head validation.

## Range Collection

### Local repository path

```bash
git fetch origin --tags
git rev-parse <base>
git rev-parse <target>
git log --first-parent --merges --oneline <base>..<target>
git log --first-parent --format='%H%x09%ad%x09%s' --date=short <base>..<target>
```

Map merge commits to PR numbers. Use `gh pr view` or the GitHub API to retrieve the final title, body, labels, merge commit, and discussion.

### GitHub-only path

- Resolve the repository and current default branch.
- Resolve base and target tags/SHAs.
- Search commits in descending date order for the range.
- Search merged PRs associated with those commits.
- Fetch the full PR when the title alone is insufficient.
- Fetch final comments/reviews when the PR body contains outdated or disputed results.

## Candidate Evidence Table

Build this table privately before drafting:

| Candidate | PR | Merged in range | Category | User impact | Final metric | Baseline/context | Quality evidence | Status/default | Caveat | Include |
|---|---:|---:|---|---|---|---|---|---|---|---:|
| Whisper pre-LM encoder | #1497 | Yes | Performance/runtime | Moves encoder off LM admission | +82.9% c16 | H200, Whisper-base, full SeedTTS EN | WER preserved | Default-on | Separate baseline from later cache work | Yes |

The table is an internal working artifact. Do not paste it into the default WeChat output.

## Validation Questions

For every candidate, answer:

1. Was it merged between the exact base and target?
2. Does the target branch still contain the behavior?
3. Is the feature default-on, opt-in, experimental, or qualification-only?
4. What exact user problem does it solve?
5. Is the performance claim final-head, current-base, or historical?
6. What hardware, model size, dataset, concurrency, and topology produced the number?
7. Was accuracy, WER, quality, output parity, or functional correctness checked?
8. Is there a tradeoff such as startup time, VRAM, TTFA, determinism cost, or lower light-load performance?
9. Does another PR supersede, absorb, or invalidate this story?
10. Can this be consolidated with adjacent work into a clearer release-level narrative?

## Metric Integrity Rules

- Never add percentage improvements from different PRs or baselines.
- Do not compare absolute QPS across different hardware as if it were an A/B result.
- Distinguish component microbenchmarks from end-to-end serving results.
- Treat one-run or noisy results cautiously.
- Report the final supported conclusion, not the largest number in the PR body.
- Preserve “within variance,” “directional,” “opt-in,” and similar qualifiers.
- If a feature is behavior-preserving, do not invent a throughput claim.
- If exact output parity is not expected, use the reported quality metric rather than implying byte identity.

## Consolidation Examples

### Good

> Whisper 完成了从请求构建、prefill 合并、Encoder CUDA Graph 到 pre-LM encoder 和缓存优化的一轮系统性升级，中高并发吞吐和延迟均明显改善。

### Too fragmented

> #1412 加了 graph，#1485 加了 coalescing，#1497 加了 pre-LM，#1553 加了 async，#1585 改了 cache，#1591 加了 pinned memory。

### Good

> Omni runtime 的 Prefill CUDA Graph、KV transfer、MPS-DP 和 CUDA IPC weight sharing 已从单点优化逐步扩展为可复用的 serving 基础设施。

### Overclaim

> SGLang-Omni 已经完成所有分布式 Omni serving 能力。
