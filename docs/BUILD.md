# Prepare and build UPSTREAM

The source base is OpenWrt v25.12.6. `sources.lock.json` pins the OpenWrt commit, the feed commits, the relayd and firmware-utils versions and `SOURCE_DATE_EPOCH` (the release `version.date`).

```sh
python3 scripts/prepare_source.py /absolute/new-build
python3 scripts/build.py --tree /absolute/new-build/openwrt --preflight-only
python3 scripts/build.py --tree /absolute/new-build/openwrt --jobs 2
```

The UPSTREAM seed includes LuCI with HTTPS, as in official release images. Add optional profiles with `--with`, once per profile:

```sh
python3 scripts/prepare_source.py /absolute/new-build --with relayd-fixes
```

Preparation clones OpenWrt at tag `v25.12.6` and checks that it resolves to the locked commit and version. It fetches the feeds pinned in `feeds.conf` and checks every feed commit. It applies `patches/upstream/*.patch`, then writes `.config` from `profiles/upstream/seed.config` plus the `seed.config` of each selected profile. A profile with `package-patches.json` copies hash-checked patches into that package, and stops if the package source version differs from the one the patches were written for. The output directory must be new. Nothing is compiled, and no device is accessed.

`build.py` runs `make defconfig`, so the resolved configuration is generated on the build host. A resolved v25.12.6 configuration has not been frozen yet; it will be published with the first v25.12.6 build. `python3 scripts/test_prepare_source.py` runs the offline profile checks.

Host requirements: Linux x86-64, GNU build tools, GCC/G++, GNU make, Perl, Python 3.12 or newer, Git, patch/quilt, pkgconf, flex/bison, ncurses development files, zstd/xz/bzip2, OpenSSL development files and usual OpenWrt build prerequisites. Budget at least 16 GiB of build space plus source storage and several GiB RAM. Clone this repository on Linux, or with `core.autocrlf=false`: `.gitattributes` keeps patches byte-exact, but older clones may still hold CRLF copies.

Package-signing private keys are not part of this repository and must be generated independently. Signing keys and host/tool versions can change rebuilt bytes.

## First release (OpenWrt main snapshot)

The `experimental-upstream-20261009` images were built on OpenWrt `main` at `bb6df54d9d` (`r36880`). To restore that exact source from its corresponding-source bundle, check out the `archive/snapshot-r36880` branch and follow its `docs/BUILD.md`. The checksums of those images remain in this branch:

```sh
sha256sum -c releases/upstream-20261009/SHA256SUMS
python3 scripts/test_validator.py path/to/openwrt-ramips-mt7621-tplink_mr500-v1-eu-squashfs-factory.bin
python3 scripts/validate_image.py path/to/image.bin --unsquashfs /path/to/unsquashfs
```

Run the checksum command in the image asset directory, using the repository manifest's absolute path if needed. None of these commands writes hardware.
