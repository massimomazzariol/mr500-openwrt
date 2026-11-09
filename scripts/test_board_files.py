#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Offline checks for the MR500 board files added by 001-device-support.patch.

Extracts the new files from the patch, checks shell syntax, and runs them
against a small file-backed uci stub: fresh install, upgrade from the
DHCP-on-eth1 images, customized setups, the 4G LED hotplug and another board.
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
DEFAULTS = 'uci-defaults/10_tplink_mr500_wwan'
LED = 'hotplug.d/iface/10-tplink-mr500-4g-led'
SH = shutil.which('sh')

# Stubs for /lib/functions.sh and uci. The database holds one "key=value"
# line per option or list item, and "pkg.section=type" lines for sections.
STUBS = r'''
board_name() { echo "$BOARD"; }
config_load() { PKG="$1"; }
config_foreach() {
	for s in $(sed -n "s/^$PKG\.\([^.=]*\)=$2\$/\1/p" "$DB"); do "$1" "$s"; done
}
config_get() {
	eval "$1=\"\$(sed -n 's/^$PKG\.$2\.$3=//p' \"\$DB\" | tr '\n' ' ' | sed 's/ \$//')\""
}
list_contains() { case " $(eval echo \$$1) " in *" $2 "*) return 0 ;; esac; return 1; }
uci() {
	[ "$1" = "-q" ] && shift
	cmd="$1"; arg="$(echo "$2" | tr -d "'")"; key="${arg%%=*}"; val="${arg#*=}"
	case "$cmd" in
	get) sed -n "s/^$key=//p" "$DB" | head -n 1 | grep . ;;
	show) sed -n "s/^\($key\.[^=]*\)=\(.*\)/\1='\2'/p" "$DB" ;;
	set) grep -v "^$key=" "$DB" > "$DB.t"; echo "$key=$val" >> "$DB.t"; mv "$DB.t" "$DB" ;;
	delete) grep -v "^$key[.=]" "$DB" > "$DB.t"; mv "$DB.t" "$DB" ;;
	add_list) echo "$key=$val" >> "$DB" ;;
	del_list) grep -vx "$key=$val" "$DB" > "$DB.t"; mv "$DB.t" "$DB" ;;
	batch) while read -r c a; do [ -n "$c" ] && uci "$c" "$a"; done ;;
	esac
}
'''

FIREWALL = ['firewall.lan=zone', 'firewall.lan.name=lan', 'firewall.lan.network=lan',
            'firewall.wan=zone', 'firewall.wan.name=wan',
            'firewall.wan.network=wan', 'firewall.wan.network=wan6']
FRESH = FIREWALL + ['network.wwan0=interface', 'network.wwan0.proto=ncm',
                    'network.wwan0.device=/dev/ttyUSB0', 'network.wwan0.pdptype=ipv4']
LEGACY = FIREWALL + ['firewall.wan.network=wwan0', 'firewall.wan.network=wwan0',
                     'network.wwan0=interface', 'network.wwan0.proto=dhcp', 'network.wwan0.device=eth1',
                     'network.wwan06=interface', 'network.wwan06.proto=dhcpv6', 'network.wwan06.device=eth1',
                     'system.led_4g=led', 'system.led_4g.sysfs=white:4g', 'system.led_4g.dev=wwan0',
                     'system.led_lan=led', 'system.led_lan.sysfs=white:lan', 'system.led_lan.dev=br-lan']


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

    def sandbox(self, name, db, replace=()):
        tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        script = self.files[BASE + name].replace('. /lib/functions.sh', '. ./stubs.sh')
        for old, new in replace:
            script = script.replace(old, new)
        # newline='\n': keep LF on Windows, a CR would break the shell scripts
        (tmp / 'script.sh').write_text(script, newline='\n')
        (tmp / 'stubs.sh').write_text(STUBS, newline='\n')
        (tmp / 'db').write_text('\n'.join(db) + '\n', newline='\n')
        return tmp

    def run_sh(self, tmp, **env):
        r = subprocess.run([SH, 'script.sh'], cwd=tmp, capture_output=True, text=True,
                           env={'PATH': '/usr/bin:/bin', 'DB': 'db', **env})
        self.assertEqual(r.returncode, 0, r.stderr)

    def run_defaults(self, db, board='tplink,mr500-v1-eu', runs=1):
        tmp = self.sandbox(DEFAULTS, db)
        for _ in range(runs):
            self.run_sh(tmp, BOARD=board)
        return (tmp / 'db').read_text().splitlines()

    def run_led(self, db, action):
        tmp = self.sandbox(LED, db, [('led=/sys/class/leds/white:4g', 'led=./led')])
        (tmp / 'led').mkdir()
        (tmp / 'led/trigger').write_text('none\n')
        self.run_sh(tmp, BOARD='tplink,mr500-v1-eu', INTERFACE='wwan0', ACTION=action, DEVICE='usb0')
        return {f.name: f.read_text().strip() for f in (tmp / 'led').iterdir()}

    def test_new_files_present(self):
        self.assertIn(BASE + DEFAULTS, self.files)
        self.assertIn(BASE + LED, self.files)

    def test_shell_syntax(self):
        for name, content in self.files.items():
            if name.startswith(BASE):
                r = subprocess.run([SH, '-n'], input=content.encode(), capture_output=True)
                self.assertEqual(r.returncode, 0, name + r.stderr.decode())

    def test_fresh_install_adds_wwan_once(self):
        db = self.run_defaults(FRESH, runs=2)
        self.assertEqual(db.count('firewall.wan.network=wwan0'), 1)
        self.assertNotIn('firewall.lan.network=wwan0', db)
        self.assertIn('network.wwan0.proto=ncm', db)

    def test_upgrade_from_dhcp_images(self):
        db = self.run_defaults(LEGACY)
        self.assertEqual(db.count('firewall.wan.network=wwan0'), 1)
        for line in ('network.wwan0.proto=ncm', 'network.wwan0.device=/dev/ttyUSB0',
                     'network.wwan0.pdptype=ipv4', 'system.led_lan.dev=br-lan'):
            self.assertIn(line, db)
        self.assertFalse([l for l in db if l.startswith(('network.wwan06', 'system.led_4g'))], db)

    def test_customized_wwan_untouched(self):
        custom = FIREWALL + ['network.wwan0=interface', 'network.wwan0.proto=dhcp', 'network.wwan0.device=usb0']
        db = self.run_defaults(custom)
        self.assertIn('network.wwan0.proto=dhcp', db)
        self.assertIn('network.wwan0.device=usb0', db)

    def test_wwan_in_custom_zone_not_added_to_wan(self):
        db = self.run_defaults(FRESH + ['firewall.lte=zone', 'firewall.lte.name=lte',
                                        'firewall.lte.network=wwan0', 'firewall.lte.network=wwan0'])
        self.assertEqual(db.count('firewall.lte.network=wwan0'), 1)
        self.assertNotIn('firewall.wan.network=wwan0', db)

    def test_led_follows_wwan_device(self):
        self.assertEqual(self.run_led(FRESH, 'ifup'), {'trigger': 'netdev', 'device_name': 'usb0', 'link': '1'})
        self.assertEqual(self.run_led(FRESH, 'ifdown'), {'trigger': 'none'})

    def test_led_configured_in_luci_wins(self):
        db = FRESH + ['system.led_mine=led', 'system.led_mine.sysfs=white:4g']
        self.assertEqual(self.run_led(db, 'ifup'), {'trigger': 'none'})

    def test_other_boards_untouched(self):
        self.assertEqual(self.run_defaults(LEGACY, board='tplink,mr600-v2-eu'), LEGACY)

    def test_network_uses_ncm_on_at_port(self):
        text = PATCH.read_text()
        self.assertIn('+\t\tucidef_set_interface "wwan0" device "/dev/ttyUSB0" protocol "ncm"', text)
        # board.d runs on every boot; firewall changes belong in uci-defaults
        network = text.split('board.d/02_network', 1)[1].split('\ndiff --git', 1)[0]
        self.assertNotIn('uci add_list', network)


if __name__ == '__main__':
    unittest.main()
