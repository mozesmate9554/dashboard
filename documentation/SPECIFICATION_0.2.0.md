# SIM CONTROL STUDIO – 0.2.0 FEJLESZTÉSI UTASÍTÁS
## Teljes projektellenőrzés, funkciók befejezése, telepíthető alkalmazások és éles tesztelhetőség

### 1. ALAPVETŐ UTASÍTÁS

Folytasd a korábban elkészített SIM CONTROL STUDIO 0.1.0 projekt fejlesztését.

**NE hozz létre új projektet, NE kezdd újra a fejlesztést, és NE cseréld le indokolatlanul a meglévő architektúrát.**

A meglévő projekt:

`/workspace/output/SIM_CONTROL_STUDIO_0.1.0_RELEASE.zip`

A ZIP tartalma a korábbi fejlesztési jelentés szerint:
- Windows x64 Bridge
- Flutter mobilalkalmazás és szerkesztő
- 40 profil-elrendezés
- Teljes forráskód
- Git-előzmények
- Magyar dokumentáció
- 18 sikeres Bridge-teszt
- 25 sikeres adat-/projektellenőrzés

Először ellenőrizd, hogy a korábbi munkaterület, forráskód és Git-repository valóban rendelkezésre áll-e.

Ha rendelkezésre áll, közvetlenül abból dolgozz.

Ha csak ZIP formában érhető el, állítsd vissza a projektet abból.

Ha egyik sem érhető el, ne állítsd, hogy a korábbi fejlesztést folytattad. Pontosan jelezd, milyen forrás hiányzik.

### 2. TELJES PROJEKTAUDIT

A fejlesztés előtt végezz részletes ellenőrzést.

Vizsgáld meg:
1. A Windows Bridge tényleges működését.
2. A Flutter alkalmazás jelenlegi állapotát.
3. A műszerfalprofilok működését.
4. A virtuális Button Box profilokat.
5. A grafikai szerkesztő tényleges képességeit.
6. A telemetria-adatfeldolgozást.
7. A Windows és mobil közötti kommunikációt.
8. A beállítások mentését és betöltését.
9. Az Assetto Corsa Rally integrációját.
10. A telepítési és terjesztési lehetőségeket.

Készíts részletes funkciómátrixot az eredeti projektkövetelmények alapján.

Minden funkcióhoz rendelj ellenőrizhető állapotot:

- Kész és tesztelt
- Kész, de még nem tesztelt
- Részlegesen működik
- Csak prototípus
- Hiányzik
- Külső környezet miatt nem ellenőrizhető

Ne tekints egy funkciót késznek pusztán azért, mert szerepel a forráskódban.

### 3. AZ ALKALMAZÁS ALAPKONCEPCIÓJA

A SIM CONTROL STUDIO egy Windows PC-vel együttműködő, mobiltelefonon vagy táblagépen használható szimulátoros műszerfal- és virtuális kezelőpanelrendszer.

A felhasználó akár két külön mobileszközt is használhat egyszerre:

**Első mobil:** digitális versenyautó-műszerfal.

**Második mobil:** működő, interaktív virtuális Button Box.

A két eszköz ugyanahhoz a Windows Bridge alkalmazáshoz kapcsolódik, de egymástól független felületet jelenít meg.

A rendszernek lehetőséget kell biztosítania arra is, hogy egyetlen mobileszközön a két funkció között váltsunk, vagy megfelelő kijelzőméret esetén kombinált elrendezést használjunk.

A fő játékcélpont az **Assetto Corsa Rally**.

Az architektúra legyen később más szimulátorokhoz is bővíthető, például Assetto Corsa, Assetto Corsa EVO vagy BeamNG.drive irányába, ha az adott játék integrációs lehetőségei ezt megengedik.

### 4. 20 AUTÓ – 20 MŰSZERFAL – 20 BUTTON BOX

A korábbi projektben meghatározott 20 autóprofilnak meg kell maradnia.

Minden autóhoz kötelezően tartozzon:

- Saját digitális műszerfal.
- Saját virtuális kezelőpanel.
- Egyedi, az adott autóhoz illeszkedő grafikai megjelenés.
- Önállóan menthető konfiguráció.
- Szerkeszthető elrendezés.
- Működő kezelőszervek.
- Telemetria-adatkapcsolat.
- Felbontásfüggetlen méretezés.

**Nem elfogadható, hogy mind a 20 autó ugyanazt az általános műszerfalat vagy Button Boxot használja eltérő logóval.**

A már meglévő autólistát használd, ne találj ki helyette új listát.

Autónként ellenőrizd, hogy a műszerfal és a Button Box milyen mértékben követi a valódi versenyautó elrendezését.

Elsődleges követelmények:
- Műszerek formája és pozíciója.
- Kijelzők arányai.
- Fordulatszám-kijelzés.
- Sebességkijelzés.
- Fokozatkijelzés.
- Váltásjelző LED-ek.
- Figyelmeztető jelzések.
- Háttérgrafikák.
- Színek és tipográfia.
- Kezelőgombok pozíciója.
- Forgókapcsolók.
- Funkciófeliratok.
- Gombvilágítás és állapotjelzés.

Ahol megfelelő referencia áll rendelkezésre, törekedj az eredeti autóhoz minél hűbb kivitelre.

Ahol nincs hiteles referencia, a felületet egyértelműen jelöld inspirált vagy közelítő változatként.

Ne állíts gyári pontosságot, ha azt nem lehet alátámasztani.

### 5. VALÓBAN MŰKÖDŐ MŰSZERFALAK

A műszerfalak ne statikus képek legyenek.

Valós telemetria alapján működjenek.

Támogatandó adatok, amennyiben a játék ténylegesen szolgáltatja őket:

- Sebesség
- Motorfordulatszám
- Aktuális sebességfokozat
- Váltásjelzés
- Gázpedálállás
- Fékpedálállás
- Kuplungállás
- Kézifékállás
- Motorhőmérséklet
- Üzemanyag
- Motorállapot
- Világításállapot
- Egyéb elérhető figyelmeztetések

Ne használj kitalált élő adatokat.

Ha egy adat nem érhető el az adott játékból, azt külön kezeld, és ne jeleníts meg valós értéknek látszó szimulált adatot.

Legyen külön DEMO mód, amelyben minden műszerfal és kezelőpanel élő játék nélkül tesztelhető.

A DEMO módot a felületen egyértelműen jelölni kell.

### 6. VIRTUÁLIS BUTTON BOX – VALÓDI VEZÉRLÉS

Minden Button Box legyen interaktív.

Támogatandó elemek:
- Nyomógomb
- Billenőkapcsoló
- Kétállású kapcsoló
- Háromállású kapcsoló
- Forgókapcsoló
- Többállású választókapcsoló
- Pillanatkapcsoló
- Világító kapcsoló
- Állapotjelző LED
- Egyedi ikon
- Szöveges címke

A felhasználó rendelhessen hozzájuk billentyűzet- vagy egyéb támogatott vezérlési műveleteket.

A Windows Bridge dolgozza fel a mobilon végrehajtott gombnyomásokat.

A vezérlés legyen alacsony késleltetésű.

Különösen fontos:
- Gombnyomás és felengedés megfelelő kezelése.
- Beragadt gombok elkerülése.
- Kapcsolatvesztés esetén biztonságos állapot.
- Dupla parancsok elkerülése.
- Testreszabható billentyűkiosztás.
- Profilonként külön menthető vezérlés.

Az olyan kapcsolóknál, amelyek valós játékállapotot reprezentálnak, különböztesd meg a ténylegesen visszaigazolt állapotot a helyileg nyilvántartott kapcsolóállapottól.

### 7. TELJES GRAFIKAI SZERKESZTŐ

A felhasználó tudjon saját műszerfalat és Button Boxot létrehozni.

Szükséges funkciók:
- Új projekt létrehozása.
- Meglévő profil másolása.
- Grafikai elemek mozgatása.
- Méretezés.
- Forgatás.
- Rétegek kezelése.
- Igazítás.
- Rácshoz illesztés.
- Zárolás.
- Átlátszóság módosítása.
- Háttérkép kezelése.
- Képek importálása.
- SVG-elemek támogatása.
- Szövegek szerkesztése.
- Színek módosítása.
- Gombfunkciók beállítása.
- Műszer-adatforrás hozzárendelése.
- Élő előnézet.
- Visszavonás és újra végrehajtás.
- Profil mentése.
- Profil exportálása és importálása.

A szerkesztő működjön érintőképernyőn is.

A kész profilokat lehessen másik mobiltelefonra átvinni.

### 8. WINDOWS BRIDGE ALKALMAZÁS

A Windows Bridge ne csupán háttérben futó technikai komponens legyen.

Készüljön hozzá magyar nyelvű, áttekinthető kezelőfelület.

Jelenítse meg:
- Bridge állapota.
- Játékcsatlakozás állapota.
- Elérhető telemetria.
- Csatlakoztatott mobileszközök.
- Eszközök neve.
- Aktív műszerfalprofil.
- Aktív Button Box profil.
- Kapcsolat minősége.
- Késleltetés.
- Hibák és figyelmeztetések.

Támogassa az automatikus helyi hálózati eszközfelderítést.

Legyen QR-kódos párosítás és szükség esetén manuális IP-címes csatlakozás.

Alkalmazz megfelelő párosítási hitelesítést. Idegen, nem párosított eszköz ne küldhessen vezérlési parancsokat.

A Windows Bridge legyen önállóan indítható, és lehetőség szerint legyen telepítője is.

### 9. ANDROID ALKALMAZÁS ELKÉSZÍTÉSE

A korábbi 0.1.0 verzió egyik legfontosabb hiányossága, hogy nem készült APK.

Ezt prioritásként kezeld.

Vizsgáld meg:
1. Elérhető-e Flutter SDK.
2. Elérhető-e Android SDK.
3. Elérhető-e működő buildkörnyezet.
4. Használható-e már telepített SDK.
5. Megoldható-e a build más, engedélyezett környezetben.
6. Elkészíthető-e automatizált GitHub Actions buildfolyamat.

Amennyiben a környezetben lehetséges, készíts valóban telepíthető Android APK-t.

Ha a környezet tiltja az SDK letöltését, ne próbáld a biztonsági korlátozásokat megkerülni.

Helyette készíts teljesen működő GitHub Actions konfigurációt, amely megfelelő környezetben lefordítja az alkalmazást, teszteket futtat, és letölthető APK build-artifactot készít.

Ellenőrizd a workflow szintaxisát és lehetőség szerint a tényleges futását.

A build csak akkor nevezhető sikeresnek, ha azt ténylegesen sikeres fordítás vagy CI-futás igazolja.

### 10. IPHONE ÉS IPAD

A Flutter forrás maradjon alkalmas iOS buildre.

Biztosítsd az iOS-specifikus projektfájlokat és konfigurációkat.

Készíts egyértelmű dokumentációt az Xcode-os fordításhoz.

Apple-aláírás és megfelelő macOS-környezet hiányában ne állítsd, hogy telepíthető IPA készült.

A mobilfelület legyen használható Android-telefonon, Android-táblagépen, iPhone-on és iPaden, az adott rendszer technikai korlátozásainak megfelelően.

### 11. ASSETTO CORSA RALLY INTEGRÁCIÓ

Különösen fontos a játék tényleges telemetriafelületének ellenőrzése.

Ne feltételezd automatikusan, hogy az Assetto Corsa Rally ugyanazokat a telemetria-interfészeket biztosítja, mint az eredeti Assetto Corsa.

Azonosítsd a ténylegesen használható adatforrásokat.

Készíts külön integrációs modult, amely:
- Fogadja a játékadatokat.
- Ellenőrzi az adatok érvényességét.
- Átalakítja őket belső telemetriaformátumra.
- Továbbítja őket a mobilalkalmazásnak.
- Észleli a kapcsolat megszakadását.
- Kezeli az újracsatlakozást.

A ténylegesen nem ellenőrzött integrációkat külön jelöld.

Készíts diagnosztikai felületet és teszttelemetria-forrást.

### 12. TELJESÍTMÉNY ÉS STABILITÁS

A cél folyamatos, reszponzív kijelzés.

Optimalizálási szempontok:
- 30 FPS minimum cél a támogatott eszközökön.
- 60 FPS cél megfelelő hardveren.
- Alacsony hálózati késleltetés.
- Hatékony telemetria-adattovábbítás.
- Felesleges adatküldés csökkentése.
- Kapcsolat automatikus helyreállítása.
- Hibás adatok kezelése.
- Mobilkijelző ébren tartása használat közben.
- Álló és fekvő tájolás támogatása.
- Különböző képarányok kezelése.

Mérd meg a ténylegesen vizsgálható teljesítményadatokat, és dokumentáld a tesztkörnyezetet.

### 13. TESZTELÉS

Bővítsd a meglévő tesztkészletet.

Kötelező tesztterületek:
- Telemetriafeldolgozás.
- Hálózati kommunikáció.
- Párosítás.
- Gombnyomás.
- Gombfelengedés.
- Kapcsolatvesztés.
- Profilbetöltés.
- Profilmentés.
- Szerkesztő.
- SVG-megjelenítés.
- Két egyidejű mobileszköz.
- Különböző képernyőfelbontások.
- Hibás konfigurációk.
- Automatikus újracsatlakozás.

Ahol nincs fizikai eszköz vagy elérhető játék, ott használj automatizált tesztet vagy szimulált tesztkörnyezetet.

A szimulált tesztet ne nevezd fizikai vagy éles játéktesztnek.

### 14. KIADÁSI CSOMAG

A következő verzió neve:

**SIM CONTROL STUDIO 0.2.0**

Készíts egységes kiadási könyvtárat.

A célzott tartalom:

- Windows Bridge futtatható alkalmazás.
- Windows telepítő, ha elkészíthető.
- Android APK, ha ténylegesen sikerül lefordítani.
- Flutter Android/iOS forráskód.
- 20 műszerfalprofil.
- 20 Button Box profil.
- Grafikai szerkesztő.
- Minta- és DEMO-adatok.
- GitHub Actions buildfolyamat.
- Teszteredmények.
- Magyar telepítési útmutató.
- Magyar használati útmutató.
- Fejlesztői dokumentáció.
- Ismert hibák listája.
- Részletes funkciómátrix.

A kiadási ZIP kizárólag valóban létező, ellenőrzött fájlokat tartalmazzon.

### 15. ELVÁRT FEJLESZTÉSI MUNKAMENET

A következő sorrendet alkalmazd.

**1. szakasz – Audit**

Olvasd be a meglévő projektet, ellenőrizd a jelenlegi állapotot, és azonosítsd a hiányosságokat.

**2. szakasz – Alapfunkciók**

Javítsd és fejezd be a Bridge, telemetria, hálózati kapcsolat és Button Box vezérlési funkcióit.

**3. szakasz – Mobilalkalmazás**

Tedd használhatóvá az összes előre telepített műszerfalat és kezelőpanelt. Fejleszd tovább a grafikai szerkesztőt.

**4. szakasz – Fordítás**

Készíts valós Windows buildet és Android APK-t, vagy állíts be ellenőrzött automatizált buildfolyamatot.

**5. szakasz – Tesztelés**

Futtasd le a szükséges automatizált ellenőrzéseket. Dokumentáld a valós és szimulált tesztek közötti különbséget.

**6. szakasz – Kiadás**

Készíts ellenőrzött, dokumentált 0.2.0 kiadási csomagot.

### 16. FONTOS FEJLESZTÉSI SZABÁLYOK

- Ne törölj működő funkciókat.
- Ne csökkentsd a profilok számát.
- Ne cseréld le a 20 egyedi autóprofilt általános sablonokra.
- Ne használj statikus képet működő műszerfalként.
- Ne állítsd működőnek a Button Boxot tényleges vezérlési teszt nélkül.
- Ne tekints mock vagy DEMO adatot éles telemetriának.
- Ne jelölj sikeresnek ellenőrizetlen buildet.
- Ne állíts telepíthető alkalmazást, ha csak forráskód készült.
- Ne tölts fel érzékeny adatokat, hitelesítő kulcsokat vagy aláírási tanúsítványokat a repositoryba.
- A fontos fejlesztési változásokat Git-commitokban rögzítsd.

### 17. ELVÁRT VÉGSŐ BESZÁMOLÓ

A fejlesztés végén magyar nyelven számolj be a következőkről:

1. Mi változott a 0.1.0 verzióhoz képest?
2. Mely funkciók működnek bizonyítottan?
3. Elkészült-e a Windows futtatható program?
4. Elkészült-e az Android APK?
5. Sikeresen lefutott-e a GitHub Actions build?
6. Működik-e a két mobileszköz egyidejű csatlakoztatása?
7. Mely autóprofilok készültek el ténylegesen?
8. Mennyire teljes az egyes autók műszerfala és kezelőpanelje?
9. Mely játékadatok érhetők el valós integráción keresztül?
10. Milyen tesztek futottak le, és milyen eredménnyel?
11. Mely funkciók hiányoznak még?
12. Pontosan hol található a letölthető kiadási csomag?

**VÉGSŐ CÉL:**

Ne csak egy forráskódcsomagot készíts, hanem a lehetőségekhez mérten ténylegesen telepíthető, használható és ellenőrzött alkalmazásokat.

A SIM CONTROL STUDIO végső célja egy profi, látványos, testreszabható szimulátoros műszerfal- és kezelőpanelrendszer, amely valódi játékadatokat jelenít meg, és képes a játék vezérlésére.

A fejlesztést a meglévő projekt átvizsgálásával kezdd, majd a fenti prioritások alapján haladj. Az egyértelműen megvalósítható lépéseket önállóan végezd el, és csak ténylegesen elkerülhetetlen külső hozzáférési vagy döntési akadály esetén kérj felhasználói beavatkozást.
