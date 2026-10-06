# AW-0176 — native eight-row activation sharing

Hypothesis: share activation collapse across eight rather than four output rows
in unchanged native PTQ decoder to reduce executable matrix cost. Frozen plan
before build; native4/native8/native8/native4 ABBA full real17408x5120 matrix,
captured early layer0 FFN-down input. Packed weights, precision and arithmetic
unchanged. Same AW137/baseadfffbe source copied into isolated row8 directory;
only N_R0_PTQ1_0 changed4→8, archived patch. Release Metal embedded build using
pinned CMake/Ninja. Initial configure failed missing Ninja; logs preserved;
retry explicit CMAKE_MAKE_PROGRAM successful61steps. No deployed runtime edits.

All outputs bitidentical to actual captured/native control, all exits0,
pressure1/growth0 baseline1135.12MiB. Steady medians native1.087/1.136ms versus
candidate1.085/1.123ms, approximately0.17%/1.18% lower cost: insufficient evidence
of actionable improvement amidst uncontrolled cache/timing variability.
First candidate process18.949s including embedded shader compilation and first
iteration52.279ms; retained, not excluded from endpoint cost (none measured).
Independent raw/output/timing/median replay passes. Full source/config/hardware /
OS/thermal/cache/model/artifact provenance in receipt and external plans.

Reject current row8 form as a meaningful component survivor. No endpoint claim,
P1/default/model/task/sampling changes or promotion. Broader candidate-generated
activation, vision/tools and replicated endpoint gates remain unfulfilled.

Raw: /Users/chad/Models/agentwing/evidence/AW-0176. Isolated build/source same
suffix prism-turbo-row8 under external runtime-builds/runtime-sources.
Receipt: evidence/AW-0176-native-row8-screen.json.
Reproduce pinned external configure/build logs, compile AW167 C++ fixture
against candidate ggml-base/ggml-metal libraries, then frozen plan and
python3 scripts/run_bonsai_native_row8.py (refuses completed-summary overwrite).
