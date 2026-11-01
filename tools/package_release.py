#!/usr/bin/env python3
"""Package existing artifacts; no placeholders named APK/IPA and no fabricated tests."""
import hashlib,json,shutil,subprocess,sys,zipfile
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'releases'
WINDOWS=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else ROOT/'releases/Windows'
release=OUTPUT/'SIM_CONTROL_STUDIO_RELEASE'
if release.exists():
    raise SystemExit('Destination already exists. Choose a fresh release output directory.')
exe=WINDOWS/'SimControlStudio.Bridge.exe'
if not exe.is_file() or exe.read_bytes()[:2]!=b'MZ':raise SystemExit('A real Windows PE build is required before packaging.')
report=json.loads((ROOT/'documentation/STATUS.json').read_text())
if report['tests']['bridge']['failed'] or report['tests']['profiles']['failed']:raise SystemExit('Failed checks; release not packaged.')
for name in ['Android','iOS','Windows','Source','Profiles','Documentation','Tests']:(release/name).mkdir(parents=True,exist_ok=True)
excluded={'.git','bin','obj','build','.dart_tool','.gradle','Pods','.symlinks','releases','__pycache__'}
def ignore(directory,names):return [name for name in names if name in excluded or name.endswith(('.pfx','.jks','.keystore','.pyc')) or name in {'local.properties','key.properties'}]
source=release/'Source/sim-control-studio'
shutil.copytree(ROOT,source,ignore=ignore)
for name in ['SimControlStudio.Bridge.exe','profiles.json']:shutil.copy2(WINDOWS/name,release/'Windows'/name)
shutil.copy2(ROOT/'tools/Install-SimControlStudio.ps1',release/'Windows/Install-SimControlStudio.ps1')
shutil.copytree(ROOT/'documentation/licenses',release/'Windows/Licenses')
shutil.copytree(ROOT/'vehicle_profiles',release/'Profiles',dirs_exist_ok=True)
shutil.copytree(ROOT/'documentation',release/'Documentation',dirs_exist_ok=True)
shutil.copytree(ROOT/'mobile_flutter/ios',release/'iOS/ios-project',ignore=ignore)
shutil.copytree(ROOT/'tests/results',release/'Tests',dirs_exist_ok=True)
shutil.copy2(ROOT/'tests/manual-results-template.json',release/'Tests/manual-results-template.json')
shutil.copy2(ROOT/'documentation/ANDROID.md',release/'Android/BUILD_STATUS.md')
shutil.copy2(ROOT/'documentation/IOS.md',release/'iOS/BUILD_AND_SIGN.md')
readme='''# SIM CONTROL STUDIO 0.1.0 – átadási csomag

**Fejlesztői részkiadás. A teljes specifikáció elfogadása még nem teljesült.**

Elindítható Windows x64 Bridge: `Windows/SimControlStudio.Bridge.exe`, a `profiles.json` fájllal együtt. Önálló .NET futtatókörnyezetet tartalmaz. Nem volt Windows GUI/élő játék futtatási teszt.

**Android APK és aláírt iOS IPA nincs ebben a csomagban.** Flutter SDK letöltési korlát, illetve macOS/Xcode/aláírás hiánya miatt ezek nem kerültek lefordításra. A teljes mobilforrás és natív projektek a `Source/sim-control-studio/mobile_flutter` könyvtárban vannak.

18 Bridge-teszt és 25 adat/projektellenőrzés sikeres. A Dart szintaxis ellenőrizve, de Flutter analyze/test/build nem futott. Futó Rally és két fizikai telefon nem volt elérhető.

A 20 autó 40 külön elrendezése a Profiles könyvtárban. Egy részleges és 19 inspirált referenciaállapot; a teljes gyári grafikai hűség nincs igazolva. Vektoros áttekintő: `Documentation/PROFILE_CATALOGUE.pdf`.

Kezdd a `Documentation/ELSO_INDITAS.md` útmutatóval, majd nézd meg az `ALLAPOT.md` és a gépi `STATUS.json` fájlt. Éles ellenőrzés: `TESZTELES.md`. A kompatibilitási mátrix sem állít nem végzett online/játékmódtesztet.

A teljes forrás mellett a helyi Git-előzmény a `Source/sim-control-studio.bundle` fájlból állítható vissza: `git clone sim-control-studio.bundle sim-control-studio`.
'''
(release/'KEZDD_ITT.md').write_text(readme)
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
subprocess.run(['git','bundle','create',str(release/'Source/sim-control-studio.bundle'),'--all'],cwd=ROOT,check=True)
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as file:
        for chunk in iter(lambda:file.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
manifest={'application':'SIM CONTROL STUDIO','version':'0.1.0','generatedAtUtc':datetime.now(timezone.utc).isoformat(),
 'releaseKind':'partial_development_release','sourceCommit':commit,'windowsArchitecture':'win-x64',
 'androidApkIncluded':False,'signedIosIpaIncluded':False,'physicalTestsPerformed':False,
 'files':[{'path':str(p.relative_to(release)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(release.rglob('*')) if p.is_file()]}
(release/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
def archive(folder,path,prefix):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for file in sorted(folder.rglob('*')):
            if file.is_file():z.write(file,Path(prefix)/file.relative_to(folder))
    with zipfile.ZipFile(path) as z:
        failure=z.testzip()
        if failure:raise RuntimeError('Corrupt ZIP member: '+failure)
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path)}
archives=[archive(release,OUTPUT/'SIM_CONTROL_STUDIO_0.1.0_RELEASE.zip','SIM_CONTROL_STUDIO_RELEASE'),
    archive(release/'Windows',OUTPUT/'SIM_CONTROL_STUDIO_0.1.0_Windows_x64.zip','SIM_CONTROL_STUDIO_Windows'),
    archive(release/'Source',OUTPUT/'SIM_CONTROL_STUDIO_0.1.0_Source.zip','SIM_CONTROL_STUDIO_Source')]
(OUTPUT/'SHA256SUMS.txt').write_text(''.join(f'{a["sha256"]}  {a["file"]}\n' for a in archives))
shutil.copy2(release/'Documentation/ALLAPOT.md',OUTPUT/'ALLAPOT.md')
shutil.copy2(release/'Documentation/STATUS.json',OUTPUT/'STATUS.json')
shutil.copy2(release/'Documentation/PROFILE_CATALOGUE.pdf',OUTPUT/'PROFILE_CATALOGUE.pdf')
print(json.dumps({'output':str(OUTPUT),'sourceCommit':commit,'archives':archives},indent=2))
