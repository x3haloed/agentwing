# AW-0138 — Default-log startup cannot prove allocation

Preserved negative observability screen. New experimental launcher/spec freezes
server/runtime-library/archived-patch and model/projector hashes before startup.
Keeps16384 context,8192 output policy,medium reasoning,T1/.95/k20/min_p.05,
presence0/repeat1,full Q8 vision1024,image projector unchanged,cacheRAM0,
checkpoints2,no context shift,parallel1,loopback-only,q8 K/Turbo4 V/flashON.

`python3 scripts/bonsai_turbo_server.py --verify-only` passes all artifact/library/
patch hashes and base revision. `python3 scripts/probe_bonsai_turbo_startup.py`
starts server under single advisory owner/60s startup watchdog/.25s host checks;
health and props HTTP200. Cleanup exit0,pressure1/swap growth0. Screen fails because
predeclared408MiB allocation line is absent at new server's default verbosity;
no allocation inferred just from readiness. No generation or image answers.

Plan/spec/launcher/command frozen; metadata
`evidence/AW-0138-turbo-server-startup.json`, raw
`/Users/chad/Models/agentwing/evidence/AW-0138`. Fixed internal SSD M1/16GB/macOS
27.0.1. Native model tool calls0; HTTP setup requests are controller reads.
Repeat with explicit diagnostic logging is separateAW-0139, not rewrittenpass.
Launcher remains experimental/unqualified and does not change active P1/default.
