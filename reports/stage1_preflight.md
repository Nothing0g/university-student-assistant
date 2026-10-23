# Stage 1 pre-flight report

Date: 2026-10-23

## Results

- Python foundation tests: run locally with `pytest -q`; the implementation includes four contract tests.
- Ollama availability/model pull: **not run successfully in this environment**. No Ollama service or pulled `qwen2.5:7b-instruct` model was available to verify.
- Structured JSON inference: **not tested** because the configured local model was unavailable.
- Cloud fallback: disabled by design (`ALLOW_CLOUD_FALLBACK=false`).

No claim is made that real Ollama inference works until the model is installed and the pre-flight is rerun.
