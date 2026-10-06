# AW-0158 — isolated bounded rollback server build

## Hypothesis and primary metric

Pinned Prism source plus archived Turbo and rollback-allocation patches builds
as a complete multimodal server without replacing existing artifacts.
Primary metric: source reconstruction, build exit and binary/library hashes.
No inference or performance claim; host memory/rollback fidelity still unproven.

## Configuration and commands

Base Prism commit adfffbe41b2cabcd51fff326ab045662265062bb. Apply AW0137 Turbo
patch then AW0157 isolated ngram allocation patch to a fresh git archive.
Source /Users/chad/Models/agentwing/runtime-sources/prism-turbo-rollback.
Build /Users/chad/Models/agentwing/runtime-builds/prism-turbo-rollback.
Pinned bundled CMake3.31.6/Ninja; AppleClang21, Release, embedded Metal,
OpenSSL off, full server target, tests/examples off, four build jobs.
Exact configure command and raw logs remain external. No model-owning process,
no task/harness/verifier/native sampler/vision/context/P1 change.

## Results and deviations

First setup failed exit128: git apply rejects absolute --directory paths.
Preserve failure; applying from archive cwd succeeds. Archive comparison covers
3531 tracked port files: only intended common/common.h differs, candidate header
matches exact AW0157 prepared header. New files supplied by the archived Turbo
patch remain part of the reconstructed source. Current port and binaries untouched.
Complete server and vision library build passes exit0 (387 build steps).
Terminal receipt seals configure/build commands, version output and all shared
library/server hashes. Source archive lacks Git metadata; displayed revision
is not the provenance authority. Base commit plus patches and reconstruction
check define the source. No inference or measured memory/fidelity admission.

## Evidence and disposition

External frozen plan/configure/build/source-check/failure evidence:
/Users/chad/Models/agentwing/evidence/AW-0158.
No promotion. Build survival alone will not prove actual allocation, rollback
logit/sampler fidelity, protocol safety, complete cost or endpoint utility.
