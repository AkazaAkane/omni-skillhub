# Editorial Rules

## What Counts as a Major Update

### Include by default

- New publicly usable model family.
- New accelerator/backend support with demonstrated execution.
- Major throughput, latency, TTFT/TTFA, RTF, memory, or concurrency improvement.
- New API or serving capability: streaming, long audio, translation, barge-in, deterministic mode, persistent sessions.
- Deployment-enabling memory or hardware qualification.
- Overload protection or a high-impact correctness/reliability fix.
- Runtime infrastructure reused by several model families.
- Integration that changes how users launch or operate the system.

### Usually omit

- Cosmetic README edits.
- CI permission changes.
- Generated calibration metadata without user-visible behavior change.
- Small refactors with no public impact.
- Test-only reorganizations.
- Open PRs outside the target range.
- Very narrow bug fixes unless they affect data loss, crashes, silent corruption, overload, or common user workflows.

## Release-Level Framing

Prefer the release story over individual implementation chronology:

1. What models became faster or newly supported?
2. What production feature became possible?
3. What hardware/deployment constraint was removed?
4. What reusable runtime capability matured?

## Approved Four-Pillar Language

The canonical compressed summary is:

1. 性能上，Qwen3-ASR、Qwen3-TTS、Whisper、MOSS-TD、Higgs 等核心模型都完成了一轮明显优化，尤其在高并发吞吐、延迟和资源利用率上提升显著。
2. 补齐了 true streaming TTS、长音频 ASR、deterministic inference、realtime barge-in 等关键能力。
3. 增强了消费级 GPU、Intel XPU / Ascend NPU 等硬件支持，同时完善了过载保护和高并发稳定性。
4. Prefill CUDA Graph、pre-LM encoder、KV transfer、MPS-DP / CUDA IPC weight sharing 等能力逐步扩展到完整 Omni serving runtime，并和 SGLang 主项目 CLI 打通。

Use this wording directly when the requested range supports all four points. Adapt only the unsupported entities or scope.

## Claim Verbs

### Safe

- 新增
- 支持
- 完成一轮优化
- 明显改善
- 在验证中达到
- 逐步扩展
- 补齐
- 降低
- 提升
- 增强

### Require strong evidence

- 全面支持
- 完整解决
- 生产可用
- 首次
- 最快
- 最优
- 无损
- 零开销

## Tradeoff Language

State material tradeoffs briefly:

- `deterministic inference`：以吞吐换取跨 batch 的可复现性；通常为 opt-in。
- Prefill CUDA Graph：可能增加启动时间和常驻显存；说明是否 default-on。
- Larger admission limits：可能增加显存或排队压力；配合过载保护解释。
- Consumer-GPU profile：说明是 qualification/configuration，而非所有模型配置都自动适用。
- Experimental accelerator backend：保留 `experimental` 标签。

## Chinese Style

- Keep official English model and feature names unchanged.
- Avoid translating `TTFA`, `TTFT`, `RTF`, `Prefill CUDA Graph`, and `pre-LM encoder` into inconsistent variants.
- Use full Chinese sentences, not fragments copied from PR titles.
- Keep one idea per numbered point in the compressed version.
- Avoid parentheses containing long benchmark detail in WeChat copy.
- Use Arabic numbers only for high-value headline metrics.
- Do not include a table in the default WeChat output.
