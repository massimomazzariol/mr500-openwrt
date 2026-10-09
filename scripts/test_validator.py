#!/usr/bin/env python3
"""Validate a conservative factory fixture and reject geometry/integrity mutations.
The fixture may be recomposed: these tests do not certify a full build or hardware.
"""
import argparse
import hashlib
import json
import lzma
from pathlib import Path
import struct
import tempfile
import zlib
from validate_image import audit

def repack(original, mutate):
    data = bytearray(original)
    length = struct.unpack_from('>I', data, 524)[0]
    kernel = bytearray(lzma.decompress(data[576:576 + length]))
    pos = kernel.rfind(bytes.fromhex('d00dfeed'))
    kernel[pos:] = mutate(bytes(kernel[pos:]))
    compressed = lzma.compress(kernel, format=lzma.FORMAT_ALONE,
                              filters=[{'id': lzma.FILTER_LZMA1, 'dict_size': 8 * 1024**2,
                                        'lc': 1, 'lp': 2, 'pb': 2}])
    rootfs = struct.unpack_from('>I', data, 0x7c)[0]
    if 576 + len(compressed) > rootfs:
        raise RuntimeError('Mutation exceeds kernel allocation')
    data[576:rootfs] = b'\xff' * (rootfs - 576)
    data[576:576 + len(compressed)] = compressed
    struct.pack_into('>I', data, 0x78, len(compressed) + 64)
    struct.pack_into('>I', data, 524, len(compressed))
    struct.pack_into('>I', data, 536, zlib.crc32(compressed))
    struct.pack_into('>I', data, 516, 0)
    struct.pack_into('>I', data, 516, zlib.crc32(data[512:576]))
    data[0x40:0x50] = bytes.fromhex('dcd73aa5c39598fbdcf9e7f40eae4737')
    data[0x40:0x50] = hashlib.md5(data).digest()
    return data

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('factory_fixture', type=Path)
    args = ap.parse_args()
    original = args.factory_fixture.read_bytes()
    rows = [{'case': 'valid conservative fixture', 'result': 'accepted', 'audit': audit(args.factory_fixture)}]
    cases = {'oversize': original + b'\xff',
             'integrity failure': original[:600] + bytes([original[600] ^ 1]) + original[601:],
             'protected flags removed': repack(original, lambda dt: dt.replace(b'read-only\0', b'read-onlx\0')),
             'unsafe firmware end': repack(original, lambda dt: dt.replace(struct.pack('>II', 0x20000, 0xf80000),
                                                                        struct.pack('>II', 0x20000, 0xfa0000)))}
    with tempfile.TemporaryDirectory(prefix='mr500-validator-') as tmp:
        for name, data in cases.items():
            path = Path(tmp) / (name.replace(' ', '-') + '-factory.bin')
            path.write_bytes(data)
            try:
                audit(path)
            except ValueError as exc:
                rows.append({'case': name, 'result': 'rejected', 'reason': str(exc)})
            else:
                raise AssertionError('Invalid fixture accepted: ' + name)
    print(json.dumps({'status': 'PASS', 'scope': 'offline fixture and image mutations', 'checks': rows}, indent=2))

if __name__ == '__main__':
    main()
