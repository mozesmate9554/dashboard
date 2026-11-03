#!/usr/bin/env python3
"""SIM CONTROL STUDIO 0.4.0 catalogue builder.

Starts from the shipped 0.3.0 catalogue (all 20 existing cars are preserved) and
- gives the Skoda Fabia RS Rally2 a new mechanical button box (the 0.3.0 photo console stays as a variant),
- adds the five further Assetto Corsa Rally cars (see build_040_cars.py).
Panel backgrounds are original raster textures generated here (no game or manufacturer artwork).
"""
import base64, copy, io, json, math, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'mobile_flutter/assets/catalog.json'
FONT = ROOT / 'mobile_flutter/assets/fonts/BarlowCondensed-SemiBold.ttf'
rng = np.random.default_rng(40)

# ---------------------------------------------------------------- textures
def carbon(w, h, cell=14, tint=(34, 37, 42)):
    y, x = np.mgrid[0:h, 0:w]
    u, v = (x // cell), (y // cell)
    twill = ((u + v) // 2) % 2
    fx, fy = (x % cell) / cell, (y % cell) / cell
    shade = np.where(twill == 0, 0.55 + 0.45 * np.sin(fx * math.pi), 0.55 + 0.45 * np.sin(fy * math.pi))
    base = np.array(tint, dtype=float)[None, None, :]
    img = base * (0.55 + 0.6 * shade[..., None])
    return Image.fromarray(np.clip(img, 0, 255).astype('uint8'))

def brushed(w, h, tone=(168, 173, 180)):
    streak = np.repeat(rng.normal(0, 1, (h, 1)) * 8, w, axis=1)
    grad = np.linspace(1.08, 0.86, h)[:, None]
    img = np.array(tone, dtype=float)[None, None, :] * grad[..., None] + streak[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype('uint8'))

def matte(w, h, tone=(48, 50, 54)):
    img = np.repeat(np.repeat(np.array(tone, dtype=float)[None, None, :], h, axis=0), w, axis=1)
    return Image.fromarray(np.clip(img, 0, 255).astype('uint8'))

def font(size):
    return ImageFont.truetype(str(FONT), size)

def screw(draw, cx, cy, r):
    draw.ellipse((cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2), fill=(18, 18, 20))
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(150, 154, 160))
    draw.ellipse((cx - r + 2, cy - r + 2, cx + r - 3, cy + r - 3), fill=(188, 192, 198))
    a = 0.6
    draw.line((cx - r * math.cos(a), cy - r * math.sin(a), cx + r * math.cos(a), cy + r * math.sin(a)), fill=(40, 42, 46), width=max(2, r // 3))

def engrave(draw, xy, text, size, anchor='mm', fill=(208, 210, 214)):
    x, y = xy
    draw.text((x, y + 1), text, font=font(size), fill=(0, 0, 0), anchor=anchor)
    draw.text((x, y), text, font=font(size), fill=fill, anchor=anchor)

def panel_background(w, h, face='carbon', frame=(168, 173, 180), face_tint=(34, 37, 42), plates=(), headings=(), title='', footer=''):
    """plates: (x, y, w, h, material) recessed sub-panels; headings: (x, y, text)."""
    base = brushed(w, h, frame)
    inner = (22, 22, w - 22, h - 22)
    surface = carbon(w - 44, h - 44, tint=face_tint) if face == 'carbon' else matte(w - 44, h - 44, face_tint)
    shadow = Image.new('L', (w, h), 0)
    ImageDraw.Draw(shadow).rounded_rectangle(inner, 26, fill=180)
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    base.paste((10, 10, 12), mask=shadow)
    mask = Image.new('L', (w - 44, h - 44), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 45, h - 45), 22, fill=255)
    base.paste(surface, (22, 22), mask)
    d = ImageDraw.Draw(base)
    for (x, y, pw, ph, material) in plates:
        plate = brushed(pw, ph, (120, 124, 130)) if material == 'brushed' else matte(pw, ph, (22, 31, 52) if material == 'navy' else (12, 12, 13) if material == 'black' else (30, 31, 34))
        pm = Image.new('L', (pw, ph), 0); ImageDraw.Draw(pm).rounded_rectangle((0, 0, pw - 1, ph - 1), 16, fill=255)
        d.rounded_rectangle((x - 3, y - 3, x + pw + 3, y + ph + 3), 18, fill=(8, 8, 10))
        base.paste(plate, (x, y), pm)
        for (sx, sy) in ((x + 14, y + 14), (x + pw - 14, y + 14), (x + 14, y + ph - 14), (x + pw - 14, y + ph - 14)):
            screw(d, sx, sy, 6)
    for (x, y, text) in headings:
        y = HEADING_ROWS.get(y, y)
        engrave(d, (x, y), text, 22, anchor='lm', fill=(196, 198, 202))
        d.line((x, y + 16, x + 9 * len(text) + 40, y + 16), fill=(90, 92, 96), width=2)
    for (sx, sy) in ((11, 11), (w - 11, 11), (11, h - 11), (w - 11, h - 11)):
        screw(d, sx, sy, 8)
    if title:
        engrave(d, (w - 48, 46), title, 24, anchor='rm', fill=(170, 172, 176))
    if footer:
        engrave(d, (w // 2, h - 40), footer, 19, anchor='mm', fill=(150, 152, 156))
    buffer = io.BytesIO(); base.save(buffer, format='PNG', optimize=True)
    return buffer.getvalue()

# ---------------------------------------------------------------- layout helpers
GRID_ROWS = {92: 92, 340: 346, 588: 600}
HEADING_ROWS = {62: 62, 310: 322, 558: 576}

def control(identifier, kind, label, action, x, y, w, h, **extra):
    # Left-hand grid: 210 px cells leave room for the engraved section headings between rows.
    if x < 1000 and h == 228 and y in GRID_ROWS:
        y, h = GRID_ROWS[y], 210
    e = {'id': identifier, 'kind': kind, 'label': label, 'field': extra.pop('field', ''), 'action': action,
         'x': x, 'y': y, 'w': w, 'h': h, 'border': False, 'z': 5}
    e.update(extra)
    if not action:
        del e['action']  # display-only key: the game has no matching input
    return e

def background_element(identifier, w, h):
    return {'id': identifier + '-body', 'kind': 'image', 'label': identifier + '-body', 'field': '', 'x': 0, 'y': 0, 'w': w, 'h': h,
            'assetId': identifier + '-body', 'border': False, 'fit': 'fill', 'nightDim': True, 'z': 0, 'locked': True}

def legend(identifier, x, y, w):
    return {'id': identifier + '-legend', 'kind': 'text', 'field': '', 'x': x, 'y': y, 'w': w, 'h': 30, 'z': 4, 'border': False,
            'label': 'LED · villogó sárga: elküldve · félig világít: Bridge végrehajtotta (feltételezett) · teljes fény: játék igazolta · piros: hiba',
            'fontSize': 16, 'letterSpacing': 1, 'foreground': '#9aa0a6', 'font': 'factory'}

def panel_layout(identifier, name, vehicle_id, w, h, elements, png, supported):
    return {'schemaVersion': 1, 'id': identifier, 'name': name, 'vehicleId': vehicle_id, 'role': 'panel', 'isBase': True,
            'version': '0.4.0', 'revision': 1, 'width': w, 'height': h, 'background': '#0a0b0d', 'adaptive': 'preserve',
            'pages': [{'id': identifier + '-p1', 'name': 'Button Box', 'elements': elements}],
            'assets': {identifier + '-body': {'type': 'png', 'name': identifier + '-body', 'base64': base64.b64encode(png).decode()}},
            'supportedFields': supported}

# ---------------------------------------------------------------- Škoda Fabia RS Rally2 0.4.0 button box
def skoda_panel():
    """Layout traced from the game's own console texture (T_IntDetails_B, Škoda Fabia RS Rally2):
    navy touch panel - servis menu / call / end call, two +/- volume keys, hazard / fog lamp / ALL.
    Game functions that sit on the wheel and stalks in the real car are grouped on the right."""
    W, H = 1600, 900
    pid = 'skoda-fabia-rs-rally2-buttonbox-040'
    navy = '#1f2b47'
    k = 1000 / 640  # console texture crop -> canvas
    def C(x0, y0, x1, y1): return dict(x=round(40 + x0 * k), y=round(80 + y0 * k), w=round((x1 - x0) * k), h=round((y1 - y0) * k))
    touch = dict(material='touch', color=navy, ledColor='#7fd3ff', sound='plastic', ring=False, caption=False)
    e = [background_element(pid, W, H)]
    e += [
        control('sk-service', 'pushButton', 'Szervizmenü', 'displayNext', **C(28, 25, 180, 125), engraving='servis\nmenu', **touch),
        control('sk-call', 'pushButton', 'Hívás fogadása', 'callAccept', **C(28, 130, 180, 225), icon='phone', **touch),
        control('sk-end', 'pushButton', 'Hívás vége', 'callEnd', **C(28, 230, 180, 330), icon='phoneEnd', **touch),
        control('sk-vol1-up', 'pushButton', 'Interkom +', 'intercomVolumeUp', **C(190, 10, 322, 175), engraving='+', **touch),
        control('sk-vol1-dn', 'pushButton', 'Interkom −', 'intercomVolumeDown', **C(190, 180, 322, 352), icon='volumeDown', engraving='−', **touch),
        control('sk-vol2-up', 'pushButton', 'Rádió +', 'radioVolumeUp', **C(332, 10, 464, 175), engraving='+', **touch),
        control('sk-vol2-dn', 'pushButton', 'Rádió −', 'radioVolumeDown', **C(332, 180, 464, 352), icon='volumeDown', engraving='−', **touch),
        control('sk-hazard', 'pushButton', 'Vészvillogó', 'hazards', **C(476, 25, 620, 125), icon='hazard', **dict(touch, ledColor='#ff8a1a')),
        control('sk-fog', 'pushButton', 'Ködlámpa', 'fogLights', **C(476, 130, 620, 225), icon='fog', **touch),
        control('sk-all', 'pushButton', 'ALL', 'acknowledge', **C(476, 230, 620, 330), icon='all', **touch),
    ]
    rubber = dict(material='rubber', ring=True)
    gx, gy, gw, gh = [1090, 1240, 1390], [96, 330, 564], 140, 214
    e += [
        control('sk-start', 'pushButton', 'Start (kormány)', 'starter', x=gx[0], y=gy[0], w=gw, h=gh, hold=True, engraving='START', color='#c8102e', ledColor='#ff4040', sound='starter', **rubber),
        control('sk-ign', 'rocker', 'Gyújtás', 'ignition', x=gx[1], y=gy[0], w=gw, h=gh, field='ignition', engraving='IGN  OFF', ledColor='#ffd23c', material='plastic', sound='metalOn'),
        control('sk-fire', 'guarded', 'FIRE', 'fireExtinguisher', x=gx[2], y=gy[0], w=gw, h=gh, engraving='FIRE', coverColor='#d0202a', ledColor='#ff3030'),
        control('sk-lights', 'cycleButton', 'Világítás · léptetés', 'lights', x=gx[0], y=gy[1], w=gw, h=gh, icon='light', **dict(touch, ledColor='#b4e2ff')),
        control('sk-high', 'pushButton', 'Távfény', 'highBeam', x=gx[1], y=gy[1], w=gw, h=gh, icon='highBeam', **dict(touch, ledColor='#3c8cff')),
        control('sk-wiper', 'cycleButton', 'Ablaktörlő · léptetés', 'wiper', x=gx[2], y=gy[1], w=gw, h=gh, states=['KI', 'INT', 'LASSÚ', 'GYORS'], icon='wiper', **touch),
        control('sk-ind-l', 'pushButton', 'Index bal', 'indicatorLeft', x=gx[0], y=gy[2], w=gw, h=gh, icon='left', **dict(touch, ledColor='#3cff6a')),
        control('sk-ind-r', 'pushButton', 'Index jobb', 'indicatorRight', x=gx[1], y=gy[2], w=gw, h=gh, icon='right', **dict(touch, ledColor='#3cff6a')),
        control('sk-hb', 'pushButton', 'Kézifék (tartsd)', 'handbrake', x=gx[2], y=gy[2], w=gw, h=gh, hold=True, engraving='HB', color='#262626', ledColor='#ff3030', sound='latch', **rubber),
        legend(pid, 48, 836, 960),
    ]
    png = panel_background(W, H, face='carbon', plates=[(28, 66, 1024, 562, 'navy'), (1070, 66, 504, 744, 'matte')],
        headings=[(48, 662, 'KÖZÉPKONZOL (játékbeli textúra alapján)'), (1090, 62, 'KORMÁNY · KAROK')], title='')
    return panel_layout(pid, 'Škoda Fabia RS Rally2 · Button Box 0.4.0', 'skoda-fabia-rs-rally2', W, H, e, png, ['ignition'])

def main():
    catalog = json.loads(CATALOG.read_text())
    vehicles = catalog['vehicles']
    skoda = next(v for v in vehicles if v['id'] == 'skoda-fabia-rs-rally2')
    if skoda.get('version') != '0.4.0':
        old = copy.deepcopy(skoda['panel'])
        old['name'] = 'Škoda Fabia RS Rally2 · Középkonzol (0.3.0 fotórekonstrukció)'
        skoda['variants'] = [old]
    skoda['panel'] = skoda_panel()
    skoda['version'] = '0.4.0'
    skoda['gameVehicleAliases'] = ['SkodaFabiaRSRally2', 'Skoda Fabia RS Rally2', 'skoda_fabia_rs_rally2']
    skoda['knownLimitations'] = list(dict.fromkeys(skoda.get('knownLimitations', []) + [
        '0.4.0 Button Box: a gombsorrend és a funkciók a gyári érintőpanel fotóját követik, a mechanikus megjelenés saját rajz.',
        'A világítás és az ablaktörlő a játékban körbeléptető (IA_CycleLights / IA_CycleWipers); a kért lépés nem igazolt játékállapot.',
    ]))
    sys.path.insert(0, str(Path(__file__).parent))
    # Game-display page (WB_GaugeSkodaFabiaRS) goes first; the 0.3.0 photo-based pages stay unchanged after it.
    import build_040_gauges
    game_page, game_assets = build_040_gauges.skoda_page()
    dash = skoda['dashboard']
    dash['pages'] = [game_page] + [p for p in dash['pages'] if p['id'] != game_page['id']]
    for key, (kind, raw) in game_assets.items():
        dash['assets'][key] = {'type': kind, 'name': key, 'base64': base64.b64encode(raw).decode()}
    dash['supportedFields'] = sorted(set(dash['supportedFields']) | {e['field'] for e in game_page['elements'] if e.get('field')})
    try:
        import build_040_cars
        build_040_cars.apply(vehicles, sys.modules[__name__])
    except ModuleNotFoundError:
        pass
    # 0.4.0: only the six requested Assetto Corsa Rally cars stay in the app.
    keep = ['skoda-fabia-rs-rally2', 'peugeot-208-rally4', 'hyundai-i20-n-rally2', 'vw-polo-gti-r5', 'peugeot-206-wrc', 'subaru-impreza-555-gra']
    vehicles[:] = sorted((v for v in vehicles if v['id'] in keep), key=lambda v: keep.index(v['id']))
    catalog['vehicles'] = vehicles
    catalog['version'] = '0.4.0'
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
    for v in vehicles:
        if v.get('version') != '0.4.0':
            continue  # the other 19 cars stay byte-identical
        folder = ROOT / 'vehicle_profiles' / v['id']; folder.mkdir(parents=True, exist_ok=True)
        (folder / 'profile.json').write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'windows_bridge/Bridge.Windows/profiles.json').write_text(json.dumps([v['id'] for v in vehicles]) + '\n')
    print(f'0.4.0 catalogue: {len(vehicles)} vehicles; {CATALOG.stat().st_size/1e6:.2f} MB')

if __name__ == '__main__':
    main()
