# Phase 1 — Qualify the model on the shared path

Read this when starting a new model, or when a PR claims a model "works with prefill CUDA graph."

Two parts: inspect before touching code, then prove replay from runtime evidence.

## 1. Inspect the model

Identify each of these before designing anything. Missing one is the usual root cause of a model-specific patch that turns out to be unnecessary:

- generation engine builder;
- model / model runner used during prefill;
- `forward()` **and** the lower-level module actually captured by Prefill CUDA Graph — these are frequently not the same, and the gap is where semantic bugs live;
- `max_prefill_tokens`;
- `chunked_prefill_size`;
- multimodal embedding path, if any;
- M-RoPE or other position metadata;
- hidden-state / output side channels;
- model-local encoder CUDA Graph or `torch.compile` paths.

That last item is a distinct mechanism. LM Prefill CUDA Graph is not the encoder graph, the decoder graph, the vocoder graph, or a compiled region. Qualify them separately and do not attribute one's gains to the other.

## 2. Read the prior adopters first

Each existing adopter already answers a question you are about to ask. Look at the closest match before writing anything:

| Adopter | What it demonstrates |
|---|---|
| Higgs-TTS | Platform / payload-contract example |
| Fun-ASR | Minimal direct adopter — the baseline shape of a correct change |
| MOSS-Transcribe-Diarize | Minimal adopter with padded-shape numerical differences |
| Qwen3-ASR | Case where the captured path bypassed required `forward()` logic |
| Qwen3-Omni | Case requiring a bounded `OmniPrefillInputs` adopter, and remaining opt-in |

If your model resembles one of these, the expected diff probably resembles that adopter's diff. A much larger diff needs a stated reason.

## 3. Prove the shared path works — before implementing anything

Run the model with the upstream breakable backend enabled and a small explicit bucket set that covers one real request. Configuration only. No model edits yet.

Verify from runtime evidence, not from inference about the code:

- capture completes;
- the request reaches graph admission;
- `can_run_cuda_graph` (or the equivalent admission check) succeeds;
- at least one actual prefill executes by graph replay;
- the request completes successfully;
- disabling Prefill CUDA Graph returns to the eager path.

**A successful capture alone is not sufficient.** Capture proves the shapes are capturable; it says nothing about whether admission accepts real batches. Models routinely capture every configured bucket and then fall back on 100% of production traffic. Prove replay.

## Gate

You may leave phase 1 when you can point at evidence of a real graph replay of a real request, and evidence that disabling the graph restores eager execution.

If the model already replays correctly, **do not change its forward path.** Go to `capture-budget.md` and then straight to the direct-adopter pattern.

If replay does not happen, capture the admission-refusal reason before moving on — the reason determines whether phase 3 is a small input fix (`graph-semantics.md`) or a no-go (`adopter-patterns.md`, case C).
