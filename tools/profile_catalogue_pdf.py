#!/usr/bin/env python3
"""Vector review document from JSON, not Flutter screenshots or live telemetry."""
import json,math
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

ROOT=Path(__file__).resolve().parents[1]
pdfmetrics.registerFont(TTFont('StudioSans','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('StudioBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
destination=ROOT/'documentation/PROFILE_CATALOGUE.pdf'
c=canvas.Canvas(str(destination),pagesize=A4)
c.setTitle('SIM CONTROL STUDIO 0.1.0 – 20 profilpár áttekintése')
c.setAuthor('SIM CONTROL STUDIO')
PW,PH=A4
def color(hexvalue,fallback='#ef3340'):
 try:return HexColor(hexvalue)
 except Exception:return HexColor(fallback)
def label(text,x,y,size=10,fill='#eeeeee',bold=False):
 c.setFillColor(color(fill));c.setFont('StudioBold' if bold else 'StudioSans',size);c.drawString(x,y,str(text))
def draw(layout,page,left,bottom,width):
 scale=width/layout['width'];height=layout['height']*scale
 c.saveState();c.translate(left,bottom);c.scale(scale,scale)
 c.setFillColor(color(layout['background']));c.rect(0,0,layout['width'],layout['height'],fill=1,stroke=0)
 for e in sorted(layout['pages'][page]['elements'],key=lambda e:e.get('z',0)):
  x,y,w,h=e['x'],layout['height']-e['y']-e['h'],e['w'],e['h'];kind=e['kind'];accent=e.get('color','#ef3340')
  c.setStrokeColor(color(accent));c.setLineWidth(1.5)
  c.setFillColor(color(e.get('background','#0e1116')))
  if kind not in ('text','leds','svg','image'):
   c.roundRect(x,y,w,h,20 if e.get('shape')=='rounded' else 4,fill=1,stroke=1)
  if kind=='leds':
   count=e.get('count',15)
   for i in range(count):
    c.setFillColor(color('#252a31'))
    if e.get('vertical'):c.roundRect(x+2,y+i*h/count+2,w-4,h/count-4,2,fill=1,stroke=0)
    else:c.roundRect(x+i*w/count+2,y+2,w/count-4,h-4,2,fill=1,stroke=0)
  elif kind in ('number','gear'):
   c.setFillColor(color(accent));c.setFont('StudioSans',min(16,w/max(1,len(e['label']))*1.3));c.drawCentredString(x+w/2,y+h-24,e['label'])
   c.setFillColor(color('#ffffff'));c.setFont('StudioBold',min(h*.5,120));c.drawCentredString(x+w/2,y+h*.24,'—')
  elif kind=='text':
   c.setFillColor(color(accent));c.setFont('StudioBold',min(e.get('fontSize',22),w/max(1,len(e['label']))*1.5));c.drawCentredString(x+w/2,y+h*.35,e['label'])
  elif kind=='analog':
   c.setStrokeColor(color('#303744'));c.setLineWidth(8);r=min(w,h)*.4;c.circle(x+w/2,y+h/2,r,fill=0,stroke=1)
   c.setFillColor(color('#ffffff'));c.setFont('StudioBold',30);c.drawCentredString(x+w/2,y+h*.24,'—')
  elif kind in ('rotary','stepper','threeState','multiState','slider'):
   c.setFillColor(color(accent));c.setFont('StudioBold',min(20,w/max(1,len(e['label']))*1.3));c.drawCentredString(x+w/2,y+h*.7,e['label'])
   c.setFillColor(color('#eeeeee'));c.setFont('StudioBold',30);c.drawCentredString(x+w*.16,y+h*.25,'−');c.drawCentredString(x+w*.84,y+h*.25,'+')
  elif kind not in ('svg','image'):
   c.setFillColor(color('#c0c6ce'));c.setFont('StudioBold',min(24,w/max(1,len(e['label']))*1.3));c.drawCentredString(x+w/2,y+h*.45,e['label'] or kind.upper())
 c.restoreState();return height

vehicles=json.loads((ROOT/'mobile_flutter/assets/catalog.json').read_text())['vehicles']
for index,v in enumerate(vehicles):
 c.setFillColor(color('#101216'));c.rect(0,0,PW,PH,fill=1,stroke=0)
 label('SIM CONTROL STUDIO / PROFILKATALÓGUS',24,PH-30,9,'#ef3340',True)
 label(v['name'],24,PH-57,18,bold=True)
 label(f'{v["modelYear"]} · {v["category"]} · {v["fidelityLabel"]}',24,PH-76,9,'#a0a9b5')
 width=PW-48
 label('MŰSZERFAL · VERSENYOLDAL',24,PH-100,8,'#a0a9b5')
 h=700*width/1200;top=PH-112;draw(v['dashboard'],0,24,top-h,width)
 label('KEZELŐPANEL · KOMBINÁLT MOBILNÉZET',24,top-h-22,8,'#a0a9b5')
 bottom=top-h-34-h;draw(v['panel'],2,24,bottom,width)
 label('Adat nélküli, JSON-ból rajzolt vektoros áttekintés. Nem Flutter képernyőkép.',24,44,8,'#a0a9b5')
 label('A gyári pixelgeometria nincs hitelesítve; a gombokhoz helyi kiosztás szükséges.',24,31,8,'#a0a9b5')
 label(f'{index+1:02d} / 20',PW-65,18,8,'#ef3340')
 c.showPage()
c.save();print(destination)
