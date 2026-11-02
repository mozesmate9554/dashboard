#!/usr/bin/env python3
"""Photo-derived driver display and central console; leaves the other 19 cars byte-identical."""
import base64, copy, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAR='skoda-fabia-rs-rally2'
SVG_HEAD='<svg xmlns="http://www.w3.org/2000/svg" '
ASSETS={}
def asset(name,w,h,body):
    text=SVG_HEAD+f'viewBox="0 0 {w} {h}">'+body+'</svg>'
    ASSETS[name]={'type':'svg','base64':base64.b64encode(text.encode()).decode(),'name':name}
    return name

def caption(identifier,text,x,y,w,h,size=32,color='#c7cdd0',group=None):
    return dict(id=identifier,kind='text',field='',label=text,x=x,y=y,w=w,h=h,font='factory',fontWeight=600,fontSize=size,letterSpacing=0,
                foreground=color,color=color,border=False,z=4,**({'group':group} if group else {}))
def value(identifier,field,label,x,y,w,h,color='#f7df58',size=180,group=None,style='factoryReadout'):
    return dict(id=identifier,kind='gear' if field=='gear' else 'number',field=field,label=label,x=x,y=y,w=w,h=h,font='factory',fontWeight=600,
                fontSize=size,foreground=color,color=color,border=False,z=5,style=style,**({'group':group} if group else {}))
def graphic(identifier,asset_id,x,y,w,h,z=0,locked=False):
    return dict(id=identifier,kind='svg',field='',label=identifier,x=x,y=y,w=w,h=h,assetId=asset_id,border=False,z=z,locked=locked)

def dashboard():
    face=asset('skoda-driver-display-bezel',1280,800,'''
<defs><linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#464a4c"/><stop offset=".12" stop-color="#1c1f21"/><stop offset=".5" stop-color="#393c3d"/><stop offset="1" stop-color="#161819"/></linearGradient><linearGradient id="glass" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#14191c"/><stop offset=".45" stop-color="#060809"/><stop offset="1" stop-color="#010202"/></linearGradient></defs>
<rect x="14" y="14" width="1252" height="772" rx="30" fill="#090b0c"/>
<rect x="24" y="24" width="1232" height="752" rx="24" fill="url(#metal)" stroke="#555b5e" stroke-width="2"/>
<rect x="52" y="51" width="1176" height="698" rx="9" fill="#030506" stroke="#090a0b" stroke-width="14"/>
<rect x="70" y="69" width="1140" height="660" rx="3" fill="url(#glass)"/>
<path d="M78 77H1201V250C840 125 450 136 78 230Z" fill="#ffffff" opacity=".018"/>
<path d="M430 237V688 M813 237V688" stroke="#343b3e" stroke-width="2"/>
<path d="M93 468H410 M455 500H789" stroke="#283034" stroke-width="2"/>
<g fill="#0c0e10" stroke="#62686b" stroke-width="2"><circle cx="39" cy="400" r="9"/><circle cx="1241" cy="400" r="9"/></g>
<g stroke="#7c8487" stroke-width="2"><path d="M34 395l10 10M34 405l10-10M1236 395l10 10M1236 405l10-10"/></g>
''')
    coolant=asset('skoda-coolant-symbol',100,90,'<g fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round"><path d="M48 12v36a13 13 0 1 1-12 0V12a6 6 0 0 1 12 0Z"/><path d="M55 20h13M55 33h10M8 72q10-10 20 0t20 0t20 0t20 0M8 85q10-10 20 0t20 0t20 0t20 0"/></g>')
    elements=[graphic('skoda-driver-bezel',face,0,0,1280,800,0,True)]
    elements += [dict(id='skoda-driver-shift-matrix',kind='leds',field='rpm',label='RPM',x=515,y=100,w=240,h=116,count=15,rows=3,shape='circle',max=7500,border=False,z=3,
                      referenceNote='A fotón LED-mátrix látható; a 15-ös szám és a kapcsolási küszöbök rekonstrukciók.')]
    elements += [dict(id='skoda-driver-coolant',kind='indicator',field='waterTemp',label='Hűtőfolyadék',x=997,y=117,w=92,h=90,assetId=coolant,style='factorySymbol',activeBelow=60,color='#55b8ff',border=False,z=4)]
    for name,text,x,y,w,h,size in [
      ('speed','Speed',104,245,280,50,42),('gear','Gear',850,245,290,50,42),('map','Map',475,245,270,48,40),
      ('limit','LC Limiter',96,472,300,50,39),('time','Time',475,587,280,45,38)]:
        elements.append(caption('skoda-driver-label-'+name,text,x,y,w,h,size,color='#f7df58' if name=='speed' else '#c7cdd0',group='driver-'+name))
    elements += [value('skoda-driver-speed','speed','Speed',112,298,284,165,group='driver-speed'),
                 value('skoda-driver-gear','gear','Gear',846,300,306,365,color='#f7f8f8',size=380,group='driver-gear'),
                 value('skoda-driver-map','engineMap','Map',465,300,316,70,size=42,style='factoryMap',group='driver-map'),
                 value('skoda-driver-mode','driveMode','Mode',465,393,316,104,color='#eef0ef',size=90),
                 value('skoda-driver-limiter','launchRpmLimit','LC Limiter',121,527,265,92,color='#eef0ef',size=110,group='driver-limit'),
                 value('skoda-driver-clock','sessionClock','Clock',106,630,290,72,size=86),
                 value('skoda-driver-stage','stageTime','Time',483,635,270,67,size=86,group='driver-time')]
    elements[-1]['format']='minutesSeconds'
    main={'id':CAR+'-driver-display','name':'Vezetői kijelző · fotóalapú rekonstrukció','elements':elements,'referenceScope':'Driver display above the steering column; not the central service monitor.'}
    engine=[]
    for i,(field,label,unit) in enumerate([('rpm','RPM','rpm'),('speed','SPEED','km/h'),('gear','GEAR',''),('waterTemp','WATER','°C'),('oilPressure','OIL','bar'),('fuel','FUEL','L'),('stageTime','STAGE','ms'),('stageDistance','DISTANCE','m')]):
        x=60+(i%4)*295;y=165+(i//4)*280
        e=value('skoda-app-engine-'+field,field,label,x,y,275,230,color='#f2f5f4',size=90,style='adaptiveReadout');e['unit']=unit;e['background']='#151b1e';e['border']=True;engine.append(e)
    engine.append(caption('skoda-app-engine-title','ALKALMAZÁS · KIEGÉSZÍTŐ TELEMETRIA',50,55,1180,60,34,'#78cf9d'))
    chassis=[dict(id='skoda-app-pressure',kind='tyres',field='tyrePressure',label='TYRE PRESSURE',x=50,y=140,w=380,h=420,color='#8ecbad',border=True),
             dict(id='skoda-app-tyre-temperature',kind='tyres',field='tyreTempMiddle',label='TYRE TEMPERATURE',x=450,y=140,w=380,h=420,color='#8ecbad',border=True),
             dict(id='skoda-app-gforce',kind='gForce',field='gX',label='G',x=850,y=140,w=360,h=420,color='#8ecbad',border=True),
             dict(id='skoda-app-pedals',kind='pedals',field='throttle',label='PEDALS',x=50,y=610,w=1160,h=130,color='#8ecbad',border=True),
             caption('skoda-app-chassis-title','ALKALMAZÁS · FUTÓMŰ ÉS PEDÁLOK',50,55,1180,60,34,'#78cf9d')]
    return dict(schemaVersion=1,id=CAR+'-dash',name='Škoda Fabia RS Rally2 · Vezetői kijelző',vehicleId=CAR,role='dashboard',isBase=True,version='0.3.0',revision=2,width=1280,height=800,background='#07090a',
                pages=[main,{'id':CAR+'-app-engine','name':'Alkalmazás · motoradatok','elements':engine},{'id':CAR+'-app-chassis','name':'Alkalmazás · futómű','elements':chassis}],
                assets={},supportedFields=[])

ICONS={
 'bolt':'<path d="M61 5 21 55h29L39 92l43-53H54Z"/>',
 'power':'<path d="M50 9v37M28 22a34 34 0 1 0 44 0" fill="none" stroke="white" stroke-width="9" stroke-linecap="round"/>',
 'hazard':'<path d="M50 10 91 82H9Z M50 31 72 70H28Z" fill="none" stroke="white" stroke-width="6"/>',
 'fog':'<g fill="none" stroke="white" stroke-width="6"><path d="M53 18c-29 4-30 59 0 63V18ZM62 28h31M62 49h31M62 70h31M72 15q-12 14 0 27t0 27t0 23"/></g>',
 'windscreen':'<g fill="none" stroke="white" stroke-width="5"><path d="M8 29Q50 5 92 29L80 78Q50 64 20 78Z"/><path d="m21 36 10 18 10-18 10 18 10-18 10 18 10-18"/></g>',
 'lamp':'<g fill="none" stroke="white" stroke-width="5" stroke-linecap="round"><path d="M30 32Q50 14 70 32v17H30Z M50 63v25M29 59 16 79M71 59l13 20M14 47H3M86 47h11"/></g>',
 'thermal':'<g fill="none" stroke="white" stroke-width="5"><path d="M14 18h72v46H14ZM29 80V66M50 80V66M71 80V66M24 30h52M24 43h52"/></g>',
 'call':'<path d="M26 13 10 23c-2 26 35 64 65 64l14-19-22-14-12 11C40 57 34 50 29 35l11-9Z"/>',
 'endCall':'<path d="m10 62 1-22c22-21 56-20 78 1v21H65V48c-12-4-19-4-31 0v14Z"/>',
 'speaker':'<path d="M8 38h17l23-21v66L25 62H8Z"/><g fill="none" stroke="white" stroke-width="5"><path d="M58 32q19 18 0 36M67 19q32 31 0 62"/></g>',
 'all':'<g fill="none" stroke="white" stroke-width="5"><path d="m12 22 69-13 7 31-69 13ZM20 25l12 16M43 21l12 16M67 17l12 16M19 53v24h69V39"/></g><text x="52" y="96" font-family="OemCondensed" font-size="24" text-anchor="middle" fill="white">ALL</text>',
}

def round_button(name,color,icon):
    return asset(name,220,255,f'''
<defs><radialGradient id="cap" cx=".35" cy=".25" r=".8"><stop stop-color="#ffffff" stop-opacity=".8"/><stop offset=".25" stop-color="{color}"/><stop offset="1" stop-color="{color}" stop-opacity=".6"/></radialGradient><linearGradient id="rim" x2="0" y2="1"><stop stop-color="#858b8e"/><stop offset=".4" stop-color="#15191c"/><stop offset="1" stop-color="#020304"/></linearGradient></defs>
<path d="M48 10h124l17 20v92H31V30Z" fill="#30363a" stroke="#b1e0ff" stroke-width="5"/>
<g transform="translate(69 18) scale(.82)" fill="white">{ICONS[icon]}</g>
<ellipse cx="114" cy="177" rx="87" ry="74" fill="#000" opacity=".5"/>
<circle cx="110" cy="163" r="88" fill="url(#rim)" stroke="#050708" stroke-width="6"/>
<circle cx="110" cy="160" r="72" fill="url(#cap)" stroke="#b2b8ba" stroke-width="2"/>
<path d="M57 127Q110 82 163 127" fill="none" stroke="white" stroke-width="5" opacity=".22"/>
''')

def touch_key(name,icon=None,text=None,color='white'):
    symbol=ICONS.get(icon,'') if icon else ''
    return asset(name,210,150,f'''<defs><linearGradient id="key" x2="0" y2="1"><stop stop-color="#6d7b94"/><stop offset="1" stop-color="#47546c"/></linearGradient></defs>
<rect x="5" y="7" width="200" height="139" rx="30" fill="#070a0d"/><rect x="11" y="6" width="188" height="127" rx="27" fill="url(#key)" stroke="#232b35" stroke-width="3"/>
'''+(f'<g transform="translate(60 23) scale(.92)" fill="{color}">{symbol}</g>' if symbol else '')+(f'<text x="105" y="56" text-anchor="middle" font-family="OemCondensed" font-size="34" fill="white">{text.split()[0]}</text><text x="105" y="97" text-anchor="middle" font-family="OemCondensed" font-size="34" fill="white">{text.split()[-1]}</text>' if text else ''))

def volume(name,flip=False):
    return asset(name,190,650,'''<defs><linearGradient id="key" x2="0" y2="1"><stop stop-color="#6e7f9e"/><stop offset=".6" stop-color="#536582"/><stop offset="1" stop-color="#46536a"/></linearGradient></defs>
<rect x="5" y="4" width="180" height="642" rx="32" fill="#080c10"/><rect x="12" y="9" width="166" height="623" rx="28" fill="url(#key)" stroke="#1f2935" stroke-width="3"/>
<path d="M73 74h44M95 52v44M73 563h44" stroke="white" stroke-width="10" stroke-linecap="square"/>
<path d="M88 465 127 213 88 209Z" fill="#eefaff"/>
<g transform="translate(30 340) scale(.7)" fill="white">'''+ICONS['speaker']+'</g>')

def console():
    face=asset('skoda-console-matte-body',1100,1450,'''
<defs><linearGradient id="body" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#3e4245"/><stop offset=".5" stop-color="#272c2e"/><stop offset="1" stop-color="#161b1e"/></linearGradient><pattern id="grain" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".8" fill="#ffffff" opacity=".1"/><circle cx="9" cy="7" r="1.1" fill="#000000" opacity=".25"/></pattern></defs>
<path d="M92 18H985l63 66v1285l-55 58H67l-42-58V93Z" fill="#080c0e"/>
<path d="M95 25H976l60 65v1260l-53 58H77l-40-50V96Z" fill="url(#body)" stroke="#575d61" stroke-width="3"/>
<path d="M95 25H976l60 65v1260l-53 58H77l-40-50V96Z" fill="url(#grain)"/>
<path d="M91 34H970l54 61M45 100v1245l38 49" fill="none" stroke="#899094" stroke-width="3" opacity=".45"/>
<rect x="251" y="364" width="562" height="883" rx="39" fill="#131b22" stroke="#0b0e11" stroke-width="6"/>
<g fill="#080b0e" stroke="#60686c" stroke-width="3"><circle cx="74" cy="103" r="10"/><circle cx="1002" cy="104" r="10"/><circle cx="75" cy="1330" r="10"/><circle cx="999" cy="1330" r="10"/></g>
<g stroke="#81898e" stroke-width="2"><path d="M68 97l12 12M68 109l12-12M996 98l12 12M996 110l12-12M69 1324l12 12M69 1336l12-12M993 1324l12 12M993 1336l12-12"/></g>
''')
    knob=asset('skoda-console-audio-knob',180,210,'''<defs><linearGradient id="knob" x2="1" y2="1"><stop stop-color="#555a60"/><stop offset=".45" stop-color="#242b30"/><stop offset="1" stop-color="#080c0f"/></linearGradient></defs><ellipse cx="92" cy="159" rx="78" ry="36" fill="#070b0e"/><path d="m47 37 22-19h48l23 20 13 102-35 29H67l-34-27Z" fill="url(#knob)" stroke="#11171c" stroke-width="4"/><path d="M91 26v91" stroke="#919b9e" stroke-width="4"/>''')
    toggle=asset('skoda-console-toggle',160,220,'''<defs><linearGradient id="lever" x2="1" y2="0"><stop stop-color="#080b0d"/><stop offset=".5" stop-color="#525e65"/><stop offset="1" stop-color="#11181d"/></linearGradient></defs><ellipse cx="81" cy="165" rx="59" ry="35" fill="#080c10" stroke="#58646a" stroke-width="3"/><path d="M63 161 52 48q0-30 28-30t28 30l-11 113Z" fill="url(#lever)" stroke="#05080b" stroke-width="5"/>''')
    fire=asset('skoda-console-fire-guard',240,400,'''<defs><linearGradient id="red" x2="1" y2="1"><stop stop-color="#ff5b46"/><stop offset=".5" stop-color="#c91f19"/><stop offset="1" stop-color="#720e0b"/></linearGradient></defs><rect x="10" y="14" width="220" height="367" rx="38" fill="#070a0b"/><path d="M22 51 59 14h121l39 39v287l-39 35H57l-35-35Z" fill="url(#red)" stroke="#520909" stroke-width="5"/><rect x="48" y="79" width="144" height="218" rx="20" fill="#e8d69a" stroke="#f2e5b6" stroke-width="3"/><path d="M115 105q-5 32 15 43-1-28 19-41 10 29-4 48 39 42 5 67-12 10-39 7-52-4-38-46 3-12 19-32-2 29 14 31-5-37 9-77Z" fill="#212a30"/><text x="120" y="271" text-anchor="middle" font-family="OemCondensed" font-size="39" fill="#212a30">FIRE</text>''')
    buttons=[
      ('audio-master','rotary','intercomVolumeUp','intercomVolumeDown','Interkom szabályzó · rekonstrukció',knob,94,72,170,210,'intercomVolume','exact channel assignment unverified'),
      ('thermal','button','fan',None,'Segédfunkció · ikon jelentése részben bizonytalan',round_button('skoda-console-thermal','#ef5a3d','thermal'),72,328,200,235,'','icon geometry observed; game assignment configurable'),
      ('master','button','electricalMaster',None,'Elektromos főkapcsoló',round_button('skoda-console-master','#ff563d','bolt'),340,63,200,235,'','function inferred from lightning icon'),
      ('toggle','toggle','auxMode',None,'Felső billenőkapcsoló · szabad kiosztás',toggle,606,72,160,220,'','unlabelled function not verified'),
      ('ignition','toggle','ignition',None,'Gyújtás',round_button('skoda-console-power','#1fbac2','power'),844,72,200,235,'ignition','power symbol observed; in-game binding configurable'),
      ('service','button','displayNext',None,'Szervizmenü',touch_key('skoda-console-service',text='servis menu'),283,388,186,143,'','label observed'),
      ('call-accept','button','callAccept',None,'Hívás fogadása',touch_key('skoda-console-call',icon='call',color='#5ed1ae'),283,588,186,143,'','phone symbol observed; no phone API used'),
      ('call-end','button','callEnd',None,'Hívás lezárása',touch_key('skoda-console-end-call',icon='endCall',color='#f18dad'),283,788,186,143,'','phone symbol observed; no phone API used'),
      ('volume-1','stepper','intercomVolumeUp','intercomVolumeDown','Interkom hangerő',volume('skoda-console-volume-1'),486,388,145,795,'intercomVolume','two volume ramps observed; channel assignment reconstructed'),
      ('volume-2','stepper','radioVolumeUp','radioVolumeDown','Rádió hangerő',volume('skoda-console-volume-2',True),646,388,145,795,'radioVolume','two volume ramps observed; channel assignment reconstructed'),
      ('hazard','button','hazards',None,'Vészvillogó',touch_key('skoda-console-hazard',icon='hazard'),817,388,186,143,'','hazard symbol observed'),
      ('fog','button','fogLights',None,'Ködlámpa',touch_key('skoda-console-fog',icon='fog'),817,588,186,143,'','lamp symbol observed; exact circuit not verified'),
      ('all','button','acknowledge',None,'ALL · felhasználói művelet',touch_key('skoda-console-all',icon='all'),817,788,186,143,'','ALL marking observed; exact function not verified'),
      ('windscreen','button','demist',None,'Szélvédőfűtés',round_button('skoda-console-windscreen','#efd34b','windscreen'),828,1000,200,235,'','windscreen symbol observed'),
      ('lights','toggle','lights',None,'Világítás',round_button('skoda-console-cabin-light','#0079fa','lamp'),828,1230,200,210,'lights','cabin-light symbol observed; mapped to existing lights action'),
      ('fire','button','fireExtinguisher',None,'FIRE · játékon belüli, szabadon kiosztható művelet',fire,57,640,194,415,'','guarded FIRE control observed; no default binding'),
    ]
    elements=[graphic('skoda-console-body',face,0,0,1100,1450,0,True)]
    for identifier,kind,action,minus,label,image,x,y,w,h,field,note in buttons:
        e=dict(id='skoda-console-'+identifier,kind=kind,field=field,label=label,action=action,x=x,y=y,w=w,h=h,assetId=image,artwork=True,border=False,fontSize=22,color='#b4e2ff',z=5,referenceNote=note)
        if minus:e['minusAction']=minus
        elements.append(e)
    return dict(schemaVersion=1,id=CAR+'-panel',name='Škoda Fabia RS Rally2 · Középkonzol',vehicleId=CAR,role='panel',isBase=True,version='0.3.0',revision=2,width=1100,height=1450,background='#0b1013',
                pages=[dict(id=CAR+'-central-console',name='Középkonzol · fotóalapú rekonstrukció',elements=elements)],assets={},supportedFields=[])


def apply_profile():
    catalog_path=ROOT/'mobile_flutter/assets/catalog.json'
    catalog=json.loads(catalog_path.read_text());previous=next(v for v in catalog['vehicles'] if v['id']==CAR)
    car=copy.deepcopy(previous)
    # The base layout IDs remain stable so existing selections continue to resolve.
    dash=dashboard();panel=console()
    dash['id']=previous['dashboard']['id'];panel['id']=previous['panel']['id']
    for layout in [dash,panel]:
        used={e['assetId'] for p in layout['pages'] for e in p['elements'] if 'assetId' in e}
        layout['assets']={k:ASSETS[k] for k in sorted(used)}
        layout['supportedFields']=sorted({e['field'] for p in layout['pages'] for e in p['elements'] if e.get('field')})
    car.update(version='0.3.0',dashboard=dash,panel=panel,fidelity='partial_reference',fidelityLabel='Fotóalapú rekonstrukció · részben igazolt',
       reconstructionVersion='0.3.0',reconstructionScope=['driver_display','central_console'],
       knownLimitations=['A vezetői kijelző a kormányoszlop felett látható egység; nem a külön középső diagnosztikai monitor.',
         'A betűtípus helyettesítő, a LED-ek száma és a perspektívából becsült pixelgeometria rekonstrukció.',
         'A középkonzol két hangerőcsatornájának kiosztása és a felirat nélküli kapcsolók funkciója nincs teljesen igazolva.',
         'A gyári rajzon nem szereplő indító/ablaktörlő/interkom műveletek az alkalmazás gyorsvezérlői között elérhetők.',
         'Az alkalmazás kiegészítő telemetriaoldalai nem gyári kijelzőoldalak. A hiányzó játékadat — jelzést kap.'])
    car['references']=[
      {'url':'https://www.skoda-motorsport.com/en/skoda-fabia-rs-rally2/basic-information/','scope':'Gyártói leírás: fő kijelző, érintős középkonzol, integrált interkom; starter a kormányon.','status':'primary_manufacturer'},
      {'url':'https://skoda-motorsport.s3.amazonaws.com/com/2024/10/Rally2_steering_wheel.jpg','scope':'Vezetői kijelző tényleges elhelyezése és Speed/Map/Gear/Time képernyőszerkezete. A kormány grafikája nincs a termékben.','status':'photo_inspected','sha256':'6fd42e0afc83aefc3e396e00eab9ec454350bb7a9643bfa47030fb60278ceb5e'},
      {'url':'https://cdn.skoda-storyboard.com/2022/10/02_FABIA_RS_Rally2_f0de083a.jpg','scope':'Középkonzoli panel: színes nyomógombok, billenő/forgó, servis menu, hívásikonok, két hangerőmező, jobb oldali ikonok, FIRE fedél.','status':'photo_inspected','sha256':'6750d7613fa9d5e890d7228375288e5b6ea0bc375267010271c894164efde86e'}]
    for i,v in enumerate(catalog['vehicles']):
        if v['id']==CAR:catalog['vehicles'][i]=car
    catalog['version']='0.3.0'
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    destination=ROOT/'vehicle_profiles'/CAR
    (destination/'profile.json').write_text(json.dumps(car,ensure_ascii=False,indent=2)+'\n')
    assets_dir=destination/'assets';assets_dir.mkdir(exist_ok=True)
    for name,data in ASSETS.items():(assets_dir/(name+'.svg')).write_bytes(base64.b64decode(data['base64']))
    (destination/'REFERENCES.md').write_text('# Škoda Fabia RS Rally2 – 0.3.0 fotóreferenciák\n\n'+'\n\n'.join(f'- {r["url"]}\n  {r["scope"]}' for r in car['references'])+'\n\nA geometria, a helyettesítő betűtípus és a nem igazolható kapcsolófunkciók rekonstrukciók. A 2022–2024-es referenciafotók nem igazolják a későbbi modellévek minden módosítását.\n')
    print('Updated only Škoda: driver display + central console; other 19 car files preserved.')

if __name__=='__main__':apply_profile()
