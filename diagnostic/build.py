#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import os,pathlib,subprocess,hashlib,json
D=pathlib.Path(__file__).resolve().parent
cc=os.environ.get('CC','mipsel-openwrt-linux-musl-gcc')
cmd=[cc,'-std=c99','-Os','-Wall','-Wextra','-Werror','-march=mips32r2','-mabi=32','-msoft-float','-static','-s','-Wl,-z,noexecstack','-ffile-prefix-map='+str(D)+'=.','mr500-diagnostic.c','-o','mr500-diagnostic-mips-static']
subprocess.run(cmd,cwd=D,check=True)
b=D/'mr500-diagnostic-mips-static'
(D/'binary-provenance.json').write_text(json.dumps({'source_sha256':hashlib.sha256((D/'mr500-diagnostic.c').read_bytes()).hexdigest(),'binary_sha256':hashlib.sha256(b.read_bytes()).hexdigest(),'bytes':b.stat().st_size,'command':['$CC' if x==cc else x.replace(str(D),'.') for x in cmd],'libc':'musl 1.2.6 (MIT), statically linked','libgcc':'GCC 14.4.0, GCC Runtime Library Exception 3.1','architecture':'ELF32 MIPS little endian o32 MIPS32r2 soft float','proprietary_code':False,'hardware_tested':False},indent=2)+'\n')
