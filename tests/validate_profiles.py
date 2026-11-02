#!/usr/bin/env python3
"""Validate the delivered data, all native configuration XML and Xcode references.
This does not substitute for a Flutter build or a physical device test.
"""
from pathlib import Path
import base64, hashlib, json, re, sys, time, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
results=[]
def check(name, action):
    started=time.monotonic()
    try:
        action();results.append({'name':name,'status':'passed','durationMs':round((time.monotonic()-started)*1000,2)})
        print('PASS',name)
    except Exception as error:
        results.append({'name':name,'status':'failed','error':str(error)});print('FAIL',name,str(error))
catalog=json.loads((ROOT/'mobile_flutter/assets/catalog.json').read_text())
vehicles=catalog['vehicles']
KINDS={'number','gear','bar','leds','analog','pedals','gForce','tyres','text','image','svg','button','hold','toggle','threeState','multiState','rotary','stepper','slider','indicator','icon','rocker','pushButton','guarded','rotarySwitch','cycleButton'}
ALLOWED={'ignition','starter','lights','flash','wiper','radio','intercom','camera','pitLimiter','brakeBiasUp','brakeBiasDown','absUp','absDown','tcUp','tcDown','diffUp','diffDown','engineMapUp','engineMapDown','drs','ers','p2p','neutral','reverse','displayNext','displayPrevious','acknowledge','drink','fan','rainLight','electricalMaster','auxMode','hazards','fogLights','demist','callAccept','callEnd','fireExtinguisher','intercomVolumeUp','intercomVolumeDown','radioVolumeUp','radioVolumeDown','highBeam','indicatorLeft','indicatorRight','handbrake','respawn'}
FIELDS={'speed','rpm','rpmLimit','gear','throttle','brake','clutch','steering','handbrake','ignition','engineRunning','waterTemp','oilTemp','oilPressure','turbo','fuel','consumption','range','engineMap','gearboxTemp','differential','faults','tyrePressure','tyreTempInner','tyreTempMiddle','tyreTempOuter','tyreWear','brakeTemp','wheelSpeed','wheelSlip','wheelLock','absActive','absLevel','tcActive','tcLevel','brakeBias','lapCurrent','lapLast','lapBest','sectors','delta','position','lap','lapsRemaining','timeRemaining','inPit','pitLimit','flags','drs','ers','hybridEnergy','battery','gX','gY','gZ','yaw','pitch','roll','suspension','stageTime','stageSplits','stageDistance','stageState','vehicleId','stageId','navigation','damage','sessionStatus','lights','wiperLevel','radioActive','intercomActive','starterActive','radioVolume','intercomVolume','sessionClock','driveMode','launchRpmLimit'}
SIX={'skoda-fabia-rs-rally2','peugeot-208-rally4','hyundai-i20-n-rally2','vw-polo-gti-r5','peugeot-206-wrc','subaru-impreza-555-gra'}
def counts():
    assert [v['id'] for v in vehicles]==['skoda-fabia-rs-rally2','peugeot-208-rally4','hyundai-i20-n-rally2','vw-polo-gti-r5','peugeot-206-wrc','subaru-impreza-555-gra']
    assert len({v['id'] for v in vehicles})==len(vehicles)
    ids=[l['id'] for v in vehicles for l in [v['dashboard'],v['panel'],*v.get('variants',[])]]
    assert len(ids)==len(set(ids))
check('Exactly the six requested ACR cars; every factory layout separately identified',counts)
signatures={'dashboard':set(),'panel':set()}
for v in vehicles:
    def validate(v=v):
        assert json.loads((ROOT/'vehicle_profiles'/v['id']/'profile.json').read_text())==v
        assert v['references'] and all(ref['url'].startswith('https://') for ref in v['references'])
        assert v['fidelity'] in ('inspired','partial_reference','reference_research')
        for role,key,layout in [('dashboard','dashboard',v['dashboard']),('panel','panel',v['panel'])]+[(l['role'],'variant:'+l['role'],l) for l in v.get('variants',[])]:
            assert layout['vehicleId']==v['id'] and layout['role']==role
            assert layout['schemaVersion']==1 and layout['version'] in ('0.2.0','0.3.0','0.4.0') and layout['isBase']
            signatures.setdefault(key,set())
            ids=set();signature=[]
            assert 1<=len(layout['pages'])<=8
            for p in layout['pages']:
                for e in p['elements']:
                    assert e['id'] not in ids;ids.add(e['id'])
                    assert e['kind'] in KINDS
                    assert 0<=e['x'] and 0<=e['y'] and e['w']>=12 and e['h']>=12
                    assert e['x']+e['w']<=layout['width'] and e['y']+e['h']<=layout['height'],e
                    assert e.get('field','') in FIELDS|{''},e
                    assert all(e[k] in ALLOWED for k in ('action','minusAction') if k in e)
                    if e['kind'] not in ('text','svg','image'):
                        signature.append(tuple(e.get(k) for k in ('kind','field','x','y','w','h','action','minusAction')))
            digest=hashlib.sha256(json.dumps(signature).encode()).hexdigest()
            assert digest not in signatures[key], 'Geometrically duplicated base layout'
            signatures[key].add(digest)
            assert len(ids)<=250
            for asset in layout.get('assets',{}).values():
                raw=base64.b64decode(asset['base64'],validate=True)
                if asset['type']=='svg':ET.fromstring(raw)
            assert all(field in FIELDS for field in layout['supportedFields'])
        if v['category'] in ('RALLY1','RALLY2'):
            controls={e.get('action') for p in v['panel']['pages'] for e in p['elements']}
            assert not controls.intersection({'absUp','tcUp','drs'}), 'Non-car-specific controls attributed to a rally car'
    check(v['name']+' pair, bindings, bounds, SVG and provenance',validate)
def skoda():
    v=next(v for v in vehicles if v['id']=='skoda-fabia-rs-rally2')
    assert v['reconstructionScope']==['driver_display','central_console']
    assert len(v['dashboard']['pages'])==3
    legacy=v['variants'][0]
    assert legacy['id']=='skoda-fabia-rs-rally2-panel' and len(legacy['pages'])==1
    controls=[e for e in legacy['pages'][0]['elements'] if e.get('action')]
    assert len(controls)==16 and all(e.get('artwork') and e.get('assetId') for e in controls)
    assert all('wheel' not in key for key in legacy['assets'])
    assert all(e.get('action')!='starter' for e in controls)
    before=json.loads((ROOT/'documentation/history/0.2.0/skoda-profile.json').read_text())
    old={e['field'] for p in before['dashboard']['pages'] for e in p['elements'] if e.get('field')}
    assert old<=set(v['dashboard']['supportedFields']),old-set(v['dashboard']['supportedFields'])
check('Skoda: 0.3.0 photo console preserved as a variant, dashboard telemetry preserved',skoda)
def premium_boxes():
    for v in vehicles:
        if v['id'] not in SIX: continue
        panel=v['panel']; assert panel['version']=='0.4.0' and panel.get('adaptive')=='preserve',v['id']
        controls=[e for e in panel['pages'][0]['elements'] if e['kind'] in ('rocker','pushButton','guarded','rotarySwitch','cycleButton')]
        assert len(controls)>=10,v['id']
        actions={e['action'] for e in controls}
        assert {'ignition','starter','lights'}<=actions,(v['id'],actions)
        assert all(e.get('minusAction') for e in controls if e['kind']=='rotarySwitch')
        assert next(e for e in controls if e['action']=='starter').get('hold') is True
        assert next(e for e in controls if e['action']=='lights')['kind']=='cycleButton','Rally lights are a game cycle, not an on/off toggle'
        assert v['gameVehicleAliases'],v['id']
check('ACR cars: separate mechanical button boxes, hold starter, cycle lights, aliases',premium_boxes)
def sounds():
    import wave
    names=['metal_toggle_on','metal_toggle_off','plastic_button','latching_switch','rotary_detent','safety_cover','starter_button']
    for n in names:
        with wave.open(str(ROOT/'mobile_flutter/assets/sounds'/(n+'.wav'))) as w:
            assert w.getframerate()==44100 and w.getnchannels()==1 and w.getnframes()/44100<.2,n
check('Seven short, preloadable switch sounds',sounds)
def native_xml():
    paths=list((ROOT/'mobile_flutter/android').rglob('*.xml'))+list((ROOT/'mobile_flutter/ios').rglob('*.plist'))+list((ROOT/'mobile_flutter/ios').rglob('*.storyboard'))+list((ROOT/'mobile_flutter/ios').rglob('*.entitlements'))+list((ROOT/'mobile_flutter/ios').rglob('*.xcscheme'))+list((ROOT/'mobile_flutter/ios').rglob('*.xcworkspacedata'))
    for p in paths:ET.parse(p)
check('Android manifests / iOS plist, entitlement, storyboard and workspace XML',native_xml)
def xcode():
    text=(ROOT/'mobile_flutter/ios/Runner.xcodeproj/project.pbxproj').read_text()
    definitions=re.findall(r'^\s*([0-9A-F]{24}) = \{',text,re.M)
    assert len(definitions)==len(set(definitions))
    references=set(re.findall(r'\b[0-9A-F]{24}\b',text))
    assert references<=set(definitions),references-set(definitions)
    assert 'TARGETED_DEVICE_FAMILY = "1,2"' in text and 'IPHONEOS_DEPLOYMENT_TARGET = 15.5' in text
check('Xcode project object references and iPhone/iPad deployment settings',xcode)
def version_identity():
    pub=(ROOT/'mobile_flutter/pubspec.yaml').read_text()
    assert re.search(r'^version: 0\.4\.0\+\d+$',pub,re.M)
    assert '<Version>0.4.0</Version>' in (ROOT/'Directory.Build.props').read_text()
    assert json.loads((ROOT/'windows_bridge/Bridge.Windows/profiles.json').read_text())==[v['id'] for v in vehicles]
check('Cross-platform version and profile ID consistency',version_identity)
target=ROOT/'tests/results/profile-tests.json';target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps({'scope':'JSON data and native project static validation; not a Flutter runtime test','passed':sum(r['status']=='passed' for r in results),'failed':sum(r['status']=='failed' for r in results),'tests':results},ensure_ascii=False,indent=2)+'\n')
sys.exit(any(r['status']=='failed' for r in results))
