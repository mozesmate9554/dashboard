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
        plate = brushed(pw, ph, (120, 124, 130)) if material == 'brushed' else matte(pw, ph, (30, 31, 34))
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
    W, H = 1600, 900
    pid = 'skoda-fabia-rs-rally2-buttonbox-040'
    cell_w, cell_h = 200, 228
    cols = [48, 284, 520, 756]
    rows = [92, 340, 588]
    def at(c, r): return dict(x=cols[c], y=rows[r], w=cell_w, h=cell_h)
    glass = dict(material='glass', shape='square', ring=False)
    e = [background_element(pid, W, H)]
    e += [
        control('sk-main', 'pushButton', 'Főkapcsoló', 'electricalMaster', **at(0, 0), engraving='MAIN', color='#2a3440', ledColor='#ffd23c', sound='latch', **glass),
        control('sk-ign', 'rocker', 'Gyújtás', 'ignition', **at(1, 0), field='ignition', engraving='IGN  OFF', ledColor='#ffd23c', material='plastic', sound='metalOn'),
        control('sk-start', 'pushButton', 'Indító (tartsd)', 'starter', **at(2, 0), hold=True, engraving='START', color='#c8102e', ledColor='#ff4040', material='rubber', sound='starter'),
        control('sk-fire', 'guarded', 'Tűzoltó', 'fireExtinguisher', **at(3, 0), engraving='FIRE', coverColor='#d0202a', ledColor='#ff3030'),
        control('sk-lights', 'cycleButton', 'Világítás · léptetés', 'lights', **at(0, 1), engraving='LIGHT', color='#2a3440', ledColor='#b4e2ff', sound='plastic', **glass),
        control('sk-highbeam', 'pushButton', 'Távfény', 'highBeam', **at(1, 1), engraving='HIGH', color='#1d3c78', ledColor='#3c8cff', sound='plastic', **glass),
        control('sk-fog', 'pushButton', 'Ködlámpa', 'fogLights', **at(2, 1), engraving='FOG', color='#2a3440', ledColor='#5cff8a', sound='plastic', **glass),
        control('sk-hazard', 'pushButton', 'Vészvillogó', 'hazards', **at(3, 1), engraving='HAZ', color='#9b1c1c', ledColor='#ff7a1a', sound='plastic', **glass),
        control('sk-wiper', 'cycleButton', 'Ablaktörlő · léptetés', 'wiper', **at(0, 2), states=['KI', 'INT', 'LASSÚ', 'GYORS'], engraving='WIPE', color='#2a3440', ledColor='#5cc8ff', sound='plastic', **glass),
        control('sk-ind-l', 'pushButton', 'Index bal', 'indicatorLeft', **at(1, 2), engraving='«', color='#2a3440', ledColor='#3cff6a', sound='plastic', **glass),
        control('sk-ind-r', 'pushButton', 'Index jobb', 'indicatorRight', **at(2, 2), engraving='»', color='#2a3440', ledColor='#3cff6a', sound='plastic', **glass),
        control('sk-demist', 'pushButton', 'Szélvédőfűtés', 'demist', **at(3, 2), engraving='DEMIST', color='#2a3440', ledColor='#ffb03c', sound='plastic', **glass),
        control('sk-map', 'rotarySwitch', 'Motortérkép', 'engineMapUp', x=1040, y=92, w=250, h=300, minusAction='engineMapDown', positions=5, states=['1', '2', '3', '4', '5'], color='#9bd158', material='alu', field=''),
        control('sk-intercom', 'rotarySwitch', 'Interkom hangerő', 'intercomVolumeUp', x=1310, y=92, w=250, h=300, minusAction='intercomVolumeDown', positions=6, states=['0', '1', '2', '3', '4', '5'], color='#e8e8e8', material='alu'),
        control('sk-service', 'pushButton', 'Szervizmenü', 'displayNext', x=1070, y=440, w=190, h=200, engraving='MENU', color='#2a3440', ledColor='#e8e8e8', sound='plastic', **glass),
        control('sk-all', 'pushButton', 'ALL', 'acknowledge', x=1330, y=440, w=190, h=200, engraving='ALL', color='#2a3440', ledColor='#e8e8e8', sound='plastic', **glass),
        control('sk-call', 'pushButton', 'Hívás fogadása', 'callAccept', x=1070, y=652, w=190, h=170, engraving='CALL', color='#1f6b34', ledColor='#3cff6a', sound='plastic', **glass),
        control('sk-end', 'pushButton', 'Hívás vége', 'callEnd', x=1330, y=652, w=190, h=170, engraving='END', color='#8a1d1d', ledColor='#ff4040', sound='plastic', **glass),
        legend(pid, 48, 836, 960),
    ]
    png = panel_background(W, H, face='carbon', plates=[(1018, 70, 556, 344, 'matte'), (1018, 424, 556, 418, 'matte')],
        headings=[(48, 62, 'TÁP · INDÍTÁS'), (48, 310, 'VILÁGÍTÁS'), (48, 558, 'LÁTÁS · JELZÉS')],
        title='RALLY2 · KÖZÉPKONZOL', footer='')
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
    try:
        import build_040_cars
        build_040_cars.apply(vehicles, sys.modules[__name__])
    except ModuleNotFoundError:
        pass
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
