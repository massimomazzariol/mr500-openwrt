#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build only the public UPSTREAM profile in an explicitly prepared source tree."""
import argparse,json,pathlib,subprocess,os
D=pathlib.Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--tree',type=pathlib.Path,required=True);a.add_argument('--jobs',type=int,default=2);a.add_argument('--preflight-only',action='store_true');args=a.parse_args();tree=args.tree.resolve()
lock=json.loads((D/'sources.lock.json').read_text());restored=json.loads((tree/'source-revision.json').read_text());assert restored['base_revision']==lock['base_revision'] and restored['feeds']==lock['feeds']
assert (tree/'.config').is_file() and (tree/'target/linux/ramips/dts/mt7621_tplink_mr500-v1-eu.dts').is_file()
print('Prepared pinned UPSTREAM source/configuration found; review host requirements in docs/BUILD.md')
if not args.preflight_only:
 env=dict(os.environ,SOURCE_DATE_EPOCH=lock['epoch'],TZ='UTC',LC_ALL='C')
 for cmd in [['./scripts/feeds','update','-i'],['./scripts/feeds','install','-a'],['make','defconfig'],['make',f'-j{args.jobs}','V=s']]:subprocess.run(cmd,cwd=tree,env=env,check=True)
 for p in (tree/'bin/targets/ramips/mt7621').glob('*tplink_mr500-v1-eu*.bin'):
  subprocess.run(['python3',str(D/'scripts/validate_image.py'),str(p),'--unsquashfs',str(tree/'staging_dir/host/bin/unsquashfs4')],check=True)
