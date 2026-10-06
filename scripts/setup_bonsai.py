#!/usr/bin/env python3
"""Acquire the exact pinned Bonsai runtime and multimodal artifacts outside Git."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from bonsai_server import ROOT, SPEC, WEIGHTS, verify


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


def download(url,path,size,digest):
    if path.exists() and path.stat().st_size==size and sha(path)==digest:return
    partial=path.with_suffix(path.suffix+'.partial')
    if path.exists() and not partial.exists():path.rename(partial)
    subprocess.run(['curl','-L','--fail','--retry','3','-C','-','-o',str(partial),url],check=True)
    if partial.stat().st_size!=size or sha(partial)!=digest:
        raise RuntimeError(f'Download integrity failed: {partial}')
    partial.rename(path)


def main():
    s=json.loads(SPEC.read_text()); WEIGHTS.mkdir(parents=True,exist_ok=True)
    required=sum(a['bytes'] for a in s['model']['artifacts'] if not (WEIGHTS/a['filename']).exists())
    if shutil.disk_usage(WEIGHTS).free<required+2*1024**3:raise RuntimeError('Insufficient disk headroom')
    demo=ROOT/'var/bonsai-demo'
    if not demo.exists():
        subprocess.run(['git','clone','--no-checkout','https://github.com/PrismML-Eng/Bonsai-demo.git',str(demo)],check=True)
        subprocess.run(['git','-C',str(demo),'checkout','--detach',s['runtime']['demo_revision']],check=True)
    revision=subprocess.check_output(['git','-C',str(demo),'rev-parse','HEAD'],text=True).strip()
    if revision!=s['runtime']['demo_revision']:
        raise RuntimeError('Demo checkout differs from pin; preserve it and restore pinned revision explicitly')
    asset=s['runtime']['asset'];cache=ROOT/'var/bonsai-downloads';cache.mkdir(exist_ok=True)
    archive=cache/asset['name'];download(asset['browser_download_url'],archive,asset['size'],asset['digest'].removeprefix('sha256:'))
    dest=demo/'bin/mac';dest.mkdir(parents=True,exist_ok=True)
    # The official archive is checked before extraction; setup mirrors Prism's signing steps.
    subprocess.run(['tar','-xzf',str(archive),'-C',str(dest),'--strip-components=1'],check=True)
    subprocess.run(['xattr','-cr',str(dest)],check=True)
    for p in dest.glob('llama-*'):
        if p.is_file():subprocess.run(['codesign','-s','-','--force','--timestamp=none',str(p)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    for a in s['model']['artifacts']:
        url='https://huggingface.co/'+s['model']['repository']+'/resolve/'+s['model']['revision']+'/'+a['filename']
        download(url,WEIGHTS/a['filename'],a['bytes'],a['sha256'])
    print(verify())


if __name__=='__main__': main()
