#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Restore the corresponding-source release bundle, without building or flashing."""
import argparse,hashlib,json,pathlib,shutil,subprocess,tarfile,tempfile
D=pathlib.Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('bundle',type=pathlib.Path);a.add_argument('output',type=pathlib.Path);a.add_argument('--sha256',required=True);args=a.parse_args()
assert hashlib.sha256(args.bundle.read_bytes()).hexdigest()==args.sha256,'Source bundle digest mismatch'
assert not args.output.exists(),'Output must be new; existing files never overwritten'
args.output.mkdir(parents=True)
with tempfile.TemporaryDirectory(dir=args.output.parent,prefix='source-unpack-') as tmp:
 tmp=pathlib.Path(tmp)
 with tarfile.open(args.bundle) as t:t.extractall(tmp,filter='data')
 manifest=json.loads((tmp/'source-bundle-manifest.json').read_text())
 for name,pin in manifest['files'].items():assert hashlib.sha256((tmp/name).read_bytes()).hexdigest()==pin,name
 with tarfile.open(tmp/'snapshots/openwrt.tar') as t:t.extractall(args.output,filter='data')
 tree=args.output/'openwrt'
 for feed in manifest['revisions']['feeds']:
  with tarfile.open(tmp/f'snapshots/{feed}.tar') as t:t.extractall(tree/'feeds',filter='data')
 shutil.copytree(tmp/'dl',tree/'dl')
 for patch in sorted((D/'patches/upstream').glob('*.patch')):subprocess.run(['git','apply',str(patch.resolve())],cwd=tree,check=True)
 shutil.copyfile(D/'releases/upstream-20261009/resolved.config',tree/'.config')
 shutil.copyfile(D/'feeds.conf',tree/'feeds.conf')
 (tree/'version').write_text('r36880-bb6df54d9d\n')
 (tree/'source-revision.json').write_text(json.dumps(manifest['revisions'],indent=2)+'\n')
print(tree.resolve())
print('Source/configuration restored. No compilation, device access or flashing performed.')
