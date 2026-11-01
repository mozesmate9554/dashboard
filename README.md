# SIM CONTROL STUDIO 0.2.0

Natív Flutter műszerfal és kezelőpanel, külön .NET 10 Windows Bridge-dzsel. A rendszer helyi hálózaton működik. Az eredeti 0.1.0 forrás és Git-előzmény megmaradt; a kiadás 20 autót és 40 külön alapelrendezést tartalmaz.

**Letöltés:** https://github.com/mozesmate9554/dashboard/releases/tag/v0.2.0

Android APK, Windows x64 telepítő és hordozható ZIP, teljes kiadási ZIP, forrás/Git bundle és SHA-256 ellenőrzőösszegek. A végleges kiadás az Android- és Windows CI sikeréhez kötött; futások: https://github.com/mozesmate9554/dashboard/actions

Új funkciók: külön jelölt DEMO PC nélkül; autónkénti billentyűkiosztás; folyamatos parancsfogadás hosszabb lenyomás közben; stabil gomb-életciklus; aktív autó/elrendezés és késleltetés az eszközlistában; szerkesztőbeli igazítás, átlátszóság és élő előnézet.

Első használat: `documentation/ELSO_INDITAS.md`. A kiadás pontos bizonyítékai: `STATUS.json`, `FUNKCIOMATRIX_0.2.0.md`, a teljes csomag `Tests` mappája. Fizikai játék-/telefonos elfogadás még szükséges; a DEMO és a két szoftveres TLS-kliens tesztje nem ilyen bizonyíték. iOS-forrás van, aláírt IPA nincs. A gyári grafikai hűség nem hitelesített.

## Könyvtárak

| Könyvtár | Tartalom |
|---|---|
| `mobile_flutter/` | Natív Android/iOS alkalmazás, adatmodell, helyi tárolás, kapcsolati kliens, műszerek, szerkesztő |
| `windows_bridge/Bridge.Core/` | Telemetriaadapterek, TLS/WebSocket, párosítás, vezérlőmotor |
| `windows_bridge/Bridge.Windows/` | WinForms kezelőfelület, rendszertálca, QR, diagnosztika, kiosztáskezelés |
| `windows_bridge/Bridge.Headless/` | Konzolos technikai host; Linuxon nincs Windows-memóriaolvasás és SendInput |
| `vehicle_profiles/` | 20 verziózott autóprofil, 40 alapelrendezés, autónkénti referenciajegyzék |
| `shared_protocol/` | A verziózott hálózati szerződés |
| `game_adapters/` | Modulhatárok és a további játékok bővítési pontjai |
| `tests/` | Automatizált Bridge-tesztek és adatellenőrzési eredmények |
| `tools/` | Katalógusgenerátor és reprodukálható buildszkriptek |
| `documentation/` | Magyar telepítési, protokoll-, tesztelési és állapotdokumentáció |

## Rövid műszaki állapot

- Rally: valódi Windows shared memory olvasó; a két megadott projekt tényleges forrása ellenőrizve, rögzített commitokkal. A valós adapter nem használ szimulált értékeket. A külön DEMO mindig megjelölt szintetikus forrás.
- Alapmezők: sebesség, RPM, fokozat, gáz, fék, nyers kormányérték, G-vektor. Staticsból autó/pálya/verzió/RPM-limit, ha rendelkezésre állnak. Minden mező saját érvényességet és időbélyeget kap.
- A Rally további ACC-szerű mezői **nem válnak automatikusan támogatottá**. ABS/TC/fékerőelosztás/szakaszidő visszaolvasása jelenleg nem igazolt.
- Több kliens, visszacsatlakozás, profilajánlás, tanúsítványhoz rögzített TLS, 120 másodperces párosítás, visszavonható készülékjogosultságok.
- SendInput billentyű és kombináció, press/hold/repeat, fókuszellenőrzés, közös módosítóbillentyűk tulajdonlása, kapcsolatvesztési és időkorlátos felengedés.
- 40 külön adatként létrehozott, eltérő geometriájú alapelrendezés. A 19 inspirált és 1 részleges referenciájú profil **nem hitelesített gyári replika**.
- AC, ACC és BeamNG OutGauge kódolt adapter, fizikai játékellenőrzés nélkül. A többi felsorolt játékhoz dokumentált bővítési pont van.

## Build

Windows forrásból, telepített .NET 10 SDK-val:

```powershell
./tools/build-windows.ps1
```

Android: Flutter 3.35 vagy újabb kompatibilis SDK, JDK 17+, Android SDK és kiadási aláírókulcs szükséges. A buildszkript előbb analizál és tesztel, csak utána fordít APK-t:

```powershell
./tools/build-android.ps1
```

iOS: macOS, Xcode, CocoaPods, Flutter, saját Apple aláírás/provisioning szükséges. Részletek: `documentation/IOS.md`.

## Ellenőrzés

```sh
dotnet run --project tests/Bridge.Tests/Bridge.Tests.csproj -c Release -- tests/results/bridge-tests.json
python3 tests/validate_profiles.py
cd mobile_flutter
flutter pub get
flutter analyze
flutter test
```

A GitHub workflow ugyanezeket az ellenőrzéseket futtatja, majd aláírt release APK-t készít. Windows alatt a natív tesztek, self-contained fordítás, NSIS telepítés és főablak-indítás is ellenőrzött. A részletes korlátok a `documentation/ISMERT_HIBAK.md` fájlban szerepelnek. A preview APK más CI-futásból történő frissítéséhez lásd az `ANDROID.md` aláírási megjegyzését.
