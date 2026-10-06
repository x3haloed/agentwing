# AW-0206 — Streaming six-bit packing alone fails writer cost gate

Completed negative, rejected writer screen. Hypothesis: replace128-index
array with streaming4codes/3bytes and pass unchangedAW205writer gates.
Onlynative6bitpackingchanged; precisequantizecompiler, book/rotation/norm,
100byteformat and4bitcontrol unchanged. Onefilepatch afterAW205series.
Exactpins/source/library/buildcommands and immutableplan in
`evidence/AW-0206-turbo6-stream-writer.json` and streambuildreceipt.
Fixed16GBM1/internalSSD; no inference/task/tool/sampling/reasoning changes.

```
python3 scripts/check_bonsai_turbo6_writer_stream.py
python3 scripts/audit_bonsai_turbo6_writer_stream.py
```

12fresh reversed192row actual layer3/31/63 ABBA cases,5windows64complete
compute/readback operations. Exactpackednorm/payloadallpass;3840ops,
pressure1/swapgrowth0. Independenthash/bytes/timing/host/capacityauditpasses.
Sixpairedsteadycostratios1.372/1.317/1.363/1.347/1.354/1.387; fourfail1.35.
Firstwarmup andcompleteprocesslifetimesretained. No costgatewaiver.

Reject as sufficientwriterfix, retainnegative/sourcepatch. Registerspilling
hypothesis notproven; inspectdynamiclookup next. Nativeattention/fullmodel/
vision/tools/endpoints remainunqualified, defaults/P1 unchanged. Rawexternal
`/Users/chad/Models/agentwing/evidence/AW-0206`.
