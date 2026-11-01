# Telemetriaadapterek – bizonyíték és korlát

## Megvizsgált Rally-referenciák

1. [LuizZak/AssettoCorsaRallyTelemetryReader](https://github.com/LuizZak/AssettoCorsaRallyTelemetryReader/tree/8bb26990def38ffd0e4afe71e04e85e5ddeb3670), commit `8bb26990def38ffd0e4afe71e04e85e5ddeb3670`. Ténylegesen elolvasva: GameConnectionController, SharedMemoryReader, Physics, StaticInfo, MIT licenc. A forrás `Local\acpmf_physics` és `Local\acpmf_static` neveket nyit meg. A Physics 4 bájtos igazítású, az UTF-16 statics mezők 2 bájtos karakterek.
2. [decnet100/acr_telemetry](https://github.com/decnet100/acr_telemetry/tree/eaef0f29c6712a2e0dbc3bfd8246b84dcdbb9586), commit `eaef0f29c6712a2e0dbc3bfd8246b84dcdbb9586`. Ténylegesen elolvasva: LICENSE, README, physics/graphics/statics leírások és parserek, ACCSharedMemory, Graphics and statics feljegyzés. A könyvtár három blokkot nyit meg: 800 bájt physics, 1588 bájt graphics, 784 bájt statics. A leírás több helyen ACC-szerződést ír le; ez önmagában nem bizonyítja, hogy a Rally minden mezőt kitölt.

Ellenőrzés dátuma: 2026-11-01. Ezek közösségi implementációk, nem a jelen játékverzió helyett elvégzett fizikai mérés. A második projekt PolyForm Noncommercial 1.0.0 licencű; **nem épült be és nem került átmásolásra a Rust implementációja**. A protokollt leíró tények összevetésre szolgáltak. Az első projekt MIT közleménye a `licenses/` mappában szerepel. A SIM CONTROL STUDIO olvasója önálló, explicit bájteltolásos C# implementáció.

## Rally v1 mezők

| Mező | Physics eltolás | Típus / átalakítás | Éles bizonyíték állapota |
|---|---:|---|---|
| packet ID | 0 | int32 LE | Referenciakód, mintateszt |
| throttle | 4 | float32, 0..1 | Referenciakód, mintateszt |
| brake | 8 | float32, 0..1 | Referenciakód, mintateszt |
| gear | 16 | int32 − 1; −1=R, 0=N | Referenciakonvenció, éles Rally-váltóellenőrzés szükséges |
| rpm | 20 | int32 | Referenciakód, mintateszt |
| steering | 24 | float32, nyers egység | Nem állítunk ellenőrizetlen fok/radián konvenciót |
| speed | 28 | float32 km/h | Referenciakód, mintateszt |
| gX/gY/gZ | 44/48/52 | float32 g, nyers tengelynevek | Referenciakód, fizikai tengelykonvenció még ellenőrizendő |

Statics: `carModel` 68, `track` 134, `ACVersion` 30 (UTF-16LE), `maxRpm` 412. Üres szöveg és nulla RPM-limit nem minősül rendelkezésre álló adatnak. A játékos nevéhez tartozó byteszakasz nem kerül a protokollba vagy exportba.

A Rally olvasó a teljes 800/784 bájtos blokkokat kísérli meg megnyitni, a graphics első 176 bájtját opcionálisan olvassa. A graphics mezőket Rally-időmérőnek **nem** nevezi át bizonyíték nélkül. A blokk elérhetősége a diagnosztika `memoryBlocks` részében látható; az opcionális statics/graphics hiánya nem állítja le a fizika alapmezőit.

A bemeneti NaN, infinity, lehetetlen sebesség/RPM/fokozat elutasításra kerül. Az egyedi hibás pedál/G-érték `invalid`, nem numerikus nulla. Az olvasó két másolatot és előtte/utána packet ID-t vet össze, legfeljebb három próbálkozással. Ez csökkenti a közben frissített lapból származó kevert minta kockázatát, de a játék által biztosított atomikus reader-lock nem áll rendelkezésre.

A nulla első packet ID érvényes. Csak új packet ID jelent új mintát; azonos ID mellett nem frissítjük kitaláltan az időbélyeget. 500 ms adatcsend után a Bridge elavultnak jelöli a mintát; a mobil saját, monoton órás 600 ms érkezési ellenőrzést is használ. Az opcionális adatok hiánya, a játék menüje vagy leállása nem vezet szimulált kitöltéshez.

## További kódolt adapterek

AC és ACC: külön adapterpéldány/azonosító az azonos memóriacsalád explicit dekóderével. Kiegészítő mezők és a graphics prefix köradatai engedélyezettek, tartományellenőrzéssel. Ez strukturális támogatás, nem minden autón/munkamenetben megtörtént élő teszt. A Rally ezeket nem örökli automatikusan.

BeamNG: loopback UDP OutGauge fogadó, 92/96 bájt, `beam` fejléc. m/s → km/h és fokozatkonverzió számított mezőként szerepel. A forrás a helyi BeamNG folyamat futását is ellenőrzi. A konkrét BeamNG-verzió OutGauge engedélyezését és csomagkiosztását a felhasználónál még ellenőrizni kell; hálózati, tetszőleges külső csomagforrás nem engedélyezett.

AC EVO, iRacing, AMS2, rF2, LMU, F1, EA WRC, DiRT Rally 2.0, RaceRoom, Forza, Project CARS, ETS2, ATS: nincs működő adapter készre jelentve. Bővítési pontok a `game_adapters/README.md` dokumentumban.

## Session és online használat

Az adapter nem szűr eleve offline/gyakorló módra. Amely munkamenetben a játék valódi, friss, megengedett telemetriát ad a megnyitott API-n, azt továbbítja. Ez **nem** bizonyíték valamennyi lehetséges Rally-játékmód létezésére vagy az online használat engedélyezésére. Replay, spectator és online állapot nem kerül kitalálásra. A kompatibilitási mátrixban minden fizikai munkamenetteszt jelenleg `not_run`.
