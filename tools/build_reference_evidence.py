#!/usr/bin/env python3
"""Build the user-requested, attributed Škoda reference evidence document in CI.
The source photographs are research evidence, never application backgrounds.
"""
import base64, hashlib, json, urllib.request
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

out=Path('reference-evidence');out.mkdir(exist_ok=True)
sources=[
 ('official-cockpit','https://skoda-motorsport.s3.amazonaws.com/com/2024/10/Rally2_steering_wheel.jpg','Škoda Motorsport / official Fabia RS Rally2 gallery'),
 ('official-console','https://cdn.skoda-storyboard.com/2022/10/02_FABIA_RS_Rally2_f0de083a.jpg','Škoda Storyboard / RS Experience press kit, October 2022'),
 ('dashboard-detail','https://images.dailyrevs.com/0000/v3/Skoda/63ef4ce282f6b2e83c761558/2023-fabia-rs-rally2-skoda-b0mei0zo2vuqxinrg.jpeg','DailyRevs / reproduced 2023 Škoda Fabia RS Rally2 press photography'),
]
records=[]
c=canvas.Canvas(str(out/'SKODA_REFERENCE_EVIDENCE.pdf'),pagesize=(1440,1100))
for name,url,credit in sources:
    request=urllib.request.Request(url,headers={'User-Agent':'SIM-CONTROL-STUDIO-reference-document/0.3.0'})
    with urllib.request.urlopen(request,timeout=60) as response: raw=response.read(20*1024*1024)
    path=out/(name+'.jpg');path.write_bytes(raw)
    info={'id':name,'url':url,'credit':credit,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    records.append(info)
    c.setFillColorRGB(.05,.06,.07);c.rect(0,0,1440,1100,fill=1,stroke=0)
    c.setFillColorRGB(.4,.95,.65);c.setFont('Helvetica-Bold',24);c.drawString(40,1050,'SKODA FABIA RS RALLY2 / REFERENCE EVIDENCE')
    c.setFillColorRGB(1,1,1);c.setFont('Helvetica',16);c.drawString(40,1018,name)
    c.drawImage(ImageReader(str(path)),40,140,width=1360,height=840,preserveAspectRatio=True,anchor='c')
    c.setFont('Helvetica',11);c.drawString(40,110,credit);c.drawString(40,86,url)
    c.drawString(40,62,'Source photographs for comparison; reconstruction and live data are separate deliverables.')
    c.showPage()
    # Machine-readable review channel; public source image bytes, no credentials.
    if len(raw)<2*1024*1024: print('REFERENCE_IMAGE_BASE64:'+name+':'+base64.b64encode(raw).decode())
c.save()
(out/'sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'referenceDocument':'reference-evidence/SKODA_REFERENCE_EVIDENCE.pdf','sources':records}))
