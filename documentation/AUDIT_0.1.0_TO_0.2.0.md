# 0.2.0 előtti projektellenőrzés

A meglévő 0.1.0 Git repositoryból folytatjuk a munkát. A baseline commit és a kiadási ZIP ellenőrizve; új projekt nem készült. A 18 Bridge-teszt újrafutott, a 25 adat/projektellenőrzés sikeres. A Windows-futtatás, Flutter-fordítás és fizikai játék/eszközellenőrzés ebből nem következik.

| Terület | Funkció | Auditállapot | Bizonyíték / hiány |
|---|---|---|---|
| Bridge | Rally byte-offset dekóder, sebesség/RPM/fokozat/pedálok | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | Hiányzó és elavult mezők megkülönböztetése | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | Hibás/NaN bináris adatok elutasítása | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | Első nulla packet ID, ismétlődés, újraindulás | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | TLS WebSocket hitelesítés és ujjlenyomat | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | Két hálózati kliens párhuzamos telemetriája | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | Kliens bontása és hitelesített újracsatlakozása | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | Tokenes párosítás és SHA-256 készüléktitok-tárolás | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | Jogosultság-visszavonás | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | Parancsok ismétlődés- és sorrendvédelme | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | Billentyűfelengedés bontás/fókuszvesztés esetén | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | Módosítóbillentyűk közös tulajdonlása | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | Ismételt input hibavisszajelzése | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Bridge | Bridge konfiguráció validálása és tárolása | Kész és tesztelt | 18 sikeres újrafuttatott .NET teszt; szintetikus bináris minták és loopback TLS. Windows/játék fizikai bizonyíték ebből nem következik. |
| Fizikai ellenőrzés | Windows SendInput tényleges játékhatás | Külső környezet miatt nem ellenőrizhető | Linux környezet, nincs futó játék vagy fizikai eszköz.  |
| Fizikai ellenőrzés | Rally named mapping és az aktuális játékverzió | Külső környezet miatt nem ellenőrizhető | Linux környezet, nincs futó játék vagy fizikai eszköz.  |
| Fizikai ellenőrzés | Két fizikai mobil Wi-Fi-n | Külső környezet miatt nem ellenőrizhető | Linux környezet, nincs futó játék vagy fizikai eszköz.  |
| Fizikai ellenőrzés | Windows WinForms felület és tálca futtatása | Külső környezet miatt nem ellenőrizhető | Linux környezet, nincs futó játék vagy fizikai eszköz.  |
| Fizikai ellenőrzés | iPhone/iPad natív futás | Külső környezet miatt nem ellenőrizhető | Linux környezet, nincs futó játék vagy fizikai eszköz.  |
| Fizikai ellenőrzés | Android fizikai futás | Külső környezet miatt nem ellenőrizhető | Linux környezet, nincs futó játék vagy fizikai eszköz.  |
| Bridge | Profillal elkülönített billentyűkiosztások | Hiányzik | Configuration.Bindings csak gameId szerint tárol.  |
| Bridge | Parancsfogadás lenyomási idő alatti késleltetése | Részlegesen működik | BridgeRuntime a fogadó ciklusban awaiteli az egész press időt. Hosszú nyomás mellett késik más parancs és heartbeat. |
| Bridge | Eszközlista aktív szerep/profil/késleltetés | Részlegesen működik | Clients csak DeviceId/Name/Role/Hz/LatencyMs; nincs aktív profil a nézetben.  |
| Bridge | Telepítő | Részlegesen működik | Portable EXE + PowerShell parancsikontelepítő. Nincs önálló telepítő EXE. |
| Mobil | Natív Flutter projekt Android/iOS | Kész, de még nem tesztelt | Dart szintaxis ellenőrizve, teljes natív projektfájlok. Flutter analyze/test/build korábban nem futott. |
| Mobil | Műszerfal / kezelőpanel / hibrid szerep | Kész, de még nem tesztelt | Kódolt nézetek és külön mentett hibridmodell. Natív build és widgetteszt hiányzik. |
| Mobil | QR és kézi IP-párosítás | Kész, de még nem tesztelt | Mobilklienst nem futtattuk; a szerver protokollját teszteltük.  |
| Mobil | Helyi és biztonságos mobilbeállítás-tárolás | Kész, de még nem tesztelt | SharedPreferences + secure storage forrás. Valódi vagy SDK-s mobilteszt szükséges. |
| Mobil | DEMO mód | Hiányzik | Nincs külön offline demó vagy Bridge demóforrás.  |
| Mobil | Élő és szimulált adat egyértelmű elválasztása | Részlegesen működik | Nincs DEMO, ezért a szükséges külön jelölés/kapu sem létezik.  |
| Profilok | 20 eredeti autóazonosító és 40 külön elrendezés | Kész és tesztelt | 25 adat/projektellenőrzés; geometriai aláírások, mezők és SVG-k validálva.  |
| Profilok | Autónkénti gyári grafikai hűség | Részlegesen működik | 1 részleges és 19 inspirált állapot; pontos pixelgeometria egyiknél sem igazolt.  |
| Profilok | Minden alapoldal natív megjelenítése | Kész, de még nem tesztelt | Widgetteszt forrása létezik, korábban nem futott.  |
| Profilok | Gombok tényleges játékspecifikus kiosztása | Részlegesen működik | Alapértelmezésben üres, biztonságos Bridge-kiosztás. A felhasználó játékában kell hozzárendelni. |
| Szerkesztő | Új profil és másolat | Kész, de még nem tesztelt | Editor és StudioLayout implementáció; SDK-teszt hiányzik.  |
| Szerkesztő | Mozgatás/méretezés érintéssel | Kész, de még nem tesztelt | Forrás és részleges adatvalidálás; Flutter-futtatás hiányzik.  |
| Szerkesztő | Forgatás és rétegsorrend | Kész, de még nem tesztelt | Forrás és részleges adatvalidálás; Flutter-futtatás hiányzik.  |
| Szerkesztő | Rács, zárolás, név szerinti csoport | Kész, de még nem tesztelt | Forrás és részleges adatvalidálás; Flutter-futtatás hiányzik.  |
| Szerkesztő | Színek, szöveg, betűméret | Kész, de még nem tesztelt | Forrás és részleges adatvalidálás; Flutter-futtatás hiányzik.  |
| Szerkesztő | SVG/PNG import és hordozható JSON | Kész, de még nem tesztelt | Forrás és részleges adatvalidálás; Flutter-futtatás hiányzik.  |
| Szerkesztő | Undo/redo és helyi mentés | Kész, de még nem tesztelt | Forrás és részleges adatvalidálás; Flutter-futtatás hiányzik.  |
| Szerkesztő | Feltételes láthatóság/engedélyezés | Kész, de még nem tesztelt | Forrás és részleges adatvalidálás; Flutter-futtatás hiányzik.  |
| Szerkesztő | Többoldalas panelek | Kész, de még nem tesztelt | Forrás és részleges adatvalidálás; Flutter-futtatás hiányzik.  |
| Szerkesztő | Adatmező és vezérlőművelet hozzárendelése | Kész, de még nem tesztelt | Forrás és részleges adatvalidálás; Flutter-futtatás hiányzik.  |
| Szerkesztő | Élő előnézet | Részlegesen működik | Az editor nem figyeli a telemetria ValueNotifiereit; csak képernyőépítéskor olvas.  |
| Szerkesztő | Igazítási műveletek | Hiányzik | Nincs külön igazítási művelet.  |
| Szerkesztő | Átlátszóság szerkesztése | Hiányzik | Nincs opacity tulajdonság és UI.  |
| Kezelőelemek | Három-/többállású választó | Részlegesen működik | A nézetek ugyanazt a korlátlan relatív +/- felületet használják.  |
| Kezelőelemek | Állapot és parancs-visszaigazolás különbsége | Kész és tesztelt | Szerver fixture és protokolltesztek; az ACK nem játékállapot.  |
| Kezelőelemek | Nézetváltáskor tartott gomb életciklusa | Részlegesen működik | Positioned elemek kulcs nélkül; didUpdateWidget nem figyeli az elem/action váltását. A tartási időzítőt nézetváltáskor meg kell szakítani. |
| Build | Windows x64 self-contained build | Kész és tesztelt | 0.1.0 PE32+ EXE és sikeres publish napló. Futtatás Windows alatt nem történt. |
| Build | Android APK | Hiányzik | Nem volt Flutter/Android SDK; hivatalos Flutter tárhely most is HTTP 403.  |
| Build | GitHub Actions workflow | Hiányzik | Nincs .github/workflows könyvtár.  |
| Build | iOS aláírt IPA | Külső környezet miatt nem ellenőrizhető | Nincs macOS/Xcode/Apple aláírás.  |
| Teljesítmény | 30/60 FPS és Wi-Fi késleltetés | Külső környezet miatt nem ellenőrizhető | Nincs natív alkalmazás/telefonos mérés.  |
| Teljesítmény | Mérhető helyi hálózati benchmark | Hiányzik | Nincs külön benchmark, csak funkcionális tesztek.  |
| Integrációk | AC/ACC/BeamNG | Részlegesen működik | Kódolt adapterek, részben bináris tesztek; éles játékellenőrzés nincs.  |
| Integrációk | További játékok és online munkamenetek | Részlegesen működik | Bővítési pontok és not_run mátrix. Nem kész adapterek. |

Prioritás: explicit DEMO és inputtilalom; profilhoz kötött kiosztás; párhuzamos, biztonságos parancskezelés; editor életciklus, előnézet, igazítás/opacity; tényleges Android CI-fordítás; Windows telepítő és mért loopback benchmark.
