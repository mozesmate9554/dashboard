# Android – build, letöltés és telepítés

A projekt verziója **0.2.0+2**, alkalmazásazonosítója `hu.simcontrol.studio`; minimum Android 7.0 / API 24. A natív Flutter-projekt a `mobile_flutter` könyvtárban maradt.

A letölthető alkalmazás kiadási oldala: https://github.com/mozesmate9554/dashboard/releases/tag/v0.2.0

Az **Assets** listából a `SIM_CONTROL_STUDIO_0.2.0.apk` fájlt töltsd le. Telefonon nyisd meg, és a saját fájlkezelődnek/böngésződnek engedélyezd az alkalmazástelepítést. A fejlesztői változat kézi telepítésű; nincs Google Play regisztráció vagy előfizetés.

## Igazolható build

Workflow: `.github/workflows/android.yml`, GitHubon: https://github.com/mozesmate9554/dashboard/actions

A build Flutter **3.35.7**, JDK 17 és GitHub által biztosított Android SDK alatt fut. A műveletsor: függőségek, 25 profil-/projektellenőrzés, szigorú `flutter analyze`, valódi `flutter test`, release APK, `apksigner verify`, APK-metaadatok és SHA-256, majd artifact-feltöltés. Sikertelen ellenőrzés után nem kerül készre jelentésre APK. A verziózott kiadás csak sikeres Android- és Windows-job után csomagol.

Köztes futásból: nyisd meg az adott sikeres **Android APK and project checks** futást; az **Artifacts** szakaszban a `SIM_CONTROL_STUDIO-Android-<commit>` ZIP tartalmazza az `app-release.apk` fájlt. Az artifact letöltéséhez GitHub-bejelentkezés kellhet, és 30 napig őrződik. A kiadási oldalon közzétett APK állandóbb letöltési hely.

A helyi Linux környezetben nincs Flutter/Android SDK; a hivatalos SDK-letöltést a hálózati szabályzat tiltja. A tényleges buildet az engedélyezett GitHub CI végzi. A pontos sikeres futást és forráscommitot a kiadási csomag `Tests/Android-CI/provenance.json` rögzíti.

## Aláírás és frissítés

Ha nincs beállított repository secret, a CI egy futáson belül használt preview kulcsot hoz létre. Ez valódi, ellenőrzött APK-aláírás, de másik futás másik kulcsot használhat. Az előző app ilyenkor nem frissíthető helyben: előbb **exportáld a személyes profiljaidat**, majd távolítsd el az előző appot, és telepítsd az újat. Az eltávolítás törli az app saját adatait.

Tartós, saját kulcshoz a repository Actions secrets közé állítsd be az `ANDROID_KEYSTORE_BASE64` és `ANDROID_KEYSTORE_PASSWORD` értékeket. Kulcsalias: `simcontrol`; a kulcs és keystore jelszava egyezzen. A privát kulcs nem kerül a forrásba, artifactba vagy kiadási ZIP-be. Helyi buildnél a `tools/build-android.ps1` és a `SIMCONTROL_KEYSTORE`, `SIMCONTROL_KEYSTORE_PASSWORD` környezeti változók használhatók.

## Első használat

A beállítási varázslóban választható a **DEMO** PC és játék nélkül. Később a Kezdőlapon és a Beállításokban kapcsolható. A DEMO felirata a teljes képernyős műszeren és a szerkesztőben is látható; a parancsok szimulált állapotot módosítanak.

Valódi használathoz ugyanazon a privát LAN-on futó Windows Bridge szükséges. A QR-kamera opcionális: kézi IP/tanúsítvány/token-párosítás is van. A hiányzó játékadat helyén `—` látható. Az interkomgomb PC-parancsot küld, nem készít hangfelvételt. A tényleges fizikai mobil-, kamera-, biztonságos tároló- és Wi-Fi-teszt külön elfogadási lépés; lásd `TESZTELES.md`.
