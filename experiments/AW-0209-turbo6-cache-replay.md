# AW-0209 — Full-model six-bit accumulated-prefix replay

## Status and hypothesis

Completed. Allsixarms independentlyaudited; technicalscreenpassed. Technical hypothesis:
Q8keys/6bitvalues limit identical-prefixlogitdisplacement and preservefinite
own32trajectories at savedearly/mid/late reasoning prefixes. Fullqualification
requiresallsixarms. This is not vision/tool/task/endpoint acceptance.

## Fixed configuration and gates

Fixed16GBM1/internalSSD; exactselectivePQmodel hashchecked. Prismadfffbe
plusAW137/AW179/AW182/AW186/AW201/AW203/AW205/AW206/AW207 sourcepatchseries;
3531sourcefiles comparedwithstationarybase,13changedfiles independently
reconstructedexactly,3518unchanged. Pinnedlibraries/headers/compiler/model/
prioroperatingprofile/fixture/hash/thermal/OS in immutableexternalplan.
Inheritedprofiledescribesartifactprovenance, not candidate launch admission.

Full16Kcontext,128batch/ubatch,oneowner,32sampledtokens,
T1/P.95/k20/minP.05/pres0/repeat1/freq0/seed42. SavedAW144ownthoughtprefixes
0/4096/7695chunks; originalmediumhistory. FreshorderF16→6bit,6bit→F16,
F16→6bit. No task/reasoning/tool/timeout/scoring narrowed: noendpointtask is
beingrun. Sameprior technicalscreen criteria: each32finitefull-logitrows,
384finiteprojectioncaptures; identicaltokenizedpromptperpair;
firstlogitrelativeL2<=.10/top20overlap>=.50. Laterowntrajectory disagreement
is descriptive because inputsequences can differ. Hostpressure<4,
swapgrowth<=1024MiB,600sarmwatchdog;16GiBfreebeforeeacharm/8GiBduringrun,
capacityandpressure sampled.5s. Stoponexecution/resourcefailure.

Buildcommand inpartialreceipt. Commands:

```
python3 scripts/run_bonsai_turbo6_cache_replay.py
python3 scripts/audit_bonsai_turbo6_cache_replay.py --partial
```

Do not startsecondrunner whilethiscampaignlive. Wholeauditorwithoutpartial
requiredafterterminalallarms. Externalraw
`/Users/chad/Models/agentwing/evidence/AW-0209`.

## Partial results and disposition

Early1186tokenpair bothclean32ownsampledtokens/logits/captures. Firstlogit
L2.0088705/top20overlap.95 passes provisionalgate; common32tokenprefix4,
4matches overall, not broadbehavioraccuracy. FreshF16prompt/logits/generated
bytes identicalpriorAW190F16control. Bothsampledpressure1/swapgrowth0.
Diagnosticlifetimes49.362/47.771s not a speedcomparison. Partialreceipt
`evidence/AW-0209-turbo6-early-pair-partial.json` pinsraw/audit/sourceproof.

Retainpartialtechnicalevidence; fullcampaignunresolved. Native fullmodel6bit
runs, but modelvision/tools/serverlaunch andaccumulatedbehavior endpoints
stillunqualified. NoP1/defaultchange or25%utilityclaim. Goal remainsactive.

Middle6bitarm nowterminalexit0:192.232s diagnostic, pressure1/swapgrowth0;
32finiteownlogitrows/384captures pass independentraw/shape/resourceaudit.
Partialreceipt `evidence/AW-0209-turbo6-middle-candidate-partial.json`.
MatchingmiddleF16control live; middlepair/fullcampaign stillunresolved.

Middle5282tokenpair nowpasses provisionalfirstrowgate: L2.00385631,
top20overlap.95; both32finiteownrows/384captures,pressure1/swapgrowth0.
MiddleF16prompt/full32logits/generatedbytes matchAW190control exactly.
Own32commonprefix0/matches0: divergentinputs prohibit subsequent-logit
equalprefix comparisons oroutputequivalenceclaim. Lifetimes192.232/184.104s
diagnostic only. Receipt `evidence/AW-0209-turbo6-middle-pair-partial.json`.
LateF16control live; allsixarmcampaign unresolved.

LateF16control nowexit0,308.483s diagnostic,32finiteownrows/384captures,
pressure1/swapgrowth0. Independentpartialauditverifiesfivearms. LateF16
prompt/full32logits/generatedbytes matchpriorAW190control exactly. Receipt
`evidence/AW-0209-late-control-partial.json`; late6bitcandidate live.
AllthreefreshF16controls reproducepriorlogits/generatedbytes, but late
pair/fullcampaign remainsunresolved.

## Terminal campaign result

Allsixarms exit0 andcomplete32ownsampledtokens/fullfinitelogitrows/384finite
projectioncaptures perarm. Originalauditorwithoutpartial passes, independent
math.fsumfirstrowL2agrees within1e-12; patch/source/library/model/harness/
fixture/resource/capacityidentitieschecked. No live modelowner aftercleanup.
FirstrowL2 early/mid/late .0088705/.00385631/.00888471; top20overlap.95/.95/1.
Commonown32tokenprefix4/0/22, overallmatches4/0/22. Notoutputequivalence.
AllthreefreshF16controls full32logits/prompt/generatedbytes bitexactAW190.
Comparedoldstationary4bit numericaldisplacementreduction65.07/75.42/66.69%
(rounded), not taskquality orspeed. Allarmspeakpressure1/swapgrowth0.
Late6bit327.857s diagnostic; 16KallocatedQ8K272MiB/V6bit200MiB=472MiB,
versusF16/F16 1024MiB. Allocation isnotRSS/speed/agentutility.

Supersedespartialcampaignstatus. Receipt
`evidence/AW-0209-turbo6-cache-terminal.json` pinsfullplan/summary/audit/
independentnumericchecks andexternalarmrawhashes. Retaintechnicalsurvivor
for fullserver/vision/native-tool/ownbehavior admission, thenselecteddev
andfrozenoriginal/expandedendpoints asrequired. No default/P1promotion;
25%utilitygoal remainsunproven. No fullGooglePolarQuant/QJLclaim.
