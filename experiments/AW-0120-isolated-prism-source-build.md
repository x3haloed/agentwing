# AW-0120 — Isolated unmodified Prism source build

## Status and hypothesis

Retained build baseline. Exact publisher runtime source compiles locally with
embedded Metal runtime-source libraries, before modifying it for Turbo cache
integration. This separates host/build failures from subsequent port failures.

## Frozen configuration and reproduction

PrismML-Eng/llama.cpp exact revision adfffbe41b2cabcd51fff326ab045662265062bb,
source tree f701dae3247ff1ba55db24d1fd83dff0cd2edff8, MIT. Shallow exact-revision
fetch into `/Users/chad/Models/agentwing/runtime-sources/prism-turbo`; source
status clean before and after build.274GiB free internal SSD, no deletion.
Task-private Python venv `/Users/chad/Models/agentwing/build-tools` installs
cmake3.31.6/ninja1.11.1.4. Existing user runtimes/launchers are untouched.

Frozen external plan records compiler, OS/hardware, source tree, build commands,
harness hash and tool versions. CMake Release/Ninja, Metal on/embedded source on,
common/tests/examples/tools/server off. Target llama, parallel2. Built into
`/Users/chad/Models/agentwing/runtime-builds/prism-baseline`. All exact argv in
external plan. `python3 scripts/build_prism_source_baseline.py` exit0.

Primary acceptance: configure/build exits0, nonempty built runtime libraries,
pressure<4/swap growth<=1024MiB.600s per-phase timeout,.5s continuous host samples.
No model, weights, task/verifier, sampling, harness/tools/permission changes.
Fixed M1 Macmini9,1/16GB/internal SSD/macOS27.0.1/26A434; Apple Clang21.

## Results and evidence

Configure exit0,3.602s; build exit0,70.998s. Compiles model—including Qwen3.5—
and CPU/BLAS/Metal backends with embedded sources. Six distinct runtime libraries
hashed, aliases recorded. Peak pressure1/swap growth0. These elapsed build phases
are provenance diagnostics, not model/runtime/agent speed claims.
`evidence/AW-0120-prism-source-build.json`; raw evidence, phase logs, acquisition
and host series `/Users/chad/Models/agentwing/evidence/AW-0120`.

## Disposition and limitations

Retain isolated baseline build. New dylib hashes differ from publisher binaries;
no assumption of identical build flags/results or model runtime admission.
Next validate source-built model execution, then preserve this baseline while
porting remapped Turbo cache types/graph/backend support. No Turbo integration,
compressed generation, vision or endpoint qualification yet. P1 and launched
original runtime unchanged.
