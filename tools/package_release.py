#!/usr/bin/env python3
"""Package verified executables, tests, profiles and Git history. Never creates placeholder apps."""
import argparse, hashlib, json, shutil, subprocess, zipfile
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', type=Path, required=True)
p.add_argument('--windows', type=Path, required=True)
p.add_argument('--apk', type=Path, required=True)
p.add_argument('--installer', type=Path, required=True)
p.add_argument('--checks', type=Path, required=True)
a = p.parse_args()
version = (ROOT/'VERSION').read_text().strip()
output = a.output.resolve(); output.mkdir(parents=True, exist_ok=True)
release = output/f'SIM_CONTROL_STUDIO_{version}'
if release.exists(): raise SystemExit('Choose a new output directory; existing release is preserved.')
for path in [a.windows/'SimControlStudio.Bridge.exe', a.installer]:
    if not path.is_file() or path.read_bytes()[:2] != b'MZ': raise SystemExit(f'Windows PE missing: {path}')
with zipfile.ZipFile(a.apk) as apk:
    names = apk.namelist()
    if 'AndroidManifest.xml' not in names or not any(n.endswith('.dex') for n in names) or not any(n.endswith('/libflutter.so') for n in names):
        raise SystemExit('APK is not a built Flutter Android application.')
    if apk.testzip(): raise SystemExit('Corrupt APK.')
bridge_path = ROOT/'tests/results/windows-bridge-tests.json'
if not bridge_path.is_file(): bridge_path = ROOT/'tests/results/bridge-tests.json'
bridge = json.loads(bridge_path.read_text())
profiles = json.loads((ROOT/'tests/results/profile-tests.json').read_text())
if bridge['failed'] or profiles['failed']: raise SystemExit('Regression checks failed.')
flutter = [json.loads(line) for line in (a.checks/'flutter-tests.jsonl').read_text().splitlines() if line.startswith('{')]
if not any(e.get('type') == 'done' and e.get('success') is True for e in flutter): raise SystemExit('No successful real Flutter test completion.')
for name in ['Android','iOS','Windows','Source','Profiles','Documentation','Tests']:
    (release/name).mkdir(parents=True)
excluded = {'.git','bin','obj','build','.dart_tool','.gradle','Pods','.symlinks','releases','__pycache__','_staging','_release-input','_release-output'}
def ignore(directory, names):
    return [n for n in names if n in excluded or n.endswith(('.pfx','.jks','.keystore','.pyc')) or n in {'local.properties','key.properties'}]
shutil.copytree(ROOT, release/'Source/sim-control-studio', ignore=ignore)
shutil.copytree(a.windows, release/'Windows', dirs_exist_ok=True)
shutil.copy2(a.installer, release/'Windows'/a.installer.name)
shutil.copy2(a.apk, release/'Android'/f'SIM_CONTROL_STUDIO_{version}.apk')
shutil.copytree(ROOT/'vehicle_profiles', release/'Profiles', dirs_exist_ok=True)
shutil.copytree(ROOT/'documentation', release/'Documentation', dirs_exist_ok=True)
shutil.copytree(ROOT/'mobile_flutter/ios', release/'iOS/ios-project', ignore=ignore)
shutil.copytree(ROOT/'tests/results', release/'Tests', dirs_exist_ok=True)
shutil.copytree(a.checks, release/'Tests/Android-CI', dirs_exist_ok=True)
shutil.copy2(ROOT/'documentation/IOS.md', release/'iOS/BUILD_AND_SIGN.md')
(release/'KEZDD_ITT.md').write_text(f'''# SIM CONTROL STUDIO {version}

Android: `Android/SIM_CONTROL_STUDIO_{version}.apk`.
Windows: `Windows/{a.installer.name}` vagy a hordozható `Windows/SimControlStudio.Bridge.exe`.

Első indítás és DEMO: `Documentation/ELSO_INDITAS.md`.
A teljes forrás, az eredeti 20 autó / 40 egyedi elrendezés és a Git-előzmény a csomag része.
Visszaállítás: `git clone Source/sim-control-studio.bundle sim-control-studio`.

Valódi CI-fordítás és automatizált tesztek: `Tests/Android-CI`, `Tests/windows-bridge-tests.json`.
A DEMO-adatok szimuláltak. A két hálózati tesztkliens nem két fizikai mobil.
A konkrét Rally-verzió, Windows játékbemenet, telefonos telepítés és Wi-Fi még fizikai ellenőrzést igényel.
iOS IPA nincs. A profilok grafikai hűsége: 1 részleges referencia, 19 inspirált; nincs hitelesített gyári replika.

Részletes állapot: `Documentation/FUNKCIOMATRIX_0.2.0.md` és `STATUS.json`.
A preview APK CI-aláírása futásonként eltérhet; frissítés előtt exportáld személyes profiljaidat.
''', encoding='utf-8')
commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
subprocess.run(['git','bundle','create',str(release/'Source/sim-control-studio.bundle'),'--all'], cwd=ROOT, check=True)
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as file:
        for chunk in iter(lambda:file.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
manifest = {'application':'SIM CONTROL STUDIO','version':version,'generatedAtUtc':datetime.now(timezone.utc).isoformat(),
    'sourceCommit':commit,'releaseKind':'installable_preview','androidApkIncluded':True,'windowsInstallerIncluded':True,
    'signedIosIpaIncluded':False,'physicalTestsPerformed':False,
    'files':[{'path':str(f.relative_to(release)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(release.rglob('*')) if f.is_file()]}
(release/'MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
def archive(folder, path, exclude=()):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in sorted(folder.rglob('*')):
            if f.is_file() and f.name not in exclude: z.write(f, Path(folder.name)/f.relative_to(folder))
    with zipfile.ZipFile(path) as z:
        if z.testzip(): raise RuntimeError('Corrupt release archive')
    return path
assets = [archive(release, output/f'SIM_CONTROL_STUDIO_{version}_RELEASE.zip'),
    archive(release/'Source', output/f'SIM_CONTROL_STUDIO_{version}_Source.zip'),
    archive(release/'Windows', output/f'SIM_CONTROL_STUDIO_{version}_Windows_x64.zip', exclude={a.installer.name})]
for src, name in [(a.apk, f'SIM_CONTROL_STUDIO_{version}.apk'), (a.installer,a.installer.name)]:
    dest=output/name; shutil.copy2(src,dest); assets.append(dest)
(output/'SHA256SUMS.txt').write_text(''.join(f'{sha(f)}  {f.name}\n' for f in assets))
print(json.dumps({'sourceCommit':commit,'assets':[{'file':f.name,'bytes':f.stat().st_size,'sha256':sha(f)} for f in assets]}, indent=2))
