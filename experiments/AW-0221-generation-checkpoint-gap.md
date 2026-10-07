# AW-0221 — Generation checkpoint gap diagnosis

Offline source/log diagnosis of rejected AW220: fifth request6850prompt tokens checks checkpoint against6692 but restores1374, replay5476tokens/194575.84ms after5436generated tokens. Source/log hashes in `evidence/AW-0221-checkpoint-gap.json`; raw external AW220 attempt20261007T173817.456074Z.

Hypothesis: bounded checkpoints during generation can preserve later reusable recurrent state and reduce replay while retaining complete exact history/reasoning/tasks/tools. Unimplemented/unresolved. First inspect generation state lifecycle and test exact-prefix restored-state correctness; screen complete capture/replay/memory cost interleaved before full integration. This is component evidence, not utility/hour or promotion. Prior long-generation cost1219962.81ms still dominates; eliminating194.576s replay alone does not prove25% or task completion. Preserve AW220 failure/P1/all endpoint gates.
