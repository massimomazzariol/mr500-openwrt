# Archer MR500 V1 EU - independent experimental OpenWrt project

> **EXPERIMENTAL - UNTESTED ON PHYSICAL HARDWARE**
>
> This independent OpenWrt port for the TP-Link Archer MR500 V1 EU has been validated offline only. No image from this project has been installed or booted on a physical MR500.
>
> Installation may render the router unbootable and may require specialized recovery equipment. A safe installation and recovery procedure has not yet been verified. Hardware flashing is not currently recommended.

**Earlier MR500 hardware identification, bring-up, modem and recovery research by [thezedt/mr500v1-openwrt](https://github.com/thezedt/mr500v1-openwrt) is a principal foundation of this work.** See [credits and exact provenance](docs/CREDITS-AND-PROVENANCE.md).

This project contains minimal device-support patches, a pinned UPSTREAM profile, optional profiles, reproducible source preparation, offline image validation and a read-only stock-shell diagnostic. The exact target is **TP-Link Archer MR500 V1 EU**. It is not an official OpenWrt release; no device submission or pull request to official OpenWrt is planned. OpenWrt and Linux remain their upstream authors' work.

The conservative firmware interval is `[0x20000,0xfa0000)` in 16-MiB SPI NOR. U-Boot and the configuration/calibration suffix are reserved. Compatibility version 2.0 protects ordinary sysupgrade from older geometry. Do not bypass it. See [layout](docs/HARDWARE-AND-GEOMETRY.md).

## OpenWrt base

This branch targets the stable release **OpenWrt v25.12.6** (`64900e756e`, `r33311-981c978eff`, Linux 6.12), with the feed commits pinned by that release. `sources.lock.json` records every pin.

The first experimental release (`experimental-upstream-20261009`) was built on an OpenWrt `main` snapshot (`bb6df54d9d`, `r36880`, Linux 6.18). That code is preserved unchanged on the `archive/snapshot-r36880` branch and the `archive-snapshot-r36880` tag. Its build metadata stays in `releases/upstream-20261009/` as history. No v25.12.6 image has been built or published yet.

## Package set

UPSTREAM follows the official OpenWrt v25.12.6 release images for ramips/mt7621: the target default packages, the MR500 device packages, and the LuCI web interface with HTTPS (`luci` and `luci-ssl`, which pull `luci-light`, `luci-app-firewall`, `luci-app-package-manager`, `uhttpd` and `px5g-mbedtls`), plus `luci-proto-ncm` for the LTE modem. The official MR600 v2 EU image, the template of this device, has a 8,323,635-byte sysupgrade with this set; the MR500 limit is 16,252,928 bytes.

Differences from the official images:

- No attended sysupgrade (`luci-app-attendedsysupgrade`, `owut`): the official upgrade server does not know this device, so it cannot build images for it.
- Packages are signed with a key generated on the build host. The image also trusts the official 25.12 key (`openwrt-keyring`), so userspace packages from `downloads.openwrt.org/releases/25.12.6` install with `apk`. Kernel modules must come from the same build, because the kernel differs from the official one.
- Buildbot-only outputs (all kmods, SDK, ImageBuilder, debug info) are not built.

## LTE modem

The Fibocom FG621-EA is driven by OpenWrt's `ncm` protocol (`comgt-ncm`), with the Fibocom profile added upstream in `71118d6522` and tested on the ASUS 4G-AX56, which has the same modem. The default `wwan0` interface uses the AT port `/dev/ttyUSB0` and is in the `wan` firewall zone. `ncm` finds the data netdev from the USB device, so it works whether the modem exposes it as `usb0` (NCM) or `eth1` (RNDIS).

In LuCI, *Network > Interfaces > wwan0* sets the SIM PIN, APN, PDP type (IPv4, IPv6 or both), authentication, and the network mode (LTE, UMTS or automatic). The 4G LED follows the `wwan0` link, unless a 4G LED is configured in *System > LED Configuration*. A sysupgrade that keeps settings from the `20261009` images moves their DHCP-on-`eth1` `wwan0` to `ncm` and drops their stale 4G LED entry; customized settings are left alone.

Not covered by official LuCI: signal strength, operator and SIM status, SMS and band locking. The three signal LEDs are not driven. None of this is verified on hardware yet; see the [hardware checklist](docs/HARDWARE-CHECKLIST.md). On connect, `ncm` writes the PDP context (`AT+CGDCONT`) and starts the data call (`AT+GTRNDIS`); it does not change the modem USB mode or firmware.

## Optional profiles

Optional profiles add to the UPSTREAM seed configuration. Select them with `scripts/prepare_source.py --with NAME`:

| Profile | Adds |
|---|---|
| `relayd-fixes` | `relayd` and its LuCI protocol `luci-proto-relay` ("Relay bridge"), with two package patches for Wi-Fi client relay bridges: directed ARP host-expiry probes ([openwrt/relayd#2](https://github.com/openwrt/relayd/pull/2)) and DHCP replies unicast to the client `chaddr` ([openwrt/relayd#1](https://github.com/openwrt/relayd/pull/1)). See [openwrt/openwrt#24446](https://github.com/openwrt/openwrt/issues/24446) |

The relayd patches are not merged upstream yet. They apply only to relayd `708a76fa`, the version that v25.12.6 ships, and preparation stops if the package source differs. The image-size gate (`check-size`, 15,872 KiB) still applies to every combination.

## Images and source

The [experimental releases](https://github.com/massimomazzariol/mr500-openwrt/releases) provide frozen UPSTREAM initramfs, factory and sysupgrade images, SHA256SUMS, build metadata, license notices and a corresponding-source bundle. PERSONAL customizations and images are not distributed here. The `factory` image is **not verified for TP-Link's stock web interface**. This project provides no qualified physical installation procedure or real-flashing command.

[Build instructions](docs/BUILD.md) describe pinned source preparation. All three image formats of the first release passed offline header/checksum, conservative DTB/layout and filesystem/metadata validation; sysupgrade metadata uses compatibility 2.0. These checks establish file properties, not boot, Ethernet/Wi-Fi/LTE operation, correct calibration, safe installation or recovery. Physical verification is pending December 2026.

The [read-only diagnostic](docs/DIAGNOSTIC.md) reports evidence and unknowns without opening flash/watchdog devices or changing services. QEMU tests execute its actual static MIPS code but do not emulate the stock kernel or MT7621 controller.

## Licensing

Project scripts and documentation: GPL-2.0-only. Existing source-specific notices, including GPL-2.0-or-later DTS, remain authoritative. The earlier reference repository declares GPLv3; its photographs, documents, helper scripts, firmware and logs are not copied into this export. See [licenses and corresponding source](docs/LICENSING.md). Disclaimers do not replace redistribution obligations.
