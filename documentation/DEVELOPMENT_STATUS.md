# DEVELOPMENT_STATUS – 0.4.0 Alpha

Frissítve: 2026-11-02. A fejlesztés innen bármikor folytatható.

## Állapot

| Terület | Állapot | Megjegyzés |
|---|---|---|
| Projektforrás | ✅ | GitHub `mozesmate9554/dashboard`, ág: `feature/sim-control-studio-0.4.0-alpha` |
| Játékfájl-leltár | ✅ csak nevek | `GAME_ASSET_REFERENCE_REPORT.md`; FModel-export nem történt |
| Internetes referenciák | ✅ 1. kör | `VEHICLE_REFERENCE_REPORT.md` |
| Világításhiba | ✅ kódban javítva | élő játékban még ellenőrizni kell |
| Škoda Button Box | ✅ | mechanikus kezelőszervek, hang, haptika, LED, éjszakai mód |
| Másik 5 autó | ✅ első változat | saját műszerfal és panel; játékbeli képernyőképekkel pontosítandó |
| Bridge | ✅ | új akciók, tesztek; verzió 0.4.0 |
| Android APK | CI-ben | lásd `TEST_REPORT.md` |
| iOS | CI-ben | szimulátor és aláírás nélküli build; fizikai teszt nincs |

## Hogyan épül fel

- `tools/build_040.py` – a 0.4.0 katalógus: Škoda Button Box, panelháttér-textúrák. A 19 régi autó bájtra azonos marad.
- `tools/build_040_cars.py` – az öt további autó műszerfala és panele.
- `tools/build_switch_sounds.py` – a hét kapcsolóhang szintézise.
- `mobile_flutter/lib/premium_controls.dart` – a mechanikus kezelőszervek, a LED-logika és a hangok.

Újragenerálás: `python3 tools/build_switch_sounds.py && python3 tools/build_040.py && python3 tests/validate_profiles.py`

## Következő lépések

1. Élő ACR-teszt: világítás-ciklus lépésszáma, `vehicleId` értékek (autófelismerés), Bridge-billentyűk.
2. Játékbeli képernyőképek a `SIM_CONTROL_STUDIO_REFERENCES/*/Cockpit_Screenshots` mappákba, majd a műszerfalak pontosítása.
3. Ha engedélyezett: FModel-vizsgálat (UE 5.4, IoStore) csak referenciaként.
4. Prémium műszerfalak (vektoros keretek, éjszakai kijelzőmód) a Škoda után a többi autóra.
5. Felhasználói gombméret- és hangválasztás a szerkesztőben (az adatmodell már támogatja: `sound`, `ledColor`, `material`).
