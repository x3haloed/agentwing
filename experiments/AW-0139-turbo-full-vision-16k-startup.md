# AW-0139 — Full multimodal16K startup confirms compressed allocation

Retained startup/resource pass. Same immutable AW-0138 experimental spec/launcher,
server/projector/model/library hashes and whole configuration, adding only
`--verbose` diagnostic logging to the frozen command. No task/sampler/context/
image/output/permission changes. Full Q8 vision projector configured,16K context,
q8 K/Turbo4 V,flashON,medium,T1/.95/k20/min_p.05,one loopback owner,no shift,
cacheRAM0/checkpoints2,1024 image cap. Native model generation/task/tool calls0.

Primary rule server healthy within60s,props readable,expected actual q8/Turbo4
408MiB allocator line present,host pressure<4/swap growth<=1024MiB.
`python3 scripts/probe_bonsai_turbo_startup_verbose.py` exit0; all pass:
HTTP health/props200;16384 cells/16 full-attention layers,272MiB q8 K plus136MiB
Turbo4 V=408MiB KV. Actual allocation matches previous conditional payload
prediction, excludes weights/recurrent/vision/scratch/checkpoints/peak RSS.
No16K occupied-history or throughput inference from capacity allocation.

.25s host samples,pressure1/swap growth0;cleanupserverexit0.4.764s diagnostic
controller wall includes cleanup; not an endpoint performance comparison.
Internal SSD M1/16GB/macOS27.0.1. Evidence
`evidence/AW-0139-turbo-server-startup.json`; raw
`/Users/chad/Models/agentwing/evidence/AW-0139`.

Usable experimental launcher: `python3 scripts/bonsai_turbo_server.py` with
`spec/bonsai-turbo-local.json`; `--verify-only` verifies all pins. Retain full
configured startup, preserving AW-0138 observation failure. Image answers,
native tool/Pi loop, long-context generation, general capability and replicated
end-to-end utility gains remain unverified. P1/default launcher unchanged.
