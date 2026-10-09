# Read-only stock-shell diagnostic

`diagnostic/mr500-diagnostic.c` is original GPL-2.0-only code, without proprietary implementation or device identity data. `diagnostic/mr500-diagnostic-mips-static` is a 59,080-byte ELF32 little-endian o32 MIPS32r2 soft-float executable, statically linked with musl 1.2.6 and libgcc's runtime exception. Their notices and corresponding source are supplied with releases.

Its default mode prints JSON to standard output. It only reads whitelisted regular proc/sys/identity candidate files, lists process/init-script names, checks device metadata/permissions without opening devices, and calls statvfs for temporary storage. It never opens flash, MTD or watchdog devices; never issues a device ioctl, erases/programs, reboots, stops services, changes permissions or transmits data. It does not copy credentials, process arguments, configuration dumps, MACs or calibration. Treat any report obtained from your own hardware as private evidence; save it locally and review before sharing.

```sh
./mr500-diagnostic-mips-static
```

There are no installation options. `--fixture-root ABSOLUTE` is explicitly labeled synthetic and cannot authorize writes. QEMU tests cover both retained stock 1.10/1.11 library prefixes, synthetic proc/sys/model/version/watchdog observations, missing interfaces, host observations and rejection of an installation option. User-mode QEMU uses the host kernel and filesystem; a library prefix is not a running stock system.

Candidate model, hardware and firmware version files are reported with source and uncertainty. When the stock environment exposes none of these, identity remains UNKNOWN: CPU type, 128-MiB RAM and 16-MiB flash are insufficient to identify a board. Label/OEM identity checks remain necessary; no guessed vendor function ABI is called. Device-node presence/read permissions do not prove actual read-only backup support or complete chip coverage. No backup device is read by this utility. Process names and watchdog sysfs observations do not prove absence of kernel or hardware watchdogs.

Rebuild with a permitted MIPS musl compiler:

```sh
CC=/path/to/mipsel-openwrt-linux-musl-gcc python3 diagnostic/build.py
```

`binary-provenance.json` and sanitized test receipts preserve hashes and compiler flags. Physical stock execution, ABI/runtime compatibility and all real-device checks remain pending.
