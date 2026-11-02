# SIM CONTROL STUDIO 0.3.0

Natív Flutter műszerfal, kezelőpanel és hibrid kijelző, külön .NET 10 Windows Bridge-dzsel. A meglévő projekt, Git-előzmény, 20 autó és 40 alapelrendezés megmaradt. A másik 19 autó grafikai fájljai változatlanok.

**[Letöltés és kiadási bizonyítékok](https://github.com/mozesmate9554/dashboard/actions/workflows/release-verified.yml)** · [Buildfutások](https://github.com/mozesmate9554/dashboard/actions)

A 0.3.0 három fejlesztése: valódi iOS-build és szimulátoros natív kapcsolatellenőrzés; Android/iOS teljes képernyő adaptív álló/fekvő nézetekkel; Škoda Fabia RS Rally2 vezetői kijelző és külön középkonzol fotóalapú, interaktív rekonstrukciója. Kormánygrafika nem része az új Škodának. A DEMO, az autónkénti kiosztás, az élő kapcsolat és a személyes elrendezésszerkesztő megmaradt.

| Kiadás | Használat |
|---|---|
| Android APK | Kézi telepítés; [útmutató és frissítés előtti profilmentés](documentation/ANDROID.md) |
| Windows x64 telepítő / portable ZIP | Bridge és helyi játékbillentyűkiosztás; [első indítás](documentation/ELSO_INDITAS.md) |
| iOS Simulator ZIP | Valódi `.app` kompatibilis macOS/Xcode-szimulátorhoz |
| iOS Unsigned ZIP | Valódi ARM64 release build, **aláírás nélkül nem telepíthető iPhone-ra** |
| Škoda Previews ZIP / összehasonlító PDF | Két nagy felbontású Flutter-render és gyártói fotóval összevetés |
| Teljes release / Source ZIP | Forrás, Git bundle, profilok, dokumentáció és tesztbizonyítékok |

**Aláírt IPA, TestFlight és fizikai iPhone-teszt nincs.** A felhasználó ellenőrzött iOS-buildet és telepítési útmutatót kért Apple-tagság nélkül; ennek megfelelő a szimulátoros és aláírás nélküli kiadás. Saját iPhone-ra Xcode és saját Apple-aláírás kell: [IOS.md](documentation/IOS.md).

A felhasználó működő éles Android–Windows–Assetto Corsa Rally rendszerről számolt be. Az adapter és a bemeneti vezérlő forrása a 0.3.0-ban változatlan; regressziós tesztek védik. A fejlesztői automatizálás loopback hálózaton, bináris mintákkal és jelölt DEMO-val fut; nem helyettesít új fizikai játék-/Wi-Fi-próbát. Hiányzó telemetria `—`, nem kitalált nulla.

Részletek: [kiadási leírás](documentation/RELEASE_0.3.0.md), [teljes képernyő](documentation/TELJES_KEPERNYO_0.3.0.md), [Škoda-referenciák](documentation/SKODA_REKONSTRUKCIO_0.3.0.md), [tesztek](documentation/TESZTELES.md). A kiadás `STATUS.json` fájlja a konkrét buildből generált eredmény; a korábbi bizonyítékok a `documentation/history/` könyvtárban maradtak.

A letöltések a legutóbbi sikeres **Package verified SIM CONTROL STUDIO 0.3.0** futás **Artifacts** listájában vannak. Külön APK-, iOS-, Škoda-előnézet- és teljes csomag tölthető le, GitHub-bejelentkezéssel, 90 napos megőrzéssel. A GitHub Releases létrehozó API HTTP 403-at adott a rendelkezésre álló jogosultsággal; ezért nincs készre jelentett Releases-oldal. A `v0.3.0` címke a ténylegesen fordított alkalmazásforrást azonosítja.

## Forrásból

Flutter **3.35.7**, Androidhoz JDK 17 és Android SDK, iOS-hez macOS/Xcode/CocoaPods. Windows Bridge: **.NET 10**. A `.github/workflows/android.yml` fordít, tesztel, ellenőrzi az APK-aláírást és a Windows-telepítőt; natív iOS-szimulátoros és Android-emulátoros integrációt futtat. A verziózott kiadás minden platformellenőrzés sikerét megköveteli.

```sh
python3 tests/validate_profiles.py
dotnet run --project tests/Bridge.Tests -c Release -- tests/results/bridge-tests.json
cd mobile_flutter
flutter pub get
flutter analyze
flutter test
```

Windows build: `tools/build-windows.ps1`; Android: `tools/build-android.ps1`; iOS: `tools/build-ios.sh`. A `tools/generate_profiles.py` a régi 19 profilt és az önállóan karbantartott új Škodát együtt állítja elő. A profilfájlok a `vehicle_profiles`, a verziózott v1 protokoll a `shared_protocol` könyvtárban találhatók.
