#!/usr/bin/env python3
"""Write an explicit, machine-readable report without inventing unavailable builds."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
DONE='Elkészült és automatizáltan tesztelt'
DEVICE='Elkészült, valós eszközön még tesztelendő'
PARTIAL='Részlegesen elkészült'
MISSING='Nem készült el'
def feature(identifier,name,status,paths,evidence,limitations=None):
 return dict(id=identifier,name=name,status=status,sourcePaths=paths,verification=evidence,limitations=limitations or [])
bridge=json.loads((ROOT/'tests/results/bridge-tests.json').read_text())
profiles=json.loads((ROOT/'tests/results/profile-tests.json').read_text())
syntax=json.loads((ROOT/'tests/results/dart-syntax.json').read_text())
items=[
 feature('windows_release','Önálló Windows x64 Bridge',DEVICE,['windows_bridge/Bridge.Windows'],{'crossBuild':'passed','physicalWindowsRun':'not_run','log':'tests/results/windows-build.log'},['A grafikus felület és a Windows API-k tényleges futtatása Windows-gépen még szükséges.']),
 feature('rally_adapter','Assetto Corsa Rally valódi shared-memory adapter',DEVICE,['windows_bridge/Bridge.Core/GameAdapters.cs'],{'binaryFixtures':'passed','realRallyGame':'not_run','referencesPinned':True},['Konkrét játékverzió és named mapping fizikai tesztje hiányzik.','Rally ABS/TC/fékerőelosztás/szakaszidő és további mezők nincsenek igazoltnak jelentve.','A nyers fokozat és G-tengely konvenció éles ellenőrzést igényel.']),
 feature('telemetry_contract','Egységes mezőmodell és elavulás',DONE,['windows_bridge/Bridge.Core/Protocol.cs','mobile_flutter/lib/models.dart'],{'dotnetTests':'passed','mobileRuntime':'not_run'},['A mobil parser és megjelenítő Flutter runtime tesztje nem futott.']),
 feature('multi_client','Többklienses kétirányú kapcsolat, bontás és újracsatlakozás',DONE,['windows_bridge/Bridge.Core/BridgeRuntime.cs'],{'localTlsWebSocketTwoClients':'passed','twoPhysicalMobiles':'not_run'},['A valódi Wi-Fi és két fizikai készülék nincs kipróbálva.']),
 feature('pairing_security','TLS, párosítás, hash-tárolás, visszavonás, sebességkorlát',DONE,['windows_bridge/Bridge.Core/Pairing.cs','windows_bridge/Bridge.Core/InputControl.cs'],{'serverTests':'passed','mobileKeychainKeystore':'not_run'},['A mobil biztonságos tárolója és QR-kamerája csak forrásként készült el.']),
 feature('control_engine','Billentyűk, kombinációk, hold/repeat, fókusz- és beragadásvédelem',DONE,['windows_bridge/Bridge.Core/InputControl.cs'],{'fixtureSinkAndTransport':'passed','realSendInputGameEffect':'not_run'},['A tényleges Windows SendInput és játékreakció még ellenőrizendő.','A játékfunkciók csak helyileg beállított kiosztással válnak elérhetővé.']),
 feature('windows_ui','Windows felület, tálca, QR, kiosztásimport és diagnosztika',DEVICE,['windows_bridge/Bridge.Windows/MainForm.cs'],{'compiled':'passed','guiRun':'not_run'},['A Windows grafikus teszt nem történt meg.']),
 feature('mobile_native','Natív Flutter Android/iOS kliens',PARTIAL,['mobile_flutter/lib','mobile_flutter/android','mobile_flutter/ios'],{'syntaxOnly':'passed','dartAnalyze':'not_run','flutterTest':'not_run','flutterBuild':'not_run'},['A Flutter SDK hivatalos letöltési célállomását a hálózati szabályzat tiltja.','A forrás nincs lefordított vagy eszközön igazolt mobilalkalmazásként jelentve.']),
 feature('mobile_roles','Műszerfal, kezelőpanel és külön menthető hibrid',PARTIAL,['mobile_flutter/lib/display.dart','mobile_flutter/lib/hybrid.dart'],{'sourceImplemented':True,'flutterRuntime':'not_run'}),
 feature('profiles_40','20 autó / 40 eltérő, verziózott alapelrendezés',DONE,['vehicle_profiles','mobile_flutter/assets/catalog.json'],{'jsonGeometryBindingsSvgUniqueness':'passed','flutterRender':'not_run'},['Ez az állapot az adatfájlokra és sémájukra vonatkozik, nem gyári grafikai hűségre vagy natív megjelenítési tesztre.']),
 feature('factory_fidelity','Gyári műszerfalak és kapcsolópanelek hű rekonstrukciója',PARTIAL,['vehicle_profiles/*/REFERENCES.md'],{'documentedFactoryReplicas':0,'partialReferenceProfiles':1,'inspiredProfiles':19},['A gyári pixelgeometria, betűk és kapcsolóhelyek teljes hitelesítése hiányzik.','Ferrari 499P forrásjelölt nem volt lekérhető; nincs hiteles gyári layoutként feltüntetve.']),
 feature('profile_pairing','Más készüléktől érkező profilajánlás',DONE,['windows_bridge/Bridge.Core/BridgeRuntime.cs','mobile_flutter/lib/main.dart'],{'serverProtocol':'passed','mobileAcceptUi':'not_run'},['Játékból automatikus autóváltáshoz nincs igazolt autóalias-lista.']),
 feature('auto_game_vehicle','Játékazonosítóból automatikus autóprofil-váltás',MISSING,['vehicle_profiles/*/profile.json'],{'vehicleIdRead':'implemented','verifiedAliasTable':'missing'},['A kézi kiválasztás és párosított eszközajánlás működési útja külön implementált.']),
 feature('editor','Érintéses vizuális szerkesztő, csoport, réteg, undo/redo és feltételek',PARTIAL,['mobile_flutter/lib/editor.dart'],{'sourceImplemented':True,'flutterRuntime':'not_run'},['Az érintéses mozgatás/méretezés, fájlválasztó és megosztás valós eszköztesztje hiányzik.','Két beépített betűstílus, legfeljebb 8 oldal, 250 elem és korlátozott képméret.']),
 feature('profile_io','JSON/SVG/PNG import-export és helyi mentés',PARTIAL,['mobile_flutter/lib/storage.dart','mobile_flutter/lib/models.dart','mobile_flutter/lib/editor.dart'],{'baseDataChecks':'passed','mobilePersistenceAndSharing':'not_run'}),
 feature('other_adapters','Assetto Corsa, ACC és BeamNG OutGauge adapterek',PARTIAL,['windows_bridge/Bridge.Core/GameAdapters.cs'],{'outgaugeBinaryFixture':'passed','acAccStructure':'implemented','physicalGames':'not_run'},['Nem teljeskörűen élesben tesztelt játékkompatibilitás.']),
 feature('remaining_games','A többi megnevezett játék integrációja',MISSING,['game_adapters/README.md'],{'extensionPoints':'documented','workingAdapters':'missing'}),
 feature('modes_online','Minden játékmód és online használat igazolása',MISSING,['documentation/COMPATIBILITY.json'],{'physicalSessionTests':'not_run'},['A mátrix kifejezetten nem állítja, hogy minden felsorolt munkamenet az adott játékverzióban létezik.']),
 feature('android_apk','Android release APK',MISSING,['mobile_flutter/android','tools/build-android.ps1'],{'apkArtifactExists':False,'reason':'Flutter SDK absent; official storage.googleapis.com destination denied by environment policy (HTTP 403).'}),
 feature('ios_ipa','Aláírt iOS IPA',MISSING,['mobile_flutter/ios','tools/build-ios.sh'],{'ipaArtifactExists':False,'reason':'Linux environment, no macOS/Xcode/Apple signing.'}),
 feature('localization','Magyar felület és angol nyelv',PARTIAL,['mobile_flutter/lib/main.dart'],{'hungarian':'sourceImplemented','englishMainNavigation':'sourceImplemented','completeEnglishEditor':'missing'}),
 feature('docs_diagnostics','Magyar útmutatók, napló és gépi állapotjelentés',DONE,['documentation','tests/results'],{'reportsGenerated':True,'secretValuesExcluded':True}),
]
status=dict(application='SIM CONTROL STUDIO',version='0.1.0',schemaVersion=1,
 generatedAtUtc=datetime.now(timezone.utc).isoformat(),releaseKind='partial_development_release',
 fullSpecificationAccepted=False,physicalTestsPerformed=False,productionSimulatedTelemetry=False,
 tests={'bridge':{'passed':bridge['passed'],'failed':bridge['failed']},'profiles':{'passed':profiles['passed'],'failed':profiles['failed']},
  'dartSyntax':{'passed':sum(f['status']=='passed' for f in syntax['files']),'kind':'syntax_only'},'flutterAnalyze':'not_run','flutterTests':'not_run','realGameTests':'not_run'},
 permittedStatusValues=[DONE,'Elkészült, valós eszközön tesztelt',DEVICE,PARTIAL,MISSING],features=items,
 missingPrerequisites=['Flutter/Dart SDK and Android SDK build access','macOS/Xcode and Apple signing for iOS','Windows running ACR','two physical mobiles'],
 nextAcceptanceSteps=['Build and analyze Flutter app with supplied tests','Install on two actual devices','Verify ACR memory layout and field conventions against the installed version','Map and test allowed game controls','Complete primary cockpit reference verification','Record actual session/online compatibility'])
(ROOT/'documentation/STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
games=json.loads((ROOT/'mobile_flutter/assets/catalog.json').read_text())['games']
modes=['practice','time_trial','qualifying','race','offline','online_multiplayer','private_server','league','rally_stage','online_rally','free_roam','test_drive','pit','garage','replay','spectator']
rows=[]
for game in games:
 for mode in modes:
  rows.append(dict(gameId=game['id'],game=game['name'],gameVersion=None,requestedSession=mode,
   sessionExistsInInstalledVersion='not_verified',telemetry='implemented_not_live_verified' if game['implemented'] else 'not_implemented',
   buttonBox='locally_mapped_SendInput_not_game_verified' if game['implemented'] else 'not_implemented',
   availableFields=['speed','rpm','gear','throttle','brake','steering','gX','gY','gZ'] if game['id']=='acr' else [],
   onlineConditions='Use only telemetry/input permitted by the actual game and event; not verified.',testStatus='not_run',
   knownIssues=['No physical test of this game/version/session.','Source availability does not prove every requested field.']))
(ROOT/'documentation/COMPATIBILITY.json').write_text(json.dumps({'schemaVersion':1,'note':'Requested coverage checklist. This does NOT assert that every session exists in every game.','rows':rows},ensure_ascii=False,indent=2)+'\n')
summary=['# Fejlesztési állapot 0.1.0','','A teljes specifikáció elfogadási feltétele **még nem teljesült**. Futó Rally és két fizikai mobil nem állt rendelkezésre. A Windows kiadás lefordult, APK/IPA nem készült.','',f'Automatizált ellenőrzések: {bridge["passed"]} Bridge + {profiles["passed"]} adat/projekt, {sum(f["status"]=="passed" for f in syntax["files"])} Dart fájl szintaxis. A Dart szintaxis nem Flutter analyzer vagy futtatott widgetteszt.','','| Funkció | Állapot |','|---|---|']
summary.extend(f'| {f["name"]} | {f["status"]} |' for f in items)
summary.extend(['','Részletek és a bizonyítékok határai: `STATUS.json`. A 40 elrendezésből 1 részleges referencia, 19 inspirált; nincs 20 hitelesített gyári replika készre jelentve.','','Az Android build hiányának konkrét oka: a hivatalos Flutter SDK célállomását a környezet hálózati szabályzata 403-mal tiltotta. Az iOS buildhez macOS, Xcode és aláírás hiányzott. A forrás és a natív projektek átadásra kerülnek.'])
(ROOT/'documentation/ALLAPOT.md').write_text('\n'.join(summary)+'\n')
print(f'Status report: {len(items)} features; full acceptance false.')
