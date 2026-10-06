# AW-0101 — Native migration profiles do not meet the existing matched contract

## Status and hypothesis

Complete static compatibility falsifier. Hypothesis: preserved native P1 and
user-directed native Bonsai settings meet the current P2 matched-configuration
invariant. Read authoritative spec and effective launcher parameters; reject
compatibility if prescribed sampling/output/reasoning settings differ.

## Results

Existing matched sampling/context/prompt/tool/permission/timeout invariant is
true. Frozen P1 T0/top_p.8/frequency.5 versus native Bonsai T1/top_p.95/frequency0
already contradict matched sampling. Output budgets512/8192 and disabled
thinking/medium reasoning additionally differ. Top_k20 and presence0 match.
Candidate frequency0 resolved from explicit launcher flag, rather than guessed
from absent JSON key. No runtime, task, permission, deadline, score or policy
has been changed by this check. Preserve P1 exactly and retain user-prescribed
Bonsai settings; do not claim current native-profile diagnostics qualify under
this existing matched contract.

## Configuration, command and evidence

python3 scripts/check_native_comparison_contract.py (exit0, compatibilityfalse).
Small evidence/AW-0101-native-contract-compatibility.json pins exact source
spec/launcher/checker hashes and parameter differences. No model inference,
hardware performance measurement, raw benchmark data or speed claim. Static
read/write work ran while AW-0100 was live; that task's full wall still includes
this incidental host activity and is not a clean comparative endpoint result.

## Disposition

Unresolved promotion-contract applicability. Before native full P1 comparisons,
explicitly resolve/version the comparison contract without silently changing
it, modifying P1, reducing Bonsai reasoning, or relaxing capability/host/protocol
or25% utility gates. Current P2 spec remains untouched and all frozen plans
preserved. This does not block safe development falsifiers or satisfy the goal.
