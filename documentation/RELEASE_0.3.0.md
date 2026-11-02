# SIM CONTROL STUDIO 0.3.0

A meglévő projekt folytatása: iOS-kompatibilitás, teljes képernyő és a Škoda Fabia RS Rally2 két részletes új felülete. A 20 autó megmaradt; a többi 19 grafikai profil változatlan. A Rally telemetriaadapter és a Windows-bemeneti vezérlő forrását nem módosítottuk.

## Letöltés

- **Android:** `SIM_CONTROL_STUDIO_0.3.0.apk`.
- **Windows:** `SIM_CONTROL_STUDIO_0.3.0_Setup_x64.exe` vagy `SIM_CONTROL_STUDIO_0.3.0_Windows_x64.zip`.
- **iOS szimulátor:** `SIM_CONTROL_STUDIO_0.3.0_iOS_Simulator.zip`.
- **iPhone ARM64 fordítás:** `SIM_CONTROL_STUDIO_0.3.0_iOS_Unsigned_NotInstallable.zip` – aláírás nélkül nem telepíthető fizikai iPhone-ra.
- **Előnézetek:** `SIM_CONTROL_STUDIO_0.3.0_Skoda_Previews.zip`, illetve `SKODA_REFERENCE_COMPARISON_0.3.0.pdf`.
- **Minden forrás és bizonyíték:** `SIM_CONTROL_STUDIO_0.3.0_RELEASE.zip`; külön Source ZIP és `SHA256SUMS.txt` is elérhető.

**Android-frissítés előtt exportáld a személyes profiljaidat.** Saját tartós signing secret nélkül a preview APK futásonként más aláírókulcsot kap; az előző app eltávolítása és újrapárosítás válhat szükségessé. A törlés az app saját adatait is törli. A Windows Bridge felhasználói konfigurációja és azonosítói megmaradnak.

## Elkészült

Valódi Xcode-szimulátorbuild, telepítés/indítás és aláírás nélküli ARM64 release fordítás. A natív teszt TLS-párosítást, Keychain-titokmentést, telemetriát, érintéses DEMO-parancsot és mentett hitelesítéssel visszacsatlakozást vizsgál. Mindhárom kijelző szerepkör álló/fekvő helyzetben kap natív ellenőrzést és képernyőképet.

Androidon natív rendszersáv-rejtés, iOS-en státuszsáv-rejtés és Home-jelző auto-hide; biztonságos kijelzőterületek, ébren tartás és visszaállítás kilépéskor. Az adaptív nézet a sűrű tartalmat lapozható, olvasható műszer-/gombcsoportokra bontja. Az eredeti geometria és a személyes másolatok továbbra is választhatók.

A Škoda vezetői kijelzője és külön középkonzolja gyártói fotókból készült. Tizenhat interaktív konzolvezérlő, külön szerkeszthető SVG-grafika és parancskötés; kormánygrafika nélkül. A font, a pixelgeometria és a nem igazolható kapcsolófunkciók rekonstrukcióként vannak jelölve. Két nagy felbontású valódi Flutter-render, két összehasonlító kép, PDF és eredetjegyzék jár a kiadáshoz.

## Ellenőrzés és korlát

A közzétételhez a Flutter analyzer, unit/widget render- és szerkesztőtesztek, a 22 Windows Bridge-regresszió, profil/hash/projektellenőrzések, APK-fordítás/aláírás, Windows telepítés/indítás, natív Android-emulátor és iPhone-szimulátor tesztjeinek sikeresnek kell lennie. Az aktuális futás azonosítója, commitja, tesztszámai és a környezet a mellékelt **STATUS.json** fájlban; a teljes ZIP `Tests` mappájában naplók és képernyőképek.

**Nincs fizikai iPhone-teszt, aláírt IPA vagy TestFlight.** Apple Developer-tagság nincs a projekthez. iPhone-ra saját macOS/Xcode/Apple-aláírás szükséges; az `IOS.md` lépésről lépésre leírja a szimulátoros és saját eszközös telepítést, valamint a későbbi TestFlight-feltöltést.

Az automatizált mobilkapcsolati tesztek loopback és jelölt szintetikus DEMO-forrást használnak; nem bizonyítanak fizikai Wi-Fi-t vagy játékhatást. A felhasználó már működő éles Android–Windows–Rally használatról számolt be; a 0.3.0 telepítése utáni valódi készülékes regressziós próba még szükséges. További autók részletes grafikája és új játékadapterek nem részei ennek a körnek.
