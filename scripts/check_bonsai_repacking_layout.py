#!/usr/bin/env python3
"""AW-0081 tiny source-derived codec falsifier; never reads model weights."""
import hashlib
import json
from pathlib import Path
import random
import re
import sys

SOURCE = Path('/Users/chad/Models/agentwing/evidence/AW-0079/source-screen')


def cpu_codes(block):
    codes = []
    for offset, width in [(0, 16), (16, 8)]:
        for n in range(5):
            for m in range(width):
                codes.append((((block[offset+m] * 3**n) & 255) * 3) >> 8)
    for n in range(4):
        for h in range(2):
            codes.append((((block[24+h] * 3**n) & 255) * 3) >> 8)
    return codes


def repack(block):
    if len(block) != 28:
        raise ValueError('Expected one PTQ1_0 block')
    codes = cpu_codes(block)
    return block[26:28] + bytes(sum(codes[j+k] << (2*k) for k in range(4)) for j in range(0, 128, 4))


def check():
    receipt = json.loads((SOURCE/'receipt.json').read_text())
    files = receipt['files'] + json.loads((SOURCE/'cpu-receipt.json').read_text())
    for item in files:
        assert hashlib.sha256((SOURCE/item['path']).read_bytes()).hexdigest() == item['sha256']
    text = (SOURCE/'ggml/src/ggml-metal/kernels/dequantize.h').read_text()
    table = [int(x) for x in re.search(r'ptq1_0_lut\[256\] = \{(.*?)\};', text, re.S).group(1).split(',') if x.strip()]
    assert len(table) == 256

    def metal_codes(block):
        out = []
        for e in range(128):
            if e < 80:
                b, n = block[e & 15], e >> 4
            elif e < 120:
                t = e - 80
                b, n = block[16+(t & 7)], t >> 3
            else:
                t = e - 120
                b, n = block[24+(t & 1)], t >> 1
            out.append((table[b] >> (2*n)) & 3)
        return out

    def verify(block):
        expected = cpu_codes(block)
        assert expected == metal_codes(block)
        packed = repack(block)
        decoded = [(packed[2+j//4] >> (2*(j%4))) & 3 for j in range(128)]
        assert decoded == expected
        assert packed[:2] == block[26:]
        return expected

    cases = 0
    for position in range(26):
        for value in range(256):
            block = bytearray(28)
            block[position] = value
            verify(bytes(block))
            cases += 1
    rng = random.Random(81)
    sensitive = False
    for _ in range(128):
        block = bytes(rng.randrange(256) for _ in range(28))
        codes = verify(block)
        sensitive |= codes != list(reversed(codes))
        cases += 1
    assert sensitive, 'Fixtures must detect reversed element ordering'
    # Raw scale preservation includes all bit patterns, without a numeric NaN claim.
    payload = bytes(range(26))
    for scale in range(65536):
        bits = scale.to_bytes(2, 'little')
        assert repack(payload+bits)[:2] == bits
    return {'experiment': 'AW-0081', 'passed': True, 'runtime_commit': receipt['runtime_commit'],
            'source_files': files, 'external_source': str(SOURCE), 'payload_fixtures': cases,
            'all_byte_values_at_each_payload_position': True, 'scale_bit_patterns_preserved': 65536,
            'reversed_order_mutation_detectable': sensitive,
            'scope': 'Source-derived integer layout oracle only; no compiled CPU/Metal execution, model artifact, real activations or speed claim',
            'disposition': 'Retained for compiled reference and real tensor checks before full conversion'}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
