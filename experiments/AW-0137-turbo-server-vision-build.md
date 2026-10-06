# AW-0137 — Turbo server and full vision build

Retained server build. Hypothesis: integrated compressed model runtime can build
full HTTP server and mtmd vision stack, accepting q8-K/Turbo3/4-V CLI configuration.

Frozen full patch `experiments/runtime-patches/AW-0137-turbo-server.patch` adds
Turbo3/4 cache parsing to AW-0135 model graph. K parser and model context explicitly
reject Turbo V without q8 K (common K parser rejects Turbo K); Turbo2 stays absent
from CLI despite registered ABI. CLI shared allowed-values help currently includes
Turbo in K list even though parser rejects it: help refinement remains outstanding.
No weight/projector/sampler/task/tool permission changes. Source exactPrismadfffbe
plus preserved Atomic074bf826 public MIT routines, original/P1 intact.

Build plan pins patch/source/harness/compiler/tool/host and argv. Release/Ninja/
embedded Metal, common/tools/serverON, tests/examplesOFF, OpenSSLOFF (loopback
HTTP, no HTTPS acquisition claim),targetllama-server/parallel2. Builds mtmd and
all server dependencies, generated UI assets included in binary. Build audit
records server/mtmd existence, server SHA/version and installed Node/npm versions;
source npm lock remains pinned through source revision. Source server reports
basecommitadfffbe, so archived patch/dylib/server hashes identify modified runtime.

`python3 scripts/build_prism_turbo_server.py` exit0. Configure3.593s/build160.407s,
.5s host checks/600s-phase watchdog,pressure1/swap growth0. Build times are not
agent/model speed claims. Output
`/Users/chad/Models/agentwing/runtime-builds/prism-turbo-server` on internal SSD,
M1/16GB/macOS27.0.1. Evidence `evidence/AW-0137-turbo-server-build.json`, raw
`/Users/chad/Models/agentwing/evidence/AW-0137`. Native server startup separately
AW-0138/AW-0139; no functional vision/tool/endpoint admission from compilation.
