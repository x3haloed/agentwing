# AW-0087 — Screen native activation capture before inference

## Status and hypothesis

Complete source screen. Hypothesis: the pinned bundled callback example can
collect bounded complete early/middle/late activations without a custom collector.
Exploratory rejection criteria: unrelated tensor copies, truncated values, or
absence of generated-token capture. These criteria were recorded after source
inspection; this is not a predeclared quantitative experiment.

## Configuration and commands

Pinned Prism runtime adfffbe41b2cabcd51fff326ab045662265062bb.
Fetched exact examples/eval-callback sources, common/debug.cpp/.h and llama.h
from the official pinned repository; hashes in the evidence receipt. Executed
bundled llama-eval-callback --help (exit 0); no model inference executed.
No model, task, sampling, context, permission or scoring configuration changed.
Storage: internal SSD. This is a source/API screen, not a performance measurement.

## Results

The example invokes one prompt decode, without a generation loop. Default
callback returns true for every scheduler query. Even filtered-out device
tensors are copied to host before the filter limits printing. Printed tensor
values are truncated. Therefore the bundled example is unsuitable for complete,
bounded activation collection. llama_context_params exposes cb_eval and its
user data, permitting a custom bounded collector to reject unrelated nodes at
the scheduler query before copying selected full inputs.

## Evidence and limitations

External source and help: /Users/chad/Models/agentwing/evidence/AW-0087.
See evidence/AW-0087-activation-capture-screen.json for exact hashes and URLs.
Source inspection has not established custom collector linkage, tensor names,
Hadamard-input selection, actual activation fidelity or accumulated behavior.

## Disposition

Reject the bundled example for this collection role. Retain the direct custom
callback path for a bounded native inference falsifier. Goal remains open.
