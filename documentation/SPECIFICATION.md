# SIM CONTROL STUDIO
## TELJES, EGYSÉGES FEJLESZTÉSI SPECIFIKÁCIÓ
### Android + iOS + Windows PC Bridge | 20 versenyautó-műszerfal + 20 hozzáillő kezelőpanel | Valós idejű telemetria és játékvezérlés

**Projektverzió:** 0.1.0  
**Elsődleges tesztjáték:** Assetto Corsa Rally  
**Elsődleges felhasználás:** Saját, privát használat  
**Mobiltechnológia:** Flutter / Dart  
**PC-platform:** Windows 10/11  
**Nyelv:** Elsődlegesen magyar, másodlagosan angol

---

# 0. LEGFONTOSABB UTASÍTÁSOK A CODEXNEK

Egy teljes értékű, telepíthető és ténylegesen használható szimulátoros alkalmazást kell megvalósítanod, SIM CONTROL STUDIO néven.

**EZ A DOKUMENTUM A PROJEKT EGYETLEN AKTUÁLIS, IRÁNYADÓ SPECIFIKÁCIÓJA.**

Ha léteznek korábbi fejlesztési utasítások, a jelen dokumentum felülírja az ellentmondó részeket. A korábban megírt, megfelelően működő forráskódot ne töröld feleslegesen, hanem illeszd az itt meghatározott architektúrához.

Ne csak tervezz!

Ne csak látványtervet vagy prototípust készíts!

Ne állj meg egy olyan alkalmazásnál, amely kizárólag szimulált telemetriaadatokat mutat!

A feladat egy tényleges program elkészítése, a hozzá tartozó forráskóddal, felhasználói felülettel, játékadapterekkel, telepíthető kiadásokkal és dokumentációval.

## Kötelező végcél

A felhasználó:

1. Telepíti a SIM CONTROL STUDIO Windows PC Bridge alkalmazást a szimulátort futtató számítógépre.
2. Telepíti a Flutter mobilalkalmazást Android-telefonra, iPhone-ra, iPadre vagy Android-tabletre.
3. Csatlakoztatja a mobilokat a PC-hez a helyi hálózaton.
4. Az első készüléken kiválasztja a Műszerfal üzemmódot.
5. A második készüléken kiválasztja a Kezelőpanel üzemmódot.
6. Mindkét készüléken kiválasztja ugyanazt a valós versenyautót, vagy engedélyezi az automatikus profilpárosítást.
7. Elindítja az Assetto Corsa Rallyt.
8. A Windows alkalmazás kiolvassa a játék valódi telemetriaadatait.
9. A műszerfalon élőben megjelennek az autó adatai.
10. A kezelőpanel gombjai a Windows alkalmazáson keresztül vezérlik a játék támogatott funkcióit.

Az egész rendszer működjön internetkapcsolat, előfizetés és külső felhőszolgáltatás nélkül.

A projekt célja nem egyetlen rövid bemutató, hanem egy hosszú távon továbbfejleszthető, saját szimulátoros alkalmazás.

**Fontos műszaki szabály:** kizárólag olyan funkciót jelölj működőnek, amelyet ténylegesen implementáltál és a rendelkezésre álló eszközökkel ellenőriztél. Ne állítsd, hogy minden játék minden adatot szolgáltat, ha erre nincs valós műszaki lehetőség.

---

# 1. ALKALMAZÁSARCHITEKTÚRA

## 1.1. Mobilalkalmazás

Az elsődleges termék egy valódi, telepíthető Flutter mobilalkalmazás.

Támogatandó platformok:

- Android telefon
- Android tablet
- iPhone
- iPad

Minden készüléken ugyanaz a Flutter-kódbázis működjön.

Ne PWA-t és ne böngészőalapú alkalmazást készíts.

A mobilon fusson a műszerfal, a Button Box és a teljes vizuális szerkesztő.

Legyen optimalizálva különböző kijelzőméretekre és képarányokra.

## 1.2. Windows PC Bridge

A Windows PC-n egy külön, kis erőforrásigényű program fusson.

Javasolt technológia:

- C#
- Támogatott .NET LTS
- Windows shared-memory olvasás
- UDP-alapú játékadapterek
- WebSocket vagy más megfelelő, kétirányú helyi kommunikáció
- Aszinkron adatfeldolgozás
- Rendszertálcára minimalizálható Windows kezelőfelület

A Windows Bridge feladatai:

- Játék felismerése
- Valódi telemetria olvasása
- Adatfeldolgozás és normalizálás
- Telemetria továbbítása a mobilkészülékeknek
- Mobilról érkező vezérlőparancsok fogadása
- Billentyűparancsok végrehajtása
- Eszközök párosítása
- Kapcsolatfigyelés
- Játékonkénti beállítások kezelése
- Diagnosztika és hibakeresés

A PC Bridge a hétköznapi használat során ne igényeljen fejlesztői környezetet.

## 1.3. Egységes kommunikáció

Egyetlen PC Bridge egyszerre több mobilkészüléket szolgáljon ki.

A telemetriát csak egyszer kell kiolvasni a játékból.

Ebből a közös adatfolyamból minden csatlakozott mobil a saját megjelenítéséhez szükséges adatokat kapja meg.

A kezelőparancsok ellentétes irányban közlekednek:

Mobilkezelőpanel → PC Bridge → Játék.

A visszaolvasható játékállapotok pedig:

Játék → PC Bridge → Összes csatlakozott mobileszköz.

---

# 2. KÉT VAGY TÖBB MOBILESZKÖZ EGYIDEJŰ HASZNÁLATA

Ez az alkalmazás egyik legfontosabb követelménye.

## 2.1. Példaműködés

Windows PC:
Assetto Corsa Rally.

Első mobil:
Škoda Fabia RS Rally2 műszerfal.

Második mobil:
Škoda Fabia RS Rally2 kezelőpanel.

A két készülék folyamatosan, ugyanahhoz a játékmenethez kapcsolódjon.

A műszerfal a játék élő adatait mutassa.

A kezelőpanel a játékban ténylegesen beállítható funkciókat vezérelje.

A második készülék leválasztása ne állítsa le az első műszerfal működését.

## 2.2. Készüléküzemmódok

A mobilalkalmazás indítása után a felhasználó három üzemmód közül választhasson:

**MŰSZERFAL**

A készülék teljes képernyős digitális műszerfal.

**KEZELŐPANEL**

A készülék teljes képernyős virtuális Button Box.

**HIBRID**

Egyetlen képernyőn műszerfal és kezelőpanel is megjelenhet.

Mindegyik módhoz külön elrendezés és profil tartozhat.

## 2.3. Automatikus profilpárosítás

A műszerfal és kezelőpanel alkosson összetartozó autóprofilt.

Példa:

A felhasználó az első telefonon kiválasztja:

Škoda Fabia RS Rally2.

A második telefonon automatikusan megjelenik az ajánlás:

Škoda Fabia RS Rally2 kezelőpanel.

A felhasználó egy érintéssel elfogadhatja.

Ugyanez mind a 20 versenyautó esetében működjön.

Amennyiben a játékból megbízhatóan kiolvasható az aktuális autó azonosítója, a program tudja automatikusan kiválasztani a megfelelő profilt.

Legyen mindig kézi felülbírálási lehetőség.

## 2.4. Párosítás és kapcsolat

Valósítsd meg:

- Helyi hálózatos kommunikáció
- QR-kódos párosítás
- Automatikus eszközfelderítés, ha a hálózat támogatja
- Manuális IP-cím és port megadás
- Korábban párosított készülékek megjegyzése
- Automatikus újracsatlakozás
- Eszközönként mentett szerepkör
- Eszközönként mentett autóprofil
- Kapcsolatállapot visszajelzés
- Késleltetés kijelzése
- Jogosultságok kezelése

Az első párosítást követően a készülék lehetőleg emberi beavatkozás nélkül csatlakozzon újra, amennyiben a PC Bridge elérhető.

A teljes kapcsolat helyi hálózaton működjön. A PC vezetékes Etherneten is csatlakozhat, ha ugyanazon helyi hálózaton elérhető.

---

# 3. 20 VALÓDI VERSENYAUTÓ – 40 EGYEDI ALAPPROFIL

**EZ KÖTELEZŐ KÖVETELMÉNY.**

A programban 20 valós versenyautó műszerfala és mindegyikhez az adott autóhoz illő, külön virtuális kezelőpanel legyen.

Ez összesen:

**20 műszerfal + 20 kezelőpanel = 40 különálló alapelrendezés.**

Nem fogadható el, hogy ugyanazt az általános műszerfalat vagy gombsort húsz különböző színnel jeleníted meg.

Minden autóhoz egyedi, az eredeti versenyautó alapján megtervezett grafikai és funkcionális elrendezés szükséges.

## 3.1. Kötelező autólista

| # | Versenyautó | Műszerfal | Kezelőpanel |
|---|---|---|---|
| 1 | Porsche 911 GT3 R (992) | Porsche GT3 R | Porsche GT3 R |
| 2 | BMW M4 GT3 | BMW M4 GT3 | BMW M4 GT3 |
| 3 | Mercedes-AMG GT3 | Mercedes-AMG GT3 | Mercedes-AMG GT3 |
| 4 | Ferrari 296 GT3 | Ferrari 296 GT3 | Ferrari 296 GT3 |
| 5 | Audi R8 LMS GT3 | Audi R8 LMS GT3 | Audi R8 LMS GT3 |
| 6 | Lamborghini Huracán GT3 EVO2 | Huracán GT3 | Huracán GT3 |
| 7 | McLaren 720S GT3 Evo | McLaren GT3 | McLaren GT3 |
| 8 | Aston Martin Vantage GT3 | Vantage GT3 | Vantage GT3 |
| 9 | Lexus RC F GT3 | Lexus GT3 | Lexus GT3 |
| 10 | Corvette Z06 GT3.R | Corvette GT3 | Corvette GT3 |
| 11 | Porsche 963 | Porsche 963 | Porsche 963 |
| 12 | Ferrari 499P | Ferrari 499P | Ferrari 499P |
| 13 | Toyota GR010 Hybrid | Toyota GR010 | Toyota GR010 |
| 14 | Cadillac V-Series.R | Cadillac Hypercar | Cadillac Hypercar |
| 15 | BMW M Hybrid V8 | BMW Hypercar | BMW Hypercar |
| 16 | Toyota GR Yaris Rally1 | Toyota Rally1 | Toyota Rally1 |
| 17 | Hyundai i20 N Rally1 | Hyundai Rally1 | Hyundai Rally1 |
| 18 | Ford Puma Rally1 | Ford Rally1 | Ford Rally1 |
| 19 | Škoda Fabia RS Rally2 | Škoda Rally2 | Škoda Rally2 |
| 20 | Dallara IR-18 IndyCar | IndyCar műszerfal | IndyCar kezelőpanel |

A huszadik autó azért konkrét Dallara IR-18, mert mind a húsz profilhoz valódi versenyautós referencia szükséges, nem általános Formula-grafika.

További általános Formula-műszerfal opcionálisan készíthető extra profilként.

---

# 4. AZ EREDETI VERSENYAUTÓK MŰSZERFALAINAK REKONSTRUKCIÓJA

## 4.1. Alapelv

Mind a 20 autó esetében a valódi jármű műszerfalát használd alapként.

Törekedj a lehető legnagyobb vizuális és funkcionális hűségre.

A megjelenítésnél figyelj:

- Az eredeti képernyő arányaira
- A fordulatszám-kijelző elhelyezkedésére
- A váltásjelző LED-ek formájára, helyére és színére
- A fokozatkijelző méretére
- A sebességkijelző elhelyezésére
- A grafikus keretekre
- Az eredeti műszercsoportosításra
- A betűk stílusára
- Az eredeti kijelző színvilágára
- A versenyautó típusára jellemző figyelmeztetésekre
- Az eredeti kijelző többoldalas funkcióira, amennyiben dokumentáltak

A cél ne egy általános versenyautós megjelenés legyen, hanem az adott autóhoz egyértelműen köthető műszerfal.

## 4.2. Referenciaanyagok

Autónként kutasd fel a rendelkezésre álló hiteles referenciaanyagokat.

Elsődleges források:

- Gyártói weboldalak
- Gyártói dokumentációk
- Hivatalos versenyautós sajtóanyagok
- Versenyautó-kézikönyvek
- Műszerfalgyártók dokumentációja
- Hiteles pilótafülke-felvételek
- A gyári kezelőszerveket egyértelműen bemutató fotók és videók

Minden autóprofilhoz készíts egy külön referenciajegyzéket.

Rögzítsd az autó modellévét, kivitelét, a referenciák forrását és azt, melyik elem milyen bizonyíték alapján készült.

Ha a kijelző többféle változatban létezik, válassz egy dokumentált kivitelű és modellévű verziót. Ne keverj össze különböző generációkat úgy, mintha ugyanarról az autóról származnának.

## 4.3. Jogtisztaság

A grafikai elemeket önállóan készítsd el SVG vagy Flutter Canvas alapokon.

Ne használj jogosulatlanul átvett gyári grafikai állományokat, betűkészleteket vagy védjegyeket.

Az eredeti elrendezés és kezelési logika alapján készíts saját, szerkeszthető grafikai rekonstrukciót.

A nem hitelesíthető részleteket ne állítsd gyári eredetűnek.

Minden profilhoz tartozzon dokumentált hűségi állapot:

- Dokumentált eredeti elrendezés alapján
- Részleges referencia alapján
- Eredeti autó által inspirált kiegészített változat

---

# 5. 20 AUTÓSPECIFIKUS KEZELŐPANEL / BUTTON BOX

**A húsz kezelőpanel ugyanolyan fontos, mint a húsz műszerfal.**

Ne készíts egyetlen univerzális Button Boxot, amelyet húsz különböző autó nevével jelenítesz meg.

Minden autóhoz külön kezeld:

- Kormánygombok
- Kormánykapcsolók
- Középkonzol
- Oldalsó kapcsolópanelek
- Forgókapcsolók
- Indítógombok
- Biztonsági kapcsolók
- Fénykapcsolók
- Világító nyomógombok
- Digitális kezelőfelületek
- Egyedi motorsport-vezérlők

A dokumentált valódi gombelrendezést, gombformákat, színeket, feliratokat és műveleteket a lehető leghűebben rekonstruáld.

## 5.1. Három kezelőpanelnézet

Ha az eredeti autó kialakítása indokolja, készíts három nézetet:

**A. Kormány**

A versenyautó eredeti kormánygombjai és forgókapcsolói.

**B. Középkonzol**

Az autó dokumentált központi és oldalsó vezérlőelemei.

**C. Kombinált mobilpanel**

Az eredeti kezelőszervek legfontosabb funkcióit összevonó, telefonos használatra optimalizált panel.

A kombinált panelen a felhasználói ergonómia miatt átrendezhető a felület, de az eredeti elemek legyenek felismerhetők.

## 5.2. Kötelező mintaprofil: Škoda Fabia RS Rally2

A Škoda Fabia RS Rally2 legyen a referenciaként elsőként kidolgozott autópáros.

Készíts:

- Eredeti jellegű Škoda Fabia RS Rally2 műszerfalat
- Eredeti kormánykapcsolókat rekonstruáló panelt
- Valós középkonzol alapján készített virtuális kezelőpanelt
- Kombinált telefonos Button Boxot

A gyári dokumentáció alapján vedd figyelembe a kormányra integrált indítógombot, a nagyobb fő kijelzőt és az érintővezérléssel, valamint interkomkezeléssel rendelkező középkonzolt.

Referenciák:

https://www.skoda-motorsport.com/en/skoda-fabia-rs-rally2/basic-information/

https://www.skoda-motorsport.com/en/skoda-fabia-rs-rally2-all-the-essentials-in-60-seconds/

A többi 19 autó ugyanezzel a gondossággal, saját hiteles referenciaanyag alapján készüljön.

## 5.3. Autóspecifikus működés

A valós autóban használt funkciókat lehetőség szerint a játék megfelelő vezérléséhez rendeld.

Például:

- Gyújtás
- Motorindítás
- Lámpák
- Ablaktörlő
- Fénykürt
- Fékerőelosztás
- ABS
- Kipörgésgátló
- Differenciálmű
- Motorüzemmód
- DRS
- ERS
- Boxutcai limiter
- Kijelzőoldalak váltása
- Rádió
- Interkom
- Kamera
- Egyéb játékspecifikus parancsok

Ne tegyél egy valósághű autópanelre olyan funkciót gyári elemként, amely az adott versenyautóban nem létezik.

Ha a szimulátoros használathoz további vezérlés szükséges, legyen külön, „Egyéni vezérlők” nézet vagy kategória.

## 5.4. Teljes szerkeszthetőség

A gyári jellegű Button Boxok legyenek:

- Másolhatók
- Szerkeszthetők
- Átméretezhetők
- Átrendezhetők
- Átszínezhetők
- Más eszközre exportálhatók
- Saját néven menthetők

A gyári jellegű eredeti profil megőrzéséhez annak szerkesztésekor alapértelmezésben személyes másolat készüljön.

---

# 6. MŰKÖDŐ VIRTUÁLIS VEZÉRLÉS

A kezelőpanel ne pusztán grafikai illusztráció legyen.

A gombok ténylegesen küldjenek vezérlőparancsokat a játék felé.

## 6.1. Gombtípusok

Implementáld a következőket:

- Egyszeri nyomógomb
- Nyomva tartásos gomb
- Kétállású kapcsoló
- Háromállású kapcsoló
- Többállású kapcsoló
- Forgóvezérlő
- Plusz/mínusz léptető
- Csúszka
- Világító állapotjelző
- Ikonos gomb
- Szöveges gomb
- Feltételesen engedélyezett kezelőelem

Az érintés megfelelő vizuális és opcionális rezgéses visszajelzést adjon.

## 6.2. Windows-billentyűparancsok

Játékprofilonként lehessen:

- Billentyűt hozzárendelni
- Billentyűkombinációt hozzárendelni
- Lenyomást és felengedést konfigurálni
- Hosszú nyomást konfigurálni
- Ismételt nyomást konfigurálni
- A parancsokat tesztelni
- Gombkiosztást menteni és exportálni

A PC Bridge kompatibilis, engedélyezett Windows-bemeneti módszerrel küldje a parancsokat.

Biztosíts beragadt billentyűk elleni védelmet, időkorlátokat és biztonságos parancsfeldolgozást.

A vezérlés alapértelmezetten csak akkor aktív, ha a megfelelő játék van előtérben, és a felhasználó engedélyezte a mobilvezérlést.

A kormányhoz, pedálhoz vagy más meglévő vezérlőhöz tartozó bemeneteket ne tiltsd le.

## 6.3. Fékerőelosztás, ABS és TC

Ezeknél különösen pontos működés szükséges.

Ha a játék csak növelés/csökkentés parancsot támogat, használj +/- léptetést.

Ne próbálj tetszőleges százalékos értéket közvetlenül beállítani, ha a játék erre nem biztosít lehetőséget.

Az aktuális értéket csak akkor jelezd vissza hiteles játékállapotként, ha azt valódi telemetria igazolja.

Különböztesd meg:

- A felhasználó által kért értéket
- Az elküldött parancsot
- A Bridge által fogadott parancsot
- A játékból visszaolvasott tényleges állapotot

## 6.4. Nem támogatott funkciók

Ha valamely funkciót az adott játék vagy autó nem támogat, jelenjen meg:

„Ez a funkció ebben a játékban nem érhető el.”

Az adott kezelőelem kikapcsolható vagy felhasználó által újrakiosztható legyen.

Ne jeleníts meg hamis, működőnek tűnő állapotot.

---

# 7. DASHBOARD ADATOK – TELJES TELEMETRIARENDSZER

Készíts egységes, bővíthető telemetria-adatmodellt.

## 7.1. Járműadatok

- Sebesség
- Motorfordulatszám
- Fordulatszámhatár
- Sebességfokozat
- Gázpedál
- Fékpedál
- Kuplungpedál
- Kormányelfordítás
- Kézifék
- Gyújtás
- Motorállapot

## 7.2. Motor és hajtáslánc

- Vízhőmérséklet
- Olajhőmérséklet
- Olajnyomás
- Turbónyomás
- Üzemanyag
- Fogyasztás
- Becsült hatótáv
- Motorüzemmód
- Váltóhőmérséklet, ha elérhető
- Differenciálmű beállításai
- Hibajelzések

## 7.3. Gumik és fékek

- Négy kerék guminyomása
- Gumi belső hőmérséklete
- Gumi középső hőmérséklete
- Gumi külső hőmérséklete
- Gumikopás
- Fékek hőmérséklete
- Keréksebesség
- Kerékcsúszás
- Kerékblokkolás
- ABS állapot
- ABS szint
- TC állapot
- TC szint
- Fékerőelosztás

## 7.4. Versenyadatok

- Aktuális köridő
- Előző köridő
- Legjobb köridő
- Szektoridők
- Időkülönbségek
- Versenypozíció
- Körszám
- Hátralévő körök
- Hátralévő idő
- Boxutca-állapot
- Boxutcai sebességhatár
- Zászlójelzések
- DRS
- ERS
- Hybrid energia
- Akkumulátor

## 7.5. Járműdinamika

- Hosszanti G-erő
- Oldalirányú G-erő
- Függőleges gyorsulás
- Yaw
- Pitch
- Roll
- Felfüggesztés elmozdulásai
- Kormányzási adatok
- Keréksebességek

## 7.6. Rallyspecifikus adatok

- Szakaszidő
- Részidők
- Szakaszon megtett távolság
- Rajt- és célállapot
- Autóazonosító
- Szakaszazonosító
- Navigációs adatok, ha a játék szolgáltatja
- Autó műszaki állapotadatai, ha elérhetők

A valódi játékmódban minden widget csak hiteles, ténylegesen beolvasott vagy egyértelműen abból számított adatot mutasson.

A számított adat legyen megkülönböztethető a közvetlenül kapott adattól.

Minden adatmező rendelkezzen értékkel, mértékegységgel, adatforrással, időbélyeggel és érvényességi állapottal.

---

# 8. ELSŐDLEGES JÁTÉK: ASSETTO CORSA RALLY

**AZ ELSŐ ELKÉSZÜLT KIADÁST ASSETTO CORSA RALLYBAN SZERETNÉM TESZTELNI.**

A fejlesztési sorrend ehhez igazodjon.

A legelső működő telemetriaadapter az Assetto Corsa Rallyhoz készüljön.

## 8.1. Valós shared-memory olvasás

Implementálj Windows alatt működő, C# alapú telemetriaolvasót.

Elsőként ellenőrizd a játék tényleges shared-memory objektumait és adatszerkezeteit.

Vizsgáld meg a releváns physics, graphics és static adatblokkokat.

Ne feltételezd ellenőrzés nélkül, hogy a Rally teljes egészében a klasszikus Assetto Corsa adatstruktúráját használja.

A struktúrákat a valós Rally-implementáció és a hiteles referenciák alapján határozd meg.

## 8.2. Kötelező technikai referenciák

https://github.com/LuizZak/AssettoCorsaRallyTelemetryReader

https://github.com/decnet100/acr_telemetry

Vizsgáld meg, hogyan olvassák és továbbítják a valódi Assetto Corsa Rally-telemetriát.

A forráskódokból tanulhatsz, de másolás vagy beépítés előtt ellenőrizd a licenceket.

Különösen fontos, hogy a különböző projektek eltérő felhasználási feltételekkel rendelkezhetnek.

## 8.3. Elsőként megvalósítandó Rally-adatok

- Valós sebesség
- Valós motorfordulatszám
- Valós sebességfokozat
- Gáz- és fékpedál, ha elérhető
- Kormányelfordítás, ha elérhető
- G-erők, ha elérhetők
- Járműazonosító, ha elérhető
- Egyéb igazoltan működő telemetriamezők

A telemetriát ne szimulált értékekből állítsd elő.

Már az első éles teszten a játékban végzett gázadás, fékezés és váltás hatására frissülnie kell a támogatott műszereknek.

## 8.4. Diagnosztika

A PC Bridge-ben külön Assetto Corsa Rally diagnosztikai oldal szükséges.

Mutassa:

- Játék felismerve / nem felismerve
- Shared memory elérhető / nem elérhető
- Élő adatfolyam aktív / inaktív
- Frissítési gyakoriság
- Utolsó adat ideje
- Sebesség
- Fordulatszám
- Fokozat
- Kapcsolódott mobileszközök

A valódi telemetria először a PC Bridge diagnosztikájában jelenjen meg, majd jusson el a mobileszközökre.

## 8.5. Rally játékmódok

Támogasd az aktuális Rally-verzióban ténylegesen elérhető valamennyi játékmódot, amennyiben az adott üzemmód elérhető telemetriát és engedélyezett vezérlést biztosít.

A rendszer legyen felkészítve:
- Gyakorlás
- Rallyszakasz
- Időmérő jellegű esemény
- Versenyesemény
- Online esemény, ha létezik és támogatott
- Egyéb elérhető munkamenetek

Ne feltételezz olyan játékmódot, amely az aktuális játékverzióban még nem létezik.

---

# 9. TOVÁBBI JÁTÉKOK TÁMOGATÁSA

A rendszer legyen moduláris.

A Rally mellett a következő játékokhoz készüljenek adapterek vagy dokumentált bővítési pontok.

Prioritás:

1. Assetto Corsa Rally
2. Assetto Corsa EVO
3. Assetto Corsa
4. BeamNG.drive
5. Assetto Corsa Competizione
6. iRacing
7. Automobilista 2
8. rFactor 2
9. Le Mans Ultimate
10. EA SPORTS F1 sorozat
11. EA SPORTS WRC
12. DiRT Rally 2.0
13. RaceRoom Racing Experience
14. Forza Motorsport
15. Forza Horizon
16. Project CARS sorozat
17. Euro Truck Simulator 2
18. American Truck Simulator
19. Egyéb támogatott autószimulátorok

Minden játékhoz külön GameAdapter implementáció készüljön.

Az adapterek közös interfészt alkalmazzanak, de a konkrét telemetria- és vezérlési protokollokat játékonként kezeljék.

A második prioritású játékoknál ne jelölj késznek olyan integrációt, amelyet még nem implementáltál és teszteltél.

A következő fejlesztések során lehessen egyenként új játékadaptereket hozzáadni a már kész mobilalkalmazás átírása nélkül.

---

# 10. MINDEN ELÉRHETŐ JÁTÉKMÓD TÁMOGATÁSA

A SIM CONTROL STUDIO ne legyen kizárólag offline, gyakorló vagy Free Practice használatra korlátozva.

A cél az, hogy minden támogatott játéknál a lehető legtöbb elérhető munkamenetben működjön.

Kezelendő üzemmódok:

- Free Practice
- Time Trial
- Qualifying
- Race
- Offline verseny
- Online multiplayer
- Privát szerver
- Liga- és bajnoki versenyek
- Rallyszakaszok
- Online rallyesemények
- Free Roam
- Tesztvezetés
- Boxutca
- Garázs
- Replay, amennyiben a telemetria hozzáférhető
- Spectator mód, amennyiben a játék biztosít megfelelő adatokat

## 10.1. Automatikus állapotkezelés

Ha a felhasználó:

- Autót vált
- Új versenyt indít
- Online szerverre csatlakozik
- Szakaszt vált
- Kilép a versenyből
- Visszatér a menübe

akkor a Bridge kezelje a változást.

A csatlakozott telefonokat ne kelljen minden munkamenet után újrapárosítani.

A választott műszerfal és kezelőpanel maradjon aktív, kivéve ha automatikus autóprofil-váltás van engedélyezve.

## 10.2. Online kompatibilitás és tisztességes használat

A rendszer kizárólag a játék által engedélyezett telemetria- és vezérlési megoldásokat használja.

Ne használjon:
- Anti-cheat megkerülést
- Tiltott memóriamódosítást
- Játékfolyamat-injektálást
- Jogosulatlan adatlekérést
- Automatikus vezetést
- Tiltott makrókat
- Online versenyelőnyt adó, nem engedélyezett funkciókat

Ha egy játék az online módhoz korlátozott telemetriát biztosít, jelenítse meg a rendelkezésre álló adatokat, és jelezze a korlátozásokat.

Az alkalmazásnak legyen biztonságos, csak olvasásra szolgáló telemetriaüzemmódja.

## 10.3. Kompatibilitási mátrix

Készíts játékonként és játékmódonként ellenőrizhető kompatibilitási táblázatot.

Tartalmazza:

- Játék neve
- Játékverzió
- Munkamenet
- Telemetria támogatás
- Button Box támogatás
- Elérhető adatmezők
- Online használat feltételei
- Tesztelési státusz
- Ismert hibák

---

# 11. TELJES VIZUÁLIS DASHBOARD SZERKESZTŐ

A Flutter mobilalkalmazáson belül működjön a szerkesztő.

A felhasználónak ne kelljen programoznia.

## 11.1. Szerkesztési funkciók

- Új dashboard
- Új kezelőpanel
- Meglévő profil szerkesztése
- Profil másolása
- Elem hozzáadása
- Elem törlése
- Drag-and-drop
- Érintéses méretezés
- Forgatás
- Rácshoz illesztés
- Rétegsorrend
- Elemzárolás
- Csoportosítás
- Visszavonás
- Ismétlés
- Színezés
- Betűtípus
- Betűméret
- Háttérkép
- Háttérszín
- Animáció
- Feltételes megjelenítés
- Határértékek
- Widget adatkapcsolat beállítása

## 11.2. Műszerfal-widgetek

Készíts legalább:

- Digitális sebességmérő
- Analóg sebességmérő
- Fordulatszámmérő
- Fordulatszám LED-sor
- Sebességfokozat
- Üzemanyagszint
- Motorhőmérséklet
- Gumihőmérséklet
- Guminyomás
- Köridő
- Rallyszakasz-idő
- Pedálgrafikon
- G-erő mérő
- Figyelmeztető lámpák
- Dinamikus szövegek
- Egyedi képek
- SVG-elemek
- Kijelzőoldal-váltás

## 11.3. Button Box szerkesztő

A kezelőpanel szerkesztőjében lehessen:

- Gombokat hozzáadni
- Gombokat mozgatni
- Kapcsolókat elhelyezni
- Forgóvezérlőket létrehozni
- Gombok feliratát módosítani
- Ikonokat cserélni
- Billentyűparancsot hozzárendelni
- Játékállapot-visszajelzést konfigurálni
- Gombcsoportokat készíteni
- Több kezelőpaneloldalt létrehozni

## 11.4. Grafikai import

A felhasználó tudjon saját:

- SVG
- PNG
- Átlátszó hátterű képfájlokat

importálni.

A támogatott SVG-elemek megjelenítése legyen vektoros és méretezhető, amennyiben a Flutter-könyvtár ezt lehetővé teszi.

Ne alakíts minden grafikát szükségtelenül pixeles képpé.

## 11.5. Mentés

Minden profil legyen:

- Helyben menthető
- Új néven menthető
- JSON-alapú
- Exportálható
- Importálható
- Verziózható

A dashboardok rendelkezzenek saját azonosítóval, verziószámmal, autóazonosítóval, eszközszereppel és támogatott adatmezők listájával.

---

# 12. MODERN FELHASZNÁLÓI FELÜLET

A program megjelenése prémium, motorsport stílusú legyen.

Alapirány:

- Sötét grafitszürke és fekete hátterek
- Piros motorsport kiemelések
- Fehér, jól olvasható adatok
- Sárga, zöld és kék állapotjelzések
- Nagy kontraszt
- Jól érinthető gombok
- Professzionális digitális versenyműszerek

A mobilalkalmazás főmenüje:

1. Kezdőlap
2. Műszerfalak
3. Kezelőpanelek
4. Autóprofilok
5. Szerkesztő
6. Játékok
7. Csatlakozás
8. Eszközök
9. Telemetria
10. Beállítások

## 12.1. Első indítás

Az első indításkor legyen konfigurációs varázsló.

Vezesse végig a felhasználót:

- Nyelvválasztás
- PC Bridge kapcsolat
- QR-kódos párosítás
- Eszközüzemmód kiválasztása
- Autóprofil kiválasztása
- Dashboard kiválasztása
- Button Box kiválasztása
- Első telemetriateszt

## 12.2. Teljes képernyő

A műszerfal és Button Box működjön valódi teljes képernyős megjelenítésben.

A készülék maradjon ébren használat közben.

Ne takarják a tartalmat állandó navigációs elemek.

A felhasználó egy mozdulattal vagy dedikált gombbal visszatérhessen a főmenübe.

---

# 13. TELJESÍTMÉNY ÉS STABILITÁS

A program működjön alacsony késleltetéssel.

Célok megfelelő hálózaton és hardveren:

- Folyamatos telemetriafolyam
- Konfigurálható megjelenítési gyakoriság
- 20/30/60 Hz beállítások, ha a forrás ezt lehetővé teszi
- Sima műszeranimációk
- Gyors Button Box reakció
- Stabil két- vagy többeszközös működés
- Alacsony PC-terhelés
- Automatikus kapcsolat-helyreállítás

A Bridge külön szálon vagy megfelelő aszinkron architektúrában kezelje az adatolvasást, hálózatot és vezérlést.

Ne legyen szükség az alkalmazás újraindítására minden játékváltás után.

A játék bezárása ne okozza a Bridge összeomlását.

Az elavult telemetriaadatokat a program ne mutassa friss értékként.

---

# 14. BIZTONSÁG ÉS HOZZÁFÉRÉS

A program elsősorban saját használatra készül.

Ne igényeljen felhasználói regisztrációt.

Ne igényeljen külső szervert.

Ne gyűjtsön szükségtelen személyes adatokat.

A helyi hálózati kapcsolat legyen védett.

Valósítsd meg:

- Párosítási tokent
- Jogosult eszközök listáját
- Eszközleválasztást
- Jogosultság-visszavonást
- Parancsok forrásának azonosítását
- Eszközönkénti szerepköröket
- Parancsok sebességkorlátozását
- Kapcsolatmegszakadáskor beragadt gombok felengedését

Az első telepítésnél a Bridge ne nyisson felesleges hálózati hozzáférést.

Az online versenyek használata során ne próbáljon megkerülni játékbiztonsági mechanizmusokat.

---

# 15. RÉSZLETES TESZTELÉSI KÖVETELMÉNYEK

A program akkor tekinthető sikeresen megvalósítottnak, ha az implementált funkciók tesztelhetők.

## Teszt A – Valódi Assetto Corsa Rally telemetria

1. Windows Bridge indítása.
2. Assetto Corsa Rally indítása.
3. Valós játékmenet elindítása.
4. Telemetriaolvasó aktiválása.
5. Sebesség, fordulatszám és fokozat ellenőrzése.
6. Adatok megjelenítése a PC Bridge diagnosztikájában.
7. Adatok továbbítása a telefonra.
8. Valós idejű műszerfrissítés ellenőrzése.

Nem elfogadható véletlenszerűen generált érték.

## Teszt B – Két mobileszköz

1. Első készülék párosítása.
2. Műszerfal mód.
3. Második készülék párosítása.
4. Button Box mód.
5. Mindkét készülék egyidejű használata.
6. Az egyik készülék lecsatlakoztatása.
7. Másik készülék zavartalan működésének ellenőrzése.
8. Automatikus újracsatlakozás ellenőrzése.

## Teszt C – Valódi vezérlés

1. A játékban egy támogatott művelethez billentyű rendelése.
2. Ugyanennek beállítása a Button Boxban.
3. Gomb megnyomása mobilon.
4. Parancs fogadása a Bridge-ben.
5. Végrehajtás a játékban.
6. Gomb felengedésének ellenőrzése.
7. Kapcsolatmegszakadási védelem ellenőrzése.

## Teszt D – Škoda Fabia RS Rally2 profilpár

1. Škoda Fabia RS Rally2 műszerfal kiválasztása.
2. Második eszközön a hozzáillő kezelőpanel automatikus felajánlása.
3. Eredeti jellegű műszerfal megjelenítése.
4. Eredeti jellegű Button Box megjelenítése.
5. Telemetriafrissítés.
6. Támogatott gombparancs végrehajtása.
7. Profilok egyedi szerkesztése.
8. Profilmentés és visszatöltés.

## Teszt E – Mind a 20 autó

Mind a 20 autóhoz ellenőrizd:

- Műszerfal betöltése
- Kezelőpanel betöltése
- Két profil összerendelése
- Műszerelemek megfelelő adatkapcsolata
- Kezelőgombok konfigurálhatósága
- Profilok szerkesztése
- Profilok mentése
- Elérhető referenciaanyagok dokumentálása

## Teszt F – Játékmódváltás

Amennyiben a tesztjáték lehetővé teszi, ellenőrizd:

- Gyakorlás
- Szakaszindítás
- Szakaszváltás
- Új autó kiválasztása
- Játék bezárása
- Játék újraindítása
- Online mód, ha rendelkezésre áll és a használat engedélyezett

## Teszt G – Hibakezelés

Teszteld:

- Bridge bezárása
- Játék bezárása
- Wi-Fi kapcsolat megszakadása
- Mobil alkalmazás háttérbe kerülése
- Nem támogatott telemetriamező
- Érvénytelen adatcsomag
- Hibás profilfájl
- Ismeretlen játék
- Hibás billentyű-hozzárendelés

Az alkalmazás ne omoljon össze.

A hibát érthetően jelezze.

---

# 16. DIAGNOSZTIKA ÉS HIBANAPLÓ

A későbbi fejlesztésekhez szükség van részletes diagnosztikára.

A PC Bridge és a mobilalkalmazás is rendelkezzen diagnosztikai felülettel.

Jelenítse meg:

- Alkalmazásverzió
- Bridge-verzió
- Aktív játék
- Játékverzió, ha megállapítható
- Adapter neve és verziója
- Telemetria állapota
- Frissítési sebesség
- Utolsó adatcsomag időpontja
- Kapcsolódott eszközök
- Kapcsolatkésleltetés
- Parancs-visszaigazolások
- Hibák
- Nem támogatott funkciók

Lehessen diagnosztikai jelentést exportálni.

A jelentés legyen alkalmas arra, hogy egy későbbi Codex-fejlesztésben a hibát elemezni lehessen.

---

# 17. TELEPÍTHETŐ ALKALMAZÁSOK

Az átadás célja egy ténylegesen használható telepítési csomag.

## 17.1. Android

Készíts:

- Flutter release APK
- APK verzióazonosító
- Telepítési útmutató
- Frissítési útmutató

Az APK a szükséges Android-követelmények teljesülése mellett telepíthető legyen.

## 17.2. iOS

Készíts:

- Teljes Flutter iOS projekt
- Xcode-konfiguráció
- iPhone és iPad támogatás
- Aláírási dokumentáció
- Telepítési útmutató

Ha rendelkezésre áll macOS, Xcode és megfelelő aláírási környezet, készíts telepíthető iOS kiadást is.

Ha nem áll rendelkezésre, ne állítsd azt, hogy elkészült az aláírt IPA. Ehelyett dokumentáld pontosan, milyen feltételek hiányoznak.

## 17.3. Windows

Készíts:

- Windows x64 PC Bridge build
- Önálló futtatható alkalmazás
- Lehetőleg Windows telepítő
- Rendszertálca-funkció
- Indítási és csatlakoztatási útmutató

## 17.4. Átadási struktúra

Hozz létre egy jól áttekinthető kiadási mappát:

SIM_CONTROL_STUDIO_RELEASE/

- Android/
- iOS/
- Windows/
- Source/
- Profiles/
- Documentation/
- Tests/

A könyvtárakba csak ténylegesen elkészült fájlokat helyezz.

Amennyiben lehetséges, hozz létre egy ZIP átadási csomagot.

---

# 18. PROJEKTSTRUKTÚRA ÉS KÉSŐBBI FEJLESZTÉS

A projekt legyen moduláris, könnyen továbbfejleszthető.

Javasolt mappák:

sim-control-studio/

- mobile_flutter/
- windows_bridge/
- game_adapters/
- shared_protocol/
- vehicle_profiles/
- dashboards/
- button_boxes/
- editor/
- tests/
- documentation/
- releases/

Minden autóprofil külön, verziózott konfigurációként szerepeljen.

Egy autóprofil összekapcsolja:

- Az autó azonosítóját
- A hozzá tartozó műszerfalat
- A hozzá tartozó kezelőpanelt
- Az autóspecifikus grafikai elemeket
- A telemetriaadatok hozzárendelését
- A játékvezérlők hozzárendelését
- A referenciaanyagokat
- Az ismert kompatibilitási korlátokat

Később új autó hozzáadásakor ne legyen szükség az alkalmazás fő működésének átírására.

Ugyanez igaz az új játékintegrációkra és új widgettípusokra.

Használj verziókezelést, dokumentált modulhatárokat és automatizált teszteket.

---

# 19. FEJLESZTÉSI SORREND

A teljes projektet fokozatosan, de egységes rendszerként készítsd el.

## Első szakasz – Működő technikai alap

- Flutter mobilalkalmazás
- Windows PC Bridge
- Kétirányú kommunikáció
- Több mobileszköz egyidejű csatlakoztatása
- Assetto Corsa Rally valós telemetriaolvasó
- Élő műszerfal
- Működő Button Box
- Alapvető diagnosztika

Az első szakasz végén a valódi Rally-telemetria működésének ellenőrizhetőnek kell lennie.

## Második szakasz – Autóspecifikus profilok

- Mind a 20 műszerfal
- Mind a 20 hozzáillő kezelőpanel
- Hiteles referenciaanyagok
- Profilpárosítás
- Valósághű grafikai elemek
- Autóspecifikus vezérlőelrendezések

## Harmadik szakasz – Szerkesztők

- Dashboard szerkesztő
- Button Box szerkesztő
- Saját SVG/PNG import
- Mentés
- Profilmásolás
- Import/export
- Többoldalas kezelőfelületek

## Negyedik szakasz – Bővített játékkompatibilitás

- Assetto Corsa EVO
- Assetto Corsa
- BeamNG.drive
- További, dokumentált protokollal rendelkező játékok
- Játékmód-kompatibilitás ellenőrzése
- Online használat feltételeinek ellenőrzése

## Ötödik szakasz – Tesztelés és kiadás

- Automatizált tesztek
- Kétklienses integrációs tesztek
- Telemetria-protokolltesztek
- Hálózati hibakezelés
- Profilbetöltés tesztelése
- Android release APK
- Windows futtatható kiadás
- iOS build, ahol a környezet ezt lehetővé teszi
- Magyar dokumentáció

A fejlesztés során ne elégedj meg egy statikus kezelőfelülettel.

A valódi adatkapcsolat és az alkalmazás használhatósága elsődleges követelmény.

---

# 20. VÉGSŐ ELFOGADÁSI FELTÉTELEK

A kész programnak a következő célt kell teljesítenie:

**Egy Windows PC-n elindítom az Assetto Corsa Rallyt, a telefonon megjelenik a valódi jármű telemetriája, és közben egy második telefonon vagy tableten egy autóspecifikus Button Box segítségével tudom használni a játék támogatott vezérlési funkcióit.**

A felhasználó választhasson mind a 20 autó műszerfalából.

A második készülék automatikusan ajánlja fel a kiválasztott autóhoz tartozó kezelőpanelt.

Mind a 40 alapprofil ténylegesen elkészített, szerkeszthető és használható legyen.

A program biztosítson saját dashboard- és Button Box-szerkesztőt.

Az elérhető valódi telemetria minden támogatott játékban és játékmódban használható legyen, az adott játék technikai és szabályzati korlátainak megfelelően.

A program később új autókkal, játékokkal, funkciókkal és elrendezésekkel bővíthető legyen.

## Átadás előtt

Készíts részletes, géppel ellenőrizhető fejlesztési állapotjelentést.

Minden nagyobb funkcióhoz jelöld:

- Elkészült és automatizáltan tesztelt
- Elkészült, valós eszközön tesztelt
- Elkészült, valós eszközön még tesztelendő
- Részlegesen elkészült
- Nem készült el

A tesztállapotokat ne hamisítsd meg.

Ha nem férsz hozzá futó Assetto Corsa Rallyhoz vagy két fizikai mobileszközhöz, készíts a rendelkezésre álló protokollreferenciák alapján tesztelhető implementációt és automatizált integrációs teszteket, majd dokumentáld a felhasználónál elvégzendő éles ellenőrzést.

Ne állíts sikeres fizikai tesztet, ha azt nem hajtottad végre.

## A feladat végrehajtása

Most kezdd el a projekt tényleges implementációját.

A teljes specifikációt munkacsomagokra bonthatod, de ne kérd a felhasználótól újra a már meghatározott követelményeket.

A szükséges architektúrai részletekben válassz ésszerű, dokumentált megoldást.

Az egyes lépések után:

1. Implementáld a funkciót.
2. Buildeld a projektet.
3. Futtasd az elérhető teszteket.
4. Javítsd a feltárt hibákat.
5. Frissítsd a dokumentációt.
6. Folytasd a következő feladattal.

Ne helyettesítsd a nem működő funkciókat látszatmegoldásokkal.

Ha a környezetben valamely build vagy hardveres teszt nem végezhető el, jelezd a konkrét okot, és készítsd el a lehető legteljesebb, ellenőrizhető átadási állapotot.

**A feladat végső eredménye ne pusztán forráskód legyen, hanem a rendelkezésre álló buildkörnyezetben létrehozható, ténylegesen telepíthető program, a teljes forráskóddal és dokumentációval együtt.**

A program neve és első verziója:

# SIM CONTROL STUDIO 0.1.0

**KEZDD MEG A FEJLESZTÉST, A TELJES PROJEKT LÉTREHOZÁSÁVAL ÉS AZ ASSETTO CORSA RALLY VALÓDI TELEMETRIAADAPTERÉNEK IMPLEMENTÁLÁSÁVAL.**