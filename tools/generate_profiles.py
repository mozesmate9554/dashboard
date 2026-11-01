#!/usr/bin/env python3
"""Build the versioned catalogue from explicitly composed, different layouts.

These are original editable drawings, NOT manufacturer-certified replicas.
Model identity references do not establish individual switch coordinates.
"""
from pathlib import Path
import base64
import json

ROOT = Path(__file__).resolve().parents[1]
W, H = 1200, 700

# id, model, selected reference year, class, accent, source, evidence scope
VEHICLES = [
 ('porsche-992-gt3-r','Porsche 911 GT3 R (992)',2023,'GT3','#ef4444','https://newsroom.porsche.com/en_US/2022/motorsport/porsche-911-gt3-r-generation-992-customer-racing-car-premiere-29222.html','Model generation; illuminated wheel buttons and digital touch panel.'),
 ('bmw-m4-gt3','BMW M4 GT3',2022,'GT3','#65baff','https://www.bmw-m.com/en/fastlane/motorsport/bmw-automotive-gaming.html','Shared physical/simulator Fanatec wheel; exact display page not established.'),
 ('mercedes-amg-gt3','Mercedes-AMG GT3',2020,'GT3','#37dfc3','https://customerracing.mercedes-amg.com/en/mercedes-amg-gt3','Model and cockpit concept; exact switch positions pending.'),
 ('ferrari-296-gt3','Ferrari 296 GT3',2023,'GT3','#ffcf32','https://www.imsa.com/news/2022/10/26/new-horse-in-town-ferrari-296-gt3-ready-for-racing-in-2023/','Championship organiser: wheel-mounted functions. Manufacturer page access challenged; not used as visual proof.'),
 ('audi-r8-lms-gt3','Audi R8 LMS GT3',2019,'GT3','#ff3f4e','https://www.audi.com/en/images/detail/audi-r8-lms-gt3-2019-68618','Manufacturer model photo identity; display/control geometry unverified.'),
 ('lamborghini-huracan-gt3-evo2','Lamborghini Huracán GT3 EVO2',2023,'GT3','#a1e63f','https://www.lamborghini.com/en-en/motorsport/motorsport-models/huracan-gt3-evo2','EVO2 identity and racing-wheel section; exact labels pending.'),
 ('mclaren-720s-gt3-evo','McLaren 720S GT3 Evo',2023,'GT3','#ff9834','https://cars.mclaren.com/uk_en/customer-racing/models-customer/720s-gt3','Customer-racing model family; EVO cockpit reconstruction remains unverified.'),
 ('aston-vantage-gt3','Aston Martin Vantage GT3',2024,'GT3','#8edc86','https://media.astonmartin.com/state-of-the-art-aston-martin-vantage-gt3-spearheads-new-era-in-top-flight-gt-racing/?lang=eng&view=cp','2024 generation identity; individual controls not established by this release.'),
 ('lexus-rcf-gt3','Lexus RC F GT3',2017,'GT3','#6dc9ee','https://toyotagazooracing.com/gt3/lexusrcfgt3/','RC F GT3 model and development; cockpit coordinate proof pending.'),
 ('corvette-z06-gt3r','Corvette Z06 GT3.R',2024,'GT3','#f3d43c','https://news.chevrolet.com/newsroom.detail.html/Pages/news/us/en/2023/jan/0127-corvette-racing.html','2024 GT3.R introduction; no road-car cockpit has been substituted.'),
 ('porsche-963','Porsche 963',2023,'HYPERCAR','#ff4e5e','https://newsroom.porsche.com/en_US/2023/motorsport/porsche-963-lmdh-motorsport-future-31003.html','Hybrid platform and wheel control complexity; exact page and rotary positions pending.'),
 ('ferrari-499p','Ferrari 499P',2023,'HYPERCAR','#ffe05b','https://www.ferrari.com/en-EN/hypercar/499p','Manufacturer URL could not be retrieved. Reference candidate only; no Modificata controls or P2P have been attributed to 499P.'),
 ('toyota-gr010','Toyota GR010 Hybrid',2024,'HYPERCAR','#ed404d','https://toyotagazooracing.com/wec/cars/2024/','2024 GR010 powertrain/specification identity; exact wheel layout pending.'),
 ('cadillac-v-series-r','Cadillac V-Series.R',2023,'HYPERCAR','#65b3ff','https://news.cadillac.com/newsroom.detail.html/Pages/news/us/en/2023/feb/0227-cadillac.html','2023 V-Series.R identity; switch/page geometry unverified.'),
 ('bmw-m-hybrid-v8','BMW M Hybrid V8',2024,'HYPERCAR','#ba89ff','https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m-bei-den-24h-le-mans.html','2024 Hypercar model; cockpit controls need a pinned close-up reference.'),
 ('toyota-yaris-rally1','Toyota GR Yaris Rally1',2024,'RALLY1','#fc4b54','https://toyotagazooracing.com/wrc/cars/2024/','2024 HYBRID specification selected; later non-hybrid Rally1 years are not blended in.'),
 ('hyundai-i20-rally1','Hyundai i20 N Rally1',2025,'RALLY1','#76cbe9','https://motorsport.hyundai.com/Corporate%20Site/Car%20Spec/i20%20N%20Rally1/2025/Hyundai%20Rally1%20Tech%20Spec.pdf','2025 non-hybrid specification; no hybrid controls are presented as original.'),
 ('ford-puma-rally1','Ford Puma Rally1',2026,'RALLY1','#79b8ff','https://www.m-sport.co.uk/post/m-sport-crews-bid-farewell-to-rally1-cars-on-rally-italia-sardegna','2026 model identity; exact control geometry not established. No assumed hybrid control.'),
 ('skoda-fabia-rs-rally2','Škoda Fabia RS Rally2',2022,'RALLY2','#64e69c','https://www.skoda-motorsport.com/en/skoda-fabia-rs-rally2/basic-information/','Confirmed: enlarged display, start button on wheel, touch centre panel and integrated intercom. Pixel geometry/other switch positions remain an original design.'),
 ('dallara-ir18','Dallara IR-18 IndyCar',2024,'INDYCAR','#8bbdff','https://www.indycar.com/News/2024/07/07-29-Steering-Wheels','Series primary reference: team-specific wheel controls. Not a universal factory wheel; P2P/neutral/radio concept only, no DRS.'),
]

def element(kind, field, x,y,w,h, label='', **extra):
    return dict(kind=kind,field=field,x=x,y=y,w=w,h=h,label=label,**extra)
def n(field,x,y,w,h,label=None,**extra): return element('gear' if field=='gear' else 'number',field,x,y,w,h,label or field.upper(),**extra)
def leds(x,y,w,h,**kw): return element('leds','rpm',x,y,w,h,'RPM',max=8000,**kw)
def text(label,x,y,w,h,size=22,**kw): return element('text','',x,y,w,h,label,fontSize=size,**kw)

# Every dashboard has a separately authored composition, not a recoloured template.
DASHBOARDS = [
 [leds(70,38,1060,40,count=20),n('gear',450,110,300,360),n('speed',80,150,300,180),n('rpm',820,150,300,180),n('lapCurrent',70,510,430,130,'LAP'),n('delta',540,510,270,130,'DELTA'),n('fuel',850,510,280,130,'FUEL')],
 [leds(65,40,60,540,vertical=True,count=18),leds(1075,40,60,540,vertical=True,count=18),n('gear',465,220,270,300),n('speed',150,90,340,210),n('rpm',710,90,340,210),n('lapBest',150,390,260,160,'BEST'),n('lapCurrent',790,390,260,160,'LAP'),element('pedals','',470,540,260,110),n('brakeBias',150,570,260,80,'BB'),n('tcLevel',790,570,260,80,'TC')],
 [leds(140,50,920,30,count=16),n('rpm',150,110,900,130),n('gear',470,290,260,280),n('speed',90,310,310,190),n('fuel',800,310,310,190),n('lapCurrent',90,560,420,90,'LAP'),n('waterTemp',760,560,350,90,'WATER')],
 [element('analog','rpm',50,90,500,500,max=9000),n('gear',650,90,310,320),leds(600,440,520,35,count=12,shape='circle'),n('speed',620,510,260,130),n('lapCurrent',900,510,240,130,'LAP',fontSize=42),n('tcLevel',970,120,170,100,'TC'),n('absLevel',970,260,170,100,'ABS')],
 [n('gear',75,90,320,400),leds(460,80,670,55,count=19),n('rpm',470,165,660,140),n('speed',475,345,300,160),n('lapCurrent',810,345,320,160,'LAP'),n('waterTemp',70,550,310,100,'WATER'),n('fuel',435,550,310,100,'FUEL'),n('brakeBias',800,550,330,100,'BB')],
 [leds(80,40,1040,36,count=13,shape='circle'),n('gear',470,125,260,330),n('speed',120,150,260,140),n('rpm',820,150,260,140),element('bar','throttle',80,335,300,90,'THROTTLE',max=1),element('bar','brake',820,335,300,90,'BRAKE',max=1),n('lapCurrent',120,510,440,120,'LAP'),n('lapBest',640,510,440,120,'BEST')],
 [n('speed',60,75,340,230),n('gear',780,75,350,440),leds(450,65,230,250,vertical=True,count=16),n('rpm',55,355,620,150),n('lapCurrent',65,550,600,100,'LAP'),n('fuel',780,555,350,100,'FUEL')],
 [leds(330,40,540,32,count=18),n('gear',460,130,280,300),n('speed',80,130,300,170),n('rpm',820,130,300,170),element('tyres','tyrePressure',60,355,320,290,'TYRE PRESSURE'),element('tyres','tyreTempMiddle',820,355,320,290,'TYRE TEMP'),n('lapCurrent',420,475,360,170,'LAP')],
 [n('rpm',70,70,1060,120),leds(70,220,1060,28,count=22),n('gear',470,300,260,300),n('speed',75,320,300,180),n('waterTemp',825,310,300,120,'WATER'),n('oilPressure',825,470,300,120,'OIL'),n('lapCurrent',60,555,340,90,'LAP')],
 [element('analog','speed',65,80,400,400,max=320),n('gear',510,80,280,360),n('rpm',830,95,300,130),leds(830,260,300,180,vertical=True,count=10),n('lapCurrent',65,530,460,130,'LAP'),n('delta',565,530,250,130,'DELTA'),n('fuel',855,530,280,130,'FUEL')],
 [leds(90,35,1020,42,count=24),n('gear',475,115,250,290),n('speed',80,130,330,160),n('rpm',790,130,330,160),element('bar','battery',70,340,340,90,'SOC',max=1),element('bar','hybridEnergy',790,340,340,90,'ENERGY',max=1000),n('lapCurrent',75,500,440,140,'LAP'),n('delta',555,500,240,140,'DELTA'),n('fuel',835,500,290,140,'FUEL')],
 [n('gear',55,115,300,350),leds(420,75,710,44,count=17),n('speed',440,150,310,150),n('rpm',800,150,310,150),element('bar','battery',425,355,700,80,'SOC',max=1),n('lapCurrent',55,535,490,110,'LAP'),n('hybridEnergy',600,535,510,110,'HYBRID ENERGY')],
 [leds(125,30,950,48,count=21),n('gear',470,160,260,350),n('rpm',80,145,310,150),n('speed',810,145,310,150),n('battery',85,345,310,150,'SOC',decimals=2),n('hybridEnergy',810,345,310,150,'ENERGY'),n('lapCurrent',250,560,700,100,'LAP')],
 [leds(72,55,42,550,vertical=True,count=20),n('speed',165,80,350,180),n('gear',775,135,340,340),n('rpm',165,300,490,150),n('battery',160,505,260,130,'SOC',decimals=2),n('fuel',445,505,260,130,'FUEL'),n('lapCurrent',750,535,370,100,'LAP')],
 [n('gear',440,105,320,370),leds(90,90,55,390,vertical=True,count=14),leds(1055,90,55,390,vertical=True,count=14),n('rpm',180,115,220,130),n('speed',800,115,220,130),n('hybridEnergy',175,335,230,140,'ENERGY'),n('battery',795,335,230,140,'SOC',decimals=2),n('lapCurrent',120,550,460,110,'LAP'),n('delta',640,550,440,110,'DELTA')],
 [leds(100,45,1000,40,count=12,shape='circle'),n('gear',440,130,320,340),n('speed',80,170,270,140),n('rpm',850,170,270,140),n('stageTime',95,520,500,130,'STAGE'),element('bar','battery',685,535,420,95,'HYBRID SOC',max=1)],
 [n('gear',85,100,350,410),n('rpm',520,105,590,130),leds(520,265,590,48,count=14),n('speed',540,360,260,145),n('waterTemp',840,360,260,145,'WATER'),n('stageTime',160,565,840,90,'STAGE')],
 [element('analog','rpm',75,110,430,430,max=8500),n('gear',650,115,370,320),leds(610,475,500,35,count=16),n('speed',625,545,240,110),n('stageTime',60,575,500,85,'STAGE'),n('turbo',905,545,215,110,'BOOST',decimals=1)],
 [leds(85,45,1030,38,count=18),n('gear',440,130,320,330),n('speed',85,155,280,170),n('rpm',835,155,280,170),n('waterTemp',70,365,310,100,'WATER'),n('oilPressure',820,365,310,100,'OIL PRESS',decimals=1),n('stageTime',85,525,480,120,'STAGE'),n('stageDistance',645,525,470,120,'DISTANCE')],
 [leds(155,40,890,30,count=15,shape='circle'),n('gear',455,140,290,300),n('speed',70,140,310,150),n('rpm',820,140,310,150),n('p2pRemaining',70,355,310,110,'PUSH TO PASS'),n('fuel',820,355,310,110,'FUEL'),n('lapCurrent',85,540,480,110,'LAP'),n('lapBest',645,540,470,110,'BEST')],
]

# Unique physical control groups and explicit wheel-coordinate sets.
# Unknown factory placements are labelled inspired in every profile and reference document.
CONTROLS = [
 [('PIT','pitLimiter','button'),('RADIO','radio','hold'),('FLASH','flash','hold'),('ACK','acknowledge','button'),('TC','tcUp','rotary','tcDown'),('ABS','absUp','rotary','absDown'),('BB','brakeBiasUp','stepper','brakeBiasDown'),('PAGE','displayNext','button')],
 [('PIT','pitLimiter','button'),('FLASH','flash','hold'),('RADIO','radio','hold'),('NEUTRAL','neutral','hold'),('TC','tcUp','rotary','tcDown'),('ABS','absUp','rotary','absDown'),('MAP','engineMapUp','rotary','engineMapDown'),('BB','brakeBiasUp','stepper','brakeBiasDown'),('ACK','acknowledge','button')],
 [('RADIO','radio','hold'),('PIT','pitLimiter','button'),('LIGHT','lights','toggle'),('FLASH','flash','hold'),('TC','tcUp','rotary','tcDown'),('ABS','absUp','rotary','absDown'),('BB','brakeBiasUp','stepper','brakeBiasDown')],
 [('PIT','pitLimiter','button'),('RADIO','radio','hold'),('FLASH','flash','hold'),('N','neutral','hold'),('BB','brakeBiasUp','rotary','brakeBiasDown'),('TC','tcUp','rotary','tcDown'),('ABS','absUp','rotary','absDown'),('PAGE','displayNext','button'),('ACK','acknowledge','button')],
 [('FLASH','flash','hold'),('RADIO','radio','hold'),('PIT','pitLimiter','button'),('WIPER','wiper','button'),('TC','tcUp','stepper','tcDown'),('ABS','absUp','stepper','absDown'),('BB','brakeBiasUp','rotary','brakeBiasDown'),('PAGE','displayNext','button')],
 [('PIT','pitLimiter','button'),('RADIO','radio','hold'),('FLASH','flash','hold'),('DRINK','drink','button'),('TC','tcUp','rotary','tcDown'),('ABS','absUp','rotary','absDown'),('BB','brakeBiasUp','rotary','brakeBiasDown'),('MAP','engineMapUp','stepper','engineMapDown')],
 [('RADIO','radio','hold'),('PIT','pitLimiter','button'),('FLASH','flash','hold'),('WIPER','wiper','button'),('BB','brakeBiasUp','rotary','brakeBiasDown'),('TC','tcUp','stepper','tcDown'),('ABS','absUp','rotary','absDown')],
 [('PIT','pitLimiter','button'),('RADIO','radio','hold'),('DRINK','drink','button'),('FLASH','flash','hold'),('TC','tcUp','rotary','tcDown'),('ABS','absUp','rotary','absDown'),('BB','brakeBiasUp','stepper','brakeBiasDown'),('WIPER','wiper','button')],
 [('RADIO','radio','hold'),('PIT','pitLimiter','button'),('FLASH','flash','hold'),('PAGE','displayNext','button'),('TC','tcUp','rotary','tcDown'),('ABS','absUp','rotary','absDown'),('BB','brakeBiasUp','stepper','brakeBiasDown')],
 [('PIT','pitLimiter','button'),('FLASH','flash','hold'),('RADIO','radio','hold'),('DRINK','drink','button'),('BB','brakeBiasUp','rotary','brakeBiasDown'),('TC','tcUp','rotary','tcDown'),('ABS','absUp','stepper','absDown'),('PAGE','displayNext','button')],
 [('PIT','pitLimiter','button'),('RADIO','radio','hold'),('FLASH','flash','hold'),('ACK','acknowledge','button'),('MAP','engineMapUp','rotary','engineMapDown'),('TC','tcUp','rotary','tcDown'),('BB','brakeBiasUp','stepper','brakeBiasDown'),('DRINK','drink','button')],
 [('RADIO','radio','hold'),('PIT','pitLimiter','button'),('FLASH','flash','hold'),('N','neutral','hold'),('MAP','engineMapUp','rotary','engineMapDown'),('BB','brakeBiasUp','rotary','brakeBiasDown'),('TC','tcUp','rotary','tcDown'),('ACK','acknowledge','button'),('PAGE','displayNext','button')],
 [('PIT','pitLimiter','button'),('RADIO','radio','hold'),('FLASH','flash','hold'),('DRINK','drink','button'),('BB','brakeBiasUp','rotary','brakeBiasDown'),('MAP','engineMapUp','rotary','engineMapDown'),('TC','tcUp','rotary','tcDown'),('PAGE','displayNext','button')],
 [('RADIO','radio','hold'),('PIT','pitLimiter','button'),('FLASH','flash','hold'),('ACK','acknowledge','button'),('MAP','engineMapUp','stepper','engineMapDown'),('TC','tcUp','rotary','tcDown'),('BB','brakeBiasUp','rotary','brakeBiasDown'),('DRINK','drink','button')],
 [('PIT','pitLimiter','button'),('RADIO','radio','hold'),('FLASH','flash','hold'),('N','neutral','hold'),('TC','tcUp','rotary','tcDown'),('MAP','engineMapUp','rotary','engineMapDown'),('BB','brakeBiasUp','rotary','brakeBiasDown'),('ACK','acknowledge','button')],
 [('START','starter','hold'),('WIPER','wiper','button'),('LIGHT','lights','toggle'),('INTERCOM','intercom','hold'),('MAP','engineMapUp','stepper','engineMapDown'),('PAGE','displayNext','button')],
 [('WIPER','wiper','button'),('START','starter','hold'),('LIGHT','lights','toggle'),('INTERCOM','intercom','hold'),('PAGE','displayNext','button')],
 [('START','starter','hold'),('LIGHT','lights','toggle'),('WIPER','wiper','button'),('RADIO','radio','hold'),('PAGE','displayNext','button'),('MAP','engineMapUp','stepper','engineMapDown')],
 [('WIPER','wiper','button'),('LIGHT','lights','toggle'),('START','starter','hold'),('INTERCOM','intercom','hold'),('PAGE','displayNext','button')],
 [('P2P','p2p','hold'),('RADIO','radio','hold'),('N','neutral','hold'),('PIT','pitLimiter','button'),('BB','brakeBiasUp','stepper','brakeBiasDown'),('MAP','engineMapUp','rotary','engineMapDown'),('ACK','acknowledge','button')],
]
WHEEL_POSITIONS = [
 [(120,180),(870,180),(120,310),(870,310),(160,470),(470,470),(780,470),(480,325)],
 [(90,140),(930,140),(90,270),(930,270),(180,450),(470,450),(760,450),(470,300),(470,590)],
 [(135,150),(875,150),(135,290),(875,290),(200,465),(490,465),(780,465)],
 [(115,130),(885,130),(115,270),(885,270),(185,450),(475,450),(765,450),(465,300),(465,590)],
 [(120,170),(880,170),(120,300),(880,300),(150,485),(465,485),(780,485),(465,330)],
 [(100,140),(900,140),(100,285),(900,285),(145,475),(455,475),(765,475),(450,320)],
 [(100,180),(900,180),(100,335),(900,335),(195,500),(495,500),(795,500)],
 [(110,150),(890,150),(110,290),(890,290),(180,470),(490,470),(800,470),(470,325)],
 [(130,165),(870,165),(130,310),(870,310),(185,475),(495,475),(805,475)],
 [(125,155),(885,155),(125,290),(885,290),(160,475),(470,475),(780,475),(470,325)],
 [(80,160),(920,160),(80,300),(920,300),(140,490),(450,490),(760,490),(465,340)],
 [(100,120),(900,120),(100,260),(900,260),(155,455),(465,455),(775,455),(465,310),(465,590)],
 [(85,145),(915,145),(85,285),(915,285),(155,475),(465,475),(775,475),(465,325)],
 [(125,160),(885,160),(125,295),(885,295),(160,485),(470,485),(780,485),(470,335)],
 [(95,150),(925,150),(95,290),(925,290),(155,470),(465,470),(775,470),(465,325)],
 [(470,330),(145,205),(865,205),(150,450),(470,515),(870,450)],
 [(125,200),(470,340),(885,200),(130,460),(885,460)],
 [(460,345),(125,190),(895,190),(125,455),(895,455),(460,520)],
 [(130,205),(870,205),(470,335),(130,460),(870,460)],
 [(95,165),(915,165),(95,310),(915,310),(170,485),(480,485),(790,485)],
]
SILHOUETTES = [
 'M90 120 L310 75 L890 75 L1110 120 L1150 440 L1030 635 L170 635 L50 440 Z',
 'M60 120 L300 90 L900 90 L1140 120 L1100 530 L900 650 L300 650 L100 530 Z',
 'M130 95 Q600 20 1070 95 L1150 300 L1080 570 Q600 690 120 570 L50 300 Z',
 'M80 110 L360 70 L840 70 L1120 110 L1160 480 L950 650 L250 650 L40 480 Z',
 'M70 100 L330 55 L870 55 L1130 100 L1100 560 L930 640 L270 640 L100 560 Z',
 'M60 125 L270 65 L930 65 L1140 125 L1100 520 L1000 650 L200 650 L100 520 Z',
 'M110 90 L340 100 L860 100 L1090 90 L1160 410 L1020 650 L180 650 L40 410 Z',
 'M80 130 Q250 30 360 90 L840 90 Q950 30 1120 130 L1100 540 L930 650 L270 650 L100 540 Z',
 'M120 100 L1080 100 L1150 460 L1000 645 L200 645 L50 460 Z',
 'M70 115 L330 55 L870 55 L1130 115 L1100 470 L1000 655 L200 655 L100 470 Z',
 'M55 130 L310 60 L890 60 L1145 130 L1115 550 L900 665 L300 665 L85 550 Z',
 'M65 100 L360 45 L840 45 L1135 100 L1125 550 L960 665 L240 665 L75 550 Z',
 'M60 125 L320 60 L880 60 L1140 125 L1110 540 L950 660 L250 660 L90 540 Z',
 'M90 120 L350 70 L850 70 L1110 120 L1150 465 L980 660 L220 660 L50 465 Z',
 'M70 110 L290 65 L910 65 L1130 110 L1110 545 L940 655 L260 655 L90 545 Z',
 'M600 60 A290 290 0 1 1 599 60 M600 125 A225 225 0 1 0 601 125',
 'M600 55 A295 295 0 1 1 599 55 M600 120 A230 230 0 1 0 601 120',
 'M600 65 A280 280 0 1 1 599 65 M600 125 A220 220 0 1 0 601 125',
 'M600 60 A285 285 0 1 1 599 60 M600 120 A225 225 0 1 0 601 120',
 'M60 135 L300 80 L900 80 L1140 135 L1090 520 L930 655 L270 655 L110 520 Z',
]

def assign_ids(elements, prefix, accent):
    for index,e in enumerate(elements):
        e['id'] = f'{prefix}-{index+1}'
        e.setdefault('color',accent); e.setdefault('z',index)
    return elements
def page(name,elements,prefix,accent): return {'id':prefix,'name':name,'elements':assign_ids(elements,prefix,accent)}
def layout(identifier, name, car, role, pages, **extra):
    fields=sorted({e.get('field') for p in pages for e in p['elements'] if e.get('field')})
    return dict(schemaVersion=1,id=identifier,version='0.1.0',revision=1,name=name,vehicleId=car,role=role,
        isBase=True,width=W,height=H,background='#080a0c',supportedFields=fields,pages=pages,**extra)

catalog=[]
for index,(car,name,year,category,accent,source,scope) in enumerate(VEHICLES):
    dash = DASHBOARDS[index]
    # p2pRemaining is not in the v1 source contract; it is explicitly unavailable.
    if car=='dallara-ir18':
        dash[4]['field']='timeRemaining'; dash[4]['label']='SESSION LEFT'
    dash.append(text(f'{name.upper()} / {year}',200,665,800,30,16,color=accent))
    systems=[element('tyres','tyrePressure',60,100,480,350,'PRESSURE'),element('tyres','tyreTempMiddle',660,100,480,350,'TEMPERATURE'),
        element('pedals','',100,500,320,130),element('gForce','',510,480,180,180),n('waterTemp',770,500,330,130,'WATER')]
    dashboard=layout(car+'-dash',name+' · Műszerfal',car,'dashboard',[
        page('Verseny',dash,car+'-race',accent),page('Rendszerek',systems,car+'-systems',accent)])
    controls=CONTROLS[index]
    wheel=[]
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 700"><path d="{SILHOUETTES[index]}" fill="#161b22" stroke="#3d4654" stroke-width="10" fill-rule="evenodd"/><rect x="350" y="130" width="500" height="130" rx="12" fill="#07090d" stroke="{accent}" stroke-width="2"/></svg>'
    wheel.append(element('svg','',0,0,W,H,'',assetId='wheel-body',border=False,z=-20))
    wheel.append(n('gear',465,135,270,120,'GEAR',fontSize=80,border=False))
    for c,(x,y) in zip(controls,WHEEL_POSITIONS[index]):
        label,action,kind,*minus=c
        wheel.append(element(kind,'',x,y,220 if kind in ('rotary','stepper') else 175,110,label,
            action=action,**({'minusAction':minus[0]} if minus else {}),shape='circle' if kind in ('rotary','hold') else 'rounded'))
    console_actions=[('IGNITION','ignition','toggle'),('START','starter','hold'),('LIGHTS','lights','toggle'),('WIPER','wiper','button')]
    if category.startswith('RALLY'): console_actions += [('INTERCOM','intercom','hold'),('PAGE','displayNext','button')]
    else: console_actions += [('FAN','fan','button'),('RAIN','rainLight','toggle')]
    console=[]
    # Distinct console widths/spacing/column grouping; selected model-year references remain separate.
    for j,(label,action,kind) in enumerate(console_actions):
        columns=2 if index in (2,6,8,15,17,18) else 3
        cw=480 if columns==2 else 320
        x=80+(j%columns)*(cw+35); y=95+(j//columns)*(165 if columns==2 else 245)
        console.append(element(kind,'',x,y,cw,135,label,action=action,shape='rounded'))
    if car=='skoda-fabia-rs-rally2':
        console=[text('TOUCH CONTROL / INTERCOM',120,40,960,45,24),
          element('toggle','',90,140,310,140,'IGNITION',action='ignition',shape='rounded'),
          element('hold','',445,140,310,140,'START',action='starter',shape='circle'),
          element('toggle','',800,140,310,140,'LIGHTS',action='lights',shape='rounded'),
          element('button','',90,340,310,135,'WIPER',action='wiper',shape='rounded'),
          element('hold','',445,340,310,135,'INTERCOM',action='intercom',shape='rounded'),
          element('button','',800,340,310,135,'PAGE',action='displayNext',shape='rounded')]
    combined=[]
    for j,c in enumerate(controls[:8]):
        label,action,kind,*minus=c
        cols=3 if category.startswith('RALLY') or index%3==0 else 4
        cw=330 if cols==3 else 250
        x=50+(j%cols)*(cw+30); y=90+(j//cols)*180
        combined.append(element(kind,'',x,y,cw,140,label,action=action,**({'minusAction':minus[0]} if minus else {}),shape='rounded'))
    combined.append(text('EGYÉNI ELRENDEZÉS / EREDETI AUTÓ ÁLTAL INSPIRÁLT',50,650,1100,30,14))
    panel=layout(car+'-panel',name+' · Kezelőpanel',car,'panel',[
      page('Kormány',wheel,car+'-wheel',accent),page('Középkonzol',console,car+'-console',accent),
      page('Kombinált mobilpanel',combined,car+'-combined',accent),page('Egyéni vezérlők',[],car+'-custom',accent)],
      assets={'wheel-body':{'type':'svg','base64':base64.b64encode(svg.encode()).decode()}})
    references=[{'url':source,'checkedOn':'2026-11-01','scope':scope,
        'status':'candidate_unretrieved' if car=='ferrari-499p' else 'reviewed_primary_or_organiser',
        'supportsExactGeometry':False}]
    if car=='skoda-fabia-rs-rally2': references.append({'url':'https://www.skoda-motorsport.com/en/skoda-fabia-rs-rally2-all-the-essentials-in-60-seconds/','checkedOn':'2026-11-01','scope':'2022 introduction: wheel start and touch console; exact pixels not established.','supportsExactGeometry':False,'status':'reviewed_primary'})
    fidelity='partial_reference' if car=='skoda-fabia-rs-rally2' else 'inspired'
    profile=dict(id=car,name=name,modelYear=year,category=category,color=accent,version='0.1.0',fidelity=fidelity,
        fidelityLabel='Részleges referencia alapján' if fidelity=='partial_reference' else 'Eredeti autó által inspirált kiegészített változat',
        gameVehicleAliases=[],references=references,knownLimitations=[
          'Factory pixel geometry, fonts and complete switch labels have NOT been verified.',
          'Drawing scale and RPM LED thresholds are editable design settings, not live engine-limit telemetry.',
          'A visible control is usable only after mapping and granting permission in the Bridge.',
          'Car profiles do not imply that the selected game includes this car or supports every field.'],
        dashboard=dashboard,panel=panel)
    catalog.append(profile)
    target=ROOT/'vehicle_profiles'/car
    target.mkdir(parents=True,exist_ok=True)
    (target/'profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n')
    reference_text=f'# {name} · {year}\n\nÁllapot: {profile["fidelityLabel"]}.\n\n'
    reference_text+='Ez saját készítésű, szerkeszthető rajz. A gyári pixelgeometria és teljes kapcsolókiosztás nincs igazolva.\n\n'
    for ref in references: reference_text+=f'- {ref["url"]}\n  - Vizsgált bizonyíték: {ref["scope"]}\n  - Státusz: {ref["status"]}; ellenőrzés: 2026-11-01.\n'
    reference_text+='\nAz összes elem pozíciója és mérete saját tervezés, nem gyári rajz átvétele. A Škoda igazolt funkciói kivételével a funkciócsoportok pontos gyári helye további kutatást igényel.\n'
    (target/'REFERENCES.md').write_text(reference_text)

GAME_NAMES=[('acr','Assetto Corsa Rally'),('acevo','Assetto Corsa EVO'),('ac','Assetto Corsa'),('beamng','BeamNG.drive'),('acc','Assetto Corsa Competizione'),('iracing','iRacing'),('ams2','Automobilista 2'),('rf2','rFactor 2'),('lmu','Le Mans Ultimate'),('f1','EA SPORTS F1'),('eawrc','EA SPORTS WRC'),('dirt2','DiRT Rally 2.0'),('raceroom','RaceRoom Racing Experience'),('forzam','Forza Motorsport'),('forzah','Forza Horizon'),('pcars','Project CARS'),('ets2','Euro Truck Simulator 2'),('ats','American Truck Simulator')]
games=[dict(id=i,name=n,implemented=i in ('acr','ac','acc','beamng'),physicalTested=False,
    status='Adapter implementálva; valós játékban még tesztelendő' if i in ('acr','ac','acc','beamng') else 'Bővítési pont dokumentálva; adapter még nem készült el') for i,n in GAME_NAMES]
payload={'schemaVersion':1,'version':'0.1.0','vehicles':catalog,'games':games}
dest=ROOT/'mobile_flutter/assets/catalog.json'; dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n')
(ROOT/'windows_bridge/Bridge.Windows/profiles.json').write_text(json.dumps([v['id'] for v in catalog])+'\n')
print(f'Generated {len(catalog)} vehicle pairs / {len(catalog)*2} layouts; factory fidelity NOT asserted.')
