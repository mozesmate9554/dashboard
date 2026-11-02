# Ellenőrzött kiadás és letöltés – 0.3.0

A **[csomagoló és átadó workflow sikeres](https://github.com/mozesmate9554/dashboard/actions/runs/41370703992)**. Az alkalmazás forrása: `4293ce2be082bf15e150b75b8225a89e3dad1f6a`, címkéje `v0.3.0`.

## Közvetlen letöltések

- [Android APK ZIP](https://github.com/mozesmate9554/dashboard/actions/runs/41370703992/artifacts/13108574855) – csomagold ki, majd nyisd meg a **SIM_CONTROL_STUDIO_0.3.0.apk** fájlt.
- [iOS-build és telepítési útmutató](https://github.com/mozesmate9554/dashboard/actions/runs/41370703992/artifacts/13109073070) – tényleges Simulator app és aláírás nélküli ARM64 release app.
- [Škoda-előnézetek és referencia-összehasonlítás](https://github.com/mozesmate9554/dashboard/actions/runs/41370703992/artifacts/13109157611) – 2560×1776 és 2200×3076 Flutter-render, két nagy összehasonlító PNG és gyártói fotós PDF.
- [Teljes kiadás](https://github.com/mozesmate9554/dashboard/actions/runs/41370703992/artifacts/13109207305) – Android, Windows x64 telepítő/EXE, iOS-build, forrás/Git bundle, 20 profil, dokumentáció, naplók és képernyőképek.

**GitHub-bejelentkezés szükséges.** Megőrzés: 2027. január 31-ig. A GitHub Releases létrehozását a rendelkezésre álló jogosultság HTTP 403-mal visszautasította; ezért a működő Actions-letöltéseket adjuk át, nem egy késznek állított Releases-oldalt.

## Tényleges ellenőrzések

**21 Flutter-, 26 adat/projekt- és 22 Bridge-teszt sikeres**, analyzer-jelzés nélkül. Mind a négy natív job sikeres: Android release APK és aláírás; Windows fordítás/telepítés/WinForms-indítás; iOS Simulator és aláírás nélküli ARM64 release build; natív Android 16 emulátor.

Androidon és az iPhone 16 Pro szimulátoron sikeres a rögzített TLS, biztonságos titoktároló, telemetria, érintéses DEMO-parancs és visszacsatlakozás. Mindhárom kijelző szerepkör álló és fekvő helyzetben tesztelt; Androidon a rendszersávok tényleges rejtését is lekérdeztük. Az iOS-build környezete Xcode 16.4 (16F6). A hálózati automatizálás loopback és jelölt DEMO, nem fizikai Wi-Fi vagy élő játék.

**Fizikai iPhone-teszt, aláírt IPA és TestFlight nincs.** Saját Apple-aláírás és macOS/Xcode szükséges a saját iPhone-os telepítéshez. A kézikönyv ezt és a későbbi TestFlight-folyamatot külön leírja.

A Škoda két új, külön szerkeszthető felülete fotóalapú rekonstrukció. Kormánygrafika nem készült; a 16 konzolvezérlő működését érintéses DEMO-teszt ellenőrzi. A másik 19 profil és a Rally-dekódoló/Windows inputvezérlő fájljai változatlanok. [Forrás- és hash-bizonyíték](MEGORZES_0.3.0.md).

A felhasználó a meglévő Android–Windows–Rally rendszer éles működéséről számolt be. A 0.3.0 újratelepítése utáni fizikai regresszió még felhasználói próba. **Android-eltávolítás előtt exportáld személyes elrendezéseidet**; a preview-aláírás miatt újratelepítés és új párosítás válhat szükségessé.

Részletek: [STATUS.json](STATUS.json), [iOS](IOS.md), [Android](ANDROID.md), [teljes képernyő](TELJES_KEPERNYO_0.3.0.md), [Škoda-referenciák](SKODA_REKONSTRUKCIO_0.3.0.md), [fizikai elfogadás](TESZTELES.md). A teljes ZIP saját Documentation/STATUS.json fájlja a CI-ben generált részletes buildjelentés; ez az oldal a végleges átadási helyeket is rögzíti.
