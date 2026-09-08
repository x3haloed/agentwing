# AW-0060 — Generic evidence-gathering instruction screen

Hypothesis: a task-independent instruction to establish repository layout and
instructions before file-type filtering, follow relevant references and verify
source-backed conclusions preserves all eight original tasks under the fixed
workspace setup. It contains no task names, answers, filenames or extension
whitelist. Original requested work, tools and reasoning remain available.

Append exactly config/evidence-grounded-prompt.txt's additional paragraph to the
original P1 instruction. Preserve original model bytes, sampling (including 0.5
frequency penalty and 512-token ceiling), tools, permissions, scoring, task
prompts, deadlines and AW-0047 exact runtime. Candidate profile is explicitly
AW0060-evidence-grounded. No modified quantization or truncation repair included.

Primary gate: all eight original tasks succeed with valid protocol and host
gates, in original manifest order. Stop at first failed utility/host/protocol
result, preserve it and mark remaining tasks unattempted. No instruction tuning
or rerun inside this experiment. Navigation alone cannot pass the gate. Even
8/8 only permits expanded development work, not promotion.

This deliberately changes the system prompt and therefore does not satisfy the
frozen matched-prompt promotion requirement. P1 remains untouched. A future
promotion design must explicitly resolve that requirement, preserve the original
P1 anchor and meet all >=25%, capability, resource and protocol gates. Do not
silently call this matched-P1 performance or replace the objective with this
screen. No held-out exposure, favorable path selection or grader changes.

Use AW-0058's fresh-server-per-task, fixed-path archive-by-rename harness and
copied unchanged original grader. Freeze all inputs; record the exact client
command passed to Popen as well as stored prompt. Static admission precedes
screen wall and is not claimed final promotion accounting. Charge staging,
startup, tools and grading; 900-second task and 60-second startup caps. Same
pressure <4 and swap-growth <=1 GiB gates. No concurrent model/build work.

Command: `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_evidence_grounded_screen.py --task all --candidate-plan spec/evidence-grounded-development.json`.

Status: frozen single-instruction capability screen; pending launch.
