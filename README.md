# Archer MR500 V1 EU — independent experimental OpenWrt project

> **EXPERIMENTAL — UNTESTED ON PHYSICAL HARDWARE**
>
> This independent OpenWrt port for the TP-Link Archer MR500 V1 EU has been compiled and validated offline, but these particular firmware images have never been installed or booted on a physical MR500.
>
> Installation may render the router unbootable and may require specialized recovery equipment. A safe installation and recovery procedure has not yet been verified. Precompiled images are provided for independent research and evaluation. Hardware flashing is not currently recommended.

**Earlier MR500 hardware identification, bring-up, modem and recovery research by [thezedt/mr500v1-openwrt](https://github.com/thezedt/mr500v1-openwrt) is a principal foundation of this work.** See [credits and exact provenance](docs/CREDITS-AND-PROVENANCE.md).

This project contains minimal device-support patches, a pinned UPSTREAM profile, reproducible source preparation, offline image validation and a read-only stock-shell diagnostic. The exact target is **TP-Link Archer MR500 V1 EU**. It is not an official OpenWrt release; no device submission or pull request to official OpenWrt is planned. OpenWrt and Linux remain their upstream authors' work.

The conservative firmware interval is `[0x20000,0xfa0000)` in 16-MiB SPI NOR. U-Boot and the configuration/calibration suffix are reserved. Compatibility version 2.0 protects ordinary sysupgrade from older geometry. Do not bypass it. See [layout](docs/HARDWARE-AND-GEOMETRY.md).

## Images and source

The [experimental releases](https://github.com/massimomazzariol/mr500-openwrt/releases) provide frozen UPSTREAM initramfs, factory and sysupgrade images, SHA256SUMS, build metadata, license notices and a corresponding-source bundle. PERSONAL customizations and images are not distributed here. The `factory` image is **not verified for TP-Link's stock web interface**. This project provides no qualified physical installation procedure or real-flashing command.

[Build instructions](docs/BUILD.md) describe pinned source restoration. All three image formats passed offline header/checksum, conservative DTB/layout and filesystem/metadata validation; sysupgrade metadata uses compatibility 2.0. These checks establish file properties, not boot, Ethernet/Wi-Fi/LTE operation, correct calibration, safe installation or recovery. Physical verification is pending December 2026.

The [read-only diagnostic](docs/DIAGNOSTIC.md) reports evidence and unknowns without opening flash/watchdog devices or changing services. QEMU tests execute its actual static MIPS code but do not emulate the stock kernel or MT7621 controller.

## Licensing

Project scripts and documentation: GPL-2.0-only. Existing source-specific notices, including GPL-2.0-or-later DTS, remain authoritative. The earlier reference repository declares GPLv3; its photographs, documents, helper scripts, firmware and logs are not copied into this export. See [licenses and corresponding source](docs/LICENSING.md). Disclaimers do not replace redistribution obligations.
