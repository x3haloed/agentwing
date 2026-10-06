# AW-0187 — native stationary-codebook Metal writer

Predeclared numeric/cost ABBA perlayer3/31/63: real192rows, reverse destination
indices. Same fixture compiled against AW182 control/AW186 candidate native
libraries. Five complete graphcompute+readback windows, first retainedwarmup,
startup/compile/upload separately retained. Numeric gate exactnibblecodes and
reservedzero bytes, finite halfnorm relative<=.0015 permits cross-CPU/GPU half
rounding; compare each arm's own CPU reference. No bitbudget/layout change.

All12exit0/numeric pass; candidate allpackedbytes exact CPU reference, control
layer31 one-half rounding difference maxrelative.00059595, gates pass. All
reverse row placements correct. Runner hostpressure1/growth0. Per-sample host
traces not retained, so no independent hosttrace replay claim. Packedoutputs /
alltimings/median ratios independently replayed. Candidate initialprocess
19.997s with firstcompute71.218ms retained, not excluded from endpoint cost.

Costgate required every adjacentratio<=1.10. One midlayer ratio1.15553 fails;
other medians show substantial within-window/interprocess variation. Overall
cost gate failed, not silently waived; numeric integrity retained, cost
unresolved pending longer repeated-window interleaved screen. No speed or
full-writer/attention/own-model/vision/tool/endpoint promotion. P1/default /
deployed runtime unchanged. Complete source/fixture/input/modelcapture/runtime /
hardware/OS/thermal/storage/cache/library pins in plan.

Raw: /Users/chad/Models/agentwing/evidence/AW-0187.
Receipt: evidence/AW-0187-codebook-metal-writer.json.
Reproduce compile same bonsai-codebook-writer.cpp against each pinned backend;
python3 scripts/check_bonsai_codebook_writer.py, refuses priorplan overwrite.
Disposition: numeric retained, failed cost gate preserved, cost unresolved.
