# Kaomoji Overlay

## AI Backend Task Plan

### Task 0 — Hardware & Compute Verification
- Add `backend/check_hardware.py` to enumerate NVIDIA/CUDA details, compute capability, and available VRAM.
- Require at least 4 GB VRAM for quantized runtime mode.
- Generate `backend/hardware_profile.log` on each pre-flight run.
- If CUDA/VRAM requirements are not met, force CPU mode and show warning: **"Consciousness will be slow"**.

### Task 1+
- Existing application tasks continue after hardware pre-flight.

### Task 5 — Plugins & 4-bit Quantization
- `PluginBase` includes `load_model()` hooks and CUDA isolation helpers.
- Plugins load with bitsandbytes NF4:
  - `load_in_4bit=True`
  - `bnb_4bit_quant_type="nf4"`
  - `device_map="auto"`
- Implemented plugins:
  - `backend/plugins/spam_detector.py` (bert-base, quantized where possible)
  - `backend/plugins/ner_detector.py` (distilbert, quantized where possible)

### Task 6.5 — Consciousness & Feedback Loop
- `backend/consciousness.py` provides persistent `ConsciousnessState` + `PerceptionLoop`.
- `backend/storage.py` stores state in SQLite JSON payload so it survives restarts.
- API middleware injects current consciousness state into plugin context.
- `POST /feedback` applies self-reflection updates to learned preferences.

### Task 8 — UI Screens (Metadata Visualization Update)
For Message Detail UI:
- Add a collapsible **Consciousness Debugger** section showing decision rationale.
- Add **Good Analysis** / **Bad Analysis** buttons that call `POST /feedback`.
