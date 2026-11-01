#!/usr/bin/env python3
"""Generate 0.2.0 evidence matrix from real CI event logs; keeps the pre-change audit immutable."""
import argparse, json, os
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--checks',type=Path,required=True);a=p.parse_args()
checks=a.checks
lines=(checks/'flutter-tests.jsonl').read_text().splitlines()
events=[]
for line in lines:
 try: events.append(json.loads(line))
 except (ValueError,TypeError): pass
if not any(e.get('type')=='done' and e.get('success') is True for e in events): raise SystemExit('Flutter CI has not passed.')
passed=sum(e.get('type')=='testDone' and e.get('result')=='success' and not e.get('hidden') for e in events)
bridge_path=ROOT/'tests/results/windows-bridge-tests.json'
if not bridge_path.exists():bridge_path=ROOT/'tests/results/bridge-tests.json'
bridge=json.loads(bridge_path.read_text());profiles=json.loads((ROOT/'tests/results/profile-tests.json').read_text())
if bridge['failed'] or profiles['failed']:raise SystemExit('Failing Bridge/profile checks.')
provenance=json.loads((checks/'provenance.json').read_text())
analyzer=(checks/'flutter-analyze.log').read_text()
if 'No issues found' not in analyzer:raise SystemExit('Analyzer is not clean.')
if not (checks/'APK-SIGNATURE.txt').exists() or 'Verified' not in (checks/'APK-SIGNATURE.txt').read_text():raise SystemExit('Verified APK signature report required.')
smoke=json.loads((ROOT/'tests/results/windows-installer-smoke.json').read_text())
if smoke.get('install')!='passed' or smoke.get('winFormsStartup')!='passed':raise SystemExit('Windows installer/startup not verified.')
audit=json.loads((ROOT/'documentation/AUDIT_0.1.0_TO_0.2.0.json').read_text())
features=[]
D='Kész és tesztelt';U='Kész, de még nem tesztelt';P='Részlegesen működik';E='Külső környezet miatt nem ellenőrizhető'
tested={*range(1,15),21,22,23,25,26,29,30,31,33,35,36,40,41,43,45,46,47,49,50,51,52,53,56}
for item in audit['features']:
 row=dict(item);n=int(row['id'][1:]);row['baselineStatus']=row['status']
 if n in tested:
  row['status']=D
  row['evidence']='Bridge regresszió és valódi loopback TLS; Flutter analyzer és futtatott tesztek; CI: '+provenance['url']
  row['remaining']='Automatizált ellenőrzés a dokumentált környezetben. Fizikai játék-, mobil- és Wi-Fi-teszt ebből nem következik.'
 if n==24:
  row.update(status=D,evidence='NSIS telepítő; Windows CI csendes telepítés és WinForms-ablak indítás; tests/results/windows-installer-smoke.json',remaining='Interaktív tálca-, QR- és játékvezérlési ellenőrzés még szükséges.')
 if n==18:
  row.update(status=P,evidence='Windows CI-ben telepítés és főablak-indítás automatizált smoke tesztje.',remaining='Teljes interaktív WinForms/tálca használat nincs manuálisan ellenőrizve.')
 if n in {27,28,37,38,39,42,44,48}:
  row.update(status=P,evidence='A forrás lefordult; modell-, mentési és renderelési tesztek futottak.',remaining='A teljes érintéses munkafolyamat, rendszermegosztás, kamera és Keychain/Keystore integráció fizikai tesztje hiányzik. A választók relatív parancsot küldenek; a kért pozíció nem igazolt játékállapot.')
 if n==32:
  row.update(evidence='20 megőrzött autópár; 1 részleges referencia, 19 inspirált. PROFILE_COMPLETENESS_0.2.0.md.',remaining='Nincs hitelesített gyári pixelgeometria vagy teljes kapcsolókiosztás.')
 if n in {34,57,58}:row['remaining']='A konkrét játékban elérhető funkciók és munkamenetek éles ellenőrzése hiányzik; további adapterek nem készültek.'
 features.append(row)
status={'application':'SIM CONTROL STUDIO','version':'0.2.0','generatedAtUtc':datetime.now(timezone.utc).isoformat(),
 'releaseKind':'installable_preview','fullSpecificationAccepted':False,'physicalTestsPerformed':False,
 'buildProvenance':provenance,'demoAvailable':True,'syntheticTelemetryIsExplicitlyLabeled':True,
 'tests':{'bridge':{'passed':bridge['passed'],'failed':bridge['failed'],'environment':bridge['environment']},'profiles':{'passed':profiles['passed'],'failed':profiles['failed']},'flutter':{'passed':passed,'failed':0,'analyzer':'No issues found','scope':'Flutter VM/widget; software rendering, not physical device'},'realGameTests':'not_run'},
 'features':features,'remaining':['Actual ACR version/memory/gear conventions and game input effect','Two physical mobiles over Wi-Fi and measured mobile FPS','Physical Android install, camera and secure storage','Signed iOS build with macOS/Xcode/Apple credentials','Factory cockpit references','Additional game/mode integrations','Full English translation']}
(ROOT/'documentation/STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
rows=['# Funkciómátrix – SIM CONTROL STUDIO 0.2.0','','Az eredeti audit: AUDIT_0.1.0_TO_0.2.0.md. Az alábbi állapotok az automatizált bizonyíték megadott körére érvényesek.','',f'CI: {provenance["url"]}',f'Forrás: `{provenance["commit"]}`',f'Tesztek: {bridge["passed"]} Bridge, {profiles["passed"]} adat/projekt, {passed} Flutter; Dart analyzer: nincs jelzés.','','| ID | Funkció | Állapot | Bizonyíték és korlát |','|---|---|---|---|']
rows += [f'| {r["id"]} | {r["feature"]} | {r["status"]} | {r["evidence"]} {r["remaining"]} |' for r in features]
(ROOT/'documentation/FUNKCIOMATRIX_0.2.0.md').write_text('\n'.join(rows)+'\n')
(ROOT/'documentation/ALLAPOT.md').write_text('\n'.join(rows[:9])+ '\n\nTelepíthető Android APK, Windows EXE és NSIS telepítő. A fizikai játék-/telefonos elfogadás még nem teljesült. Részletek: FUNKCIOMATRIX_0.2.0.md, STATUS.json, ISMERT_HIBAK.md.\n')
vehicles=json.loads((ROOT/'mobile_flutter/assets/catalog.json').read_text())['vehicles']
rows=['# Profilonkénti teljesség – 0.2.0','','Az eredeti 20 autó és mind a 40 alapelrendezés megmaradt. Mindegyik műszerfal 2, kezelőpanel 4 oldalas; ezek mellett 20 szerkeszthető hibrid állítható össze.','','Renderelési bizonyíték: mindegyik oldal 360×800, 900×420 és 1366×1024 méreten, hiányzó és explicit DEMO-adatokkal. A vezérlők műveletekhez kötöttek; valódi PC-billentyűkiosztást a felhasználó állít be az adott játékban és profilban.','','| Autó | Műszerfal / panel elemek | Panelműveletek | Referencia és készültség |','|---|---|---|---|']
for v in vehicles:
 count=lambda k:sum(len(p['elements']) for p in v[k]['pages'])
 actions=sorted({e['action'] for p in v['panel']['pages'] for e in p['elements'] if 'action' in e})
 rows.append(f'| {v["name"]} | {count("dashboard")} / {count("panel")} | {", ".join(actions)} | {v["fidelityLabel"]}; működő adat-/vezérlőkötések, gyári hűség és játékhatás nincs hitelesítve |')
(ROOT/'documentation/PROFILE_COMPLETENESS_0.2.0.md').write_text('\n'.join(rows)+'\n')
print(f'Recorded {len(features)} evidence rows, {passed} Flutter tests and {len(vehicles)} vehicle pairs.')
