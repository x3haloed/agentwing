# AW-0084 — Native Metal packing compatibility

## Status and hypothesis

Tiny compatibility check passed. Pinned installed GGML Metal library can
execute both private packing formats with close component outputs.

## Identities and fixed conditions

Prism runtime source adfffbe41b2cabcd51fff326ab045662265062bb; native libraries
from installed pinned release, exact hashes in evidence. Four matching public
headers downloaded from that commit. Test source in
`experiments/fixtures/bonsai-packing-metal.cpp`. First 64 real sampled blocks
from AW-0083 rearranged as a 64x128 matrix, paired exact PQ2 repack; synthetic
ones, alternating signs, sine and one-hot inputs. No full model or vision
stack loaded; no prompt, sampler or agent task. Apple M1 internal SSD; actual
OS/compiler/thermal identity retained. Exclusive model-owner lock and
preflight; no concurrent inference. Timeout 60s. No sampled host-gate or
performance claim. Source blocks and compiled binary remain outside Git.

## Primary metric and cheap falsifier

Require native Metal compute success, finite outputs and relative L2 between
formats <=1e-4 on this tiny fixture. This is a provisional component
falsifier, not broader fidelity authority or a borrowed model threshold.
Both formats could share an error; independent CPU matmul oracle is next.

## Commands and results

Compile the fixture against the pinned headers and installed libggml,
libggml-base, libggml-metal with clang++ -std=c++17 -O2 and runtime rpath.
Execute with external PTQ/PQ fixture paths; exit 0. Across 256 output values,
relative L2=1.7417e-6 and maximum absolute difference=8.19564e-7. No timing
was scored. Pinned runtime uses embedded Metal library; raw log retained.
Exact source/header/library/binary/fixture/raw hashes and host provenance:
`evidence/AW-0084-native-metal-compatibility.json`. External artifacts under
`/Users/chad/Models/agentwing/evidence/AW-0084/`.

## Limitations and disposition

No independent CPU output oracle, real full projection, actual activation,
accumulated model behavior, unified-memory residency or decode/endpoint rate
validated yet. Keep alternative packing for next fidelity/cost checks; not
promoted. No frozen profile, task, verifier or prior failure changed.
