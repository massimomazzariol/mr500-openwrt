# Licensing and binary publication audit

The frozen firmware is an aggregate of separately licensed OpenWrt/Linux components, not a single work covered solely by this repository's LICENSE. Root LICENSE applies to project-owned scripts/documentation; file-specific upstream terms remain authoritative.

The publication audit inventories **131 UPSTREAM packages** and resolves their build recipes and source archives. Linux/kernel modules, BusyBox and other GPL components have corresponding source, modifications and build configuration supplied through the release's source bundle and this repository. LGPL components (including ubus/uci) have original source/license terms and build recipes; the source permits rebuilding and replacing libraries. musl uses MIT terms; libgcc is supplied under GPLv3 with the GCC Runtime Library Exception 3.1. Mbed TLS offers Apache-2.0 OR GPL-2.0-or-later; original dual-license notices remain supplied. Other BSD/ISC/MIT/Zlib notices remain in their source archives and binary license companion.

The MediaTek Wi-Fi firmware has **separate non-open-source binary redistribution terms**. Its license permits unmodified binary redistribution with copyright/disclaimer, non-endorsement and other conditions. Each installed blob in the frozen image was compared byte for byte with the licensed original mt76 archive. The complete unchanged MediaTek notice accompanies the binary assets in `LICENSE-NOTICES.tar.gz`; it is not relabeled GPL or modified. No claim of unrestricted reverse-engineering permission is made for these blobs.

PPP's required acknowledgment is retained: This product includes software developed by Computing Services at Carnegie Mellon University (http://www.cmu.edu/computing/). PPP's original COPYING and BSD/GPL license files accompany the release. Other package acknowledgments/notices remain supplied as well.

Every experimental binary release is accompanied at the same release location by:

- `mr500-corresponding-source-20261009.tar.gz`: exact core/feed source snapshots and 107 original source archives, with original copyright/license files. Restricted, unrelated Broadcom archives are excluded.
- `LICENSE-NOTICES.tar.gz`: unchanged attribution/license texts, including the MediaTek firmware notice and PPP acknowledgment.
- `BUILD-METADATA-upstream-20261009.tar.gz`: full resolved configuration, package manifest, pinned revisions, image hashes, source inventory and notices-verification receipt.
- `SHA256SUMS`, `SOURCES-SHA256SUMS` and `RELEASE-SHA256SUMS`.

The shared device/formatter changes are the two repository patches. Binary/source links, source preparation and build scripts are in README and docs/BUILD.md; corresponding source is actually delivered, rather than relying solely on an upstream URL or disclaimer. All original license/attribution/modification notices remain applicable. The diagnostic's original source and musl/GCC runtime sources are also supplied.

No OEM TP-Link firmware, extracted proprietary library, real device dump, calibration, credential or unreviewed third-party material is published here. Eligibility was checked against retained source/license evidence, not inferred from a private repository setting. Image checks found no embedded private signing key, personal build path or nonempty authorized_keys. Native image contents and hashes were not changed during publication.
