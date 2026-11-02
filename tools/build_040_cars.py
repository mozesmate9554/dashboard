#!/usr/bin/env python3
"""The five further Assetto Corsa Rally cars of SIM CONTROL STUDIO 0.4.0.

Each car gets its own dashboard and its own mechanical button box. Layouts follow the
research in documentation/VEHICLE_REFERENCE_REPORT.md; artwork is original (generated here).
Functions without a matching game input (e.g. horn, tarmac/gravel selector) are NOT invented.
"""
import base64, io, math
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

# ---------------------------------------------------------------- per-car definitions
def peugeot_208(m):
    vid = 'peugeot-208-rally4'; W, H = 1600, 900
    yellow, red = '#ffcf1f', '#ff2a2a'
    pal = [yellow] * 9 + [red] * 6  # Rally4 guide: yellow ramp, then fixed / flashing red
    road = [
        el('p208-leds', 'leds', 'rpm', 90, 60, 1420, 70, 'RPM', count=15, max=6300, palette=pal, shape='circle', border=False),
        el('p208-gear', 'gear', 'gear', 620, 170, 360, 420, '', fontSize=330, color='#ffffff', border=False, font='sans', fontWeight=700),
        el('p208-speed', 'number', 'speed', 120, 190, 420, 200, 'km/h', fontSize=120, color=yellow, border=False),
        el('p208-rpm', 'number', 'rpm', 1060, 190, 420, 200, 'rpm', fontSize=110, color=yellow, border=False),
        el('p208-water', 'number', 'waterTemp', 120, 430, 300, 150, 'Víz °C', fontSize=64, color='#9fd4ff', warningAbove=115, border=False),
        el('p208-oilT', 'number', 'oilTemp', 1180, 430, 300, 150, 'Olaj °C', fontSize=64, color='#9fd4ff', border=False),
        el('p208-oilP', 'number', 'oilPressure', 120, 620, 300, 150, 'Olajnyomás bar', fontSize=64, color='#9fd4ff', decimals=1, border=False),
        el('p208-map', 'number', 'engineMap', 650, 640, 300, 130, 'Map', fontSize=60, color=yellow, border=False),
        el('p208-alarm', 'indicator', 'faults', 1180, 620, 300, 150, 'Riasztás (kék)', color='#2f7bff', border=False),
        txt('p208-page', '1 · ROAD', 650, 790, 300, 50, 26, '#8a8f96'),
    ]
    stage = [
        el('p208s-leds', 'leds', 'rpm', 90, 60, 1420, 90, 'RPM', count=15, max=6300, palette=pal, shape='circle', border=False),
        el('p208s-gear', 'gear', 'gear', 560, 180, 480, 560, '', fontSize=440, color='#ffffff', border=False, font='sans', fontWeight=700),
        el('p208s-time', 'number', 'stageTime', 100, 300, 420, 180, 'Szakaszidő', fontSize=70, color=yellow, border=False),
        el('p208s-speed', 'number', 'speed', 1080, 300, 420, 180, 'km/h', fontSize=100, color=yellow, border=False),
        txt('p208s-page', '2 · STAGE', 650, 790, 300, 50, 26, '#8a8f96'),
    ]
    dash = dash_layout(m, vid + '-dash-040', 'Peugeot 208 Rally4 · Műszerfal', vid, W, H, [('Road', road), ('Stage', stage)],
        housing(W, H, screen=(60, 40, 1540, 860), screen_color=((10, 10, 12), (2, 2, 3))))
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
        limitations=['A TARMAC/GRAVEL és a KLAXON gombnak nincs játékbeli bemenete, ezért nem szerepel.', 'Víz/olaj hő- és nyomásértéket az ACR-adapter nem ad: „—” jelenik meg.'])

def hyundai_i20(m):
    vid = 'hyundai-i20-n-rally2'; W, H = 1600, 900
    orange, blue = '#ff7a1a', '#3aa0ff'
    main = [
        el('i20-leds', 'leds', 'rpm', 160, 50, 1280, 60, 'RPM', count=12, max=7000, palette=['#3cff6a'] * 4 + ['#ffd23c'] * 4 + ['#ff2a2a'] * 4, border=False),
        el('i20-gear', 'gear', 'gear', 600, 150, 400, 480, '', fontSize=380, color='#ffffff', border=False, font='sans', fontWeight=700, background='#0b1a2c'),
        el('i20-speed', 'number', 'speed', 120, 160, 440, 220, 'km/h', fontSize=130, color=orange, border=False),
        el('i20-rpm', 'number', 'rpm', 1040, 160, 440, 220, 'rpm', fontSize=110, color=blue, border=False),
        el('i20-throttle', 'pedals', '', 120, 420, 440, 330, 'Pedálok', border=False),
        el('i20-g', 'gForce', '', 1040, 410, 440, 340, 'G', color=orange, border=False),
        el('i20-time', 'number', 'stageTime', 600, 660, 400, 110, 'Szakaszidő', fontSize=56, color='#ffffff', border=False),
    ]
    dash = dash_layout(m, vid + '-dash-040', 'Hyundai i20 N Rally2 · Műszerfal', vid, W, H, [('Verseny', main)],
        housing(W, H, screen=(60, 30, 1540, 870), screen_color=((8, 16, 30), (2, 4, 9))))
    pid = vid + '-buttonbox-040'; c = m.control
    e = [m.background_element(pid, W, H),
        c('i20-master', 'guarded', 'Főkapcsoló', 'electricalMaster', 48, 92, 200, 228, engraving='MASTER', coverColor='#d0202a', ledColor=orange),
        c('i20-ign', 'rocker', 'Gyújtás', 'ignition', 284, 92, 200, 228, field='ignition', engraving='IGN  OFF', ledColor=orange),
        c('i20-start', 'pushButton', 'Indító (tartsd)', 'starter', 520, 92, 200, 228, hold=True, engraving='START', color='#c8102e', ledColor='#ff4040', sound='starter', **RUBBER),
        c('i20-fire', 'guarded', 'Tűzoltó', 'fireExtinguisher', 756, 92, 200, 228, engraving='FIRE', coverColor='#d0202a', ledColor='#ff3030'),
        c('i20-lights', 'cycleButton', 'Világítás · léptetés', 'lights', 48, 340, 200, 228, engraving='LIGHT', color='#16273d', ledColor='#b4e2ff', sound='plastic', **GLASS),
        c('i20-high', 'pushButton', 'Távfény', 'highBeam', 284, 340, 200, 228, engraving='HIGH', color='#16273d', ledColor='#3c8cff', sound='plastic', **GLASS),
        c('i20-haz', 'pushButton', 'Vészvillogó', 'hazards', 520, 340, 200, 228, engraving='HAZ', color='#7a1414', ledColor='#ff7a1a', sound='plastic', **GLASS),
        c('i20-wiper', 'cycleButton', 'Ablaktörlő · léptetés', 'wiper', 756, 340, 200, 228, states=['KI', 'INT', 'LASSÚ', 'GYORS'], engraving='WIPE', color='#16273d', ledColor='#5cc8ff', sound='plastic', **GLASS),
        c('i20-ind-l', 'pushButton', 'Index bal', 'indicatorLeft', 48, 588, 200, 228, engraving='«', color='#16273d', ledColor='#3cff6a', sound='plastic', **GLASS),
        c('i20-ind-r', 'pushButton', 'Index jobb', 'indicatorRight', 284, 588, 200, 228, engraving='»', color='#16273d', ledColor='#3cff6a', sound='plastic', **GLASS),
        c('i20-demist', 'pushButton', 'Szélvédőfűtés', 'demist', 520, 588, 200, 228, engraving='DEMIST', color='#16273d', ledColor=orange, sound='plastic', **GLASS),
        c('i20-fan', 'pushButton', 'Ventilátor', 'fan', 756, 588, 200, 228, engraving='FAN', color='#16273d', ledColor=orange, sound='plastic', **GLASS),
        c('i20-map', 'rotarySwitch', 'Motortérkép', 'engineMapUp', 1040, 92, 250, 300, minusAction='engineMapDown', positions=5, states=['1', '2', '3', '4', '5'], color=orange, material='alu'),
        c('i20-page', 'rotarySwitch', 'Kijelzőoldal', 'displayNext', 1310, 92, 250, 300, minusAction='displayPrevious', positions=4, states=['1', '2', '3', '4'], color=blue, material='alu'),
        c('i20-hb', 'pushButton', 'Kézifék (tartsd)', 'handbrake', 1070, 440, 230, 380, hold=True, engraving='HB', color='#262626', ledColor='#ff3030', sound='latch', **RUBBER),
        c('i20-respawn', 'pushButton', 'Visszahelyezés', 'respawn', 1330, 440, 230, 380, engraving='RESET', color='#3a1010', ledColor='#ff4040', sound='plastic', **GLASS),
        m.legend(pid, 48, 836, 960)]
    panel = m.panel_layout(pid, 'Hyundai i20 N Rally2 · Button Box 0.4.0', vid, W, H, e,
        m.panel_background(W, H, face='carbon', face_tint=(26, 32, 44), plates=[(1018, 70, 556, 344, 'matte'), (1018, 424, 556, 418, 'matte')],
            headings=[(48, 62, 'POWER'), (48, 310, 'LIGHTS · VISION'), (48, 558, 'SIGNALS · CLIMATE')], title='RALLY2 · SWITCH PANEL'), ['ignition'])
    return dict(id=vid, name='Hyundai i20 N Rally2', modelYear=2021, category='RALLY2', color='#ff7a1a', dashboard=dash, panel=panel,
        aliases=['HyundaiI20NRally2', 'Hyundai i20 N Rally2', 'hyundai_i20_n_rally2'],
        references=[{'url': 'https://motorsport.hyundai.com/Corporate%20Site/Car%20Spec/i20%20N%20Rally2/Hyundai%20Rally2%20Tech%20Specs.pdf', 'scope': 'Gyári műszaki adatlap; a cockpit-kiosztás nem gyárilag dokumentált.', 'status': 'primary_manufacturer_document'},
                    {'url': 'https://racemarket.net/rally/rally-cars-for-sale/r5/hyundai-i20-n-rally2-step-2-i7004', 'scope': 'Hirdetési utastérfotók elrendezési referenciaként.', 'status': 'photo_reference'}],
        limitations=['A konzol gombkiosztása referencián alapuló saját elrendezés; a játékbeli WB_GaugeHyundaiI20NRally2 képernyőképével még pontosítandó.'])

def polo_r5(m):
    vid = 'vw-polo-gti-r5'; W, H = 1600, 900
    red = '#e3001b'
    main = [
        el('polo-rpm', 'analog', 'rpm', 500, 40, 600, 600, 'RPM', max=8000, color=red, border=False),
        el('polo-gear', 'gear', 'gear', 690, 640, 220, 220, '', fontSize=180, color='#ffffff', border=False, font='sans', fontWeight=700),
        el('polo-leds', 'leds', 'rpm', 120, 60, 320, 40, 'RPM', count=8, max=7600, palette=['#ffffff'] * 5 + [red] * 3, border=False),
        el('polo-leds2', 'leds', 'rpm', 1160, 60, 320, 40, 'RPM', count=8, max=7600, palette=['#ffffff'] * 5 + [red] * 3, border=False),
        el('polo-speed', 'number', 'speed', 120, 170, 340, 200, 'km/h', fontSize=110, color='#ffffff', border=False),
        el('polo-time', 'number', 'stageTime', 1140, 170, 340, 200, 'Szakaszidő', fontSize=60, color='#ffffff', border=False),
        el('polo-water', 'number', 'waterTemp', 120, 450, 340, 160, 'Víz °C', fontSize=60, color='#d0d4d8', border=False),
        el('polo-map', 'number', 'engineMap', 1140, 450, 340, 160, 'Map', fontSize=60, color=red, border=False),
        el('polo-pedals', 'pedals', '', 120, 650, 340, 200, 'Pedálok', border=False),
        el('polo-g', 'gForce', '', 1240, 650, 200, 200, 'G', color=red, border=False),
    ]
    dash = dash_layout(m, vid + '-dash-040', 'Volkswagen Polo GTI R5 · Műszerfal', vid, W, H, [('Verseny', main)],
        housing(W, H, screen=(60, 30, 1540, 870), screen_color=((14, 14, 16), (3, 3, 4))))
    pid = vid + '-buttonbox-040'; c = m.control
    e = [m.background_element(pid, W, H),
        c('polo-master', 'guarded', 'Főkapcsoló', 'electricalMaster', 48, 92, 200, 228, engraving='MAIN', coverColor='#d0202a', ledColor='#ffffff'),
        c('polo-ign', 'rocker', 'Gyújtás', 'ignition', 284, 92, 200, 228, field='ignition', engraving='IGN  OFF', ledColor=red),
        c('polo-start', 'pushButton', 'Indító (tartsd)', 'starter', 520, 92, 200, 228, hold=True, engraving='START', color=red, ledColor='#ffffff', sound='starter', **RUBBER),
        c('polo-fire', 'guarded', 'Tűzoltó', 'fireExtinguisher', 756, 92, 200, 228, engraving='FIRE', coverColor='#d0202a', ledColor='#ff3030'),
        c('polo-lights', 'cycleButton', 'Világítás · léptetés', 'lights', 48, 340, 200, 228, engraving='LIGHT', color='#202020', ledColor='#ffffff', sound='plastic', **RUBBER),
        c('polo-high', 'pushButton', 'Távfény', 'highBeam', 284, 340, 200, 228, engraving='HIGH', color='#202020', ledColor='#3c8cff', sound='plastic', **RUBBER),
        c('polo-haz', 'pushButton', 'Vészvillogó', 'hazards', 520, 340, 200, 228, engraving='HAZ', color='#202020', ledColor='#ff7a1a', sound='plastic', **RUBBER),
        c('polo-wiper', 'cycleButton', 'Ablaktörlő · léptetés', 'wiper', 756, 340, 200, 228, states=['KI', 'INT', 'LASSÚ', 'GYORS'], engraving='WIPE', color='#202020', ledColor='#ffffff', sound='plastic', **RUBBER),
        c('polo-ind-l', 'pushButton', 'Index bal', 'indicatorLeft', 48, 588, 200, 228, engraving='«', color='#202020', ledColor='#3cff6a', sound='plastic', **RUBBER),
        c('polo-ind-r', 'pushButton', 'Index jobb', 'indicatorRight', 284, 588, 200, 228, engraving='»', color='#202020', ledColor='#3cff6a', sound='plastic', **RUBBER),
        c('polo-demist', 'pushButton', 'Szélvédőfűtés', 'demist', 520, 588, 200, 228, engraving='DEMIST', color='#202020', ledColor='#ffffff', sound='plastic', **RUBBER),
        c('polo-page', 'pushButton', 'Kijelzőoldal', 'displayNext', 756, 588, 200, 228, engraving='PAGE', color='#202020', ledColor='#ffffff', sound='plastic', **RUBBER),
        c('polo-map', 'rotarySwitch', 'Motortérkép', 'engineMapUp', 1040, 92, 250, 300, minusAction='engineMapDown', positions=5, states=['1', '2', '3', '4', '5'], color=red, material='alu'),
        c('polo-respawn', 'pushButton', 'Visszahelyezés', 'respawn', 1330, 120, 220, 240, engraving='RESET', color='#3a1010', ledColor='#ff4040', sound='plastic', **GLASS),
        c('polo-hb', 'pushButton', 'Kézifék (tartsd)', 'handbrake', 1070, 440, 470, 380, hold=True, engraving='HANDBRAKE', color='#262626', ledColor=red, sound='latch', **RUBBER),
        m.legend(pid, 48, 836, 960)]
    panel = m.panel_layout(pid, 'Volkswagen Polo GTI R5 · Button Box 0.4.0', vid, W, H, e,
        m.panel_background(W, H, face='matte', face_tint=(20, 20, 22), frame=(150, 150, 152), plates=[(1018, 70, 556, 344, 'brushed'), (1018, 424, 556, 418, 'matte')],
            headings=[(48, 62, 'POWER'), (48, 310, 'LIGHTS · VISION'), (48, 558, 'SIGNALS')], title='R5 · CONSOLE'), ['ignition'])
    return dict(id=vid, name='Volkswagen Polo GTI R5', modelYear=2018, category='R5', color='#e3001b', dashboard=dash, panel=panel,
        aliases=['VWPoloGTIR5', 'VolkswagenPoloGTIR5', 'VW Polo GTI R5', 'vw_polo_gti_r5'],
        references=[{'url': 'https://www.volkswagen-newsroom.com/en/the-new-polo-gti-driving-presentation-2512/the-new-polo-gti-r5-gti-goes-rallying-2567', 'scope': 'Gyári bemutató; a játék 2018-as változatot modellez (505 Games 0.6 changelog).', 'status': 'primary_manufacturer'}],
        limitations=['A játék saját ívelt fordulatszám-kijelzője (T_PoloGaugeRpm) alapján analóg-íves fő műszer; a pontos skála játékbeli képernyőképpel pontosítandó.'])

def peugeot_206(m):
    vid = 'peugeot-206-wrc'; W, H = 1600, 900
    ink = '#10200c'
    lcd = [
        el('p206-leds', 'leds', 'rpm', 160, 70, 1280, 56, 'RPM', count=20, max=8000, palette=['#f2f2f2'] * 14 + ['#ff3030'] * 6, border=False),
        el('p206-gear', 'gear', 'gear', 610, 170, 380, 420, '', fontSize=330, color=ink, foreground=ink, border=False, font='factory', fontWeight=700),
        el('p206-rpm', 'number', 'rpm', 150, 200, 420, 180, 'RPM', fontSize=110, color=ink, foreground=ink, border=False, font='factory'),
        el('p206-speed', 'number', 'speed', 1030, 200, 420, 180, 'KM/H', fontSize=110, color=ink, foreground=ink, border=False, font='factory'),
        el('p206-water', 'number', 'waterTemp', 150, 430, 420, 150, 'EAU °C', fontSize=70, color=ink, foreground=ink, border=False, font='factory'),
        el('p206-time', 'number', 'stageTime', 1030, 430, 420, 150, 'TEMPS', fontSize=60, color=ink, foreground=ink, border=False, font='factory'),
        el('p206-throttle', 'bar', 'throttle', 150, 640, 640, 110, 'GAZ', max=1, color='#20401a', foreground=ink, border=False),
        el('p206-brake', 'bar', 'brake', 810, 640, 640, 110, 'FREIN', max=1, color='#20401a', foreground=ink, border=False),
    ]
    dash = dash_layout(m, vid + '-dash-040', 'Peugeot 206 WRC (1999) · LCD műszerfal', vid, W, H, [('LCD', lcd)],
        housing(W, H, tone=(22, 22, 24), screen=(110, 40, 1490, 800), screen_color=((150, 170, 120), (118, 138, 92)), gloss=True))
    pid = vid + '-buttonbox-040'; c = m.control
    e = [m.background_element(pid, W, H),
        c('p206-master', 'guarded', 'Főkapcsoló', 'electricalMaster', 48, 92, 200, 228, engraving='COUPE', coverColor='#d0202a', ledColor='#ff3030'),
        c('p206-ign', 'rocker', 'Gyújtás', 'ignition', 284, 92, 200, 228, field='ignition', engraving='ON  OFF', ledColor='#ffb020', material='alu'),
        c('p206-start', 'pushButton', 'Démarreur (tartsd)', 'starter', 520, 92, 200, 228, hold=True, engraving='START', color='#1d1d1d', ledColor='#ff3030', sound='starter', **RUBBER),
        c('p206-fire', 'guarded', 'Tűzoltó', 'fireExtinguisher', 756, 92, 200, 228, engraving='FEU', coverColor='#d0202a', ledColor='#ff3030'),
        c('p206-lights', 'cycleButton', 'Phares · léptetés', 'lights', 48, 340, 200, 228, engraving='PHARES', color='#1d1d1d', ledColor='#ffb020', sound='metalOn', **RUBBER),
        c('p206-high', 'rocker', 'Távfény', 'highBeam', 284, 340, 200, 228, engraving='HIGH  LOW', ledColor='#3c8cff', material='alu'),
        c('p206-fog', 'rocker', 'Ködlámpa', 'fogLights', 520, 340, 200, 228, engraving='ANTIB.', ledColor='#ffb020', material='alu'),
        c('p206-wiper', 'cycleButton', 'Essuie-glace · léptetés', 'wiper', 756, 340, 200, 228, states=['KI', 'INT', 'LASSÚ', 'GYORS'], engraving='E-G', color='#1d1d1d', ledColor='#ffb020', sound='metalOn', **RUBBER),
        c('p206-ind-l', 'pushButton', 'Index bal', 'indicatorLeft', 48, 588, 200, 228, engraving='«', color='#1d1d1d', ledColor='#3cff6a', sound='latch', **RUBBER),
        c('p206-ind-r', 'pushButton', 'Index jobb', 'indicatorRight', 284, 588, 200, 228, engraving='»', color='#1d1d1d', ledColor='#3cff6a', sound='latch', **RUBBER),
        c('p206-haz', 'rocker', 'Vészvillogó', 'hazards', 520, 588, 200, 228, engraving='WARN', ledColor='#ff7a1a', material='alu'),
        c('p206-fan', 'rocker', 'Ventilátor', 'fan', 756, 588, 200, 228, engraving='VENT', ledColor='#ffb020', material='alu'),
        c('p206-map', 'rotarySwitch', 'Motortérkép', 'engineMapUp', 1040, 92, 250, 300, minusAction='engineMapDown', positions=4, states=['1', '2', '3', '4'], color='#ffb020', material='alu'),
        c('p206-respawn', 'pushButton', 'Visszahelyezés', 'respawn', 1330, 120, 220, 240, engraving='RESET', color='#3a1010', ledColor='#ff4040', sound='plastic', **GLASS),
        c('p206-hb', 'pushButton', 'Kézifék (tartsd)', 'handbrake', 1070, 440, 470, 380, hold=True, engraving='FREIN À MAIN', color='#262626', ledColor='#ff3030', sound='latch', **RUBBER),
        m.legend(pid, 48, 836, 960)]
    panel = m.panel_layout(pid, 'Peugeot 206 WRC (1999) · Button Box 0.4.0', vid, W, H, e,
        m.panel_background(W, H, face='matte', face_tint=(36, 37, 40), frame=(178, 182, 188), plates=[(1018, 70, 556, 344, 'brushed'), (1018, 424, 556, 418, 'brushed')],
            headings=[(48, 62, 'ALIMENTATION'), (48, 310, 'ÉCLAIRAGE'), (48, 558, 'SIGNALISATION')], title='WRC 1999 · INTERRUPTEURS'), ['ignition'])
    return dict(id=vid, name='Peugeot 206 WRC (1999)', modelYear=1999, category='WRC', color='#c9d6a8', dashboard=dash, panel=panel,
        aliases=['Peugeot206WRC', 'Peugeot 206 WRC', 'Peugeot206', 'peugeot_206_wrc'],
        references=[{'url': 'https://en.wikipedia.org/wiki/Peugeot_206_WRC', 'scope': 'Típustörténet; a játék 1999-es autót modellez.', 'status': 'secondary'},
                    {'url': 'https://www.largus.fr/actualite-automobile/une-peugeot-206-wrc-pilotee-par-marcus-gronholm-en-vente-10316395.html', 'scope': 'Utastérfotó (2001-es C31): a széria 206 műszerfal-alapformája megmaradt.', 'status': 'photo_reference'}],
        limitations=['Monokróm LCD-jellegű kijelző a játék T_Peugeot206WRCLCD textúrája alapján; a pontos szegmensek képernyőképpel pontosítandók.', 'Francia feliratok korhű stílusban; a pontos gyári feliratok nincsenek igazolva.'])

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
    dash = dash_layout(m, vid + '-dash-040', 'Subaru Impreza 555 Gr.A (1993) · Analóg műszerek', vid, W, H, [('Analóg', analog)],
        housing(W, H, tone=(14, 14, 15), screen=None, cutouts=[(800, 340, 285), (300, 370, 155)], radius=60))
    pid = vid + '-buttonbox-040'; c = m.control
    e = [m.background_element(pid, W, H),
        c('s555-master', 'guarded', 'Főkapcsoló', 'electricalMaster', 48, 92, 200, 228, engraving='MASTER', coverColor='#d0202a', ledColor='#ff3030'),
        c('s555-ign', 'rocker', 'Gyújtás', 'ignition', 284, 92, 200, 228, field='ignition', engraving='IGN  OFF', ledColor='#ffb020', material='plastic'),
        c('s555-start', 'pushButton', 'Indító (tartsd)', 'starter', 520, 92, 200, 228, hold=True, engraving='START', color='#1d1d1d', ledColor='#ff3030', sound='starter', **RUBBER),
        c('s555-fire', 'guarded', 'Tűzoltó', 'fireExtinguisher', 756, 92, 200, 228, engraving='FIRE', coverColor='#d0202a', ledColor='#ff3030'),
        c('s555-lights', 'cycleButton', 'Világítás · léptetés', 'lights', 48, 340, 200, 228, engraving='LIGHTS', color='#1d1d1d', ledColor='#ffb020', sound='metalOn', **RUBBER),
        c('s555-high', 'rocker', 'Távfény / pótfényszóró', 'highBeam', 284, 340, 200, 228, engraving='SPOT  OFF', ledColor='#3c8cff', material='plastic'),
        c('s555-fog', 'rocker', 'Ködlámpa', 'fogLights', 520, 340, 200, 228, engraving='FOG  OFF', ledColor='#ffb020', material='plastic'),
        c('s555-wiper', 'cycleButton', 'Ablaktörlő · léptetés', 'wiper', 756, 340, 200, 228, states=['KI', 'INT', 'LASSÚ', 'GYORS'], engraving='WIPE', color='#1d1d1d', ledColor='#ffb020', sound='rotary', **RUBBER),
        c('s555-ind-l', 'pushButton', 'Index bal', 'indicatorLeft', 48, 588, 200, 228, engraving='«', color='#1d1d1d', ledColor='#3cff6a', sound='latch', **RUBBER),
        c('s555-ind-r', 'pushButton', 'Index jobb', 'indicatorRight', 284, 588, 200, 228, engraving='»', color='#1d1d1d', ledColor='#3cff6a', sound='latch', **RUBBER),
        c('s555-haz', 'rocker', 'Vészvillogó', 'hazards', 520, 588, 200, 228, engraving='HAZ  OFF', ledColor='#ff7a1a', material='plastic'),
        c('s555-fan', 'rocker', 'Ventilátor', 'fan', 756, 588, 200, 228, engraving='FAN  OFF', ledColor='#ffb020', material='plastic'),
        c('s555-respawn', 'pushButton', 'Visszahelyezés', 'respawn', 1060, 120, 220, 240, engraving='RESET', color='#3a1010', ledColor='#ff4040', sound='plastic', **GLASS),
        c('s555-page', 'pushButton', 'Tripmaster nullázás / oldal', 'displayNext', 1320, 120, 220, 240, engraving='TRIP', color='#1d1d1d', ledColor='#ff9a3a', sound='latch', **RUBBER),
        c('s555-hb', 'pushButton', 'Kézifék (tartsd)', 'handbrake', 1070, 440, 470, 380, hold=True, engraving='HANDBRAKE', color='#262626', ledColor='#ff3030', sound='latch', **RUBBER),
        m.legend(pid, 48, 836, 960)]
    panel = m.panel_layout(pid, 'Subaru Impreza 555 Gr.A (1993) · Button Box 0.4.0', vid, W, H, e,
        m.panel_background(W, H, face='matte', face_tint=(24, 24, 26), frame=(140, 142, 146), plates=[(1018, 70, 556, 344, 'matte'), (1018, 424, 556, 418, 'matte')],
            headings=[(48, 62, 'POWER'), (48, 310, 'LIGHTING'), (48, 558, 'SIGNALS · AUX')], title='GROUP A · 1993'), ['ignition'])
    return dict(id=vid, name='Subaru Impreza 555 Group A (1993)', modelYear=1993, category='GROUP A', color='#1f4fa8', dashboard=dash, panel=panel,
        aliases=['SubaruImprezaS3', 'Subaru Impreza S3', 'Subaru Impreza 555', 'subaru_impreza_s3'],
        references=[{'url': 'https://isdc.ie/forum/threads/subaru-impreza-555-group-a-technical-specifications-and-stats-impreza555-com.42273/', 'scope': 'Műszerek: Stack ST400 analóg fordulatszámmérő 0–8000/min, VDO vízhőmérő, Coralba tripmaster, GEMS adatgyűjtő.', 'status': 'secondary_specification'},
                    {'url': 'https://www.carthrottle.com/news/duo-90s-rally-icons-land-assetto-corsa-rally', 'scope': 'A játék az 1993-as Group A specifikációt modellezi.', 'status': 'secondary'}],
        limitations=['A Stack/VDO műszerek stílusa saját rajz, márkajelzés nélkül.', 'Vízhőmérsékletet és tripmaster-távolságot az ACR-adapter jelenleg nem ad: „—” jelenik meg.'])

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
