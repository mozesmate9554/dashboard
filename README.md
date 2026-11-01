# SIM CONTROL STUDIO 0.1.0

Natív Flutter műszerfal és kezelőpanel, külön C# / .NET 10 LTS Windows PC Bridge-dzsel. A futó rendszer helyi hálózaton működik, felhő, előfizetés és regisztráció nélkül.

**Ez ellenőrizhető fejlesztői kiadás, nem a teljes specifikáció minden pontjának készre jelentése.** A Windows x64 kiadás lefordult. A Bridge automatizált tesztjei valódi helyi TLS/WebSocket kapcsolaton is futnak. Az Android/iOS forrás és natív projektek elkészültek, de ebben a környezetben Flutter fordítás nem történt. APK és aláírt IPA nincs a csomagban.

Az átadás tényleges tartalmát a `documentation/STATUS.json`, az elvégzett ellenőrzéseket a `tests/results/` rögzíti. A `documentation/ELSO_INDITAS.md` vezeti végig az első éles tesztet.

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

- Rally: valódi Windows shared memory olvasó; a két megadott projekt tényleges forrása ellenőrizve, rögzített commitokkal. Nincs véletlenadat-generátor a termékben.
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

Az utolsó három parancs a kiadási környezetben **nem futott le**. A Dart szintaxis tree-sitter ellenőrzése nem típusellenőrzés, nem Flutter-fordítás és nem widgetteszt.
