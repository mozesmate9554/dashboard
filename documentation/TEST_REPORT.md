# TEST_REPORT – SIM CONTROL STUDIO 0.4.0 Alpha

Build: [GitHub Actions run 41716176406](https://github.com/mozesmate9554/dashboard/actions/runs/41716176406) · commit `8f3977c` · ág `feature/sim-control-studio-0.4.0-alpha` · 2026-11-03

## Letöltések (GitHub-bejelentkezés szükséges)

| Csomag | Link |
|---|---|
| **Android APK** (aláírt release) | https://github.com/mozesmate9554/dashboard/actions/runs/41716176406/artifacts/13270566755 |
| **Windows Bridge** (telepítő + hordozható EXE) | https://github.com/mozesmate9554/dashboard/actions/runs/41716176406/artifacts/13270840383 |
| Előnézetek (mind a 6 műszerfal minden oldala, 6 Button Box nappal/éjjel) | https://github.com/mozesmate9554/dashboard/actions/runs/41716176406/artifacts/13269597955 |

## Automatizált tesztek – lefutottak, sikeresek ebben a runban

| Teszt | Eredmény |
|---|---|
| `flutter analyze` | **No issues found** |
| Flutter unit- és widgettesztek | **24/24 sikeres** |
| Profil- és natívprojekt-validáció (`validate_profiles.py`) | **13/13 sikeres** |
| Windows Bridge-tesztek (.NET, Windows runner) | **23/23 sikeres** |
| Android release APK build és aláírás | sikeres |
| Windows telepítő build, csendes telepítés, WinForms-indítás | sikeres |
| Android-emulátor (natív TLS, Keystore, érintéses DEMO) | **a jelentés írásakor még futott** – eredménye a run oldalán |
| iOS szimulátor és aláírás nélküli build | **a jelentés írásakor a macOS-sorban várt** – eredménye a run oldalán |

Ebben a körben új vagy módosult:
- A felhasználói referenciafotók alapján: Škoda középkonzol (gombafejű gombok), Škoda „Car Info” oldal, 208 „Valós kijelző” oldal – mind a valódi Flutter-renderelővel ellenőrizve.
- Bridge: leállításkor egy már lezárt kliens bezárása nem dob többé `ObjectDisposedException`-t (a CI átviteli benchmarkja egyszer elakadt rajta).
- Mind a 6 műszerfal **minden oldala** a valódi Flutter-renderelővel készül el (előnézet-artifact). A tesztek ellenőrzik, hogy minden elrendezés érvényes és a vásznon belül van.
- A teljes képernyős (adaptív) nézet a játékhű LED-sorokat egy sorba rendezi; a teszt 6 autó × álló/fekvő tájolásra fut.
- Az editor-teszt a Škoda új, játékbeli kijelzőoldalán a „Map” jelvényt mozgatja, átméretezi, visszavonja és menti; a gyári elrendezés változatlan marad.
- Bridge: a léptető világításgomb a beállított ideig nyomva tartja a billentyűt; a kézifék kapcsolatvesztéskor felengedődik.

## Nem automatizálható – élő ellenőrzés szükséges

Ezek **nem** lettek igazolva:
- A játékbeli hatás (világítás, távfény, index, kézifék, motortérkép) valódi Assetto Corsa Rally alatt.
- A játék `CycleLights` ciklusának lépésszáma.
- A játék által küldött `vehicleId` értékek, vagyis hogy az automatikus autófelismerés élesben talál-e.
- A műszerfalak futás közbeni színei és a váltásjelző küszöbök egy része (i20, Polo, Škoda): a Blueprint-logika nem exportálható, ezek feltételezések.
- Élő ACR alatt az adapter csak sebességet, fordulatszámot, fokozatot, pedálokat, G-erőt, fordulatszám-limitet és autóazonosítót ad. A többi kijelzőmező (Map, hőmérsékletek, trip, kézifék, világítás) **„—”** lesz; DEMO módban mindegyik szimulált értéket mutat.
- Fizikai Android-telefon Wi-Fi-n, a hangok késleltetése és a haptika valódi eszközön.
- Fizikai iPhone/iPad: nincs eszköz és Apple-aláírás.

Ellenőrzőlista a próbához: `TELEPITES_0.4.0.md`, 4. pont.
