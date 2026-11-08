#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Prepare a pinned OpenWrt source tree for the MR500, without building or flashing.

Clones OpenWrt at the commit in sources.lock.json, fetches the pinned feeds,
applies the device patches and writes .config from the UPSTREAM seed plus any
optional profiles (profiles/optional/<name>/).
"""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess

D = pathlib.Path(__file__).resolve().parents[1]
OPTIONAL = D / 'profiles/optional'


def git(*args, cwd):
    return subprocess.run(['git', *args], cwd=cwd, check=True, text=True,
                          capture_output=True).stdout.strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def install_package_patches(tree, profile):
    """Copy hash-checked package patches; refuse if the package source moved."""
    manifest = json.loads((profile / 'package-patches.json').read_text())
    recipe = tree / manifest['package']
    if 'PKG_SOURCE_VERSION:=' + manifest['source_version'] not in (recipe / 'Makefile').read_text():
        raise SystemExit(f'{profile.name}: {manifest["package"]} is not at {manifest["source_version"]}')
    target = recipe / 'patches'
    target.mkdir(exist_ok=True)
    for row in manifest['patches']:
        source = profile / 'patches' / row['file']
        if digest(source) != row['sha256']:
            raise SystemExit(f'{profile.name}: patch hash mismatch: {row["file"]}')
        if (target / row['file']).exists():
            raise SystemExit(f'{profile.name}: package patch already present: {row["file"]}')
        shutil.copyfile(source, target / row['file'])


def main():
    names = sorted(p.name for p in OPTIONAL.iterdir() if p.is_dir())
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('output', type=pathlib.Path, help='new directory; the tree is created in OUTPUT/openwrt')
    a.add_argument('--with', dest='profiles', action='append', default=[], choices=names,
                   help='optional profile to include (repeatable)')
    args = a.parse_args()
    lock = json.loads((D / 'sources.lock.json').read_text())
    if args.output.exists():
        raise SystemExit('Output must be new; existing files are never overwritten')
    args.output.mkdir(parents=True)
    tree = args.output / 'openwrt'

    git('clone', '--branch', lock['base_tag'], lock['source_url'], str(tree), cwd=args.output)
    if git('rev-parse', 'HEAD', cwd=tree) != lock['base_revision']:
        raise SystemExit(f'{lock["base_tag"]} does not resolve to {lock["base_revision"]}')
    if (tree / 'version').read_text().strip() != lock['base_version']:
        raise SystemExit('OpenWrt version file differs from sources.lock.json')

    shutil.copyfile(D / 'feeds.conf', tree / 'feeds.conf')
    subprocess.run(['./scripts/feeds', 'update', '-a'], cwd=tree, check=True)
    feeds = {feed: git('rev-parse', 'HEAD', cwd=tree / 'feeds' / feed) for feed in lock['feeds']}
    if feeds != lock['feeds']:
        raise SystemExit(f'Feed revisions differ from sources.lock.json: {feeds}')

    for patch in sorted((D / 'patches/upstream').glob('*.patch')):
        git('apply', str(patch), cwd=tree)

    config = (D / 'profiles/upstream/seed.config').read_text()
    for name in args.profiles:
        profile = OPTIONAL / name
        if (profile / 'package-patches.json').exists():
            install_package_patches(tree, profile)
        config += (profile / 'seed.config').read_text()
    (tree / '.config').write_text(config)
    (tree / 'source-revision.json').write_text(json.dumps(
        {'base_revision': lock['base_revision'], 'feeds': feeds, 'profiles': args.profiles}, indent=2) + '\n')
    print(tree.resolve())
    print('Source/configuration prepared. No compilation, device access or flashing performed.')


if __name__ == '__main__':
    main()
