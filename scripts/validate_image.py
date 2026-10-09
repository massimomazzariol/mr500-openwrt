#!/usr/bin/env python3
"""Independent, regular-file-only MR500 image audit. No hardware access."""
import argparse
import hashlib
import json
import lzma
from pathlib import Path
import stat
import struct
import subprocess
import zlib

SPAN = 0xf80000
START = 0x20000

def need(condition, message):
    if not condition:
        raise ValueError(message)

def fdt_properties(data):
    magic, total, off_struct, off_strings = struct.unpack_from('>4I', data)
    need(magic == 0xd00dfeed and total == len(data), 'Invalid appended DTB')
    stack, props, pos = [], {}, off_struct
    while pos < len(data):
        token = struct.unpack_from('>I', data, pos)[0]; pos += 4
        if token == 1:
            end = data.index(b'\0', pos)
            stack.append(data[pos:end].decode()); pos = (end + 4) & ~3
        elif token == 2:
            stack.pop()
        elif token == 3:
            size, name_offset = struct.unpack_from('>II', data, pos); pos += 8
            name_start = off_strings + name_offset
            name = data[name_start:data.index(b'\0', name_start)].decode()
            props[('/'.join(stack), name)] = data[pos:pos + size]
            pos = (pos + size + 3) & ~3
        elif token == 4:
            continue
        elif token == 9:
            break
        else:
            raise ValueError('Invalid FDT token')
    return props

def audit(path, unsquashfs=None):
    need(stat.S_ISREG(path.stat().st_mode) and not path.is_symlink(), 'Only isolated regular image files accepted')
    data = path.read_bytes()
    need(576 <= len(data) <= SPAN, 'Image exceeds conservative firmware span')
    sysupgrade = 'sysupgrade' in path.name
    initramfs = 'initramfs' in path.name
    metadata = None
    payload = data
    if sysupgrade:
        magic, crc, kind, size = struct.unpack_from('>IIB3xI', data, len(data) - 16)
        need(magic == 0x46577830 and kind == 1 and 24 < size <= len(data), 'Missing fwtool metadata')
        need(crc == (zlib.crc32(data[:-16]) ^ 0xffffffff), 'Metadata CRC mismatch')
        metadata = json.loads(data[len(data) - size + 8:-16])
        need(metadata.get('compat_version') == '2.0', 'Unsafe compatibility metadata')
        need('tplink,mr500-v1-eu' in metadata.get('new_supported_devices', []), 'Wrong new supported device')
        payload = data[:-size]
    need(struct.unpack_from('<I', payload)[0] == 3, 'Wrong TP-Link header version')
    need(struct.unpack_from('>I', payload, 0x70)[0] == SPAN, 'Wrong TP-Link capacity declaration')
    ko, kl, ro, rl, bo, bl = struct.unpack_from('>6I', payload, 0x74)
    need(ko == 512 and bo == 0 and bl == 0, 'Unexpected bootloader/kernel offsets')
    salted = bytearray(payload)
    stored = bytes(salted[0x40:0x50])
    salted[0x40:0x50] = bytes.fromhex('dcd73aa5c39598fbdcf9e7f40eae4737')
    need(hashlib.md5(salted).digest() == stored, 'TP-Link MD5 mismatch')
    hdr = bytearray(payload[512:576])
    magic, hc, timestamp, length, load, entry, dc = struct.unpack_from('>7I', hdr)
    need(magic == 0x27051956 and hdr[28:32] == bytes([5, 5, 2, 3]), 'Wrong MIPS Linux LZMA uImage format')
    need(load == entry == 0x80001000, 'Unexpected uImage load/entry address')
    struct.pack_into('>I', hdr, 4, 0)
    need(zlib.crc32(hdr) == hc, 'uImage header CRC mismatch')
    need(576 + length <= len(payload) and 64 + length == kl, 'Kernel length mismatch')
    packed = payload[576:576 + length]
    need(zlib.crc32(packed) == dc, 'uImage data CRC mismatch')
    expanded = lzma.decompress(packed, memlimit=256 * 1024**2)
    dtpos = expanded.rfind(bytes.fromhex('d00dfeed'))
    need(dtpos >= 0, 'Appended DTB missing')
    props = fdt_properties(expanded[dtpos:])
    need(b'tplink,mr500-v1-eu\0' in props[('', 'compatible')], 'Wrong DTB device')
    expected = {'uboot': (0, 0x20000), 'firmware': (0x20000, SPAN),
                'dualconfig': (0xfa0000, 0x10000), 'ispconfig': (0xfb0000, 0x10000),
                'romfile': (0xfc0000, 0x10000), 'config': (0xfd0000, 0x10000),
                'filler': (0xfe0000, 0x10000), 'radio': (0xff0000, 0x10000)}
    seen = {}
    for (node, key), value in props.items():
        if key != 'label' or value.rstrip(b'\0').decode() not in expected:
            continue
        label = value.rstrip(b'\0').decode()
        need(label not in seen, 'Duplicate partition label')
        need(struct.unpack('>II', props[(node, 'reg')]) == expected[label], 'Wrong partition geometry: ' + label)
        need(label == 'firmware' or (node, 'read-only') in props, 'Unprotected partition: ' + label)
        if label == 'firmware':
            need(props[(node, 'openwrt,offset')] == struct.pack('>I', 512), 'Wrong splitter offset')
        seen[label] = expected[label]
    need(seen == expected, 'Missing protected partitions')
    result = {'file': path.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
              'status': 'UNTESTED ON PHYSICAL HARDWARE', 'dtb_sha256': hashlib.sha256(expanded[dtpos:]).hexdigest(),
              'partitions': seen, 'metadata': metadata, 'container_bytes_remaining': SPAN - len(data),
              'uimage_load': load, 'uimage_entry': entry, 'kernel_container_bytes': kl,
              'installed_board_policy_checked': False}
    if not initramfs:
        need(ro % 0x10000 == 0 and ko + kl <= ro and ro + rl <= len(payload), 'Rootfs bounds invalid')
        need(payload[ro:ro + 4] == b'hsqs', 'SquashFS missing')
        used = struct.unpack_from('<Q', payload, ro + 40)[0]
        need(96 <= used <= rl and struct.unpack_from('<H', payload, ro + 28)[0] == 4, 'Invalid SquashFS superblock')
        overlay = (START + ro + used + 0xffff) & ~0xffff
        need(overlay < 0xfa0000, 'No overlay capacity')
        markers = [pos for pos in range((ro + used + 3) & ~3, len(payload) - 3, 4)
                   if payload[pos:pos + 4] == bytes.fromhex('deadc0de')]
        need(markers and all(pos + 4 <= SPAN for pos in markers), 'Missing bounded JFFS2 EOF marker')
        result.update(rootfs_physical=START + ro, squashfs_bytes_used=used,
                      overlay_start_estimate=overlay, overlay_capacity_estimate=0xfa0000 - overlay,
                      eof_offsets=markers)
        if unsquashfs:
            policy = subprocess.check_output([str(unsquashfs), '-cat', '-o', str(ro), str(path),
                                              'etc/board.d/05_compat-version'], timeout=30).decode()
            need('tplink,mr500-v1-eu)' in policy and
                 'ucidef_set_compat_version "2.0"' in policy.split('tplink,mr500-v1-eu)', 1)[1].split(';;', 1)[0],
                 'Installed MR500 compatibility guard missing')
            result['installed_board_policy_checked'] = True
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--unsquashfs', type=Path, help='Mandatory in full build audit; verify installed compatibility policy')
    args = parser.parse_args()
    print(json.dumps(audit(args.image, args.unsquashfs), indent=2))
