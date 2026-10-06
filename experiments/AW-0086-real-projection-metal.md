# AW-0086 — Full real projection shape Metal fidelity

## Status and hypothesis

Passed component fidelity screen. Exact packing alternative survives native
Metal execution on full FFN-up projection shapes across early/middle/late
layers, with sampled independent CPU dot-oracle checks.

## Configuration identities and fixed conditions

Pinned model artifact hash `53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3` verified before reads,
Prism runtime adfffbe; native/header/library provenance inherited and verified
from AW-0084/AW-0082. Full real blk.0/31/63.ffn_up tensors, each 5120x17408,
exact native repack. Native repacker matches Python on all 2010 AW-0083 sampled
blocks and rejects invalid length/capacity. Original full model unchanged.
Four synthetic inputs (ones, alternating, sine, one-hot), no captured model
activations or Hadamard transform. Exclusive model-owner lock, internal SSD,
fixed M1; actual OS/thermal/host recorded. Existing pressure<4 / swap+1024MiB
gates checked during native operations; 150s timeout per process. No task,
prompt, sampling or inference-speed claim applies to these projection checks.

## Primary metric and cheap falsifier

Require successful finite native outputs and mutual relative L2<=1e-4 across
all outputs. Check 32 evenly spaced rows per tensor against pinned CPU decoder
and independent math.fsum dot calculation for all four patterns, same limit.
This provisional component falsifier is not broad model acceptance authority.
Frozen selection/source/binary pins recorded externally before execution.

## Commands and results

Build native repacker and full-shape Metal fixture with clang++ -std=c++17
-O2 against pinned native libraries. Run
`python3 scripts/check_bonsai_real_projection_metal.py`. All three projections
pass. CPU-oracle relative L2 ranges about 1.16e-6 to 1.91e-6. Pressure peak
1, swap growth 0 MiB.
No timing was scored. All frozen sources/raw artifact hashes independently
recomputed after execution. Small summary in
`evidence/AW-0086-real-projection-audit.json`, SHA-256 `4edaf8d5446b97d45a1d7773baa4f33e888f0878f74b98c3321f24762c2fe12c`;
raw evidence including frozen plan, binaries, real tensor fixtures, native
outputs/logs/pressure and recursive hashes under `/Users/chad/Models/agentwing/evidence/AW-0086`.

## Limitations and disposition

Independent CPU oracle samples 32 rows; mutual comparison covers every output.
Only FFN-up operation family and synthetic inputs tested. Actual transformed
activation distributions, attention/down projections, candidate accumulated
behavior, full artifact integrity and complete physical cost remain open.
Only pressure during native work/phase boundaries sampled, not a continuous
full-inference admission. No endpoint or runtime throughput result implied.
Retained for those next gates, not promoted. AW-0080 failure preserved.
