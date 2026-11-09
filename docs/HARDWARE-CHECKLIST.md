# Hardware checklist

Offline checks prove patches, configuration, packaging and image size. They cannot prove that the modem, SIM, Wi-Fi calibration, LEDs or buttons work. Use this list on the first physical MR500, together with the recovery preparation in [layout](HARDWARE-AND-GEOMETRY.md). Record each result.

## Before the first OpenWrt boot

Save the modem state from the stock shell, so it can be restored later. Even an initramfs boot brings up `wwan0`, and `ncm` then writes PDP context 1.

```
AT+GTUSBMODE?
AT+GTAUTOCONNECT?
AT+CGDCONT?
AT+GTRNDIS?
```

Record the stock modem firmware revision (`AT+CGMR`) as well. Do not change the USB mode while qualifying the device.

The stock firmware itself forces USB mode 36 (NCM) at every boot and clears PDP context 1 before each connection, using context 2 for data. Returning to stock therefore restores both; the saved values are a cross-check.

## RAM-only test before installing

Run every check below from the initramfs image first. It runs from RAM and writes nothing to the NOR flash; a power cycle returns to stock. It needs the serial console (3.3 V UART, 115200 8N1) and a TFTP server, as documented by thezedt.

1. Interrupt U-Boot with `4` or `tpl`, load `openwrt-...-tplink_mr500-v1-eu-initramfs-kernel.bin` with `tftpboot`, then `bootm`.
2. Before anything else, copy every partition of this router to the PC over SSH (`cat /proc/mtd`, then each `/dev/mtdN`). The `romfile`, `config` and `radio` partitions hold this unit's MAC addresses, identity and Wi-Fi calibration; no other dump can replace them. Keep the copies off the router and record their SHA-256.
3. Go through the modem, SIM and board checks below. Only when they pass, install the sysupgrade image from the initramfs system.
4. If a check fails, power cycle: the router boots stock again. Report the failing check with `logread` and `dmesg`.

## Modem and SIM

1. `ls /dev/ttyUSB*` shows the option ports. `/dev/ttyUSB0` answers `AT` with `OK`. If another port answers instead, set it as the modem device of `wwan0` in LuCI and report it.
2. `ifstatus wwan0` and `ifstatus wwan0_4` are up, and `wwan0_4` has an IPv4 address.
3. A LAN client reaches the internet over LTE, with the WAN cable unplugged.
4. With a PIN-locked SIM: a wrong PIN leaves `wwan0` down with `PIN_FAILED` in `logread`; the correct PIN set in LuCI connects.
5. An APN set in LuCI is used: `AT+CGDCONT?` shows it after reconnecting.
6. The network mode set in LuCI (LTE, UMTS, automatic) is accepted without `SETMODE_FAILED`.
7. The 4G LED turns on with the `wwan0` link and off when the interface is stopped.
8. `uci show firewall` lists `wwan0` once in the `wan` zone, also after a reboot and after a sysupgrade that keeps settings.
9. After a kept-settings sysupgrade from a `20261009` image, `wwan0` uses `proto ncm` on `/dev/ttyUSB0`, `wwan06` and the old `led_4g` entry are gone.

## Board

1. Ethernet: `lan1`-`lan3` and `wan` link and pass traffic; `wan` gets a DHCP address.
2. MAC addresses: LAN uses the label MAC, WAN is LAN+1, and the radios match the stock assignment.
3. Wi-Fi: 2.4 GHz (MT7603E) and 5 GHz (MT7613) start, scan and pass traffic at expected range. Weak signal or no start can point to wrong calibration data.
4. LEDs: power, LAN, WAN and WLAN follow their triggers.
5. Buttons: `reset` reboots on a short press, factory-resets on a long press, and enters failsafe during boot; `wlan` toggles the radios.
6. `sysupgrade -T` accepts the sysupgrade image, and the compatibility check rejects images without compatibility 2.0.
