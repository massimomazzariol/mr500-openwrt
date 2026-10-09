# Hardware and protected geometry

MR500 V1 EU: MT7621DAT, 128 MiB DDR3, 16 MiB SPI NOR, MT7530 switch,
MT7603EN 2.4 GHz, MT7613BEN 5 GHz (mt7615/mt7663 driver/firmware family),
Fibocom FG621-EA LTE modem over USB. Exact retail component IDs, GPIO behavior,
port mapping, MAC derivations and modem interface names need hardware checks.
The prototype source follows the earlier community port; it is not an accepted
OpenWrt target. The default modem USB mode is not changed automatically.

| Region | Half-open physical range | Policy |
|---|---|---|
| U-Boot | 0x000000–0x020000 | read-only |
| firmware | 0x020000–0xfa0000 | sole firmware/rootfs/overlay span |
| dualconfig | 0xfa0000–0xfb0000 | read-only, reserved on both profiles |
| ispconfig | 0xfb0000–0xfc0000 | read-only, reserved on both profiles |
| romfile / identity | 0xfc0000–0xfd0000 | read-only |
| config | 0xfd0000–0xfe0000 | read-only |
| filler / vendor data | 0xfe0000–0xff0000 | read-only |
| radio calibration | 0xff0000–0x1000000 | read-only |

Firmware length is `0xf80000` = 16,252,928 bytes = 15,872 KiB (15.5 MiB).
At 64-KiB erase geometry, sectors 2–249 belong to firmware; sectors 0–1 and
250–255 remain protected. Stock 1.11 reserves dualconfig/ispconfig; stock 1.10
allows its rootfs to extend over those addresses. Conservatively reserve them
for both. A stock 1.10 backup/rollback still needs the original full-region data,
including bytes omitted from the new usable firmware span.

The TP-Link tag is 512 bytes; native boot uImage begins at physical 0x20200.
Rootfs placement is aligned dynamically after the kernel; do not hardcode the
old fixture's offset. `openwrt,uimage` splitting accounts for the tag. SquashFS
and JFFS2 overlay are children of the bounded firmware partition and cannot
allocate beyond 0xfa0000 through normal partition-based sysupgrade.
Read-only partition attributes constrain normal MTD paths, not malicious root
access to unrelated raw interfaces.

The image recipe limits factory and sysupgrade to 15,872 KiB, checks sysupgrade
again after metadata, and uses a dedicated `16Mmr500safe` formatter layout.
The formatter leaves alignment/EOF headroom and rejects rootfs overflow.
Factory format is a boot container, **not evidence of stock WebUI acceptance**.
The safe source sets image compatibility 2.0 and the running board's compatibility
version to 2.0. This should reject ordinary upgrades to old 1.x geometry; force
options can bypass policy and must not be used. Both actual metadata and installed
board policy must be checked on a full build and again on hardware.
