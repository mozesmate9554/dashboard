#!/usr/bin/env python3
"""Driver displays of SIM CONTROL STUDIO 0.4.0, rebuilt from the game's own UMG widgets.

Source: Assetto Corsa Rally `Data/UI/Widgets_Gauges/WB_Gauge*.uasset`, exported read-only to JSON with
FModel (UE5.6 + usmap). Only the widget *layout* (positions, sizes, fonts sizes, colours, visibility,
LED rpm windows) is taken over; every graphic is drawn here. Game fonts are not redistributed.

Widget coordinates are 1024 x 1024 UV-atlas pixels. Each display is mapped onto the app canvas with
one uniform scale, so proportions match the game. Widgets the game ships *hidden* (Visibility=Hidden or
RenderOpacity=0) are not on the main page; they go to a separate "hidden fields" page and say so.
Colours that are set at runtime by Blueprint code (not exported) are marked as assumptions.
"""
import base64, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def _png(image):
    buffer = io.BytesIO(); image.save(buffer, format='PNG', optimize=True); return buffer.getvalue()

def _font(size):
    for path in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'):
        try: return ImageFont.truetype(path, size)
        except OSError: pass
    return ImageFont.load_default()

def el(i, kind, field, x, y, w, h, label='', **extra):
    e = {'id': i, 'kind': kind, 'field': field, 'label': label, 'x': round(x), 'y': round(y), 'w': round(w), 'h': round(h), 'z': 4, 'border': False}
    e.update(extra); return e

def readout(i, field, x, y, w, h, color, size, font='sans', weight=600, **extra):
    return el(i, 'number' if field != 'gear' else 'gear', field, x, y, w, h, '', style='factoryReadout', foreground=color, color=color,
              fontSize=size, font=font, fontWeight=weight, **extra)

def label(i, text, x, y, w, h, color, size, font='factory', weight=600, **extra):
    return el(i, 'text', '', x, y, w, h, text, foreground=color, color=color, fontSize=size, font=font, fontWeight=weight, letterSpacing=0, **extra)

def flash(i, x, y, w, h, color, ratio, z=2, **extra):
    """A full-area shift-light overlay (the game's Red/Green/Yellow overlay borders)."""
    return el(i, 'leds', 'rpm', x, y, w, h, 'Shift', count=1, minRatio=ratio, max=8000, palette=[color], offColor='#00000000', glow=False, z=z, **extra)

def body(w, h, draw):
    """Plain moulded housing with a recessed screen; `draw(d, img)` paints the screen artwork."""
    img = Image.new('RGB', (w, h), (15, 16, 18)); d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 4, w - 5, h - 5), 36, outline=(58, 60, 64), width=3)
    draw(d, img)
    return _png(img)

def page(pid, index, name, elements, asset):
    bg = {'id': f'{pid}-body-{index}', 'kind': 'image', 'field': '', 'label': 'Ház', 'x': 0, 'y': 0, 'w': elements[0], 'h': elements[1],
          'assetId': asset, 'border': False, 'fit': 'fill', 'nightDim': True, 'z': 0, 'locked': True}
    return {'id': f'{pid}-p{index + 1}', 'name': name, 'elements': [bg] + elements[2]}

def layout(pid, name, vid, w, h, pages, assets, background='#050607'):
    built = [page(pid, i, n, (w, h, es), a) for i, (n, es, a) in enumerate(pages)]
    fields = sorted({e['field'] for p in built for e in p['elements'] if e.get('field')})
    return {'schemaVersion': 1, 'id': pid, 'name': name, 'vehicleId': vid, 'role': 'dashboard', 'isBase': True, 'version': '0.4.0',
            'revision': 2, 'width': w, 'height': h, 'background': background, 'pages': built, 'supportedFields': fields,
            'source': 'Játékbeli WB_Gauge widget elrendezése (FModel JSON-export, csak olvasás); saját grafika.',
            'assets': {k: {'type': t, 'name': k, 'base64': base64.b64encode(v).decode()} for k, (t, v) in assets.items()}}

def svg(path_d, view='0 0 100 100'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}"><g fill="#ffffff">{path_d}</g></svg>'.encode()

# Original pictograms (ISO-style symbols, drawn here).
HANDBRAKE = svg('<path d="M50 14a36 36 0 1 0 0.01 0zm0 8a28 28 0 1 1-0.01 0z"/>'
                '<path d="M42 32h12a11 11 0 0 1 0 22h-6v14h-6zm6 6v10h6a5 5 0 0 0 0-10z"/>'
                '<path d="M12 22l5 4a34 34 0 0 0 0 48l-5 4a40 40 0 0 1 0-56zM88 22l-5 4a34 34 0 0 1 0 48l5 4a40 40 0 0 0 0-56z"/>')
LOWBEAM = svg('<path d="M58 22c18 0 30 12 30 28s-12 28-30 28h-6V22zm0 8v40c12 0 22-8 22-20s-10-20-22-20z"/>'
              '<path d="M8 30h36l-4 7H8zm0 13h36l-4 7H8zm0 13h36l-4 7H8zm0 13h36l-4 7H8z"/>')

SHOT = 'Futásidejű szín/küszöb: a Blueprint-logika nem exportálható, ezért feltételezett érték.'

# ------------------------------------------------------------------ Škoda Fabia RS Rally2
def skoda_page():
    """WB_GaugeSkodaFabiaRS: 880 x 491 black screen, rounded (20 px) bezel; big gear field with a red
    (F74D4A) shift overlay; bottom strip 'Map' + green (31B87F) badge, handbrake icon (left 200 px),
    wipers icon (Hidden in the game) and lights icon (right 16 px)."""
    s, ox, oy = 1.3, 68, 70
    W, H = 1280, 800
    def X(v): return ox + v * s
    def Y(v): return oy + v * s
    gx0, gw = X(45), 790 * s          # SizeBox_39 (790 wide) centred in the 880 screen
    def art(d, img):
        d.rounded_rectangle((ox - 14, oy - 14, ox + 880 * s + 14, oy + 491 * s + 14), 40, fill=(4, 4, 5), outline=(70, 72, 76), width=4)
        d.rounded_rectangle((ox, oy, ox + 880 * s, oy + 491 * s), 26, fill=(0, 0, 0))
        d.rounded_rectangle((X(57), Y(412), X(57) + 200 * s * .9, Y(412) + 88 * s * .82), 20, fill=(25, 24, 25))  # Map badge plate
        f = _font(22); d.text((ox + 6, oy + 491 * s + 26), 'WB_GaugeSkodaFabiaRS · játékbeli elrendezés, saját grafika', font=f, fill=(90, 92, 96))
    png = body(W, H, art)
    elements = [
        flash('skg-red', gx0 + 12 * s, Y(6), gw - 24 * s, 400 * s, '#F74D4A', .93, referenceNote='RedOverlay (F74D4A) a váltási ponton. ' + SHOT),
        readout('skg-gear', 'gear', gx0, Y(6), gw, 400 * s, '#ffffff', 425, weight=700,
                referenceNote='GearText: NotoSans Bold 327 px. A szerkesztőben fekete, futás közben a háttérhez igazodik; itt fehér (feltételezés).'),
        label('skg-map-label', 'Map', X(57) + 4, Y(418), 92, 70, '#ffffff', 42, font='factory', weight=400),
        readout('skg-map', 'engineMap', X(57) + 100, Y(416), 74, 72, '#000000', 62, weight=800, background='#31B87F', shape='rounded'),
        el('skg-handbrake', 'indicator', 'handbrake', gx0 + 200 * s - 4, Y(410), 104, 104, 'Kézifék', style='factorySymbol', assetId='skg-handbrake',
           activeAbove=.05, color='#ff4a3d'),
        el('skg-lights', 'indicator', 'lights', gx0 + gw - 16 * s - 150 * s * .8, Y(412), 150 * s * .8, 90 * s * .8, 'Világítás', style='factorySymbol',
           assetId='skg-lights', color='#3cff6a'),
    ]
    assets = {'skg-body': ('png', png), 'skg-handbrake': ('svg', HANDBRAKE), 'skg-lights': ('svg', LOWBEAM)}
    return {'id': 'skoda-fabia-rs-rally2-dashboard-p0', 'name': 'Játékbeli kijelző (WB_GaugeSkodaFabiaRS)',
            'elements': [{'id': 'skg-body-img', 'kind': 'image', 'field': '', 'label': 'Ház', 'x': 0, 'y': 0, 'w': W, 'h': H, 'assetId': 'skg-body',
                          'border': False, 'fit': 'fill', 'nightDim': True, 'z': 0, 'locked': True}] + elements}, assets

# ------------------------------------------------------------------ Peugeot 208 Rally4
P208_WINDOW = (5200, 6100, 6150)  # WB_208MultiPhaseRPMLed, gears 1-4: split 5200-6100 over 10 LEDs, all on 6100+, flash 6150+

def peugeot_208():
    vid, W, H = 'peugeot-208-rally4', 1600, 900
    pid = vid + '-dash-040'
    s = 1.4
    sx, sy, sw, sh = 149, 150, 930 * s, 512 * s * .985
    cx = sx + sw / 2
    def screen(d, img):
        d.rounded_rectangle((sx - 16, sy - 16, sx + sw + 16, sy + sh + 16), 30, fill=(4, 4, 5), outline=(70, 72, 76), width=4)
        d.rectangle((sx, sy, sx + sw, sy + sh), fill=(0, 0, 0))
        lx0 = (W - 878 * s) / 2
        d.rounded_rectangle((lx0 - 18, 26, lx0 + 878 * s + 18, 26 + 53 * s + 24), 22, fill=(8, 8, 9), outline=(58, 60, 64), width=3)
        # rect1 / rect2 boxes of the widget (RPM box, Speed box)
        for (bx, by, bw, bh) in [(cx - 108 * s, sy + sh - 27 * s - 43 * s - 40, 216 * s, 86 * s), (cx + 322 * s - 93 * s, sy + sh - 33 * s - 136 * s, 186 * s, 136 * s)]:
            d.rounded_rectangle((bx, by, bx + bw, by + bh), 14, outline=(150, 152, 156), width=3)
    def trip(d, img):
        tx, ty, tw, th = 118, 70, 718 * 1.9, 390 * 1.9
        d.rounded_rectangle((tx - 18, ty - 18, tx + tw + 18, ty + th + 18), 34, fill=(24, 26, 30), outline=(70, 72, 76), width=4)
        d.rounded_rectangle((tx, ty, tx + tw, ty + th), 18, fill=(0xDB, 0xE0, 0xF1))
        for kx in (tx + 17 * 1.9, tx + tw - 75 * 1.9):
            d.rounded_rectangle((kx, ty + 19, kx + 58 * 1.9 - 32, ty + th - 19), 10, fill=(0x33, 0x3F, 0x93))
    leds = []
    lx0, lstep = (W - 878 * s) / 2, (878 * s - 53 * s) / 9
    lo, hi, flash_rpm = P208_WINDOW
    for i in range(10):
        start = lo + (hi - lo) * i / 10
        leds.append(el(f'p208-led{i}', 'leds', 'rpm', lx0 + i * lstep, 36, 53 * s, 53 * s, 'RPM', count=1, min=start, max=start + 1,
                       palette=['#ffcf1f'], shape='circle', z=3))
        leds.append(el(f'p208-ledr{i}', 'leds', 'rpm', lx0 + i * lstep, 36, 53 * s, 53 * s, 'RPM', count=1, min=hi, max=hi + 1,
                       palette=['#ff2a2a'], shape='circle', offColor='#00000000', z=4))
    leds[0]['referenceNote'] = ('WB_208MultiPhaseRPMLed (1-4. fokozat): 5200-6100 rpm között 10 LED fokozatosan, 6100 felett mind, 6150 felett villog. '
                                'A LED-színeket az M_Peugeot208RPMLed anyag adja (nem exportált); a sárga→piros a gyári User Guide szerint.')
    main = leds + [
        readout('p208-gear', 'gear', cx - 260, sy + 6, 520, 470, '#ffffff', 392, referenceNote='GearText: NotoSans SemiBold 280 px, középen.'),
        readout('p208-rpm', 'rpm', cx - 108 * s + 8, sy + sh - 27 * s - 43 * s - 34, 216 * s - 16, 86 * s - 12, '#F8F8F8', 81),
        label('p208-speed-label', 'Speed', cx + 322 * s - 93 * s, sy + sh - 33 * s - 130 * s, 186 * s, 50, '#DADADA', 42, font='factory', weight=400),
        readout('p208-speed', 'speed', cx + 322 * s - 93 * s + 10, sy + sh - 33 * s - 130 * s + 52, 186 * s - 20, 136 * s - 64, '#5DC6EE', 67),
    ]
    hidden = [
        label('p208h-note', 'A játék 208-as kijelzőjén REJTETT mezők (Map, OilP, OilT, WaterT)', 160, 60, 1280, 60, '#8a8f96', 32),
        label('p208h-map-l', 'Map', 200, 200, 560, 60, '#DADADA', 42, font='factory', weight=400),
        readout('p208h-map', 'engineMap', 200, 260, 560, 150, '#ECF831', 120, font='factory'),
        label('p208h-oilp-l', 'OilP', 840, 200, 560, 60, '#DADADA', 42, font='factory', weight=400),
        readout('p208h-oilp', 'oilPressure', 840, 260, 560, 150, '#1AD325', 120, decimals=1),
        label('p208h-oilt-l', 'OilT', 200, 480, 560, 60, '#DADADA', 42, font='factory', weight=400),
        readout('p208h-oilt', 'oilTemp', 200, 540, 560, 150, '#1AD325', 120),
        label('p208h-wat-l', 'WaterT', 840, 480, 560, 60, '#DADADA', 42, font='factory', weight=400),
        readout('p208h-wat', 'waterTemp', 840, 540, 560, 150, '#F0A122', 120),
    ]
    k = 1.9; tx, ty = 118, 70
    blue = '#384497'
    trip_page = [
        label('p208t-menu', 'MENU', tx + 17 * k - 40, ty + 120, 170, 44, '#ffffff', 34, rotation=-90),
        label('p208t-mode', 'MODE', tx + 17 * k - 40, ty + 470, 170, 44, '#ffffff', 34, rotation=-90),
        label('p208t-clr1', 'CLR', tx + 718 * k - 75 * k - 30, ty + 120, 150, 44, '#ffffff', 34, rotation=-90),
        label('p208t-clr2', 'CLR', tx + 718 * k - 75 * k - 30, ty + 470, 150, 44, '#ffffff', 34, rotation=-90),
        label('p208t-gps', 'GPS', tx + 140, ty + 260, 120, 70, '#35358E', 58, font='factory', weight=700),
        readout('p208t-dist', 'stageDistance', tx + 260, ty + 40, 760, 300, blue, 150, scale=.001, decimals=2,
                referenceNote='DistanceFromStart (David Sans 80 px): a szakasz elejétől megtett út, km.'),
        label('p208t-km1', 'km', tx + 1030, ty + 230, 120, 90, '#35358E', 80),
        readout('p208t-final', '', tx + 520, ty + 400, 500, 240, blue, 110,
                referenceNote='DistanceFinal: a szakasz teljes hossza. Az ACR-adapter ezt nem adja, ezért „—”.'),
        label('p208t-km2', 'km', tx + 1030, ty + 540, 120, 90, '#35358E', 80),
    ]
    real, real_png = peugeot_208_real_page(W, H)
    assets = {pid + '-screen': ('png', body(W, H, screen)), pid + '-trip': ('png', body(W, H, trip)), pid + '-real': ('png', real_png)}
    return layout(pid, 'Peugeot 208 Rally4 · Műszerfal (játékbeli widget + valós kijelző)', vid, W, H,
                  [('Kijelző', main, pid + '-screen'), ('Valós kijelző (fotó alapján)', real, pid + '-real'),
                   ('GPS tripmeter', trip_page, pid + '-trip'), ('Rejtett mezők', hidden, pid + '-screen')], assets)

# ------------------------------------------------------------------ Hyundai i20 N Rally2
def hyundai_i20():
    """WB_GaugeHyundaiI20NRally2: 855 x 535 black screen. Centre column: blue 'RPM' + value, huge cyan
    (02FEFF) gear, speed. Full-screen shift overlays: green side bars (75 px), yellow full, red centre (425 px).
    The tWater/pWater/tOil/pOil/TExh and Emerg/Map/Boost/Shift columns have RenderOpacity 0 (hidden)."""
    vid, W, H = 'hyundai-i20-n-rally2', 1600, 900
    pid = vid + '-dash-040'
    s = 1.55; sw, sh = 855 * s, 535 * s; sx, sy = (W - sw) / 2, (H - sh) / 2
    cx = W / 2
    def screen(d, img):
        d.rounded_rectangle((sx - 16, sy - 16, sx + sw + 16, sy + sh + 16), 30, fill=(4, 4, 5), outline=(70, 72, 76), width=4)
        d.rectangle((sx, sy, sx + sw, sy + sh), fill=(0, 0, 0))
    main = [
        flash('i20-yellow', sx + 3, sy, sw - 6, sh, '#FFC90D', .90, z=1, referenceNote='YellowOverlay (FFC90D). ' + SHOT),
        flash('i20-green-l', sx + 3, sy, 75 * s, sh, '#00FF79', .82, referenceNote='GreenOverlay: 75 px-es oldalsávok (00FF79). ' + SHOT),
        flash('i20-green-r', sx + sw - 3 - 75 * s, sy, 75 * s, sh, '#00FF79', .82),
        flash('i20-red', cx - 425 * s / 2, sy, 425 * s, sh, '#C90E05', .96, z=3, referenceNote='RedOverlay: középső 425 px-es sáv (C90E05). ' + SHOT),
        label('i20-rpm-label', 'RPM', cx - 190, sy + 35 * s + 20, 110, 60, '#1571B1', 34),
        readout('i20-rpm', 'rpm', cx - 80, sy + 35 * s, 270, 92, '#ffffff', 78),
        readout('i20-gear', 'gear', cx - 300, sy + 150, 600, 520, '#02FEFF', 500, weight=400,
                referenceNote='GearText: Sui Generis 350 px, cián (02FEFF). A játék betűtípusa nem kerül terjesztésre.'),
        readout('i20-speed', 'speed', cx - 200, sy + sh - 150, 400, 104, '#ffffff', 78),
    ]
    rows = [('tWater', 'waterTemp', 0), ('pWater', '', 0), ('tOil', 'oilTemp', 0), ('pOil', 'oilPressure', 1), ('TExh', '', 0)]
    rows2 = [('Emerg', '', 0), ('Map', 'engineMap', 0), ('Boost', 'turbo', 2), ('Shift', '', 0)]
    hidden = [label('i20h-note', 'A játékban 0 átlátszatlanságú (rejtett) bal/jobb oszlopok', 160, 50, 1280, 60, '#8a8f96', 32)]
    for n, (name, field, dec) in enumerate(rows):
        hidden += [label(f'i20h-l{n}', name, 180, 140 + n * 140, 260, 110, '#1571B1', 64),
                   readout(f'i20h-v{n}', field, 460, 140 + n * 140, 300, 110, '#ffffff', 84, decimals=dec)]
    for n, (name, field, dec) in enumerate(rows2):
        hidden += [label(f'i20h-r{n}', name, 860, 140 + n * 140, 260, 110, '#1571B1', 64),
                   readout(f'i20h-w{n}', field, 1140, 140 + n * 140, 280, 110, '#ffffff', 84, decimals=dec)]
    return layout(pid, 'Hyundai i20 N Rally2 · Műszerfal (játékbeli widget)', vid, W, H,
                  [('Kijelző', main, pid + '-screen'), ('Rejtett mezők', hidden, pid + '-screen')], {pid + '-screen': ('png', body(W, H, screen))})

# ------------------------------------------------------------------ Volkswagen Polo GTI R5
def polo_r5():
    """WB_GaugeVolkswagenPoloGTIR5: two screens in one atlas. 'Top' (874 x 504): five rounded boxes
    (160/110/150/150/284 x 70, the last one the session timer), ignition state, final distance, RPM
    value and a 508 x 320 gear container with arched RPM bars (T_PoloGaugeRpm tinted 52D921 / FF7E00 /
    D80000) behind a yellow (DDCB21) gear. 'Bottom' (840 x 480): 3 columns x 4 rows of rounded boxes
    (Gear+RPM, Time, Speed, Trip [part.], Trip [total])."""
    vid, W, H = 'vw-polo-gti-r5', 1600, 900
    pid = vid + '-dash-040'
    yl = '#EFFF00'
    s = 1.6; tw, th = 874 * s, 504 * s; tx, ty = (W - tw) / 2, (H - th) / 2
    top_boxes = [(10, 160), (170, 110), (280, 150), (430, 150), (580, 284)]
    gx, gy, gw, gh = tx + (874 - 508) / 2 * s, ty + (504 - 100 - 320) * s, 508 * s, 320 * s
    def top(d, img):
        d.rounded_rectangle((tx - 16, ty - 16, tx + tw + 16, ty + th + 16), 30, fill=(4, 4, 5), outline=(70, 72, 76), width=4)
        d.rectangle((tx, ty, tx + tw, ty + th), fill=(0, 0, 0))
        for (bx, bw) in top_boxes:
            d.rounded_rectangle((tx + bx * s, ty + 18 * s, tx + (bx + bw) * s, ty + 88 * s), 16, outline=(235, 235, 235), width=3)
        # arched bar track (T_PoloGaugeRpm is an arc; drawn here as an original arc track)
        d.arc((gx - 40, gy + 10, gx + gw + 40, gy + gh * 2.2), 200, 340, fill=(30, 32, 34), width=int(60 * s))
    bs = 1.68; bw_, bh_ = 840 * bs, 480 * bs; bx0, by0 = (W - bw_) / 2, (H - bh_) / 2
    cols = [(0, 320), (320, 260), (580, 260)]
    def bottom(d, img):
        d.rounded_rectangle((bx0 - 16, by0 - 16, bx0 + bw_ + 16, by0 + bh_ + 16), 30, fill=(4, 4, 5), outline=(70, 72, 76), width=4)
        d.rectangle((bx0, by0, bx0 + bw_, by0 + bh_), fill=(0, 0, 0))
        for (cx0, cw) in cols:
            for r in range(4):
                fill = (235, 235, 235) if (cx0 == 320 and r == 3) else None
                d.rounded_rectangle((bx0 + (cx0 + 4) * bs, by0 + (r * 120 + 4) * bs, bx0 + (cx0 + cw - 4) * bs, by0 + (r * 120 + 116) * bs), 18,
                                    outline=(235, 235, 235), width=3, fill=fill)
    arcs = []
    for n, (color, ratio, dy) in enumerate([('#52D921', .80, .62), ('#FF7E00', .90, .38), ('#D80000', .96, .14)]):
        arcs.append(flash(f'polo-bar{n}', gx, gy + gh * dy, gw, 130 * s * .55, color, ratio,
                          referenceNote=('Green/Yellow/Red overlay a T_PoloGaugeRpm textúrával. ' + SHOT) if n == 0 else ''))
    main = arcs + [
        el('polo-gear-bkg', 'text', '', W / 2 - 115 * s, gy + gh - 260 * s, 230 * s, 260 * s, '', background='#000000', z=3),
        readout('polo-gear', 'gear', W / 2 - 115 * s, gy + gh - 260 * s, 230 * s, 260 * s, '#DDCB21', 384),
        readout('polo-timer', 'stageTime', tx + 590 * s, ty + 22 * s, 264 * s, 62 * s, yl, 64),
        label('polo-ign-title', 'Ignition', tx + 20 * s, ty + 110 * s, 140 * s, 44 * s, yl, 42),
        el('polo-ign', 'indicator', 'ignition', tx + 160 * s, ty + 108 * s, 90 * s, 48 * s, 'ON', color=yl),
        readout('polo-final', '', tx + 680 * s, ty + 106 * s, 180 * s, 52 * s, yl, 64,
                referenceNote='DistanceFinal: szakaszhossz – az ACR-adapter nem adja, ezért „—”.'),
        readout('polo-rpm', 'rpm', W / 2 - 160, gy + gh + 24, 320, 90, yl, 64),  # in the 100 px strip under the gear container
    ]
    def cell(c, r): return bx0 + (cols[c][0] + 10) * bs, by0 + (r * 120 + 10) * bs, (cols[c][1] - 20) * bs, 100 * bs
    x, y, w, h = cell(1, 0); gear_rpm = [readout('polob-rpm', 'rpm', x, y + 10, w * .62, h - 20, yl, 77), readout('polob-gear', 'gear', x + w * .62, y, w * .38, h, '#3FD01A', 131)]
    x, y, w, h = cell(1, 3); timer = [label('polob-time-t', 'Time', x, y, w * .4, 50, '#000000', 45, weight=400), readout('polob-time', 'stageTime', x, y + 50, w, h - 56, '#000000', 64)]
    x, y, w, h = cell(2, 0); speed = [readout('polob-speed', 'speed', x, y, w * .58, h, yl, 111), label('polob-speed-t', 'Speed', x + w * .6, y + 10, w * .4, 40, '#ffffff', 30), label('polob-kmh', 'Kmh', x + w * .6, y + 50, w * .4, 50, '#ffffff', 47)]
    x, y, w, h = cell(2, 1); part = [label('polob-part-t', 'Trip [part.]', x, y, w, 44, '#ffffff', 36, weight=400), readout('polob-part', 'stageDistance', x, y + 44, w * .75, h - 48, yl, 67, scale=.001, decimals=2), label('polob-part-km', 'Km', x + w * .76, y + 60, w * .24, 50, '#ffffff', 40)]
    x, y, w, h = cell(2, 2); total = [label('polob-total-t', 'Trip [total]', x, y, w, 44, '#ffffff', 36, weight=400), readout('polob-total', '', x, y + 44, w * .75, h - 48, yl, 67), label('polob-total-km', 'Km', x + w * .76, y + 60, w * .24, 50, '#ffffff', 40)]
    trip = gear_rpm + timer + speed + part + total
    assets = {pid + '-top': ('png', body(W, H, top)), pid + '-bottom': ('png', body(W, H, bottom))}
    return layout(pid, 'Volkswagen Polo GTI R5 · Műszerfal (játékbeli widget)', vid, W, H,
                  [('Felső kijelző', main, pid + '-top'), ('Alsó kijelző', trip, pid + '-bottom')], assets)

# ------------------------------------------------------------------ Peugeot 206 WRC
def peugeot_206():
    """WB_GaugePeugeot206: LCD (T_Peugeot206WRCLCD_B) with a 760 x 53 RPM bar, three shift LEDs (6700+,
    7000-7300; the first one never lights), a 300 x 460 gear box (A5A58F) with a red (FF0000) 7-segment
    gear, red (D60000) distance-from-start / time-of-day / final-distance readouts on the right and green
    (48C579) LCD tiles: GEAR, FUEL and RACE / WARM UP / PRACTICE. WATER T, OIL T, OIL P are Hidden."""
    vid, W, H = 'peugeot-206-wrc', 1600, 900
    pid = vid + '-dash-040'
    lcd_green = (0x48, 0xC5, 0x79)
    def lcd(d, img):
        d.rounded_rectangle((30, 20, W - 31, H - 21), 40, fill=(20, 20, 22), outline=(70, 72, 76), width=4)
        g = np.linspace(0, 1, H - 100)[:, None, None]
        col = np.array((172, 174, 150))[None, None, :] * (1 - g) + np.array((140, 144, 120))[None, None, :] * g
        img.paste(Image.fromarray(np.repeat(col, W - 120, axis=1).astype('uint8')), (60, 50))
        d = ImageDraw.Draw(img)
        d.rectangle((640, 150, 960, 640), fill=(0xA5, 0xA5, 0x8F))
        for (x0, x1) in [(110, 430), (470, 790), (1150, 1500)]:
            d.rounded_rectangle((x0, 690, x1, 850), 10, fill=lcd_green)
    shift = [
        el('p206-led1', 'leds', 'rpm', 1280, 64, 70, 70, 'RPM', count=1, min=19999, max=20000, palette=['#ff2a1a'], shape='circle',
           referenceNote='WB_306RPMLed_1: 19999 rpm-es küszöb – a játékban gyakorlatilag soha nem gyullad ki.'),
        el('p206-led2', 'leds', 'rpm', 1370, 64, 70, 70, 'RPM', count=1, min=6700, max=6701, palette=['#ff2a1a'], shape='circle'),
        el('p206-led3', 'leds', 'rpm', 1460, 64, 70, 70, 'RPM', count=1, min=7000, max=7001, palette=['#ff2a1a'], shape='circle',
           referenceNote='WB_306RPMLed_2: 7000-7300 rpm között világít.'),
    ]
    ink, red = '#101408', '#D60000'
    main = shift + [
        el('p206-bar', 'leds', 'rpm', 90, 70, 1160, 60, 'RPM', count=38, max=8000, palette=['#1a1e10'], offColor='#00000000', glow=False,
           referenceNote='WB_GaugeRPMBar (760 x 53) – a görbét az FC_RPMBarLanciaDeltaHFIntegraleEVO adja; itt lineáris (feltételezés).'),
        readout('p206-gear', 'gear', 650, 150, 300, 490, '#FF0000', 430, font='factory', weight=700),
        readout('p206-dist', 'stageDistance', 1040, 160, 470, 110, red, 90, font='factory', scale=.001, decimals=3),
        readout('p206-clock', 'sessionClock', 1040, 300, 470, 110, red, 90, font='factory'),
        readout('p206-final', '', 1040, 440, 470, 110, red, 90, font='factory', referenceNote='DistanceFinal: az ACR-adapter nem adja.'),
        label('p206-gear-t', 'GEAR', 120, 694, 300, 34, '#b3000000', 28),
        readout('p206-gear2', 'gear', 120, 724, 300, 120, ink, 110, font='factory'),
        label('p206-fuel-t', 'FUEL', 480, 694, 300, 34, '#b3000000', 28),
        readout('p206-fuel', 'fuel', 480, 724, 300, 120, ink, 110, font='factory'),
        label('p206-race', 'RACE', 1160, 700, 330, 46, '#cc000000', 34),
        label('p206-warm', 'WARM UP', 1160, 748, 330, 46, '#33000000', 34),
        label('p206-prac', 'PRACTICE', 1160, 796, 330, 46, '#33000000', 34,
              referenceNote='A futamtípus kiemelését a Blueprint végzi; az ACR-adapter nem adja, ezért a RACE fix.'),
    ]
    hidden = [label('p206h-note', 'A játékban rejtett LCD-mezők: WATER T, OIL T, OIL P', 160, 160, 1280, 60, '#202418', 34)]
    for n, (name, field, dec) in enumerate([('WATER T', 'waterTemp', 0), ('OIL T', 'oilTemp', 0), ('OIL P', 'oilPressure', 1)]):
        hidden += [label(f'p206h-l{n}', name, 120 + n * 460, 694, 320, 34, '#b3000000', 28),
                   readout(f'p206h-v{n}', field, 120 + n * 460, 724, 320, 120, ink, 110, font='factory', decimals=dec)]
    def lcd2(d, img):
        lcd(d, img); d = ImageDraw.Draw(img)
        d.rectangle((60, 150, W - 60, 680), fill=(156, 160, 136))
        for n in range(3): d.rounded_rectangle((110 + n * 460, 690, 450 + n * 460, 850), 10, fill=lcd_green)
    assets = {pid + '-lcd': ('png', body(W, H, lcd)), pid + '-lcd2': ('png', body(W, H, lcd2))}
    return layout(pid, 'Peugeot 206 WRC (1999) · LCD (játékbeli widget)', vid, W, H,
                  [('LCD', main, pid + '-lcd'), ('Rejtett mezők', hidden, pid + '-lcd2')], assets)

# ------------------------------------------------------------------ Subaru Impreza 555 Group A
def subaru_555(analog_elements, analog_png):
    """WB_GaugeSubaruImprezaS3 holds only the tripmeter: dark (252402) body, red LCD (2D0000) and three
    red (D60000) 7-segment readouts: time of day (174,338 / 254x92), distance from start (480,338 / 365x108)
    and final distance (174,468 / 254x94). The analogue instruments are 3D meshes and stay as before."""
    vid, W, H = 'subaru-impreza-555-gra', 1600, 900
    pid = vid + '-dash-040'
    s = 1.6; ox, oy = -16, -360  # trip body X(140)..X(880) centred, top at y=120
    def X(v): return ox + v * s
    def Y(v): return oy + v * s
    def trip(d, img):
        d.rounded_rectangle((X(140), Y(300), X(880), Y(600)), 30, fill=(0x25, 0x24, 0x02), outline=(70, 72, 76), width=4)
        d.rounded_rectangle((X(160), Y(320), X(860), Y(580)), 16, fill=(0x2D, 0, 0))
        d.text((X(160), Y(600) + 16), 'WB_GaugeSubaruImprezaS3 · tripmeter-elrendezés, saját grafika', font=_font(22), fill=(90, 92, 96))
    red = '#D60000'
    tripmeter = [
        readout('s555t-clock', 'sessionClock', X(174), Y(338), 254 * s, 92 * s, red, 100, font='factory'),
        readout('s555t-dist', 'stageDistance', X(480), Y(338), 365 * s, 108 * s, red, 110, font='factory', scale=.001, decimals=3),
        readout('s555t-final', '', X(174), Y(468), 254 * s, 94 * s, red, 100, font='factory',
                referenceNote='DistanceFinal: az ACR-adapter nem adja, ezért „—”.'),
    ]
    assets = {pid + '-analog': ('png', analog_png), pid + '-trip': ('png', body(W, H, trip))}
    return layout(pid, 'Subaru Impreza 555 Gr.A (1993) · Analóg + tripmeter (játékbeli widget)', vid, W, H,
                  [('Analóg', analog_elements, pid + '-analog'), ('Tripmeter', tripmeter, pid + '-trip')], assets)

# ------------------------------------------------------------------ pages traced from the user's reference photos
# The photos only serve as a reference: nothing of them is embedded, everything is drawn here.

def arc_gauge(i, field, x, y, w, h, maximum, arc, color='#ffffff', **extra):
    return el(i, 'analog', field, x, y, w, h, '', style='bandArc', max=maximum, arc=arc, color=color, **extra)

def peugeot_208_real_page(W=1600, H=900):
    """Colour rally display of the real car (user photo): oil temp / oil pressure arcs on the left, water
    temp arc on the right, tachometer arc with a big gear in the middle, blue rpm digits, and a bottom row
    with the map pill, the speed box and the surface pill ('Asph'). Returns (elements, png)."""
    sx, sy, sw, sh = 150, 120, 1300, 640
    green, red, yellow = '#3ad13a', '#ff2a2a', '#f2d22a'
    def art(d, img):
        d.rounded_rectangle((60, 40, W - 61, H - 41), 70, fill=(20, 20, 22), outline=(52, 54, 58), width=4)
        d.rounded_rectangle((90, 70, W - 91, H - 71), 52, fill=(12, 12, 13))
        for n in range(16):  # vent / LED row on the upper edge of the housing
            cx = 330 + n * 62; d.ellipse((cx - 7, 50, cx + 7, 64), fill=(4, 4, 5))
        for (cx, cy) in [(112, 260), (112, 640), (W - 113, 260), (W - 113, 640)]:
            d.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=(48, 50, 54)); d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(10, 10, 11))
        d.rectangle((sx - 6, sy - 6, sx + sw + 6, sy + sh + 6), fill=(30, 31, 34))
        d.rectangle((sx, sy, sx + sw, sy + sh), fill=(0, 0, 0))
        d.rounded_rectangle((390, 668, 590, 738), 14, outline=(242, 210, 42), width=4)   # Map pill
        d.rounded_rectangle((650, 668, 950, 738), 10, outline=(170, 172, 176), width=3)  # speed box
        d.rounded_rectangle((1010, 668, 1210, 738), 14, outline=(170, 172, 176), width=3)  # surface pill
        d.rectangle((1230, 470, 1430, 640), fill=(26, 27, 30))  # spare data window (right bottom)
    side = dict(width=.05, labelSize=.075, pointer='marker')
    elements = [
        label('p208r-oilt-l', 'OIL', 175, 140, 120, 56, '#ffffff', 48),
        readout('p208r-oilt', 'oilTemp', 165, 196, 170, 96, green, 90),
        label('p208r-oilt-u', '°C', 175, 292, 120, 40, '#ffffff', 34),
        arc_gauge('p208r-oilt-arc', 'oilTemp', 200, 130, 320, 250, 150, dict(side, cx=.0, cy=.5, r=.9, start=40, sweep=-80, min=50,
                  bands=[[50, 110, green], [110, 150, red]], ticks=[50, 100, 150], labels=['50', '100', '150'])),
        label('p208r-oilp-l', 'OIL', 175, 430, 120, 56, '#ffffff', 48),
        readout('p208r-oilp', 'oilPressure', 165, 486, 170, 96, green, 90, decimals=1),
        label('p208r-oilp-u', 'bar', 175, 582, 120, 40, '#ffffff', 34),
        arc_gauge('p208r-oilp-arc', 'oilPressure', 200, 420, 320, 250, 10, dict(side, cx=.0, cy=.5, r=.9, start=40, sweep=-80,
                  bands=[[0, 1.5, red], [1.5, 10, green]], ticks=[0, 5, 10], labels=['0', '5', '10'])),
        label('p208r-wat-l', 'WAT', 1300, 140, 140, 56, '#ffffff', 48),
        readout('p208r-wat', 'waterTemp', 1290, 196, 160, 96, green, 90),
        label('p208r-wat-u', '°C', 1305, 292, 130, 40, '#ffffff', 34),
        arc_gauge('p208r-wat-arc', 'waterTemp', 1080, 130, 320, 250, 120, dict(side, cx=1.0, cy=.5, r=.9, start=140, sweep=80, min=40,
                  bands=[[40, 100, green], [100, 120, red]], ticks=[40, 80, 120], labels=['40', '80', '120'])),
        arc_gauge('p208r-tach', 'rpm', 520, 140, 560, 500, 7000, dict(cx=.5, cy=.62, r=.5, width=.035, start=195, sweep=150, labelSize=.065,
                  bands=[[0, 6100, '#d8d8d8'], [6100, 7000, red]], ticks=list(range(0, 7001, 1000)), labels=[str(n) for n in range(8)], needleFrom=.62),
                  color=red, referenceNote='Fordulatszám-ív a felhasználó fotója alapján; a piros mező 6100 rpm-től (a játék 208-as váltásjelzőjével egyezően).'),
        readout('p208r-gear', 'gear', 690, 300, 220, 250, '#ffffff', 270, weight=700),
        readout('p208r-rpm', 'rpm', 690, 560, 220, 70, '#3c78ff', 64),
        label('p208r-map-l', 'Map', 400, 674, 100, 58, yellow, 46),
        readout('p208r-map', 'engineMap', 495, 674, 80, 58, yellow, 50),
        readout('p208r-speed', 'speed', 660, 674, 170, 58, '#ffffff', 52),
        label('p208r-kmh', 'km/h', 830, 680, 110, 46, '#cfd2d6', 36),
        readout('p208r-surface', 'driveMode', 1020, 674, 180, 58, '#cfd2d6', 46,
                referenceNote='A fotón „Asph” (aszfalt). A burkolatválasztónak nincs ACR-adatmezője, ezért élesben „—”.'),
    ]
    return elements, _png_body(W, H, art)

def _png_body(W, H, art):
    img = Image.new('RGB', (W, H), (8, 8, 9)); art(ImageDraw.Draw(img), img); return _png(img)

def skoda_car_info_page(W=1280, H=800):
    """'Car Info' page of the real Fabia RS Rally2 display (user photo): nEng / Gear / sCar on top,
    IGN SYNC ERR USB status pills, a temperature list (tExh green, tWater blue highlight), Map/Boost/
    LC Limiter box, a pressure/electrics list and the page tab bar. Returns (page dict, assets)."""
    ox, oy, sw, sh = 70, 70, 1140, 640
    def X(f): return ox + f * sw
    def Y(f): return oy + f * sh
    left_rows = [('nChrgr', '', 'rpm', 0, None), ('tExh', '', '°C', 0, (0x8b, 0xd6, 0x4a)), ('tOil', 'oilTemp', '°C', 1, None),
                 ('tWater', 'waterTemp', '°C', 1, (0x7e, 0xc8, 0xf2)), ('tGbx', 'gearboxTemp', '°C', 1, None), ('tReDiff', '', '°C', 1, None)]
    right_rows = [('pRail', '', 'bar', 1), ('pFuel', '', 'bar', 2), ('pOil', 'oilPressure', 'bar', 1), ('pReDiffClutch', '', 'bar', 1),
                  ('vBatt', '', 'V', 2), ('iPbuTotal', '', 'A', 1)]
    row_h = .068
    def art(d, img):
        d.rounded_rectangle((20, 20, W - 21, H - 21), 18, fill=(70, 72, 76), outline=(110, 112, 116), width=3)  # anodised bezel
        for (cx, cy) in [(42, 260), (42, 540), (W - 43, 260), (W - 43, 540)]:
            d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=(20, 20, 22))
        d.rectangle((ox - 8, oy - 8, ox + sw + 8, oy + sh + 8), fill=(10, 10, 11))
        d.rectangle((ox, oy, ox + sw, oy + sh), fill=(0, 0, 0))
        box = (32, 33, 36)
        d.rounded_rectangle((X(.02), Y(.02), X(.33), Y(.17)), 10, fill=box)
        d.rounded_rectangle((X(.58), Y(.02), X(.98), Y(.15)), 10, fill=box)
        d.rounded_rectangle((X(.58), Y(.17), X(.96), Y(.33)), 10, fill=box)
        for n, (_, _, _, _, hi) in enumerate(left_rows):
            y0 = Y(.30 + n * row_h)
            d.rounded_rectangle((X(.02), y0, X(.33), y0 + row_h * sh - 6), 6, fill=hi or box)
        for n in range(len(right_rows)):
            y0 = Y(.35 + n * row_h)
            d.rounded_rectangle((X(.58), y0, X(.98), y0 + row_h * sh - 6), 6, fill=box)
        for n in range(4):  # ERR pill stays dark; the others light up from telemetry elements
            x0 = X(.02 + n * .078); d.rounded_rectangle((x0, Y(.20), x0 + .07 * sw, Y(.26)), 22, fill=(40, 41, 44))
        d.line((X(.02), Y(.985), X(.08), Y(.985)), fill=(90, 210, 80), width=5)
    elements = [
        label('skc-neng-l', 'nEng', X(.12), Y(.025), X(.23) - X(.12), 36, '#d8d8d8', 30, weight=400),
        readout('skc-neng', 'rpm', X(.06), Y(.065), X(.29) - X(.06), 70, '#f2d22a', 62),
        label('skc-gear-l', 'Gear', X(.40), Y(.03), X(.51) - X(.40), 40, '#d8d8d8', 32, weight=400),
        readout('skc-gear', 'gear', X(.37), Y(.08), X(.54) - X(.37), 210, '#ffffff', 200, weight=700),
        label('skc-scar-l', 'sCar', X(.72), Y(.025), X(.84) - X(.72), 36, '#d8d8d8', 30, weight=400),
        readout('skc-scar', 'speed', X(.65), Y(.055), X(.91) - X(.65), 66, '#f2d22a', 62, decimals=1),
        label('skc-map-l', 'Map', X(.61), Y(.18), 150, 32, '#e8e8e8', 30, weight=400),
        readout('skc-map', 'engineMap', X(.89), Y(.18), 36, 32, '#000000', 28, background='#8bd64a', shape='rounded'),
        label('skc-boost-l', 'Boost', X(.61), Y(.225), 150, 32, '#e8e8e8', 30, weight=400),
        readout('skc-boost', '', X(.85), Y(.225), 90, 32, '#e8e8e8', 30),
        label('skc-lc-l', 'LC Limiter', X(.61), Y(.27), 190, 32, '#e8e8e8', 30, weight=400),
        readout('skc-lc', 'launchRpmLimit', X(.82), Y(.27), 130, 32, '#e8e8e8', 30),
    ]
    for n, (name, ok, field) in enumerate([('IGN', True, 'ignition'), ('SYNC', True, 'engineRunning'), ('ERR', False, ''), ('USB', False, '')]):
        x0 = X(.02 + n * .078)
        if ok:
            elements.append(label(f'skc-pill-{name.lower()}', name, x0, Y(.20), .07 * sw, .06 * sh, '#ffffff', 26, background='#ff5a2a', shape='rounded',
                                  visibleWhen={'field': field, 'op': '>=', 'value': 1}))
        else:
            elements.append(label(f'skc-pill-{name.lower()}', name, x0, Y(.20), .07 * sw, .06 * sh, '#cfd2d6', 26))
    for n, (name, field, unit, dec, hi) in enumerate(left_rows):
        y0 = Y(.30 + n * row_h); ink = '#101010' if hi else '#e8e8e8'
        elements += [label(f'skc-l{n}', name, X(.03), y0 + 2, 110, row_h * sh - 10, ink, 28, weight=400),
                     readout(f'skc-lv{n}', field, X(.18), y0 + 2, 90, row_h * sh - 10, ink, 28, decimals=dec),
                     label(f'skc-lu{n}', unit, X(.27), y0 + 2, 60, row_h * sh - 10, ink, 24, weight=400)]
    for n, (name, field, unit, dec) in enumerate(right_rows):
        y0 = Y(.35 + n * row_h)
        elements += [label(f'skc-r{n}', name, X(.59), y0 + 2, 200, row_h * sh - 10, '#e8e8e8', 28, weight=400),
                     readout(f'skc-rv{n}', field, X(.83), y0 + 2, 90, row_h * sh - 10, '#e8e8e8', 28, decimals=dec),
                     label(f'skc-ru{n}', unit, X(.92), y0 + 2, 50, row_h * sh - 10, '#e8e8e8', 24, weight=400)]
    tabs = ['Car\nInfo', 'Chassis\nInfo', 'Engine\nInfo', 'Stage\nInfo', 'Chassis\nValues', 'Engine\nValues', 'Engine\nTest', 'Devices\nStatus', 'Devices\nCurrent', 'Mask\nError', 'Alarm\nInfo']
    for n, tab in enumerate(tabs):
        color = '#6fdc5a' if n == 0 else '#e8e8e8' if n < 4 else '#5c5f64'
        elements.append(label(f'skc-tab{n}', tab, X(.015 + n * .088), Y(.885), .085 * sw, .095 * sh, color, 20, weight=400))
    elements[0]['referenceNote'] = ('A valódi Fabia RS Rally2 kijelzőjének „Car Info” oldala a felhasználó fotója alapján. '
                                    'A játék nem ad nChrgr, tExh, tReDiff, pRail, pFuel, pReDiffClutch, vBatt, iPbuTotal és Boost értéket: ezek „—”.')
    png = _png_body(W, H, art)
    page = {'id': 'skoda-fabia-rs-rally2-dashboard-carinfo', 'name': 'Car Info (valós kijelző, fotó alapján)',
            'elements': [{'id': 'skc-body-img', 'kind': 'image', 'field': '', 'label': 'Ház', 'x': 0, 'y': 0, 'w': W, 'h': H, 'assetId': 'skc-body',
                          'border': False, 'fit': 'fill', 'nightDim': True, 'z': 0, 'locked': True}] + elements}
    return page, {'skc-body': ('png', png)}
