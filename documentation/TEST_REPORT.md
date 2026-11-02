# TEST_REPORT – SIM CONTROL STUDIO 0.4.0 Alpha

Build: [GitHub Actions run 41494732335](https://github.com/mozesmate9554/dashboard/actions/runs/41494732335) · commit `50a9d18` · ág `feature/sim-control-studio-0.4.0-alpha` · 2026-11-02

## Letöltések (GitHub-bejelentkezés szükséges)

| Csomag | Link |
|---|---|
| **Android APK** (aláírt release, 75,7 MB) | https://github.com/mozesmate9554/dashboard/actions/runs/41494732335/artifacts/13166751431 |
| **Windows Bridge** (telepítő + hordozható EXE) | https://github.com/mozesmate9554/dashboard/actions/runs/41494732335/artifacts/13166880212 |
| Előnézetek (6 Button Box nappal/éjjel, 6 műszerfal) | https://github.com/mozesmate9554/dashboard/actions/runs/41494732335/artifacts/13164804562 |
| Android-emulátor bizonyítékok | https://github.com/mozesmate9554/dashboard/actions/runs/41494732335/artifacts/13166198137 |

## Automatizált tesztek – lefutottak, sikeresek

| Teszt | Eredmény |
|---|---|
| `flutter analyze` | **No issues found** |
| Flutter unit és widget tesztek | **24/24 sikeres** |
| Profil- és natívprojekt-validáció (`validate_profiles.py`) | **33/33 sikeres** |
| Windows Bridge-tesztek (.NET, Windows runner) | **23/23 sikeres**, köztük az új „0.4.0 Rally actions: cycle lights, high beam, indicators, handbrake hold” |
| Android release APK build és aláírás | sikeres |
| Windows telepítő build, telepítés és WinForms-indítási füstteszt | sikeres |
| Android 16 emulátor: natív TLS, Keystore, telemetria, érintéses DEMO-parancs, rendszersávok | sikeres |
| iOS szimulátor és aláírás nélküli ARM64 build | **a jelentés írásakor a macOS runner sorában várt**; az eredmény a fenti run oldalán látható |

Új tesztek a 0.4.0-ban:
- Mind a 6 autó minden mechanikus kezelőszerve valódi DEMO-parancsot küld. A fedeles kapcsoló fedelének nyitása nem küld parancsot. A tartott gombok `down` után `up` parancsot küldenek. DEMO-ban sosem jelenik meg „JÁTÉK IGAZOLTA”.
- LED-logika: csak érvényes telemetria igazolhat állapotot.
- Autófelismerés: csak explicit alias alapján.
- Bridge: a léptető világításgomb a beállított ideig lenyomva tartja a billentyűt. A kézifék kapcsolatvesztéskor felengedődik.
- A 0.3.0 Škoda-konzol változatként változatlanul működik (a meglévő 16 vezérlős teszt).
- Adaptív, hibrid és teljes képernyős nézetek mind a 25 autóra, álló és fekvő tájolásban.

## Nem automatizálható – élő ellenőrzés szükséges

Ezek **nem** lettek igazolva:
- A játékbeli hatás (világítás, távfény, index, kézifék, motortérkép) valódi Assetto Corsa Rally alatt.
- A játék `CycleLights` ciklusának lépésszáma.
- A játék által küldött `vehicleId` értékek, vagyis hogy az automatikus autófelismerés élesben talál-e.
- Fizikai Android-telefon Wi-Fi-n, a hangok késleltetése és a haptika valódi eszközön.
- Fizikai iPhone/iPad: nincs eszköz és Apple-aláírás.

Ellenőrzőlista a ma esti próbához: `TELEPITES_0.4.0.md`, 4. pont.
