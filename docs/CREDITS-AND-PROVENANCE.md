# Credits and provenance

**thezedt's [mr500v1-openwrt](https://github.com/thezedt/mr500v1-openwrt) is a principal reference**, not work independently created by this project. The reviewed reference snapshot is `754bb75f3a7cdd5cddb0181f4efe94df547dca85`. Its README, relevant file history and root LICENSE were reviewed; the repository declares GPLv3. Later work includes commit `234350c6e7c36d32bb1d4e5d1d915d21d2116fd3` (OpenWrt 25.12, helpers/revert notes) and `7b0f89b4caa414ebe9c498649ccce1cd2280f878` (U-Boot, modem modes, restoring OEM). Its physical experiences do not qualify our new images.

Attribution to thezedt covers MR500 identification (MT7621, RAM/NOR, radios, switch and Fibocom FG621-EA), earlier bring-up, UART/recovery observations, modem USB modes and LTE findings. This export contains no copied README prose, photographs, stock binaries/dumps, helper scripts, PDFs or logs from that repository. File-specific rights were considered; materials whose necessity or rights are unclear remain local. Linking to research does not license its included third-party proprietary material.

OpenWrt's MR600 V2 EU support is the source template for the MR500 DTS, image recipe, network and LED integration. Original addition: `78110c3b5fce119d13cd45dadd33ca396c8ce197`, Linos Giannopoulos. The template also includes upstream WAN-MAC correction `eaa1d41b55901c5c92e7df3ba2c5ff123af8b04d`, Rosen Penev and Jonas Jelonek. The DTS declares GPL-2.0-or-later. Upstream authors' notices are retained. Linux, the MT7621 platform, mt76 and all included packages remain their respective authors' works.

Local MR500 device-support commit `e2c6be5bee0626b10c485ec995a5cc93ae1f3248`, by Massimo Mazzariol, produced `001-device-support.patch`. It changes the copied MR600 template for the MR500 modem/interface, device identity and board wiring. `002-protected-layout.patch` adds the conservative NOR boundary, compatibility 2.0, image-size gates and firmware-utils formatter layout. These are the exact patches used for the frozen UPSTREAM build at OpenWrt baseline `bb6df54d9d1cb486f7102e9863f0380cb9f3a1f3`.

New work here includes conservative-layout analysis and modifications, independent native-image/DTB/checksum/filesystem validation, frozen artifact provenance, source preparation, publication separation and the read-only diagnostic. All remain offline evidence. No official upstream submission is made or intended.

Exact copied/modified third-party sources in the public export:

| Source | Disposition / license |
|---|---|
| MR600 DTS and target image/network/LED templates in pinned OpenWrt | Modified through the two shared patches; original GPL/SPDX terms retained |
| OpenWrt `LICENSES/GPL-2.0` | Unchanged root LICENSE |
| OpenWrt/musl/GCC and MediaTek license notices | Unchanged notices supplied with releases and source bundle |
| Kernel, packages, host tools and feed snapshots | Unchanged corresponding-source archives, with their original notices; modifications are separately supplied as patches |
| thezedt files | No files copied; findings explicitly credited and linked |

The machine-readable `publication-manifest.json` lists each reviewed export and SHA-256. `sources.lock.json`, build metadata, release SHA256SUMS and the corresponding-source manifest identify revisions and artifacts. This repository's own GPL-2.0-only license does not override any third-party file's terms.
