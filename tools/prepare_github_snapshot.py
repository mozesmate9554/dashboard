#!/usr/bin/env python3
"""Prepare a committed, secret-free source tree for the GitHub connector.
The output stays in work/ and is not a network credential or a release artifact.
"""
import base64,json,subprocess,sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
commit=sys.argv[1] if len(sys.argv)>1 else 'HEAD'
out=Path(sys.argv[2]) if len(sys.argv)>2 else root.parent/'github-snapshot.json'
rows=[]
for raw in subprocess.check_output(['git','ls-tree','-r','-z',commit],cwd=root).split(b'\0'):
 if not raw:continue
 meta,path=raw.split(b'\t',1);mode,kind,sha=meta.decode().split();name=path.decode()
 if name.endswith(('.jks','.keystore','.pfx','.env')) or name in ('key.properties','local.properties'):
  raise SystemExit('Refusing signing/credential file: '+name)
 data=subprocess.check_output(['git','cat-file','blob',sha],cwd=root)
 try:content=data.decode('utf-8');encoding='utf-8'
 except UnicodeDecodeError:content=base64.b64encode(data).decode();encoding='base64'
 rows.append(dict(path=name,mode=mode,type=kind,sha=sha,content=content,encoding=encoding))
out.write_text(json.dumps({'commit':subprocess.check_output(['git','rev-parse',commit],cwd=root,text=True).strip(),'files':rows},ensure_ascii=False,separators=(',',':')))
print(json.dumps({'files':len(rows),'manifestBytes':out.stat().st_size,'manifestPath':str(out)}))
