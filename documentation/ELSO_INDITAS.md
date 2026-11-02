# Első indítás és éles teszt

## 1. Windows

1. Futtasd a `SIM_CONTROL_STUDIO_0.3.0_Setup_x64.exe` telepítőt, vagy csomagold ki a `Windows` könyvtárat egy írható helyre. A `SimControlStudio.Bridge.exe` és `profiles.json` maradjon együtt.
2. Indítsd el a Bridge EXE-t. A mellékelt kiadás önálló, nem igényel külön .NET fejlesztői környezetet.
3. Válaszd az **Assetto Corsa Rally** adaptert. Alapértelmezett TCP-port: **19760**.
4. Válaszd ki a PC tényleges Ethernet/Wi-Fi IPv4-címét, majd jelöld be a **Helyi hálózat engedélyezése** mezőt. Az első alapbeállítás csak `127.0.0.1` címen figyel; ezt a mobil nem éri el.
5. Indítsd el a Bridge-et. A Windows tűzfal felugró kérdésénél a saját privát hálózatodra engedélyezd a programot. A telepítő nem nyit automatikusan tűzfalszabályt. Szükséges bejövő TCP: 19760; opcionális felderítéshez UDP: 19761.
6. A jobb felső ablakbezárás és a minimalizálás a rendszertálcára rejti az alkalmazást. Teljes leállítás: tálca → **Kilépés**.

Helyi állományok: `%LOCALAPPDATA%\SimControlStudio`. A `bridge.json` a kiosztásokat, a `devices.json` kizárólag a készülékek titkainak hashét, a `bridge.pfx` a Bridge saját TLS-kulcsát tartalmazza. Ezek nem kerülnek a diagnosztikai exportba. A fájlok a saját Windows-fiók könyvtárjában vannak; a PFX-et ne oszd meg.

## 2. Android és iOS

Android APK: a GitHub kiadási oldal Assets listájában `SIM_CONTROL_STUDIO_0.3.0.apk`. A letöltés és az aláírás/frissítés részletei: `ANDROID.md`. iOS-hez tényleges szimulátoros és aláírás nélküli ARM64 build, forrás és Xcode-útmutató van (`IOS.md`), aláírt IPA nincs.

PC nélküli kipróbálás: a varázslóban válaszd a **DEMO** gombot; később a Kezdőlap DEMO kapcsolójával is bekapcsolhatod. A teljes képernyőn és a szerkesztőben is látható a DEMO jelölés. A szimulált parancs nem jut a Windows bemenetéhez. Valódi játékhoz kapcsold ki a DEMO módot.

A ténylegesen elkészített, aláírt mobilkiadás telepítése után:

1. Indítsd el a mobilalkalmazást. Válassz nyelvet.
2. A PC-n nyisd meg a **QR-párosítás** ablakot. A token 120 másodpercig érvényes, nem kerül felderítési válaszba vagy naplóba.
3. A mobilon olvasd be a QR-kódot, és ellenőrizd, hogy a teljes SHA-256 tanúsítványujjlenyomat egyezik a PC-n láthatóval.
4. Ha a kamera vagy felderítés nem elérhető, másold át a teljes `simcontrol://pair?...` hivatkozást. Kézzel IP, port, ujjlenyomat és átmeneti token is megadható.
5. Válassz Műszerfal, Kezelőpanel vagy Hibrid szerepet, majd autóprofilt.
6. A készüléktitok Android titkosított tárolóba / iOS Keychainbe kerül. Újraindításkor a mobil a mentett Bridge-hez újracsatlakozik.

Az automatikus felderítés a hálózat broadcast-támogatásától függ. A felderített ujjlenyomatot is össze kell vetni a PC-vel. iOS alatt a broadcast-felderítés további Apple multicast-jogosultságot igényelhet; a kézi IP/QR-kapcsolat az elsődleges tartalékút.

## 3. Első valódi Rally-adatok

1. Ne futtasd egyszerre az AC-t, ACC-t és Rallyt: közös shared-memory neveket használhatnak, ezért a Bridge ilyenkor elutasítja a bizonytalan forrást.
2. Indítsd el a Rallyt és egy tényleges vezetési munkamenetet.
3. A Bridge **Rally diagnosztika** oldalán ellenőrizd: játék felismerve, memória elérhető, állapot `live`, változó sebesség/RPM/fokozat.
4. A támogatott folyamatnevek alapértéke `acr`, `acr-Win64-Shipping`. Ha más a valódi futó EXE neve, a Bridge leállítása után állítsd be a `bridge.json` `rallyProcessNames` tömbjében a pontos kiterjesztés nélküli folyamatnevet. Ne egy tetszőleges másik programot válassz.
5. A telefonon nyisd meg a műszerfalat. Gázadásra, fékezésre és váltásra az értékeknek a játékkal együtt kell változniuk.
6. Ellenőrizd külön a fokozatkódolást: a v1 adapter `0=R, 1=N, 2=1` nyers kiosztást használ. Ha az adott Rally-verzió ettől eltér, ne használd megtévesztő értékkel: exportálj diagnosztikát és javítsd az adaptert.

A felhasználó már működő éles Android–Windows–Rally rendszerről számolt be. A 0.3.0 telepítése utáni regressziós próba a saját környezetében még szükséges. Az adapter implementációjának létezése és a bináris mintatesztek sikere nem bizonyítja egy nem futtatott játékverzió működését.

## 4. Második mobil és profilpár

Párosíts egy második készüléket, és válassz Kezelőpanel szerepet. Az első mobilon választott profilról a Bridge a másodiknak profilajánlást küld; a Kezdőlapon egy érintéssel elfogadható. Ez kézi ajánlás, nem gyárinak állított, ismeretlen autóazonosító-heurisztika. A kézi profilválasztás mindig megmarad.

A játékból kapott autóazonosító megjelenik a telemetriában. Az automatikus autóváltáshoz a konkrét játékverzióban igazolt aliaslista még hiányzik; jelenleg nincs önkényes részszavas párosítás.

## 5. Tényleges gombvezérlés

1. Először olvasási módban ellenőrizd a telemetriát.
2. A játékban rendelj egy egyszerű billentyűt az ott ténylegesen létező funkcióhoz.
3. A Bridge **Játékvezérlés** lapján rendeld ugyanazt a billentyűt az adott művelethez, például `lights → L`. A lap tetején választhatsz játékalapértelmezést vagy konkrét autóazonosítót. Az elmentett autókiosztás a teljes alapértelmezést felülírja; új autókiosztás induláskor a játék aktuális sorait mutatja, mentéskor lesz külön példány. A példában az L nem gyári Rally-kiosztás: neked kell a játékban is beállítani.
4. `press`: egyszeri billentyű; `hold`: lenyomás/felengedés; `repeat`: legfeljebb 3 másodperces, helyileg konfigurált ismétlés. A mobil `hold` eleméhez `hold` vagy `repeat` Bridge-kiosztás tartozzon.
5. A Bridge **Eszközök** lapján engedélyezd a második készülék vezérlését. Ezután jelöld be a globális Mobilvezérlés mezőt.
6. Vidd előtérbe a valódi játékot, majd nyomd meg a mobilgombot. A diagnosztikában először `received`, majd `executed` vagy indokolt `rejected` jelenik meg.
7. Az `executed` azt igazolja, hogy a Bridge elküldte a Windows-bemenetet. A játékban történt változást külön ellenőrizd; aktuális állapotként a kijelző csak valódi visszaolvasott mezőt mutat.

A mobilon a szürke gomb hiányzó hozzárendelést, kapcsolatot, engedélyt vagy feltételt jelezhet. Egy valódi autó gombjának jelenléte nem jelenti, hogy azt a kiválasztott játék is vezérelhető funkcióként kínálja.

Fékerőelosztás/ABS/TC esetén csak a játék támogatott növelés/csökkentés parancsait rendeld hozzá. A csúszka is relatív léptetést küld; nem ír be kitalált abszolút százalékot. A Rally v1 ezek tényleges állapotát nem jelenti vissza.

Ha a játék rendszergazdaként fut, a normál jogosultságú Bridge bemenetét a Windows elutasíthatja. Használd őket azonos, lehetőleg normál jogosultsági szinten. Az alkalmazás nem kér automatikus emelést, nem injektál a játékba és nem módosít játékfolyamat-memóriát.

## 6. Frissítés és helyreállítás

A Bridge leállítása után cseréld az EXE-t és a profilazonosítókat tartalmazó JSON-t. A LocalAppData állományok megmaradnak. A mobil frissítését ugyanazzal az aláírókulccsal kell készíteni. A Bridge minden új indításkor kikapcsolja a globális mobilvezérlést.

Ha a mobilon törlöd a mentett hitelesítést, a PC-n is vond vissza a régi készülék párosítását, mielőtt ugyanazzal az eszközazonosítóval új tokent használsz. Ha változik a PC IP-címe, a teljes kézi címet frissítsd, az ujjlenyomatot ellenőrizd. Tanúsítványcsere után új párosítás szükséges.
