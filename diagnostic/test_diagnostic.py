#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import pathlib,tempfile,subprocess,json,os,re,hashlib
D=pathlib.Path(__file__).resolve().parent
R=pathlib.Path(os.environ.get('MR500_ROOT',D.parents[2])).resolve()
receipts=[]
with tempfile.TemporaryDirectory(dir=D,prefix='fixture-') as temp:
 root=pathlib.Path(temp)
 for release in ('110','111'):
  files={'tmp/sysinfo/model':'TP-Link Archer MR500 V1 EU','etc/hardware_version':'V1','etc/firmware_version':f'1.{10 if release=="110" else 11}.0 SYNTHETIC','proc/version':'Linux version 3.10.14 SYNTHETIC','proc/mtd':'dev: size erasesize name\nmtd0: 01000000 00010000 "synthetic-nor"\n','proc/meminfo':'MemTotal: 131072 kB\nMemAvailable: 98304 kB\n','proc/42/comm':'watchdog','sys/class/mtd/mtd0/size':'16777216','sys/class/mtd/mtd0/erasesize':'65536','sys/class/watchdog/watchdog0/nowayout':'1'}
  for name,text in files.items():
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text+'\n')
  stock=R/f'work/oem-updater-reuse/rootfs-{release}'
  assert stock.is_dir(),'Restore archived stock QEMU library fixtures or set MR500_ROOT'
  for mode in ('fixture','user-mode-host-observations'):
   cmd=['qemu-mipsel','-strace','-L',str(stock),str(D/'mr500-diagnostic-mips-static')]
   if mode=='fixture':cmd+=['--fixture-root',str(root)]
   p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stderr
   report=json.loads(p.stdout)
   assert report['writes'] is False and report['device_open'] is False and report['hardware_installation_authorized'] is False
   assert not re.search(r'\b(?:reboot|kill|socket|connect|unlink|truncate|chmod|mount|umount)\(',p.stderr)
   assert not re.search(r'(?:open|openat)\([^\n]*"/dev/(?:flash|mtd|watchdog)',p.stderr)
   # ioctl against standard output can be libc tty detection, never a flash device.
   for line in p.stderr.splitlines():
    if 'ioctl(' in line:assert re.search(r'ioctl\((?:0|1|2),',line),line
   if mode=='fixture':
    assert report['execution_scope']=='SYNTHETIC_FIXTURE_UNDER_QEMU'
    assert any(x.get('value')==files['etc/firmware_version'] for x in report['identity_evidence'])
    assert report['relevant_process_names']==[{'pid':'42','comm':'watchdog'}]
   else:assert report['execution_scope']=='OBSERVATIONS_FROM_CURRENT_KERNEL_NOT_INDEPENDENTLY_IDENTIFIED'
   receipts.append({'stock_library_prefix':release,'mode':mode,'status':'PASS','report_sha256':hashlib.sha256(p.stdout.encode()).hexdigest(),'host_kernel_not_stock_kernel':True,'no_device_open_or_destructive_syscall':True})
 # Bad flags cannot activate any write path.
 p=subprocess.run(['qemu-mipsel',str(D/'mr500-diagnostic-mips-static'),'hardware-install'],capture_output=True,text=True);assert p.returncode==2
(D/'test-results.json').write_text(json.dumps({'cases':5,'tests':receipts,'hardware':'PENDING','reports_not_published':'Host/live observations may identify devices or host systems; only sanitized test receipts are public'},indent=2)+'\n')
print('PASS: 4 QEMU runs (two stock prefixes), invalid-operation rejection; no destructive syscalls')
