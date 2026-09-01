---
name: sglang-omni-release-note
description: Create evidence-based SGLang-Omni release highlights and concise Chinese WeChat announcements for a tag, commit, or date range. Use when summarizing major model support, performance improvements, serving features, hardware coverage, runtime infrastructure, and reliability changes. Default to a four-pillar WeChat summary; rely on GitHub automatic release notes for exhaustive PR lists unless the user explicitly requests a manual changelog.
---

# SGLang-Omni Release Note Skill

Create a human-readable summary of the most important SGLang-Omni changes in a release range. Optimize for accurate editorial synthesis rather than a raw list of merged pull requests.

## Quality Contract

A strong result must:

- define the exact base and target, such as `v0.1.1 -> main` or `v0.1.2 -> v0.1.2.post1`;
- use only changes merged into the target range;
- distinguish measured results, design intent, and inference;
- preserve model names, feature names, defaults, opt-in status, hardware, concurrency, and material caveats;
- avoid adding percentages from different baselines or benchmark configurations;
- prefer a few representative metrics over a dense benchmark dump;
- explain user impact, not merely implementation details;
- keep GitHub's automatic release notes as the exhaustive changelog when that is the project policy;
- produce polished Chinese suitable for WeChat by default.

## Inputs

Collect or infer these inputs before writing:

| Input | Required | Notes |
|---|---:|---|
| Base tag/commit | Yes | Example: `v0.1.1` |
| Target tag/commit | Yes | Example: `main`, a release tag, or an exact SHA |
| Output mode | No | Default: `wechat-four-pillar` |
| Language | No | Default: Chinese, retaining official English model/feature names |
| Length | No | Default: 4 numbered points plus an optional one-sentence opening |
| Audience | No | Default: SGLang/Speech/ML systems community |
| Include PR numbers | No | Default: omit from WeChat; retain in internal evidence |

Do not repeat a question when the range or audience is already available from the conversation.

## Output Modes

### `wechat-four-pillar` — default

Write a concise Chinese summary using the four approved editorial pillars below. This is the preferred mode when GitHub will auto-generate the detailed release notes.

### `wechat-expanded`

Write a medium-length Chinese announcement with short sections for performance, models/hardware, serving features, and runtime/reliability. Keep it editorial, not exhaustive.

### `github-editorial-intro`

Write only the title, opening paragraph, highlights, and closing paragraph that sit above GitHub's automatically generated PR list.

### `manual-detailed`

Produce a categorized Markdown release note with representative metrics and PR references. Use only when explicitly requested.

## Default Editorial Frame

The default WeChat summary should communicate these four points:

1. **Core-model performance:** Qwen3-ASR, Qwen3-TTS, Whisper, MOSS-TD, Higgs, and other major models completed a meaningful optimization cycle, especially in high-concurrency throughput, latency, and resource utilization.
2. **Serving capabilities:** true streaming TTS, long-audio ASR, deterministic inference, realtime barge-in, and similar production-facing capabilities were added or completed.
3. **Hardware and stability:** consumer GPUs, Intel XPU, Ascend NPU, overload protection, and high-concurrency stability were expanded.
4. **Omni runtime:** Prefill CUDA Graph, pre-LM encoder, KV transfer, MPS-DP / CUDA IPC weight sharing, and SGLang CLI integration increasingly form a complete Omni serving runtime.

Preserve these pillars unless the evidence in the requested range does not support one of them.

## Default Workflow

### 1. Freeze the range

Resolve the exact base and target. Record the cutoff date and target SHA internally. Never mix open or unmerged work into a release summary unless the user explicitly asks for a roadmap section.

### 2. Build a merged-change inventory

List merged PRs or first-parent merge commits in the range. Capture:

- PR number and title;
- merge commit/date;
- affected model or subsystem;
- feature/performance/reliability category;
- user-visible impact;
- final benchmark and correctness evidence;
- default, opt-in, experimental, or qualification-only status;
- important caveats.

Use `references/evidence-workflow.md` for the collection procedure and evidence table.

### 3. Select only material updates

Promote a change when it materially affects at least one of:

- supported models or accelerators;
- throughput, latency, TTFT/TTFA, RTF, memory, or concurrency ceiling;
- public serving APIs or streaming behavior;
- deployment topology or hardware accessibility;
- overload handling, correctness, lifecycle safety, or high-concurrency reliability;
- reusable runtime infrastructure that enables multiple model families.

Usually exclude cosmetic documentation, CI permissions, generated metadata, minor refactors, and narrow test-only changes unless they unlock or protect a public capability.

### 4. Consolidate related PRs into one story

Do not turn the output into “PR soup.” Combine related work into model- or capability-level narratives, for example:

- Whisper: request construction + prefill coalescing + Encoder CUDA Graph + pre-LM encoder + cache improvements;
- Qwen3-TTS: AR host-work reduction + overload control + playback continuity + deterministic inference;
- Omni runtime: Prefill CUDA Graph adoption + KV transfer + weight sharing + unified CLI.

When multiple PRs use different baselines, report them as separate improvements or use qualitative wording. Never sum their percentages.

### 5. Choose representative evidence

For each major performance story, select at most one or two metrics that are:

- measured on the final or clearly identified candidate;
- compared against a valid baseline;
- relevant to the user-visible claim;
- accompanied by hardware and concurrency when needed;
- accuracy- or quality-qualified.

Prefer statements such as:

> Qwen3-TTS 在 H100 的优化配置下从 10.71 QPS 提升到 16.15 QPS，同时 c64 TTFA p95 从 4.76 秒降至 0.54 秒。

Avoid vague or cumulative claims such as:

> 多个优化叠加后性能提升超过 100%。

### 6. Draft the WeChat message

Default structure:

- optional one-sentence opening identifying the range;
- four numbered points following the approved pillars;
- optional one-sentence conclusion describing the shift from model enablement to a more complete production serving runtime.

Keep official model and feature names in English. Use Chinese for explanation and transitions.

### 7. Run the final audit

Before returning the result, verify:

- every named model/feature is inside the release range;
- opt-in and experimental features are not described as defaults;
- benchmark percentages match their stated baseline and concurrency;
- WER/quality parity is not claimed without evidence;
- high-concurrency or hardware-specific results are not generalized universally;
- GitHub auto-generated notes and the WeChat summary are not duplicating each other unnecessarily;
- the output covers the important update classes without becoming exhaustive.

## Writing Rules

- Lead with impact, then name the mechanism.
- Prefer “完成一轮明显优化”“提升显著”“逐步扩展” over unsupported superlatives.
- Do not claim “production-ready,” “first,” “best,” or “fully supported” without explicit evidence.
- Preserve labels such as `experimental`, `opt-in`, `qualification-only`, and `disabled by default`.
- Spell `true streaming TTS` when distinguishing incremental generation from buffered or post-hoc chunking.
- Use `realtime barge-in`, `deterministic inference`, `Prefill CUDA Graph`, `pre-LM encoder`, `KV transfer`, `MPS-DP`, and `CUDA IPC weight sharing` consistently.
- Use no more than three headline numbers in the default four-point WeChat version.
- Omit PR numbers and raw URLs from the WeChat copy unless explicitly requested.
- Do not end with a generic call to action.

## Default Output Contract

Unless the user requests another mode, return only the polished WeChat copy. Do not include the evidence table, research process, or discarded candidates.

Use the canonical example in `examples/v0.1.1-to-current-wechat.md` as the style and compression target, not as a fact source for a different release range.

## Progressive References

Read only the references needed for the task:

| Need | Reference |
|---|---|
| Collect and validate merged changes | `references/evidence-workflow.md` |
| Decide what to include and how to word claims | `references/editorial-rules.md` |
| Produce a specific output shape | `references/output-templates.md` |
| Match the approved v0.1.1-to-current WeChat style | `examples/v0.1.1-to-current-wechat.md` |
