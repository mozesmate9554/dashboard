#!/usr/bin/env python3
"""The five further Assetto Corsa Rally cars of SIM CONTROL STUDIO 0.4.0.

Each car gets its own dashboard and its own mechanical button box. Layouts follow the
research in documentation/VEHICLE_REFERENCE_REPORT.md; artwork is original (generated here).
Functions without a matching game input (e.g. horn, tarmac/gravel selector) are NOT invented.
"""
import base64, io, math
import build_040_gauges as gauges
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

rng = np.random.default_rng(4004)

GLASS = dict(material='glass', shape='square', ring=False)
RUBBER = dict(material='rubber', ring=True)

def png_bytes(image):
    buffer = io.BytesIO(); image.save(buffer, format='PNG', optimize=True); return buffer.getvalue()

def el(i, kind, field, x, y, w, h, label='', **extra):
    if kind in ('number', 'gear'):
        extra.setdefault('font', 'factory')
    e = {'id': i, 'kind': kind, 'field': field, 'label': label, 'x': x, 'y': y, 'w': w, 'h': h, 'z': 3}
    e.update(extra); return e

def txt(i, label, x, y, w, h, size=22, color='#c8ccd0', **extra):
    return el(i, 'text', '', x, y, w, h, label, fontSize=size, foreground=color, border=False, font='factory', **extra)

def dash_layout(m, pid, name, vid, w, h, pages, png, background='#050607'):
    elements_bg = {'id': pid + '-body', 'kind': 'image', 'label': pid + '-body', 'field': '', 'x': 0, 'y': 0, 'w': w, 'h': h,
                   'assetId': pid + '-body', 'border': False, 'fit': 'fill', 'nightDim': True, 'z': 0, 'locked': True}
    built = []
    for index, (page_name, elements) in enumerate(pages):
        body = dict(elements_bg, id=f'{pid}-body-{index}')
        built.append({'id': f'{pid}-p{index + 1}', 'name': page_name, 'elements': [body] + elements})
    fields = sorted({e['field'] for _, es in pages for e in es if e.get('field')})
    return {'schemaVersion': 1, 'id': pid, 'name': name, 'vehicleId': vid, 'role': 'dashboard', 'isBase': True, 'version': '0.4.0',
            'revision': 1, 'width': w, 'height': h, 'background': background, 'pages': built,
            'assets': {pid + '-body': {'type': 'png', 'name': pid + '-body', 'base64': base64.b64encode(png).decode()}},
            'supportedFields': fields}

def housing(w, h, tone=(16, 17, 19), screen=None, screen_color=(4, 5, 6), gloss=True, radius=40, cutouts=()):
    """A display housing: moulded plastic body, recessed screen and optional round gauge cutouts."""
    img = np.repeat(np.repeat(np.array(tone, dtype=float)[None, None, :], h, axis=0), w, axis=1)
    base = Image.fromarray(np.clip(img, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((6, 6, w - 7, h - 7), radius, outline=(60, 62, 66), width=3)
    if screen:
        x0, y0, x1, y1 = screen
        d.rounded_rectangle((x0 - 10, y0 - 10, x1 + 10, y1 + 10), 22, fill=(2, 2, 3))
        if isinstance(screen_color, tuple) and len(screen_color) == 2:
            top, bottom = screen_color
            grad = np.linspace(0, 1, y1 - y0)[:, None, None]
            col = np.array(top)[None, None, :] * (1 - grad) + np.array(bottom)[None, None, :] * grad
            col = np.repeat(col, x1 - x0, axis=1)
            base.paste(Image.fromarray(np.clip(col, 0, 255).astype('uint8')), (x0, y0))
        else:
            d.rounded_rectangle(screen, 14, fill=screen_color)
        if gloss:
            overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            ImageDraw.Draw(overlay).polygon([(x0, y0), (x0 + (x1 - x0) * .55, y0), (x0 + (x1 - x0) * .35, y1), (x0, y1)], fill=(255, 255, 255, 9))
            base = Image.alpha_composite(base.convert('RGBA'), overlay).convert('RGB')
            d = ImageDraw.Draw(base)
    for (cx, cy, r) in cutouts:
        d.ellipse((cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14), fill=(6, 6, 7))
        d.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), outline=(70, 72, 76), width=4)
    return png_bytes(base)


GX, GY, GW, GH = [1090, 1240, 1390], [96, 330, 564], 140, 214

def strip(c, prefix, items, style):
    """Right-hand group: wheel/stalk functions that are not on the car's switch panel."""
    out = []
    for i, (key, kind, label, action, extra) in enumerate(items):
        params = dict(style); params.update(extra)
        out.append(c(f'{prefix}-{key}', kind, label, action, x=GX[i % 3], y=GY[i // 3], w=GW, h=GH, **params))
    return out

def grid(c, prefix, cols, rows, x0, y0, cw, ch, gap, keys, style):
    """Switch-panel matrix traced from the game texture: keys = rows of (key, label, action, extra) or None."""
    out = []
    for r, row in enumerate(keys):
        for col, key in enumerate(row):
            if key is None: continue
            k, label, action, extra = key
            params = dict(style); params.setdefault('caption', False); params.update(extra)
            out.append(c(f'{prefix}-{k}', params.pop('kind', 'pushButton'), label, action, x=x0 + col * (cw + gap), y=y0 + r * (ch + gap), w=cw, h=ch, **params))
    return out

# ---------------------------------------------------------------- per-car definitions
def peugeot_208(m):
    vid = 'peugeot-208-rally4'; W, H = 1600, 900
    yellow, red = '#ffcf1f', '#ff2a2a'
    dash = gauges.peugeot_208()  # rebuilt from WB_GaugePeugeot208Rally4
    pid = vid + '-buttonbox-040'; c = m.control
    yl = '#ffcf1f'
    # Layout traced from the game's own switch-panel texture (Peugeot208/Textures/T_IntDetails_B).
    k = 1000 / 877
    def C(x0, y0, x1, y1): return dict(x=round(40 + x0 * k), y=round(80 + y0 * k), w=round((x1 - x0) * k), h=round((y1 - y0) * k) + 42)
    o = dict(material='outline', ledColor=yl, sound='latch', ring=False)
    e = [m.background_element(pid, W, H),
        c('p208-main', 'rotarySwitch', 'Főkapcsoló OFF/ON', 'electricalMaster', **C(160, 40, 290, 150), minusAction='electricalMaster', positions=2, states=['OFF', 'ON'], color='#e0262b', material='alu'),
        c('p208-power', 'pushButton', 'Power (gyújtás)', 'ignition', **C(175, 180, 272, 270), icon='power', color='#e0262b', **o),
        c('p208-start', 'pushButton', 'START (tartsd)', 'starter', **C(175, 300, 272, 390), hold=True, engraving='START', color='#e0262b', **dict(o, sound='starter')),
        c('p208-road', 'cycleButton', 'Road / Stage térkép', 'engineMapUp', **C(315, 95, 412, 210), engraving='ROAD\nSTAGE', color='#e8e8e8', leds=2, states=['ROAD', 'STAGE'], **o),
        c('p208-surface', 'pushButton', 'Tarmac / Gravel (nincs játékakció)', '', **C(315, 260, 412, 375), engraving='TARMAC\nGRAVEL', color='#e6dc2a', leds=2, **o),
        c('p208-launch', 'pushButton', 'Launch (nincs játékakció)', '', **C(465, 95, 565, 190), engraving='LAUNCH', color='#6bc23a', **o),
        c('p208-map', 'cycleButton', 'Map 1-2-3', 'engineMapUp', **C(465, 265, 565, 375), engraving='MAP', color='#6bc23a', leds=3, states=['1', '2', '3'], **o),
        c('p208-horn', 'pushButton', 'Kürt (nincs játékakció)', '', **C(610, 55, 705, 140), icon='horn', color='#f08a1c', **o),
        c('p208-hazard', 'pushButton', 'Warning', 'hazards', **C(610, 175, 705, 270), icon='hazard', color='#f08a1c', **o),
        c('p208-demist', 'pushButton', 'Demister', 'demist', **C(610, 295, 705, 385), icon='demist', color='#2f6bff', **o),
        c('p208-win-l', 'pushButton', 'Ablak bal (nincs játékakció)', '', **C(30, 130, 115, 340), engraving='FEL\nLE', color='#e8e8e8', leds=0, **o),
        c('p208-win-r', 'pushButton', 'Ablak jobb (nincs játékakció)', '', **C(750, 130, 835, 340), engraving='FEL\nLE', color='#e8e8e8', leds=0, **o),
    ]
    rubber = dict(material='rubber', ring=True)
    gx, gy, gw, gh = [1090, 1240, 1390], [96, 330, 564], 140, 214
    e += [
        c('p208-lights', 'cycleButton', 'Világítás · léptetés', 'lights', x=gx[0], y=gy[0], w=gw, h=gh, icon='light', color='#e8e8e8', **o),
        c('p208-high', 'pushButton', 'Távfény', 'highBeam', x=gx[1], y=gy[0], w=gw, h=gh, icon='highBeam', color='#2f6bff', **dict(o, ledColor='#3c8cff')),
        c('p208-wiper', 'cycleButton', 'Ablaktörlő (jobb kar)', 'wiper', x=gx[2], y=gy[0], w=gw, h=gh, states=['KI', 'INT', 'LASSÚ', 'GYORS'], icon='wiper', color='#e8e8e8', **o),
        c('p208-ind-l', 'pushButton', 'Index bal', 'indicatorLeft', x=gx[0], y=gy[1], w=gw, h=gh, icon='left', color='#6bc23a', **dict(o, ledColor='#3cff6a')),
        c('p208-ind-r', 'pushButton', 'Index jobb', 'indicatorRight', x=gx[1], y=gy[1], w=gw, h=gh, icon='right', color='#6bc23a', **dict(o, ledColor='#3cff6a')),
        c('p208-fire', 'guarded', 'Tűzoltó', 'fireExtinguisher', x=gx[2], y=gy[1], w=gw, h=gh, engraving='FIRE', coverColor='#d0202a', ledColor='#ff3030'),
        c('p208-page', 'pushButton', 'Kijelzőoldal', 'displayNext', x=gx[0], y=gy[2], w=gw, h=gh, engraving='PAGE', color='#e8e8e8', **o),
        c('p208-respawn', 'pushButton', 'Visszahelyezés', 'respawn', x=gx[1], y=gy[2], w=gw, h=gh, engraving='RESET', color='#e0262b', **o),
        c('p208-hb', 'pushButton', 'Kézifék (tartsd)', 'handbrake', x=gx[2], y=gy[2], w=gw, h=gh, hold=True, engraving='HB', color='#262626', ledColor='#ff3030', sound='latch', **rubber),
        m.legend(pid, 48, 836, 960)]
    panel = m.panel_layout(pid, 'Peugeot 208 Rally4 · Button Box 0.4.0', vid, W, H, e,
        m.panel_background(W, H, face='matte', face_tint=(40, 42, 46), plates=[(28, 66, 1024, 560, 'black'), (1070, 66, 504, 744, 'matte')],
            headings=[(48, 662, 'KAPCSOLÓPANEL (játékbeli textúra alapján)'), (1090, 62, 'KAROK · KIEGÉSZÍTŐK')], title=''), ['ignition'])
    return dict(id=vid, name='Peugeot 208 Rally4', modelYear=2020, category='RALLY4', color='#ffcf1f', dashboard=dash, panel=panel,
        aliases=['Peugeot208Rally4', 'Peugeot 208 Rally4', 'peugeot_208_rally4'],
        references=[{'url': 'https://www.manualslib.com/manual/2872833/Peugeot-208-Rally-4-2021.html', 'scope': 'Gyári User Guide: váltásjelző LED-ek, kék riasztó-LED, 10 kijelzőoldal, MAIN/POWER/START, ROAD/STAGE, WARNING, LIGHTS, DEMISTER, FANS, jobb oldali ablaktörlőkar.', 'status': 'primary_manufacturer_document'}],
        limitations=['A TARMAC/GRAVEL, LAUNCH, KLAXON és ablakemelő gombnak nincs játékbeli bemenete: a panelen szerepelnek, de parancsot nem küldenek.', 'Az ACR-adapter jelenleg csak sebességet, fordulatszámot, fokozatot, pedálokat, G-erőt, fordulatszám-limitet és autóazonosítót ad; a többi kijelzőmező (Map, hőmérsékletek, trip, kézifék, világítás) élesben „—”.'])

def hyundai_i20(m):
    vid = 'hyundai-i20-n-rally2'; W, H = 1600, 900
    orange, blue = '#ff7a1a', '#3aa0ff'
    dash = gauges.hyundai_i20()  # rebuilt from WB_GaugeHyundaiI20NRally2
    pid = vid + '-buttonbox-040'; c = m.control
    # Traced from HyundaiI20/Textures/T_IntDetails_B: dark 3 x 5 key matrix next to the wheel.
    key = dict(material='touch', color='#26292e', ledColor=orange, sound='plastic', ring=False)
    N = ''
    e = [m.background_element(pid, W, H)] + grid(c, 'i20', 3, 5, 292, 82, 168, 144, 6, [
        [('ign', 'IGN', 'ignition', dict(engraving='IGN')), ('haz', 'Vészvillogó', 'hazards', dict(icon='hazard')), ('pfuel', 'Pump Fuel (nincs játékakció)', N, dict(engraving='PUMP\nFUEL'))],
        [('freset', 'Fuel reset (nincs játékakció)', N, dict(engraving='FUEL\nRESET')), ('fan', 'Ventilátor', 'fan', dict(icon='fan')), ('demist', 'Szélvédőfűtés', 'demist', dict(icon='demist'))],
        [('trip', 'Trip / kijelzőoldal', 'displayNext', dict(engraving='Trip')), ('fanrdif', 'Fan Rdif (nincs játékakció)', N, dict(engraving='FAN\nRDIF')), ('pwat', 'Pump Wat (nincs játékakció)', N, dict(engraving='PUMP\nWAT'))],
        [('fog', 'Ködlámpa', 'fogLights', dict(icon='fog')), ('popoff', 'Reset popoff (nincs játékakció)', N, dict(engraving='RESET\nPOPOFF')), ('fanwat', 'Fan Wat (nincs játékakció)', N, dict(engraving='FAN\nWAT'))],
        [('pdu', 'PDU reset (nincs játékakció)', N, dict(engraving='PDU\nRESET')), None, ('respawn', 'Visszahelyezés', 'respawn', dict(icon='right', engraving='RESET'))],
    ], key)
    rubber = dict(material='rubber', ring=True)
    e += strip(c, 'i20', [
        ('start', 'pushButton', 'Start (kormány)', 'starter', dict(hold=True, engraving='START', color='#c8102e', ledColor='#ff4040', sound='starter', material='rubber', ring=True)),
        ('lights', 'cycleButton', 'Világítás · léptetés', 'lights', dict(icon='light')),
        ('high', 'pushButton', 'Távfény', 'highBeam', dict(icon='highBeam', ledColor='#3c8cff')),
        ('ind-l', 'pushButton', 'Index bal', 'indicatorLeft', dict(icon='left', ledColor='#3cff6a')),
        ('ind-r', 'pushButton', 'Index jobb', 'indicatorRight', dict(icon='right', ledColor='#3cff6a')),
        ('wiper', 'cycleButton', 'Ablaktörlő · léptetés', 'wiper', dict(states=['KI', 'INT', 'LASSÚ', 'GYORS'], icon='wiper')),
        ('fire', 'guarded', 'Tűzoltó', 'fireExtinguisher', dict(engraving='FIRE', coverColor='#d0202a', ledColor='#ff3030')),
        ('map', 'pushButton', 'Motortérkép +', 'engineMapUp', dict(engraving='MAP +')),
        ('hb', 'pushButton', 'Kézifék (tartsd)', 'handbrake', dict(hold=True, engraving='HB', color='#262626', ledColor='#ff3030', sound='latch', material='rubber', ring=True)),
    ], key) + [m.legend(pid, 48, 836, 960)]
    panel = m.panel_layout(pid, 'Hyundai i20 N Rally2 · Button Box 0.4.0', vid, W, H, e,
        m.panel_background(W, H, face='carbon', face_tint=(26, 32, 44), plates=[(276, 66, 548, 770, 'black'), (1070, 66, 504, 744, 'matte')],
            headings=[(48, 62, 'KAPCSOLÓMÁTRIX'), (1090, 62, 'KORMÁNY · KAROK')], title=''), ['ignition'])
    return dict(id=vid, name='Hyundai i20 N Rally2', modelYear=2021, category='RALLY2', color='#ff7a1a', dashboard=dash, panel=panel,
        aliases=['HyundaiI20NRally2', 'Hyundai i20 N Rally2', 'hyundai_i20_n_rally2'],
        references=[{'url': 'https://motorsport.hyundai.com/Corporate%20Site/Car%20Spec/i20%20N%20Rally2/Hyundai%20Rally2%20Tech%20Specs.pdf', 'scope': 'Gyári műszaki adatlap; a cockpit-kiosztás nem gyárilag dokumentált.', 'status': 'primary_manufacturer_document'},
                    {'url': 'https://racemarket.net/rally/rally-cars-for-sale/r5/hyundai-i20-n-rally2-step-2-i7004', 'scope': 'Hirdetési utastérfotók elrendezési referenciaként.', 'status': 'photo_reference'}],
        limitations=['A kapcsolómátrix a játékbeli T_IntDetails_B textúrát, a műszerfal a WB_GaugeHyundaiI20NRally2 widgetet követi; a váltásjelző overlayek küszöbe feltételezés (a Blueprint-logika nem exportálható).'])

def polo_r5(m):
    vid = 'vw-polo-gti-r5'; W, H = 1600, 900
    red = '#e3001b'
    dash = gauges.polo_r5()  # rebuilt from WB_GaugeVolkswagenPoloGTIR5
    pid = vid + '-buttonbox-040'; c = m.control
    # Traced from VWPoloGTI/Textures/T_IntDetails_B: 3 x 5 matrix of coloured round rubber caps + SOS.
    cap = dict(material='rubber', ring=False, sound='plastic', ledColor='#ffffff')
    dk, rd, bl, og, gn = '#2b2d30', '#d23a3a', '#3f7fd8', '#e08a4a', '#2f9e5a'
    N = ''
    e = [m.background_element(pid, W, H)] + grid(c, 'polo', 3, 5, 336, 84, 150, 146, 6, [
        [('horn', 'Kürt (nincs játékakció)', N, dict(engraving='HORN', color=dk)), ('start', 'START (tartsd)', 'starter', dict(engraving='START', color=rd, hold=True, sound='starter')), ('ign', 'IGN', 'ignition', dict(engraving='IGN', color=rd))],
        [('fog', 'Ködlámpa', 'fogLights', dict(engraving='FOG', color=bl)), ('wiper', 'Ablaktörlő · léptetés', 'wiper', dict(kind='cycleButton', states=['KI', 'INT', 'LASSÚ', 'GYORS'], engraving='WIPE', color=bl)), ('fan', 'Ventilátor', 'fan', dict(engraving='FAN', color=bl))],
        [('dim', 'Dim display (nincs játékakció)', N, dict(engraving='DIM\nDISPL', color=dk)), ('haz', 'Vészvillogó', 'hazards', dict(engraving='HAZ', color=rd)), ('maplight', 'Map light (nincs játékakció)', N, dict(engraving='MAP\nLIGHT', color=dk))],
        [('popoff', 'Reset popoff (nincs játékakció)', N, dict(engraving='RESET\nPOPOFF', color=og)), ('err', 'Reset err / nyugtázás', 'acknowledge', dict(engraving='RESET\nERR', color=og)), ('trip', 'Reset trip (nincs játékakció)', N, dict(engraving='RESET\nTRIP', color=gn))],
        [('setup', 'Setup page', 'displayNext', dict(engraving='SETUP\nPAGE', color=dk)), None, ('hydr', 'Hydr bleed (nincs játékakció)', N, dict(engraving='HYDR\nBLEED', color=dk))],
    ], cap)
    e.append(c('polo-sos', 'pushButton', 'SOS (nincs játékakció)', N, x=60, y=180, w=200, h=260, engraving='SOS', color='#c62828', material='rubber', ring=True))
    key = dict(material='touch', color='#26292e', ledColor='#ffffff', sound='plastic', ring=False)
    e += strip(c, 'polo', [
        ('lights', 'cycleButton', 'Világítás · léptetés', 'lights', dict(icon='light')),
        ('high', 'pushButton', 'Távfény', 'highBeam', dict(icon='highBeam', ledColor='#3c8cff')),
        ('map', 'rotarySwitch', 'Motortérkép', 'engineMapUp', dict(minusAction='engineMapDown', positions=5, states=['1', '2', '3', '4', '5'], color=red, material='alu')),
        ('ind-l', 'pushButton', 'Index bal', 'indicatorLeft', dict(icon='left', ledColor='#3cff6a')),
        ('ind-r', 'pushButton', 'Index jobb', 'indicatorRight', dict(icon='right', ledColor='#3cff6a')),
        ('fire', 'guarded', 'Tűzoltó', 'fireExtinguisher', dict(engraving='FIRE', coverColor='#d0202a', ledColor='#ff3030')),
        ('demist', 'pushButton', 'Szélvédőfűtés', 'demist', dict(icon='demist')),
        ('respawn', 'pushButton', 'Visszahelyezés', 'respawn', dict(engraving='RESET')),
        ('hb', 'pushButton', 'Kézifék (tartsd)', 'handbrake', dict(hold=True, engraving='HB', color='#262626', ledColor='#ff3030', sound='latch', material='rubber', ring=True)),
    ], key) + [m.legend(pid, 48, 836, 960)]
    panel = m.panel_layout(pid, 'Volkswagen Polo GTI R5 · Button Box 0.4.0', vid, W, H, e,
        m.panel_background(W, H, face='matte', face_tint=(150, 152, 156), frame=(150, 150, 152), plates=[(40, 150, 240, 320, 'black'), (300, 66, 530, 770, 'matte'), (1070, 66, 504, 744, 'matte')],
            headings=[(48, 62, 'SOS · KAPCSOLÓMÁTRIX'), (1090, 62, 'KORMÁNY · KAROK')], title=''), ['ignition'])
    return dict(id=vid, name='Volkswagen Polo GTI R5', modelYear=2018, category='R5', color='#e3001b', dashboard=dash, panel=panel,
        aliases=['VWPoloGTIR5', 'VolkswagenPoloGTIR5', 'VW Polo GTI R5', 'vw_polo_gti_r5'],
        references=[{'url': 'https://www.volkswagen-newsroom.com/en/the-new-polo-gti-driving-presentation-2512/the-new-polo-gti-r5-gti-goes-rallying-2567', 'scope': 'Gyári bemutató; a játék 2018-as változatot modellez (505 Games 0.6 changelog).', 'status': 'primary_manufacturer'}],
        limitations=['A két képernyő a WB_GaugeVolkswagenPoloGTIR5 widget elrendezését követi; az ívelt RPM-sávok küszöbe és a dobozok futásidejű színei feltételezések.', 'A szakaszhossz (Trip [total]) mezőt az ACR-adapter nem adja.'])

def peugeot_206(m):
    vid = 'peugeot-206-wrc'; W, H = 1600, 900
    ink = '#10200c'
    dash = gauges.peugeot_206()  # rebuilt from WB_GaugePeugeot206
    pid = vid + '-buttonbox-040'; c = m.control
    # Traced from Peugeot206/Textures/T_IntDetails_B: two rows of labelled keys (French), lighting
    # switch row (CligG / Veil / Code / Broul / Phare / CligD) and a 1-4 rotary selector.
    lab = dict(material='label', color='#b9c4a6', ledColor='#ffb020', sound='latch', ring=False)
    N = ''
    e = [m.background_element(pid, W, H)] + grid(c, 'p206', 7, 2, 40, 96, 136, 96, 8, [
        [('gmv', 'Gmv · ventilátor', 'fan', dict(engraving='Gmv')), ('ab', 'AB (nincs játékakció)', N, dict(engraving='AB')), ('contact', 'CONTACT · gyújtás', 'ignition', dict(engraving='CONTACT')),
         ('clim', 'CLIM (nincs játékakció)', N, dict(engraving='CLIM')), ('ppeau', 'PPeEau (nincs játékakció)', N, dict(engraving='PPeEau')), ('detresse', 'DETRESSE · vészvillogó', 'hazards', dict(engraving='DETRESSE')), ('ppess2', 'PPeEss2 (nincs játékakció)', N, dict(engraving='PPeEss2'))],
        [('desemb', 'DESEMB · páramentesítő', 'demist', dict(engraving='DESEMB')), ('ppess1', 'PpeEss1 (nincs játékakció)', N, dict(engraving='PpeEss1')), ('lp2', 'LP2 (nincs játékakció)', N, dict(engraving='LP2')),
         ('extinct', 'Extinct · tűzoltó', 'fireExtinguisher', dict(engraving='Extinct')), ('lp1', 'LP1 (nincs játékakció)', N, dict(engraving='LP1')), ('dem', 'DEM · indító (tartsd)', 'starter', dict(engraving='DEM', hold=True, sound='starter')), ('rear', 'REAR (nincs játékakció)', N, dict(engraving='REAR', color='#2f4f9a'))],
    ], lab)
    sw = dict(material='touch', color='#2a2c30', ledColor='#ffb020', sound='metalOn', ring=False)
    e += grid(c, 'p206l', 6, 1, 40, 300, 152, 130, 12, [[
        ('cligg', 'CligG · index bal', 'indicatorLeft', dict(engraving='CligG', ledColor='#3cff6a')), ('veil', 'Veil (nincs játékakció)', N, dict(engraving='Veil')),
        ('code', 'Code · világítás léptetés', 'lights', dict(kind='cycleButton', engraving='Code')), ('broul', 'Broul · ködlámpa', 'fogLights', dict(engraving='Broul')),
        ('phare', 'Phare · távfény', 'highBeam', dict(engraving='Phare', ledColor='#3c8cff')), ('cligd', 'CligD · index jobb', 'indicatorRight', dict(engraving='CligD', ledColor='#3cff6a'))]], sw)
    e.append(c('p206-map', 'rotarySwitch', 'Választó 1-4 (motortérkép)', 'engineMapUp', x=760, y=470, w=260, h=210, minusAction='engineMapDown', positions=4, states=['1', '2', '3', '4'], color='#ffb020', material='alu'))
    e += strip(c, 'p206', [
        ('wiper', 'cycleButton', 'Essuie-glace · léptetés', 'wiper', dict(states=['KI', 'INT', 'LASSÚ', 'GYORS'], engraving='E-G')),
        ('page', 'pushButton', 'Kijelzőoldal', 'displayNext', dict(engraving='PAGE')),
        ('respawn', 'pushButton', 'Visszahelyezés', 'respawn', dict(engraving='RESET')),
        ('hb', 'pushButton', 'Frein à main (tartsd)', 'handbrake', dict(hold=True, engraving='HB', color='#262626', ledColor='#ff3030', sound='latch', material='rubber', ring=True)),
    ], sw) + [m.legend(pid, 360, 836, 700)]
    panel = m.panel_layout(pid, 'Peugeot 206 WRC (1999) · Button Box 0.4.0', vid, W, H, e,
        m.panel_background(W, H, face='matte', face_tint=(36, 37, 40), frame=(178, 182, 188), plates=[(28, 80, 1024, 200, 'matte'), (28, 292, 1024, 150, 'black'), (1070, 66, 504, 520, 'matte')],
            headings=[(48, 62, 'INTERRUPTEURS'), (48, 460, 'ÉCLAIRAGE'), (1090, 62, 'DIVERS')], title=''), ['ignition'])
    return dict(id=vid, name='Peugeot 206 WRC (1999)', modelYear=1999, category='WRC', color='#c9d6a8', dashboard=dash, panel=panel,
        aliases=['Peugeot206WRC', 'Peugeot 206 WRC', 'Peugeot206', 'peugeot_206_wrc'],
        references=[{'url': 'https://en.wikipedia.org/wiki/Peugeot_206_WRC', 'scope': 'Típustörténet; a játék 1999-es autót modellez.', 'status': 'secondary'},
                    {'url': 'https://www.largus.fr/actualite-automobile/une-peugeot-206-wrc-pilotee-par-marcus-gronholm-en-vente-10316395.html', 'scope': 'Utastérfotó (2001-es C31): a széria 206 műszerfal-alapformája megmaradt.', 'status': 'photo_reference'}],
        limitations=['Az LCD a WB_GaugePeugeot206 widget elrendezését követi; a 7-szegmenses játékbetűtípus helyett szabad betűtípus szerepel.', 'A kapcsolófeliratok a játékbeli T_IntDetails_B textúráról származnak.'])

def subaru_555(m):
    vid = 'subaru-impreza-555-gra'; W, H = 1600, 900
    analog = [
        el('s555-tach', 'analog', 'rpm', 520, 60, 560, 560, 'RPM', max=8000, style='classic', redline=7000, caption='STACK-STÍLUS · RPM ×1000', color='#ff3a1a', face='#0a0a0b', border=False),
        el('s555-water', 'analog', 'waterTemp', 150, 220, 300, 300, 'VÍZ', max=140, style='classic', redline=110, divisor=20, caption='°C ×20', color='#ff3a1a', face='#0a0a0b', border=False),
        el('s555-shift', 'leds', 'rpm', 700, 640, 200, 60, 'SHIFT', count=1, max=7000, palette=['#ff2a1a'], shape='circle', border=False),
        el('s555-gear', 'gear', 'gear', 1160, 200, 300, 330, '', fontSize=240, color='#f2f2f2', border=False, font='sans', fontWeight=700),
        el('s555-trip', 'number', 'stageDistance', 150, 660, 420, 170, 'TRIP (Coralba-stílus)', fontSize=70, color='#ff9a3a', font='factory', decimals=2, border=False, background='#120804'),
        el('s555-speed', 'number', 'speed', 1060, 660, 420, 170, 'km/h', fontSize=80, color='#f2f2f2', border=False),
    ]
    analog = [e for e in analog if e['id'] != 's555-trip'] + [
        gauges.readout('s555-clock', 'sessionClock', 150, 660, 200, 170, '#D60000', 70, font='monospace', background='#2D0000'),
        gauges.readout('s555-dist', 'stageDistance', 360, 660, 260, 170, '#D60000', 70, font='monospace', scale=.001, decimals=3, background='#2D0000')]
    dash = gauges.subaru_555(analog, housing(W, H, tone=(14, 14, 15), screen=None, cutouts=[(800, 340, 285), (300, 370, 155)], radius=60))
    pid = vid + '-buttonbox-040'; c = m.control
    # Traced from SubaruImprezaS3/Textures/T_IntDetails_B: label strips over a row of toggles
    # (WASH : WIPE, HORN, BRAKE BLOWER, HEATER, Max Run), red hazard switch, Coralba tripmaster keys.
    N = ''
    def plate(i, text, x, y, w, bg, fg):
        return {'id': f's555-plate-{i}', 'kind': 'text', 'field': '', 'label': text, 'x': x, 'y': y, 'w': w, 'h': 54, 'z': 4,
                'border': False, 'background': bg, 'foreground': fg, 'fontSize': 30, 'font': 'sans', 'fontWeight': 600, 'letterSpacing': 1}
    tog = dict(material='alu', ledColor='#ffb020', caption=False)
    xs = [40, 210, 380, 550, 720]
    e = [m.background_element(pid, W, H),
        plate('wash', 'WASH : WIPE', 40, 96, 330, '#f2c230', '#1a1a1a'), plate('horn', 'HORN', 380, 96, 160, '#f2c230', '#1a1a1a'),
        plate('blower', 'BRAKE BLOWER', 550, 96, 330, '#1c1c1c', '#f0f0f0'), plate('heater', 'HEATER', 40, 420, 330, '#1c1c1c', '#f0f0f0'),
        plate('maxrun', 'Max Run', 380, 420, 330, '#2b2b2b', '#f0f0f0'),
        c('s555-wash', 'pushButton', 'Wash (nincs játékakció)', N, x=xs[0], y=160, w=150, h=220, engraving='WASH', color='#2b2d30', material='rubber', ring=False, caption=False),
        c('s555-wipe', 'cycleButton', 'Wipe · ablaktörlő léptetés', 'wiper', x=xs[1], y=160, w=150, h=220, states=['KI', 'INT', 'LASSÚ', 'GYORS'], engraving='WIPE  OFF', **tog),
        c('s555-horn', 'pushButton', 'Horn (nincs játékakció)', N, x=xs[2], y=160, w=150, h=220, engraving='HORN', color='#2b2d30', material='rubber', ring=False, caption=False),
        c('s555-blower-l', 'rocker', 'Brake blower bal (nincs játékakció)', N, x=xs[3], y=160, w=150, h=220, engraving='ON  OFF', **tog),
        c('s555-blower-r', 'rocker', 'Brake blower jobb (nincs játékakció)', N, x=xs[4], y=160, w=150, h=220, engraving='ON  OFF', **tog),
        c('s555-heater', 'rocker', 'Heater · páramentesítő', 'demist', x=xs[0], y=484, w=150, h=220, engraving='ON  OFF', **tog),
        c('s555-maxrun', 'rocker', 'Max Run (nincs játékakció)', N, x=xs[2], y=484, w=150, h=220, engraving='MAX  RUN', **tog),
        c('s555-hazard', 'rocker', 'Vészvillogó', 'hazards', x=xs[3], y=484, w=150, h=220, engraving='HAZ  OFF', ledColor='#ff3030', material='plastic', caption=False),
        c('s555-ign', 'rocker', 'Gyújtás', 'ignition', x=xs[1], y=484, w=150, h=220, field='ignition', engraving='IGN  OFF', **tog),
        c('s555-start', 'pushButton', 'Indító (tartsd)', 'starter', x=xs[4], y=484, w=150, h=220, hold=True, engraving='START', color='#c62828', ledColor='#ff3030', sound='starter', material='rubber', ring=True, caption=False),
    ]
    trip = dict(material='label', color='#d9d9d6', ledColor='#ff9a3a', sound='latch', ring=False)
    keys = [('break', 'BREAK', N), ('speed', 'SPEED', N), ('trip1', 'TRIP1', N), ('trip2', 'TRIP2', 'displayNext'), ('option', 'OPTION', N), ('split', 'SPLIT', N), ('reset', 'RESET', N)]
    e += grid(c, 's555t', 7, 1, 40, 750, 128, 70, 6, [[(k, f'Coralba {t}' + (' (nincs játékakció)' if not a else ' · kijelzőoldal'), a, dict(engraving=t)) for k, t, a in keys]], trip)
    key = dict(material='touch', color='#26292e', ledColor='#ffb020', sound='plastic', ring=False)
    e += strip(c, 's555', [
        ('lights', 'cycleButton', 'Világítás · léptetés', 'lights', dict(icon='light')),
        ('high', 'pushButton', 'Távfény / pótfényszóró', 'highBeam', dict(icon='highBeam', ledColor='#3c8cff')),
        ('fog', 'pushButton', 'Ködlámpa', 'fogLights', dict(icon='fog')),
        ('ind-l', 'pushButton', 'Index bal', 'indicatorLeft', dict(icon='left', ledColor='#3cff6a')),
        ('ind-r', 'pushButton', 'Index jobb', 'indicatorRight', dict(icon='right', ledColor='#3cff6a')),
        ('fire', 'guarded', 'Tűzoltó', 'fireExtinguisher', dict(engraving='FIRE', coverColor='#d0202a', ledColor='#ff3030')),
        ('master', 'guarded', 'Főkapcsoló', 'electricalMaster', dict(engraving='MASTER', coverColor='#d0202a', ledColor='#ff3030')),
        ('respawn', 'pushButton', 'Visszahelyezés', 'respawn', dict(engraving='RESET')),
        ('hb', 'pushButton', 'Kézifék (tartsd)', 'handbrake', dict(hold=True, engraving='HB', color='#262626', ledColor='#ff3030', sound='latch', material='rubber', ring=True)),
    ], key)
    panel = m.panel_layout(pid, 'Subaru Impreza 555 Gr.A (1993) · Button Box 0.4.0', vid, W, H, e,
        m.panel_background(W, H, face='matte', face_tint=(200, 200, 198), frame=(140, 142, 146), plates=[(28, 80, 1024, 640, 'matte'), (28, 736, 1024, 100, 'black'), (1070, 66, 504, 744, 'matte')],
            headings=[(1090, 62, 'KORMÁNY · KIEGÉSZÍTŐK')], title=''), ['ignition'])
    return dict(id=vid, name='Subaru Impreza 555 Group A (1993)', modelYear=1993, category='GROUP A', color='#1f4fa8', dashboard=dash, panel=panel,
        aliases=['SubaruImprezaS3', 'Subaru Impreza S3', 'Subaru Impreza 555', 'subaru_impreza_s3'],
        references=[{'url': 'https://isdc.ie/forum/threads/subaru-impreza-555-group-a-technical-specifications-and-stats-impreza555-com.42273/', 'scope': 'Műszerek: Stack ST400 analóg fordulatszámmérő 0–8000/min, VDO vízhőmérő, Coralba tripmaster, GEMS adatgyűjtő.', 'status': 'secondary_specification'},
                    {'url': 'https://www.carthrottle.com/news/duo-90s-rally-icons-land-assetto-corsa-rally', 'scope': 'A játék az 1993-as Group A specifikációt modellezi.', 'status': 'secondary'}],
        limitations=['A Stack/VDO műszerek stílusa saját rajz, márkajelzés nélkül.', 'Vízhőmérsékletet, napszakot és tripmaster-távolságot az ACR-adapter jelenleg nem ad: „—” jelenik meg. A tripmeter elrendezése a WB_GaugeSubaruImprezaS3 widgetet követi.'])

CARS = [peugeot_208, hyundai_i20, polo_r5, peugeot_206, subaru_555]

def apply(vehicles, m):
    existing = {v['id'] for v in vehicles}
    for build in CARS:
        car = build(m)
        profile = {'id': car['id'], 'name': car['name'], 'modelYear': car['modelYear'], 'category': car['category'], 'color': car['color'],
                   'version': '0.4.0', 'fidelity': 'reference_research', 'fidelityLabel': 'Referenciakutatás alapján · saját grafika',
                   'gameVehicleAliases': car['aliases'], 'references': car['references'], 'knownLimitations': car['limitations'],
                   'dashboard': car['dashboard'], 'panel': car['panel']}
        if car['id'] in existing:
            index = next(i for i, v in enumerate(vehicles) if v['id'] == car['id']); vehicles[index] = profile
        else:
            vehicles.append(profile)
