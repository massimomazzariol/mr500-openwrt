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

## Modem and SIM

1. `ls /dev/ttyUSB*` shows the option ports. `/dev/ttyUSB0` answers `AT` with `OK`. If another port answers instead, set it as the modem device of `wwan0` in LuCI and report it.
2. `ifstatus wwan0` and `ifstatus wwan0_4` are up, and `wwan0_4` has an IPv4 address.
3. A LAN client reaches the internet over LTE, with the WAN cable unplugged.
4. With a PIN-locked SIM: a wrong PIN leaves `wwan0` down with `PIN_FAILED` in `logread`; the correct PIN set in LuCI connects.
5. An APN set in LuCI is used: `AT+CGDCONT?` shows it after reconnecting.
6. The network mode set in LuCI (LTE, UMTS, automatic) is accepted without `SETMODE_FAILED`.
7. The 4G LED turns on with the `wwan0` link and off when the interface is stopped.
8. `uci show firewall` lists `wwan0` once in the `wan` zone, also after a reboot and after a sysupgrade that keeps settings.

## Board

1. Ethernet: `lan1`-`lan3` and `wan` link and pass traffic; `wan` gets a DHCP address.
2. MAC addresses: LAN uses the label MAC, WAN is LAN+1, and the radios match the stock assignment.
3. Wi-Fi: 2.4 GHz (MT7603E) and 5 GHz (MT7613) start, scan and pass traffic at expected range. Weak signal or no start can point to wrong calibration data.
4. LEDs: power, LAN, WAN and WLAN follow their triggers.
5. Buttons: `reset` reboots on a short press, factory-resets on a long press, and enters failsafe during boot; `wlan` toggles the radios.
6. `sysupgrade -T` accepts the sysupgrade image, and the compatibility check rejects images without compatibility 2.0.
