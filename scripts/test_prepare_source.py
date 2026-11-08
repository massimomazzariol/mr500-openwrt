#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Offline checks for the optional package-patch profiles in prepare_source.py."""
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import prepare_source as ps

PROFILE = ps.OPTIONAL / 'relayd-fixes'


class PackagePatches(unittest.TestCase):
    def tree(self, version):
        tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        manifest = json.loads((PROFILE / 'package-patches.json').read_text())
        recipe = tmp / manifest['package']
        recipe.mkdir(parents=True)
        (recipe / 'Makefile').write_text(f'PKG_SOURCE_VERSION:={version}\n')
        return tmp, recipe, manifest

    def test_installs_hash_checked_patches(self):
        tmp, recipe, manifest = self.tree(json.loads((PROFILE / 'package-patches.json').read_text())['source_version'])
        ps.install_package_patches(tmp, PROFILE)
        for row in manifest['patches']:
            self.assertEqual(ps.digest(recipe / 'patches' / row['file']), row['sha256'])

    def test_refuses_other_package_version(self):
        tmp, _, _ = self.tree('0000000000000000000000000000000000000000')
        with self.assertRaises(SystemExit):
            ps.install_package_patches(tmp, PROFILE)

    def test_refuses_existing_patch(self):
        tmp, recipe, manifest = self.tree(json.loads((PROFILE / 'package-patches.json').read_text())['source_version'])
        (recipe / 'patches').mkdir()
        (recipe / 'patches' / manifest['patches'][0]['file']).write_text('other')
        with self.assertRaises(SystemExit):
            ps.install_package_patches(tmp, PROFILE)

    def test_lock_matches_feeds_conf(self):
        lock = json.loads((ps.D / 'sources.lock.json').read_text())
        pins = dict(line.split()[1:3] for line in (ps.D / 'feeds.conf').read_text().splitlines() if line.strip())
        self.assertEqual({k: v.split('^')[1] for k, v in pins.items()}, lock['feeds'])


if __name__ == '__main__':
    unittest.main()
