# AW-0210 — Fullserver/vision build and pinned six-bit launch path

## Status, hypothesis and gates

Completed artifactbuild/commandverification. Hypothesis: native6bit survivor
builds serverandvision executables withpriorcodec/model libraries andsource
unchanged. Buildexit0/nonemptyexecutables, exactpriorlibrary/sourceidentity,
pressure<4/swapgrowth<=1024MiB/freeSSD>=8GiB/600sphase. No modelstartup,
visionunderstanding, toolbehavior orendpointadmission claimed.

## Configuration and commands

Fixed16GBM1/internalSSD, Prismadfffbe +AW137/AW179/AW182/AW186/AW201/AW203/
AW205/AW206/AW207series. ExistingReleaseCMake/Metalembedded/OpenSSLdisabled.
ModelselectiveattentionPQ6.041GB andQ8visionprojector629MB unchanged/pinned.
Exactsource/library/binary/patch/compiler/hardwareOS/thermal/storage/parent
provenance andbuildcommand in `evidence/AW-0210-turbo6-fullserver-build.json`.

```
python3 scripts/build_bonsai_turbo6_fullserver.py
python3 scripts/bonsai_turbo6_server.py --verify-only
```

Newisolated profile `spec/bonsai-turbo6-local.json`, launcher
`scripts/bonsai_turbo6_server.py`:16Kcontext/oneowner/Q8keys/Turbo6values,
fullQ8vision1024imagecap, nativeT1/P.95/k20/minP.05/pres0/repeat1/freq0/medium,
cp2/cacheRAM0/noctxshift/flashon/loopback.8192outputcap iscaller-supplied,
not enforcedby launcher. Weights hashingstreams8MiBchunks; exactsameartifact
hashes verified. Runtimebanner honestlyreports build0/commitunknown; base+
patchseries/artifact hashes authoritative. P1/operationaldefaults unchanged.
Startupdiskgate16GiB/runtime8GiB, pressure/swapguards andownerlock preserved.

## Storage recovery and results

PriorNoMachinesessionlog grewagain outsidebenchmarks:206,040,997,888B
allocated,logical494,080,602,978B; free77,512,372,224B. Repeateduser-authorized
truncationofsameexplicitlog reclaimedabout192GiB; afterallocated16,781,312B,
free283,537,833,984B. Writerretainsoldoffset, logicalsize immediatelylarge
againwhileallocatedsmall; diskguards measureactualcapacity. No weights,
source, evidence, objects orotheruserdata removed. Recoveryreceipt pinned.

120buildsteps/exit0,90.236s diagnostic. ServerandvisionCLI built;
priornativecodec/model libraries and13changedsourcefiles unchanged.
Independentraw/library/host/capacity replay passes; exactversionbanner/
weight/server/library/visionCLI/patch/buildreceiptverification passes.
Commandchecks allnativeflags andloopback/fullprojector paths pass. Fullmodel
hasnotbeenstartedthroughnewserver. No setup/componenttiming isendpointgain.

## Evidence and disposition

Largebuildlog/hosttrace/recoveryreceipt under
`/Users/chad/Models/agentwing/evidence/AW-0210`. Smallbuildandlaunchverification
receipts committed. Retainexperimentalbuilt launchpath forstartup/images/
nativeLookupcontinuation/Pifilecopy admission, then longnativehistory/tool
behavior andfrozenendpoint ladder. No fullGooglePolarQuant/QJLclaim or
candidatepromotion; full25%verifiedutilitygoal remainsunproven.
