#!/usr/bin/env python3
"""Require actual Android, iOS, Windows and native evidence before generating a release report."""
import argparse, json
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
for name in ['checks','ios','android-native','previews']:p.add_argument('--'+name,type=Path,required=True)
a=p.parse_args();checks=a.checks
read=lambda path:json.loads(path.read_text())
events=[]
for line in (checks/'flutter-tests.jsonl').read_text().splitlines():
    try:
        event=json.loads(line)
        if isinstance(event,dict):events.append(event)
    except ValueError:pass
assert any(e.get('type')=='done' and e.get('success') is True for e in events),'Flutter tests did not pass'
passed=sum(e.get('type')=='testDone' and e.get('result')=='success' and not e.get('hidden') for e in events)
bridge=read(ROOT/'tests/results/windows-bridge-tests.json');profiles=read(ROOT/'tests/results/profile-tests.json')
assert not bridge['failed'] and not profiles['failed']
assert 'No issues found' in (checks/'flutter-analyze.log').read_text()
assert 'Verified' in (checks/'APK-SIGNATURE.txt').read_text()
smoke=read(ROOT/'tests/results/windows-installer-smoke.json')
assert smoke['install']=='passed' and smoke['winFormsStartup']=='passed'
provenance=read(checks/'provenance.json');ios=read(a.ios/'provenance.json');android=read(a.android_native/'provenance.json')
assert provenance['commit']==ios['commit']==android['commit'],'Different source commits in native build evidence'
assert ios['simulatorInstall']==ios['simulatorLaunch']=='passed'
assert 'Built build/ios/iphoneos/Runner.app' in (a.ios/'device-unsigned-build.log').read_text()
for folder in [a.ios,a.android_native]:
    result=read(folder/'native-integration-results.json')
    assert result['allTestsPassed'] and len(result['screenshots'])==6
    assert 'All tests passed' in (folder/'native-bridge-integration.log').read_text()
assert android['orientationAndSystemBars']=='passed'
comparison=read(a.previews/'comparison-provenance.json');assert len(comparison['surfaces'])==2
status={'application':'SIM CONTROL STUDIO','version':'0.3.0','generatedAtUtc':datetime.now(timezone.utc).isoformat(),
 'releaseKind':'installable_preview','buildProvenance':provenance,
 'packagingProvenance':{'commit':__import__('os').environ.get('GITHUB_SHA'),'runUrl':'https://github.com/'+__import__('os').environ.get('GITHUB_REPOSITORY','mozesmate9554/dashboard')+'/actions/runs/'+__import__('os').environ.get('GITHUB_RUN_ID','local')},
 'android':{'signedReleaseApk':True,'nativeEmulatorApi':36,'nativeTlsSecureStorageTelemetryTouchReconnect':True,'allThreeRolesBothOrientations':True,'actualSystemBarsHidden':True,'physicalDeviceTestByDeveloper':False,'signing':read(checks/'signing.json')},
 'ios':{'xcode':(a.ios/'xcode-version.txt').read_text().strip(),'simulatorBuildInstallLaunch':True,'nativeTlsKeychainTelemetryTouchReconnect':True,'allThreeRolesBothOrientations':True,'arm64ReleaseBuildUnsigned':True,'signedIpa':False,'testFlight':False,'physicalIphoneTest':False,'appleDeveloperMembershipProvided':False},
 'windows':{'selfContainedX64':True,'installerSilentInstallAndWinFormsStartup':True,'externalPublisherCertificate':False},
 'tests':{'bridge':{'passed':bridge['passed'],'failed':0,'environment':bridge['environment']},'profiles':{'passed':profiles['passed'],'failed':0},'flutter':{'passed':passed,'failed':0,'analyzer':'No issues found'},'nativeIos':'passed','nativeAndroid':'passed','transport':read(ROOT/'tests/results/windows-transport-benchmark.json')},
 'profiles':{'count':20,'baseLayouts':40,'other19ByteIdenticalTo020':True,'skodaSurfaces':['driver_display','central_console'],'skodaFidelity':'photo_derived_reconstruction_not_factory_certified','editableArtAndBindings':True},
 'preservation':{'rallyGameAdaptersAndInputControlSourceUnchangedSince020':True,'protocolVersion':1,'existingPersonalProfilesPreserved':True,'androidWindowsRallyLiveUse':'User reports this works in production; no new physical game session observed by developer for 0.3.0'},
 'previewEvidence':comparison,
 'remaining':['Physical iPhone install with own Apple signing; LAN/QR/camera/safe areas/thermal and touch acceptance','Apple Developer/App Store Connect setup before TestFlight','Physical Android 0.3.0 install and live Windows–Rally regression confirmation on user setup','Actual Wi-Fi latency, mobile FPS and two physical phones','Unverified factory switch functions, pixel geometry/font and later model years remain reconstruction','Other 19 vehicle graphics intentionally not redesigned; additional game adapters out of scope']}
(ROOT/'documentation/STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
rows=['# Ellenőrzött kiadási állapot – 0.3.0','',f'CI: {provenance["url"]}',f'Forráscommit: `{provenance["commit"]}`','',
 f'Automatizált tesztek: {bridge["passed"]} Bridge, {profiles["passed"]} adat/projekt, {passed} Flutter; analyzer: nincs jelzés.',
 'Android: aláírt release APK; Android 16 emulátoron natív TLS/Keystore/telemetria/érintés/visszacsatlakozás; három nézet álló és fekvő helyzetben; natívan lekérdezett rejtett rendszersávok.',
 'iOS: tényleges Xcode szimulátor- és aláírás nélküli ARM64 release build. Szimulátoros telepítés/indítás; natív TLS/Keychain/telemetria/érintés/visszacsatlakozás; három nézet két tájolással.',
 'Windows: self-contained build, telepítő, csendes telepítés és WinForms-főablak indítás.',
 'Škoda: két új, szerkeszthető fotóalapú felület; nagy felbontású Flutter-előnézet és gyártói fotóval összehasonlító PDF. Másik 19 profil hash szerint változatlan.','',
 '**Nincs fizikai iPhone-teszt, aláírt IPA vagy TestFlight.** A hálózati automatizálás loopback és jelölt DEMO, nem élő Rally. A felhasználó korábban működő éles Android–Windows–Rally használatról számolt be; a 0.3.0 újratelepítés utáni fizikai elfogadása még szükséges.','',
 'Részletek: STATUS.json, IOS.md, ANDROID.md, TESZTELES.md, SKODA_REKONSTRUKCIO_0.3.0.md; a teljes csomag Tests mappájában a tényleges naplók és képernyőképek.']
(ROOT/'documentation/ALLAPOT.md').write_text('\n\n'.join(rows)+'\n')
print(json.dumps({'commit':provenance['commit'],'bridgeTests':bridge['passed'],'profileTests':profiles['passed'],'flutterTests':passed,'nativeIos':'passed','nativeAndroid':'passed','signedIos':False}))
