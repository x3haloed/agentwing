# AW-0122 — Initial remapped type registration build failure

Rejected patch. First isolated Turbo registration adds internal144/145/146 IDs
while preserving original42/142/143 and increases count147. Copies Atomic KV
block definitions/prototypes and complete CPU codec file into Prism base build.
Frozen patch/hash/source baseline/commands in external plan. CMake configuration
passes; build exits1 because full Atomic file additionally defines unrelated
TQ3_1S/TQ4_1S weight formats absent from Prism. This is integration failure,
not a KV arithmetic failure. Peak pressure1/swap growth0.

Evidence `evidence/AW-0122-turbo-registration.json`, raw
`/Users/chad/Models/agentwing/evidence/AW-0122`; failed patch preserved under
`experiments/runtime-patches/AW-0122-rejected-turbo-registration.patch`.
MIT public source, Atomic074bf826e1b06005a51737d29387e36657f41bf7 on Prism
adfffbe41b2cabcd51fff326ab045662265062bb. Internal SSD M1/16GB/macOS27.0.1.
No model/task/tool/sampling changes or endpoint claims. Corrected extraction
is separately frozen AW-0123; no rewriting this failed result.
