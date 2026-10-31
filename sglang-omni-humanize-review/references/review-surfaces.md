# Omni review surfaces

Use relevant rows to build independent hypotheses before history, then derive three-route search terms. Mechanism words and candidate invariants below are prompts, not established bugs or claims that every mode exists. Confirm the actual contract, guard and reachable trigger at the reviewed SHA; discard an invariant that does not apply.

## Architecture and source routing

The checked [pipeline overview](https://github.com/sgl-project/sglang-omni/blob/a91bcac9d550c41491746de7773efa9432ee2c00/docs/developer_reference/pipeline.md) separates coordinator routing, stage IO/transport, scheduler execution, and model-runner forward work. Stages use a common scheduler surface rather than branching on scheduler type. SGLang-backed AR execution composes with the upstream scheduler; native/backend-specific paths must be traced independently.

| Changed surface / starting paths | Trace and review | Focused evidence when relevant |
| --- | --- | --- |
| API, router, request lowering: `sglang_omni/serve/`, `sglang_omni/http/`, `sglang_omni/client/` | Public parameters to model validation; omitted versus explicit defaults; response shape/status; selected worker capabilities; readiness and disconnect behavior. | Boundary validation, schema compatibility, unsupported model/input rejected before backend work, changed router dispatch. |
| Pipeline/config: `sglang_omni/config/`, `sglang_omni/pipeline/`, `examples/configs/` | Config → factory → stage topology; device placement; fan-in/out; terminal completion; startup failure rollback; ownership of defaults. | Actual config loading and changed lifecycle path; reject invalid placement/topology before partially initializing resources. |
| Scheduling/runner: `sglang_omni/scheduling/`, `sglang_omni/model_runner/` | Admission, queueing, batching, prefill/decode, abort; per-row/request identity; KV/slot allocation and release; shared versus model-local work. | A regression that reaches the changed scheduler; abort before admission/queued/running as implicated; slot reuse after failure; concurrent rows and repeated requests. |
| Relay/process/TP: `sglang_omni/relay/`, `sglang_omni/comm/`, stage IO | Control messages versus tensor ownership; rank-0/follower behavior; same-device versus cross-device transfer; synchronization, lifetime, shutdown, late messages. | Matching transport/topology smoke or concurrency reproduction; abort propagation; no double completion, leaked shared memory, or surviving workers. |
| Model integration: `sglang_omni/models/<family>/` | Registry/checkpoint architecture → pipeline config → request builder → actual runner/decoder; supported inputs, shapes/dtypes/masks; EOS, lengths and sampling; shared mechanics reused. | Documented serving command and affected mode; reference/numerical or quality comparison; unsupported modes rejected; actual candidate dispatch demonstrated. |
| Streaming codec/vocoder/audio output | Chunk order and request identity; sample rate/channels/PCM dtype; codec delay, overlap/trim, final flush; meaningful distinction between empty chunks and a request with no required output. | Decodable output, cumulative duration, last partial chunk/EOS, long input where implicated; interleaved streams; abort with no stale chunk delivered to a new request. |
| ASR/diarization/audio input | Resampling, channel handling, padding/length units, tokenizer/language behavior, timestamps and speaker labels; input and output streaming boundary if supported. | Changed format/duration/language path; WER/CER with explicit dataset/scoring policy, timestamp/speaker checks where changed; empty/short input if relevant. |
| Realtime/Cascade/session paths, when present | Session/turn/generation identity; ordering, backpressure; interruption/truncation; session close/reconnect and state isolation; upstream cancellation reaching ongoing inference. | Exact conversation event sequence or audio replay reaching the affected path; cancellation and recovery; no prior-turn output after interruption. |
| CUDA/compiled/kernel paths | Actual dispatch predicates; capture/replay shapes and addresses; padded versus active rows; warmup/stream ordering; device/precision constraints; fallback semantics. | Dispatch proof and changed kernel/model path on matching hardware; eager/reference comparison; replay across changing lengths/batches, cleanup after abort if affected. |
| MLX/native C++/MPS/XPU paths, when present | Backend selection; import/build boundaries; dtype/quantization/layout; lazy execution and synchronization; buffer and stream lifetime; native/Python API semantics; unsupported modes. | Build plus actual affected-device execution when changed; golden/reference checks with tolerances and sample population; busy/deadline/cancel recovery for server changes. CUDA evidence does not qualify another backend. |
| Memory/cache/offload | Residency by stage; peak versus steady-state allocation; graph-pinned buffers; transfer scheduling; cache key identity and invalidation; retained references after completion/error. | Memory under the affected request/concurrency/length; cold/warm distinctions; repeated-request plateau; correctness and latency with the actual offload setting. |
| Tests/CI/benchmarks/docs | Tests invoke the candidate and meaningful assertions; backend markers map to real CI lanes; benchmark setup is reusable; documented commands/config match source. | Exact CI revision, suite/device/selection, sample/failure/skip counts; observed results separated from commands proposed or copied from history. |

## Mechanism vocabulary and candidate invariants

Use synonyms and actual symbols from the independent code pass; historical owners come from target-tree history. Conditions limit applicability after recall, rather than acting as a mandatory path filter.

| Surface | Mechanism / condition terms | Candidate invariant to verify in current code |
| --- | --- | --- |
| API/router/lowering | capability mismatch, global enum, explicit default, pre-backend validation | A selected model accepts only executable parameters; omitted and explicit values preserve intended semantics. |
| Pipeline/config | partial initialization, rollback, factory forwarding, terminal completion | Validation and failed startup cannot leave inconsistent topology or owned resources alive. |
| Scheduling/runner | late arrival, slot reuse, stale row, exactly-once release, abort race | A cancelled/completed request cannot mutate a reused slot; each resource has one terminal owner. |
| Relay/process/TP | tensor lifetime, fan-in, follower abort, shutdown ordering, IPC | Control and tensor lifetimes agree; leader/follower completion and cancellation do not deadlock or double-complete. |
| Model integration | registry dispatch, checkpoint mapping, padding mask, EOS | The documented route executes the intended model and respects valid lengths/dtypes/output termination. |
| Streaming audio | final flush, empty chunk, truncated tail, codec delay, chunk ordering | Required final audio is delivered once in order; allowed intermediate emptiness is not mistaken for request failure. |
| ASR/diarization | resampling, sample/frame units, timestamp drift, speaker boundary | Length/timestamp units and model input rates remain consistent through conversion and aggregation. |
| Realtime/session | generation identity, late output, truncation, backpressure, reconnect | Prior-turn output cannot escape after interruption into the next active generation. |
| CUDA/compiled | graph replay, state reuse, capture address, active/padded rows | Candidate dispatch and replay use live request state with valid shapes/addresses and initialized buffers. |
| MLX/native/MPS/XPU | lazy execution, synchronization, backend fallback, buffer lifetime | The selected backend truly executes the changed path; asynchronous values outlive their consumers. |
| Memory/cache/offload | cache identity, eviction, retained reference, graph-pinned buffer | Reuse/eviction/offload preserves identity, required residency and release ownership. |
| CI/benchmark/docs | unexecuted test, fallback coverage, noisy calibration, sample exclusion | The claimed path/population matches the actual test or experiment; failures are not silently dropped. |

## Existing integration guidance to consult

- [TTS integration](https://github.com/sgl-project/sglang-omni/blob/a91bcac9d550c41491746de7773efa9432ee2c00/docs/developer_reference/tts_model_integration.md): request builders, shared AR bootstrap/scheduler, typed payloads, and abort cleanup across preprocessing/handoff/AR boundaries. Use the target tree to resolve its current helpers.
- [Configuration](https://github.com/sgl-project/sglang-omni/blob/a91bcac9d550c41491746de7773efa9432ee2c00/docs/developer_reference/config.md): stage/factory parameters, backend/device resolution and rank placement. Check the actual factory signature and config load path instead of assuming YAML fields are enforced automatically.
- For reference encoding, communication, profiling, or a particular model, locate the corresponding target-branch developer guide/cookbook and neighboring working implementation. Docs explain intent; executing code establishes current behavior.

## Evidence by PR type

Adapted from the user's existing `sglang-omni-review-pr` evidence classification. Apply only the relevant rows; these are review criteria, not a reason to run every suite.

| PR type | Evidence that resolves the changed behavior or claim |
| --- | --- |
| Bug fix | Concrete reproduction/issue, root cause, focused regression at the failure boundary, and adjacent behavior preserved. |
| Performance | Controlled baseline/candidate revisions and operating conditions; relevant latency/tail/throughput; quality when output can change; repeats/noise and failure counts; profiler evidence when bottleneck diagnosis is part of the claim. |
| Refactor | Behavior equivalence and shared-contract coverage; concrete reduction in duplication, delegation, or maintenance cost; no speedup claim without measurement. |
| New model/capability | Pipeline mapping and shared-component reuse; public request/config route; supported and rejected modes; documented serving command smoke; E2E quality and performance/reference evidence appropriate to the claimed scope. |
| CI/benchmark/calibration | Actual gated condition and sample population, repetition/contamination policy, provenance, raw reference versus tolerance/slack, post-apply validation, and actionable failure diagnostics. |
| API/config plumbing | Default preservation or explicitly intended change; public option routing to supporting models; early validation; boundary/capability tests and user-facing docs as needed. Accuracy/performance may be N/A with a reason when runtime/model behavior is unaffected. |
| Documentation | Commands and configuration checked against current code; measured claims linked to evidence; no inference requirement unless needed to verify a changed claim. |

For a benchmark-plan review, evaluate whether the proposed controls, population, metrics, and decision thresholds test the stated hypothesis. Label unexecuted experiments as proposals. For mixed PRs, assess each changed claim without repeating identical validation requirements.

## Evidence matched to audio claims

For streaming performance, distinguish time to first audio, inter-chunk gaps/underruns, request completion latency, output duration, and aggregate throughput. State the RTF definition: request wall time per generated-audio second and aggregate audio-seconds per wall-second are different measurements. Record concurrency, prompt/reference lengths, generated lengths, cache state, device, checkpoint, precision, and baseline/candidate revisions.

Choose quality checks that measure the changed output: WER/CER can test intelligibility but not speaker similarity or music quality; bitwise parity may be inappropriate across backends, while loose waveform comparison may miss truncation. Use the repository's established model-specific evaluator and justified tolerances. Never silently drop failed or empty outputs from a quality/performance population.

For an optimization, connect profiler/local evidence to the actual serving path before requesting a broad benchmark. For a lifecycle fix, demonstrate the trigger and recovery invariant. Do not require all rows or a full production matrix for a narrow PR.
