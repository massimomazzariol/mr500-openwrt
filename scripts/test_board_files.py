#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Offline checks for the MR500 board files added by 001-device-support.patch.

Extracts the new files from the patch, checks shell syntax, and runs the
firewall uci-defaults script twice against stubbed OpenWrt functions.
"""
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

D = pathlib.Path(__file__).resolve().parents[1]
PATCH = D / 'patches/upstream/001-device-support.patch'
BASE = 'target/linux/ramips/mt7621/base-files/etc/'
SH = shutil.which('sh')

# Stubs for /lib/functions.sh: one wan zone (cfg02) whose networks live in a file.
STUBS = r'''
board_name() { echo "$BOARD"; }
config_load() { :; }
config_foreach() { "$1" cfg01; "$1" cfg02; }
config_get() {
	case "$1:$2:$3" in
	name:cfg01:name) name=lan ;;
	name:cfg02:name) name=wan ;;
	networks:cfg01:network) networks=lan ;;
	networks:cfg02:network) networks="$(cat "$STATE")" ;;
	esac
}
list_contains() { case " $(eval echo \$$1) " in *" $2 "*) return 0 ;; esac; return 1; }
uci() { echo "$*" >> "$LOG"; [ "$1" = add_list ] && printf ' %s' "${2#*=}" | tr -d "'" >> "$STATE"; }
'''


def new_files(patch):
    """Return {path: content} for files created by a git diff."""
    files = {}
    for chunk in re.split(r'^diff --git ', patch.read_text(), flags=re.M)[1:]:
        if '\nnew file mode' not in chunk:
            continue
        path = chunk.split(' b/', 1)[1].split('\n', 1)[0]
        body = chunk.split('\n@@', 1)[1].split('\n', 1)[1]
        files[path] = ''.join(line[1:] + '\n' for line in body.splitlines() if line.startswith('+'))
    return files


@unittest.skipUnless(SH, 'needs a POSIX sh')
class BoardFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = new_files(PATCH)
        cls.tmp = pathlib.Path(tempfile.mkdtemp())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def script(self, name):
        path = self.tmp / pathlib.Path(name).name
        path.write_text(self.files[BASE + name].replace('. /lib/functions.sh', '. ./stubs.sh'))
        (self.tmp / 'stubs.sh').write_text(STUBS)
        return path

    def run_sh(self, path, board):
        env = {'PATH': '/usr/bin:/bin', 'BOARD': board, 'STATE': 'state', 'LOG': 'log'}
        return subprocess.run([SH, path.name], cwd=self.tmp, env=env, capture_output=True, text=True)

    def test_new_files_present(self):
        self.assertIn(BASE + 'uci-defaults/10_tplink_mr500_wwan', self.files)
        self.assertIn(BASE + 'hotplug.d/iface/10-tplink-mr500-4g-led', self.files)

    def test_shell_syntax(self):
        for name, content in self.files.items():
            if name.startswith(BASE):
                r = subprocess.run([SH, '-n'], input=content, capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, name + r.stderr)

    def test_firewall_defaults_add_wwan_once(self):
        path = self.script('uci-defaults/10_tplink_mr500_wwan')
        (self.tmp / 'state').write_text('wan wan6')
        (self.tmp / 'log').write_text('')
        for _ in range(2):
            r = self.run_sh(path, 'tplink,mr500-v1-eu')
            self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.tmp / 'log').read_text().splitlines(),
                         ["add_list firewall.cfg02.network=wwan0"])

    def test_firewall_defaults_ignore_other_boards(self):
        path = self.script('uci-defaults/10_tplink_mr500_wwan')
        (self.tmp / 'state').write_text('wan wan6')
        (self.tmp / 'log').write_text('')
        self.assertEqual(self.run_sh(path, 'tplink,mr600-v2-eu').returncode, 0)
        self.assertEqual((self.tmp / 'log').read_text(), '')

    def test_network_uses_ncm_on_at_port(self):
        text = PATCH.read_text()
        self.assertIn('+\t\tucidef_set_interface "wwan0" device "/dev/ttyUSB0" protocol "ncm"', text)
        # board.d runs on every boot; firewall changes belong in uci-defaults
        self.assertNotIn("+\t\tuci add_list firewall", text)


if __name__ == '__main__':
    unittest.main()
