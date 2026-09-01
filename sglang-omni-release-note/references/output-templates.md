# Output Templates

## Template A — WeChat Four-Pillar Summary

```markdown
从 <base> 到 <target>，SGLang-Omni 最近的重大更新可以概括为四点：

1. 性能上，<core models> 等核心模型都完成了一轮明显优化，尤其在高并发吞吐、延迟和资源利用率上提升显著。
2. 补齐了 <major serving features> 等关键能力。
3. 增强了 <hardware coverage>，同时完善了 <stability capabilities>。
4. <runtime infrastructure> 等能力逐步扩展到完整 Omni serving runtime，并和 <integration> 打通。
```

Use one optional closing sentence only when it adds a real release-level conclusion:

```markdown
整体上，这一阶段的重点已经从“支持更多模型”进一步转向“把多模态和语音模型更高效、稳定地 serve 起来”。
```

## Template B — Expanded WeChat Announcement

```markdown
**SGLang-Omni <range> 重大更新**

最近一轮更新的重点不只是增加模型覆盖，而是系统性提升 ASR、TTS 和 Omni workload 的 serving 性能，并补齐实际部署需要的能力。

**性能优化**
<2-4 sentences consolidating the most important model stories and no more than three metrics.>

**新模型与硬件**
<new models, consumer GPU profiles, Intel XPU, Ascend NPU, quantization/offload.>

**Serving features**
<true streaming TTS, long-audio ASR, translations, deterministic inference, barge-in, overload protection.>

**Runtime**
<Prefill CUDA Graph, pre-LM encoder, KV transfer, MPS-DP/CUDA IPC weight sharing, CLI integration.>

<one restrained concluding sentence>
```

## Template C — GitHub Editorial Intro Above Auto-Generated Notes

```markdown
# SGLang-Omni <version>

This release focuses on <one-sentence scope>.

## Highlights

- **Performance:** <one compact synthesis>
- **Serving capabilities:** <one compact synthesis>
- **Models and hardware:** <one compact synthesis>
- **Runtime and reliability:** <one compact synthesis>

The complete merged pull-request list is generated automatically below.
```

## Template D — Manual Detailed Release Note

Use only when explicitly requested:

```markdown
# SGLang-Omni <version>

<introduction>

## Highlights

### Performance
- **Model:** impact, representative metric, correctness qualifier, PR.

### New Models and Hardware
- New model/backend/qualification.

### ASR Features
- Public ASR capability.

### TTS and Realtime Serving
- Public TTS/realtime capability.

### Runtime and Reliability
- Reusable runtime or high-impact reliability change.

---

<release-level conclusion>
```

Do not use Template D merely because many PRs exist. GitHub automatic release notes are preferable for exhaustive enumeration.
