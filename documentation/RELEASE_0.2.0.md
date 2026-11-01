# SIM CONTROL STUDIO 0.2.0

A meglévő 0.1.0 projekt folytatása, az eredeti 20 autóval és 40 külön alapelrendezéssel. Natív Flutter mobilalkalmazás és .NET 10 Windows Bridge.

Letölthető fájlok ezen a kiadási oldalon:

- `SIM_CONTROL_STUDIO_0.2.0.apk`: Android 7.0+ alkalmazás.
- `SIM_CONTROL_STUDIO_0.2.0_Setup_x64.exe`: felhasználói Windows x64 telepítő.
- `SIM_CONTROL_STUDIO_0.2.0_Windows_x64.zip`: hordozható Windows-változat.
- `SIM_CONTROL_STUDIO_0.2.0_RELEASE.zip`: alkalmazások, profilok, teljes forrás, Git-előzmény, magyar útmutatók, teszteredmények és fájlonkénti SHA-256 manifest.
- `SIM_CONTROL_STUDIO_0.2.0_Source.zip`: forrás és visszaállítható Git bundle.
- `SHA256SUMS.txt`: a kiadási fájlok ellenőrzőösszegei.

Újdonságok: külön jelölt helyi és Bridge DEMO, autónkénti billentyűkiosztás, párhuzamos parancsfogadás, biztonságos gomb-életciklus, aktív profil/késleltetés az eszközlistában, szerkesztőbeli igazítás és átlátszóság, valóban frissülő előnézet, bővített automatizált tesztek és helyi TLS-teljesítménymérés.

Az APK-t a GitHub Actions valóban lefordítja, az aláírását ellenőrzi. A Windows CI telepíti a Bridge-et és ellenőrzi a főablak indulását. Az adott kiadáshoz tartozó pontos eredmények a teljes csomag `Tests` és `Documentation/STATUS.json` állományaiban vannak.

Kipróbálás PC nélkül: a mobilos varázslóban válaszd a DEMO lehetőséget, vagy a Kezdőlapon kapcsold be a DEMO módot. A szimulált műszereket és vezérlést állandó DEMO felirat különbözteti meg az élő játéktól.

A konkrét Assetto Corsa Rally-verzió, a Windows-bemenet játékhatása és két fizikai telefon Wi-Fi-kapcsolata még éles ellenőrzést igényel. A két tesztkliens szoftveres kliens. A 30/60 Hz hálózati mérés nem mobil FPS-mérés. A 20 autó közül 1 részleges referencia, 19 inspirált; nincs hitelesített gyári replika. Aláírt iOS IPA nem készült.

A preview APK aláírókulcsa CI-futásonként változhat. Másik futásból származó APK telepítése előtt exportáld a saját profiljaidat; eltérő aláírás esetén a korábbi alkalmazás eltávolítása szükséges. Saját, tartós kiadási kulcs beállítása: a forrás `documentation/ANDROID.md` útmutatója szerint.
