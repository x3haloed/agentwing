# Bonsai 2 local inference

Agentwing's new local strategy uses Ternary Bonsai 2 27B PTQ1_0 and its Q8
vision projector on PrismML's llama.cpp Metal backend. All model inference,
including image encoding, runs on this Mac. Exact revisions, hashes and settings
are in `spec/bonsai-local.json`; AW-0062 preserves the failed initial admission; AW-0063 records corrected admission evidence.

Acquire or verify the pinned runtime and both weight artifacts:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/setup_bonsai.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_agent.py --check-only
```

For local chat and image uploads, start the guarded loopback server:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/bonsai_server.py
```

Open http://127.0.0.1:8080. The OpenAI-compatible API is available at
http://127.0.0.1:8080/v1. Pi can connect using `scripts/pi-bonsai.sh`.
Stop the server with Ctrl-C before running the managed agent launcher:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_agent.py \
  --workspace /absolute/path/to/project \
  --task-file /absolute/path/to/task.txt
```

Add `--image /absolute/path/to/image.png` to attach a local image (repeat for
multiple images). Attachments are preserved and hashed alongside the task.

This launcher preserves a copy, applies the existing workspace-write and
loopback-outbound boundary, owns both process groups, and monitors memory pressure
and swap. Inspect the copied workspace before applying its changes. Build outputs,
Git metadata, node_modules and .venv are excluded from the copy. Completion is an
unscored user-task result.

Initial operating limits: one active rollout, 8192 context tokens, FP16 KV,
2048 maximum Pi output tokens, medium reasoning effort. Large images are capped
at 1024 vision tokens; this downscales fine details and can affect OCR. The full
vision stack is loaded, but this profile does not claim full 262K context or
uncapped-image admission on the 16 GB host. Stop on critical pressure (level 4)
or more than 1024 MiB swap growth. Another model-owning process must be stopped
before launching this configuration.

Repeat admission checks with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/probe_bonsai_local.py
```

Functional admission is separate from autonomous work-rate promotion. Historical
Swiftlet/P1 launchers and frozen benchmark configurations remain reproducible
controls. Publisher throughput and benchmark scores are not local endpoint results.

Admission passed twice with zero swap growth (pressure peak 2). Managed Pi image
attachment also passed with zero swap growth (pressure peak 1). See
`evidence/AW-0063-admission-audit.json` and `evidence/AW-0063-managed-vision.json`.
