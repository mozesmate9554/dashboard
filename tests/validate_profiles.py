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
KINDS={'number','gear','bar','leds','analog','pedals','gForce','tyres','text','image','svg','button','hold','toggle','threeState','multiState','rotary','stepper','slider','indicator','icon'}
ALLOWED={'ignition','starter','lights','flash','wiper','radio','intercom','camera','pitLimiter','brakeBiasUp','brakeBiasDown','absUp','absDown','tcUp','tcDown','diffUp','diffDown','engineMapUp','engineMapDown','drs','ers','p2p','neutral','reverse','displayNext','displayPrevious','acknowledge','drink','fan','rainLight'}
FIELDS={'speed','rpm','rpmLimit','gear','throttle','brake','clutch','steering','handbrake','ignition','engineRunning','waterTemp','oilTemp','oilPressure','turbo','fuel','consumption','range','engineMap','gearboxTemp','differential','faults','tyrePressure','tyreTempInner','tyreTempMiddle','tyreTempOuter','tyreWear','brakeTemp','wheelSpeed','wheelSlip','wheelLock','absActive','absLevel','tcActive','tcLevel','brakeBias','lapCurrent','lapLast','lapBest','sectors','delta','position','lap','lapsRemaining','timeRemaining','inPit','pitLimit','flags','drs','ers','hybridEnergy','battery','gX','gY','gZ','yaw','pitch','roll','suspension','stageTime','stageSplits','stageDistance','stageState','vehicleId','stageId','navigation','damage','sessionStatus','lights','wiperLevel','radioActive','intercomActive','starterActive'}
def counts():
    assert len(vehicles)==20
    assert len({v['id'] for v in vehicles})==20
    assert len({v[k]['id'] for v in vehicles for k in ('dashboard','panel')})==40
check('20 required vehicles / 40 separately identified layouts',counts)
signatures={'dashboard':set(),'panel':set()}
for v in vehicles:
    def validate(v=v):
        assert json.loads((ROOT/'vehicle_profiles'/v['id']/'profile.json').read_text())==v
        assert v['references'] and all(ref['url'].startswith('https://') for ref in v['references'])
        assert v['fidelity'] in ('inspired','partial_reference')
        for role,key in [('dashboard','dashboard'),('panel','panel')]:
            layout=v[key];assert layout['vehicleId']==v['id'] and layout['role']==role
            assert layout['schemaVersion']==1 and layout['version']=='0.2.0' and layout['isBase']
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
    pages=v['panel']['pages'];assert [p['name'] for p in pages[:3]]==['Kormány','Középkonzol','Kombinált mobilpanel']
    assert any(e.get('action')=='starter' for e in pages[0]['elements'])
    assert any(e.get('action')=='intercom' for e in pages[1]['elements'])
check('Skoda wheel starter / touch-console intercom / three views',skoda)
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
    assert re.search(r'^version: 0\.3\.0\+\d+$',pub,re.M)
    assert '<Version>0.3.0</Version>' in (ROOT/'Directory.Build.props').read_text()
    assert json.loads((ROOT/'windows_bridge/Bridge.Windows/profiles.json').read_text())==[v['id'] for v in vehicles]
check('Cross-platform version and profile ID consistency',version_identity)
target=ROOT/'tests/results/profile-tests.json';target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps({'scope':'JSON data and native project static validation; not a Flutter runtime test','passed':sum(r['status']=='passed' for r in results),'failed':sum(r['status']=='failed' for r in results),'tests':results},ensure_ascii=False,indent=2)+'\n')
sys.exit(any(r['status']=='failed' for r in results))
