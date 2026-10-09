# Restore and build UPSTREAM

Download `mr500-corresponding-source-20261009.tar.gz` and `SOURCES-SHA256SUMS` from the same experimental release as the images. Verify the bundle checksum, then:

```sh
python3 scripts/prepare_source.py mr500-corresponding-source-20261009.tar.gz /absolute/new-build --sha256 HASH_FROM_SOURCES_SHA256SUMS
python3 scripts/build.py --tree /absolute/new-build/openwrt --preflight-only
python3 scripts/build.py --tree /absolute/new-build/openwrt --jobs 2
```

Preparation restores the exact source snapshots, downloaded source archives, shared patches and frozen resolved UPSTREAM config. Feed indexing uses `update -i`, without fetching new revisions. `sources.lock.json` identifies the original commits. Source snapshots are release assets, not a redundant full source tree in this repository. Original copyright/license files are retained in the snapshots and archives.

Host requirements: Linux x86-64, GNU build tools, GCC/G++, GNU make, Perl, Python 3.12 or newer (safe tar extraction), Git, patch/quilt, pkgconf, flex/bison, ncurses development files, zstd/xz/bzip2, OpenSSL development files and usual OpenWrt build prerequisites. Budget at least 16 GiB of build space plus source storage and several GiB RAM. These are external host dependencies, not redistributed toolchain binaries.

No OpenWrt rebuild was done during publication. Source restoration and patch/configuration preflight are rehearsed; a complete fresh recompilation and bit-for-bit equality are **not demonstrated**. Package-signing private keys are excluded and must be generated independently; the original public key is retained for provenance. Signing keys and host/tool versions can change rebuilt bytes. SOURCE_DATE_EPOCH is pinned. Kernel/module/toolchain sources and build recipes are included in the corresponding-source release bundle.

Offline checks after obtaining images:

```sh
sha256sum -c releases/upstream-20261009/SHA256SUMS
python3 scripts/test_validator.py path/to/openwrt-ramips-mt7621-tplink_mr500-v1-eu-squashfs-factory.bin
python3 scripts/validate_image.py path/to/image.bin --unsquashfs /path/to/unsquashfs
```

Run the checksum command in the image asset directory, using the repository manifest's absolute path if needed. None of these commands writes hardware.
