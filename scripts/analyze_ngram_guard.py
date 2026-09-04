#!/usr/bin/env python3
"""Check whether Swiftlet's hard trigram guard forbids normal tokenized text."""

import hashlib
import json
from pathlib import Path

import tokenizers


ROOT = Path(__file__).resolve().parents[1]
dependencies = json.loads((ROOT / "spec/dependencies.json").read_text())
model = Path(dependencies["qwen3_6_35b_a3b_8bit_qpack"]["local_path"])
path = model / "tokenizer.json"
tokenizer = tokenizers.Tokenizer.from_file(str(path))
fixtures = {
    "loopback_literal": "127.0.0.1",
    "repeated_parameter_types": "def add(left: int, right: int) -> int:\n    return left + right\n",
    "three_typed_parameters": "def mix(first: int, second: int, third: int) -> int:\n    return first + second + third\n",
    "two_tool_calls": (
        "<tool_call>\n<function=bash>\n<parameter=command>cat a.txt</parameter>\n</function>\n</tool_call>\n"
        "<tool_call>\n<function=bash>\n<parameter=command>cat b.txt</parameter>\n</function>\n</tool_call>"
    ),
    "repeated_path": "cat /tmp/project/src/module.py; python3 /tmp/project/src/module.py",
}
results = []
for name, text in fixtures.items():
    ids = tokenizer.encode(text, add_special_tokens=False).ids
    seen, blocked = set(), []
    for index in range(2, len(ids)):
        gram = tuple(ids[index - 2:index + 1])
        if gram in seen:
            blocked.append({"position": index, "required_token_id": ids[index],
                            "required_token": tokenizer.decode([ids[index]]),
                            "repeated_trigram": tokenizer.decode(list(gram))})
        seen.add(gram)
    results.append({"fixture": name, "text": text, "token_ids": ids,
                    "blocked_required_tokens": blocked})

print(json.dumps({
    "schema_version": 1,
    "runtime_revision": dependencies["swiftlet"]["revision"],
    "tokenizers_version": tokenizers.__version__,
    "tokenizer_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "guard_ngram_size": 3,
    "scope": "Canonical tokenizer paths, not all possible segmentations; no model inference or endpoint score.",
    "fixtures": results,
}, indent=2))
