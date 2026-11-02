#!/usr/bin/env python3
"""Compare authentic source photographs with actual Flutter-rendered previews."""
import argparse, hashlib, json, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

p=argparse.ArgumentParser();p.add_argument('--previews',type=Path,required=True);p.add_argument('--references',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=True)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=lambda size:ImageFont.truetype(fontpath,size)
records=json.loads((a.references/'sources.json').read_text())
pdf=canvas.Canvas(str(a.output/'SKODA_REFERENCE_COMPARISON_0.3.0.pdf'),pagesize=(1400,1150))
outputs=[]
for role,reference,title,crop,notes in [
 ('dashboard','official-cockpit','DRIVER DIGITAL DISPLAY',(.461,.221,.535,.286),[
  'Observed: Speed at left; Map boxes and ROAD centrally; large Gear at right; LC Limiter, clock and Time below.',
  'Reconstructed: bezel dimensions, font substitute, LED count/thresholds and the exact coolant icon geometry.',
  'The small original display is enlarged for inspection. Source pixels do not establish factory pixel geometry.',
  'LC Limiter is a separate unsupported launch-limit field in live Rally data, never relabelled engine RPM limit.',
 ]),
 ('panel','official-console','SEPARATE CENTRAL CONSOLE',(.265,.29,.66,.875),[
  'Observed: rotary and toggle; coloured caps; servis menu; call keys; twin volume ramps; hazard/fog/ALL; FIRE cover.',
  'Reconstructed: front-on geometry from perspective, unlabelled switch functions and the two audio channel assignments.',
  'All 16 controls are editable elements with separate vector artwork and configurable logical command bindings.',
  'Starter, wiper and push-to-talk remain available in application quick controls. No steering wheel is drawn.',
 ])]:
    raw=a.references/(reference+'.jpg');preview=a.previews/f'SKODA_{role.upper()}_0.3.0.png'
    source=Image.open(raw).convert('RGB');box=tuple(round(v*(source.width if i%2==0 else source.height)) for i,v in enumerate(crop));detail=source.crop(box)
    board=Image.new('RGB',(4200,3450 if role=='panel' else 2700),'#0b1115');d=ImageDraw.Draw(board)
    d.text((100,65),'SIM CONTROL STUDIO / 0.3.0',font=font(42),fill='#88d3a9')
    d.text((100,135),'ŠKODA FABIA RS RALLY2 — '+title,font=font(55),fill='white')
    d.text((100,240),'MANUFACTURER PHOTO / DETAIL CROP',font=font(31),fill='#a6b6bf')
    d.text((2200,240),'ACTUAL FLUTTER RENDER / EDITABLE RECONSTRUCTION',font=font(28),fill='#a6b6bf')
    imageheight=2300 if role=='panel' else 1400
    for image,rect in [(detail,(100,310,1950,imageheight)),(Image.open(preview).convert('RGB'),(2200,310,1900,imageheight))]:
        x,y,w,h=rect;fitted=ImageOps.contain(image,(w,h),Image.Resampling.LANCZOS)
        board.paste(fitted,(x+(w-fitted.width)//2,y+(h-fitted.height)//2))
    y=310+imageheight+70
    d.line((100,y-28,4100,y-28),fill='#33474f',width=3)
    for note in notes:
        for line in textwrap.wrap(note,155):d.text((100,y),line,font=font(33),fill='#d2dbdf');y+=48
        y+=15
    record=next(r for r in records if r['id']==reference)
    for line in textwrap.wrap('Source: '+record['credit']+' | '+record['url'],170):d.text((100,y),line,font=font(25),fill='#8aabb8');y+=37
    d.text((100,board.height-90),'Source photo © Škoda Auto / attribution for technical comparison. App: original vectors, synthetic DEMO values. Not factory certified.',font=font(26),fill='#b9c4ca')
    path=a.output/f'SKODA_{role.upper()}_COMPARISON_0.3.0.png';board.save(path,optimize=True)
    pdf.setFillColorRGB(.04,.06,.08);pdf.rect(0,0,1400,1150,fill=1,stroke=0)
    pdf.drawImage(ImageReader(board),0,0,width=1400,height=1150,preserveAspectRatio=True,anchor='c')
    pdf.linkURL(record['url'],(0,0,1400,1150),relative=0);pdf.showPage()
    outputs.append({'role':role,'source':record,'sourceCropPixels':box,'previewSha256':hashlib.sha256(preview.read_bytes()).hexdigest(),'previewSize':Image.open(preview).size,'comparison':path.name})
pdf.save()
(a.output/'comparison-provenance.json').write_text(json.dumps({'version':'0.3.0','scope':'Actual Flutter renderer and attributed source-photo crops; not a physical device test','surfaces':outputs},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(outputs,ensure_ascii=False,indent=2))
