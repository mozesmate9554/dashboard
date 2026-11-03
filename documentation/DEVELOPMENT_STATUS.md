# DEVELOPMENT_STATUS – 0.4.0 Alpha

Frissítve: 2026-11-03. A fejlesztés innen bármikor folytatható.

## Állapot

| Terület | Állapot | Megjegyzés |
|---|---|---|
| Projektforrás | ✅ | GitHub `mozesmate9554/dashboard`, ág: `feature/sim-control-studio-0.4.0-alpha` |
| Játékfájl-vizsgálat | ✅ | FModel (UE5.6 + usmap), csak olvasás: kapcsolópanel-textúrák és 47 kijelző-widget JSON; részletek: `GAME_ASSET_REFERENCE_REPORT.md` |
| Internetes referenciák | ✅ 1. kör | `VEHICLE_REFERENCE_REPORT.md` |
| Világításhiba | ✅ kódban javítva | élő játékban még ellenőrizni kell |
| Škoda Button Box | ✅ | mechanikus kezelőszervek, hang, haptika, LED, éjszakai mód |
| Másik 5 autó | ✅ játékhű változat | kezelőpanel a `T_IntDetails_B` textúrák, műszerfal a `WB_Gauge*` widgetek alapján |
| Bridge | ✅ | új akciók, tesztek; verzió 0.4.0 |
| Android APK | CI-ben | lásd `TEST_REPORT.md` |
| iOS | CI-ben | szimulátor és aláírás nélküli build; fizikai teszt nincs |

## Hogyan épül fel

- `tools/build_040.py` – a 0.4.0 katalógus: Škoda Button Box, panelháttér-textúrák. A 19 régi autó bájtra azonos marad.
- `tools/build_040_cars.py` – az öt további autó kezelőpanele.
- `tools/build_040_gauges.py` – mind a hat műszerfal a játékbeli widgetek elrendezése szerint.
- `tools/build_switch_sounds.py` – a hét kapcsolóhang szintézise.
- `mobile_flutter/lib/premium_controls.dart` – a mechanikus kezelőszervek, a LED-logika és a hangok.

Újragenerálás: `python3 tools/build_switch_sounds.py && python3 tools/build_040.py && python3 tests/validate_profiles.py`

## Következő lépések

1. Élő ACR-teszt: világítás-ciklus lépésszáma, `vehicleId` értékek (autófelismerés), Bridge-billentyűk.
2. Élő képernyőképpel ellenőrizni a nem exportálható, futás közben beállított színeket és váltásjelző küszöböket (i20, Polo, Škoda).
3. Ha az ACR telemetria ad szakaszhosszt, a `DistanceFinal` mezők bekötése.
4. Felhasználói gombméret- és hangválasztás a szerkesztőben (az adatmodell már támogatja: `sound`, `ledColor`, `material`).
