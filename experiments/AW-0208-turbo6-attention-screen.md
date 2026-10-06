# AW-0208 — Native six-bit attention consumer passes numeric and cost screens

## Status and hypothesis

Completed native component survivor. AW207 Metal-written6bit values lower
actualattentionerror versusstationary4bit without >10% nativeconsumer cost
regression. All48cases must exit0, finite, relativeL2<=.005 againstpacked
float64oracle; candidate uncompressed-referenceerror lower everylayer/mode/
shape; all24pairedsteadycostratios<=1.10; pressure<4/swapgrowth<=1024MiB,
freeSSD>=8GiB,90sprocesswatchdog. Declared before execution.

## Fixed configuration

AW207 currentnative libraries/patchseries, same4/6binaryselectedbyargument;
actualAW207Metal-writtenvalueswith192reversedrows undone,4KVheads48active
keys padded64,256dimensions,GQA24queryheads. F16/Q8keyinputs frompinned
AW180/AW116; layers3/31/63. FreshABBA for eachmode/layer/queryshape1and128.
128querycolumns replicate the savedquery, not a freshcausal128tokenprefill.
Fivewindows16completeattention+inverse+readbacks percase,3840operations.
F16norm/native4bit68B,6bit100B; vectorhalfcentroid/matrixfloatcentroidpaths.
Fixed16GBM1/internalSSD, hardwareOS/thermal/cache/source/binary/library/
fixture hashes and buildcommand in receipt. No inference,task,tool,sampling,
reasoning or activeprofile/default/P1 change.

```
python3 scripts/check_bonsai_turbo6_attention.py
python3 scripts/audit_bonsai_turbo6_attention.py
```

## Results

48/48 numericalpass, all24qualityandcostpairs pass.6bit attentionerror versus
uncompressedreference reduces72.24–74.96% relative to4bit. Consumerpaired
costratios1.0236–1.0757:2–8%extra cost, no speedclaim. Maximumoriginaloracle
relativeL2.001341<.005. Firstwarmup/setup/compileuploads retained separately;
componenttimings are notfullinstallation/endpoint accounting.

Independent float64bitdecode+WHTinverse+scalar math.fsum attention agrees
with declaredoracles within5e-7 and everyGPUoutputwithin.005; all48selected
nativevector/matrix/F16/Q8pipelinesverifiedfromlogs. CPUfallbackinverse is
explicitly denied in fixture. Rawhash/timing/pressure/capacity replay passes:
pressure1/swapgrowth0,minfree114,198,638,592B. Independentoutput-to-original
referencequality replay also passes. Half-second-or-faster sampled traces
are not fullmodel hostqualification.

## Evidence and disposition

`evidence/AW-0208-turbo6-attention-screen.json` pins fullplan/result/audit/
qualityreplay/buildcommand; largeinputs/outputs under
`/Users/chad/Models/agentwing/evidence/AW-0208`. No deviations orfailedcases.

Retain writer+consumer survivor for fullmodel candidate-generatedaccumulated
activations and nativebehavior, then fullvision/tools/endpoint ladders.
Nativecomponent success doesnot establish toolproposalbudgetperformance,
generalcapability or25%P1utilitygain. Sixbitcachestilllargerthan4bit and
morecostly here; memoryarithmeticnotRSS. NotfullGooglePolarQuant/QJL.
P1frozen; fullgoal remainsunproven.
