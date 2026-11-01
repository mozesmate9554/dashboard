# Külső összetevők és referenciák

## Windows kiadásban szereplő összetevők

- .NET 10.0.14 / ASP.NET Core / Windows Desktop runtime: Microsoft/.NET Foundation, a hozzájuk tartozó licenc és harmadik fél közlemények a `licenses` könyvtárban vannak. A build SDK 10.0.403 volt.
- QRCoder 1.6.0: MIT, Raffael Herrmann. Eredeti repository `codebude/QRCoder`, mai kanonikus hely `Shane32/QRCoder`; a NuGet csomag által megadott commit `bd980577640c47f8bb881cf24c8443415a579d36`. A pontos MIT közlemény mellékelve.
- Gradle wrapper 8.11.1: Apache License 2.0. A hivatalos wrapper JAR a natív Android projektben van; a kiadási disztribúció ellenőrzőösszege a wrapper properties fájljában szerepel.

## Telemetriareferenciák

A `LuizZak/AssettoCorsaRallyTelemetryReader` MIT közleménye megőrizve. A `decnet100/acr_telemetry` PolyForm Noncommercial projekt összehasonlítási referencia; a Rust kódját a csomag nem tartalmazza, és arra nem linkel futó függőségként. A pontos olvasott commitok és a levezetés határai a `TELEMETRY.md` dokumentumban vannak.

BeamNG OutGauge forrás: [gyártói protokolldokumentáció](https://documentation.beamng.com/modding/protocols/), ellenőrizve 2026-11-01. Saját C# csomagdekóder; nem átvett Lua modul. A gyártói dokumentáció néhány mezőt nem implementáltnak jelöl; például az olajnyomás nem kerül élő adatként megjelenítésre. Beállítás: Options → Other → Protocols → OutGauge; cél a Bridge gépen `127.0.0.1`, alap UDP 4444.

## Mobil forrás függőségei

A közvetlen Flutter/Dart csomagok verzióit a `pubspec.yaml` rögzíti: shared_preferences, flutter_secure_storage, file_picker, mobile_scanner, wakelock_plus, flutter_svg, crypto, path_provider, share_plus, cross_file. A kiválasztott verziók SDK-korlátait a pub.dev csomagmetaadatából ellenőriztük. A forráscsomag nem tartalmazza e könyvtárak teljes letöltött implementációját vagy még nem létező APK-ját. Egy későbbi natív kiadás licencnézete és beágyazott plugin-közleményei a ténylegesen feloldott függőségeket is vegyék figyelembe.

A PDF áttekintő generálásához ReportLab és beágyazott DejaVu Sans betű szolgált; a DejaVu közlemény külön mellékelve. A PDF a saját JSON-elrendezések vektoros dokumentációja, nem gyártói fénykép vagy Flutter képernyőkép.

## Autónevek és grafika

A modellek neve szöveges azonosítás. Nincs átvett gyári logó, kereskedelmi betűkészlet, képernyőgrafika vagy fénykép a profilokban. Az SVG-k és alapkompozíciók saját rajzok. A hűségi állapot nem minősül gyártói jóváhagyásnak. Autónként külön `REFERENCES.md` jelzi, mit támaszt alá az adott forrás és mi maradt nem igazolt.
