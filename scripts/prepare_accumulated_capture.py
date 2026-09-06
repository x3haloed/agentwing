#!/usr/bin/env python3
"""Apply AW-0042 observer only to an explicitly supplied isolated AW-0041 clone."""
import argparse
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE='d44752e'


def main():
    p=argparse.ArgumentParser();p.add_argument('checkout',type=Path);a=p.parse_args();checkout=a.checkout.resolve()
    if checkout.name!='Swiftlet-AW0042' or checkout.parent!=Path('/Users/chad/Models/agentwing/reproductions'):
        raise SystemExit('Requires the isolated Swiftlet-AW0042 reproduction checkout')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip()
    assert head.startswith(BASE),head
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout,text=True).strip(),'Checkout must be clean'
    source=checkout/'Sources/SwiftletCore/QwenMetalModel.swift';text=source.read_text()
    single='''            routedExpertObserver?(li, picks.map { $0.0 })
            var bufs: [MTLBuffer] = []'''
    single_new='''            routedExpertObserver?(li, picks.map { $0.0 })
            ExpertActivationTrace.shared?.capture(
                layer: li, position: state.position, phase: "single-token",
                input: readSlot(slot, reg.xmoe, config.hiddenSize),
                experts: picks.map { $0.0 }, weights: weights)
            var bufs: [MTLBuffer] = []'''
    chunk='''                routedExpertObserver?(li, picks.map { $0.0 })
                unionSet.formUnion(picks.map { $0.0 })'''
    chunk_new='''                routedExpertObserver?(li, picks.map { $0.0 })
                ExpertActivationTrace.shared?.capture(
                    layer: li, position: basePosition + t, phase: "chunked-prefill",
                    input: readSlot(prefillSlot(t), reg.xmoe, config.hiddenSize),
                    experts: picks.map { $0.0 }, weights: weights)
                unionSet.formUnion(picks.map { $0.0 })'''
    assert text.count(single)==1 and text.count(chunk)==1,'Capture source boundary changed'
    source.write_text(text.replace(single,single_new).replace(chunk,chunk_new))
    shutil.copyfile(ROOT/'probes/activation_capture/AccumulatedActivationTrace.swift',checkout/'Sources/SwiftletCore/ExpertActivationTrace.swift')
    print('Applied opt-in capture to isolated checkout; build and validation still required')


if __name__=='__main__':main()
