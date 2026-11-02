# VEHICLE_REFERENCE_REPORT – SIM CONTROL STUDIO 0.4.0 Alpha

Állapot: **internetes kutatás, 1. kör (2026-11-02)**. Kiegészíti a `GAME_ASSET_REFERENCE_REPORT.md` fájlt.

## Szabály a képekhez

A valódi fotók **tervezési referenciaként** szolgálnak (elrendezés, arányok, színek, feliratok, kapcsolótípusok). A kiadott alkalmazásba nem másoljuk be a gyártói vagy harmadik féltől származó fotókat, logókat és márkajelzéseket. A grafika saját vektoros rajz, a referenciák alapján.

**Elsődleges hitelesség:** a mobil műszerfal a *játékbeli* autót tükrözi, ezért a döntő referencia a játék `WB_Gauge*` kijelzőjének élő képe. A valódi autó fotói a kapcsolópanelhez és az anyaghatásokhoz kellenek, mert a játékbeli cockpit is ezekből készült.

## Játékbeli változatok (megerősítve)

| Autó | ACR-azonosító | Változat a játékban | Forrás |
|---|---|---|---|
| Peugeot 208 Rally4 | `Peugeot208Rally4` | 2020+ Rally4 | játék eszközlistája |
| Škoda Fabia RS Rally2 | `SkodaFabiaRSRally2` | 2022+ RS Rally2 | játék eszközlistája |
| Hyundai i20 N Rally2 | `HyundaiI20NRally2` | 2021+ i20 N Rally2 | játék eszközlistája |
| VW Polo GTI R5 | `VWPoloGTIR5` | **2018** Polo GTI R5 | [505 Games 0.6 changelog](https://support.505games.com/support/solutions/articles/150000233496-assetto-corsa-rally-early-access-update-0-6) |
| Peugeot 206 WRC | `Peugeot206WRC` | **1999** 206 WRC | [505 Games 0.6 changelog](https://support.505games.com/support/solutions/articles/150000233496-assetto-corsa-rally-early-access-update-0-6) |
| Subaru Impreza | `SubaruImprezaS3` | **1993** Impreza 555 Group A (első versenyév, nem az 1995-ös McRae-autó) | [CarThrottle](https://www.carthrottle.com/news/duo-90s-rally-icons-land-assetto-corsa-rally), [bsimracing](https://www.bsimracing.com/assetto-corsa-rally-1993-subaru-impreza-gr-a/) |

## Autónként

### 1. Škoda Fabia RS Rally2 – első mérföldkő

- **Forrás:** a [Škoda Motorsport alapinformációs oldala](https://www.skoda-motorsport.com/en/skoda-fabia-rs-rally2/basic-information/) és a 0.3.0 `REFERENCES.md` gyári fotói (kormány + kijelző, középkonzol).
- **Igazolt:** nagyobb fő kijelző; **érintéses** középső kezelőpanel; integrált interkomvezérlés; indítógomb a kormányon.
- **Játékból:** külön kijelzőelemek a kéziféknek (be/ki/hiba) és az ablaktörlőnek (int/slow/fast). A világítást és az ablaktörlőt a játék körbeléptetéssel kezeli.
- **Következmény a Button Boxhoz:** a valódi középkonzol **érintőfelületű gombmező**, nem billenőkapcsolós panel. A hűség érdekében a Škoda-panel világító, érintéses gombmezőt kap, billenő- és fedeles kapcsolót csak ott, ahol a fotó igazolja (FIRE-fedél).
- **Hiányzik:** a kijelzőgyártó és a betűtípus neve, valamint a pontos gombfeliratok éjjel.

### 2. Peugeot 208 Rally4 – a legjobban dokumentált

- **Forrás:** [Peugeot 208 Rally4 User Guide (Version E), manualslib](https://www.manualslib.com/manual/2872833/Peugeot-208-Rally-4-2021.html).
- **Váltásjelző:** sárga LED-ek kb. 5200–6000/min között, fix piros 6100–6150, villogó piros 6150 fölött. A játék saját `WB_208MultiPhaseRPMLed` widgetje ezt a többfázisú LED-sort követi.
- **Riasztó-LED:** villogó **kék** jelzés alacsony olajnyomásnál (<2,5 bar 900/min fölött), 115 °C feletti vízhőnél és alacsony akkufeszültségnél.
- **Kijelzőoldalak:** 1 Road, 2 Stage, 3–4 Check, 5 Brake bedding, 6–7 Mechanical, 8 hűtés/fék/kézifék, 9 kisáramú fogyasztók, 10 diagnosztika.
- **Konzol:** MAIN (főkapcsoló) → POWER (sárga LED) → START (csak nyomva tartva forgat). Az első indítás előtti olajnyomás-feltöltéshez a KLAXON + START kell.
- **Funkciógombok sárga LED-del:** ROAD / STAGE térkép, TARMAC / GRAVEL, WARNING, LIGHTS (hosszú nyomás: kényszerített), DEMISTER, FANS.
- **Jobb kar:** ablaktörlő int / lassú / gyors (1–3. fokozat), húzásra mosó.
- **Kiegészítő billentyűzet:** rövid nyomás = fényerő / oldalváltás; hosszú = üzemanyag-pumpa, fogyasztás-nullázás.

### 3. Hyundai i20 N Rally2

- **Forrás:** [Hyundai Motorsport műszaki adatlap](https://motorsport.hyundai.com/Corporate%20Site/Car%20Spec/i20%20N%20Rally2/Hyundai%20Rally2%20Tech%20Specs.pdf), [Wikipedia](https://en.wikipedia.org/wiki/Hyundai_i20_N_Rally2), [Racemarket hirdetés](https://racemarket.net/rally/rally-cars-for-sale/r5/hyundai-i20-n-rally2-step-2-i7004) (fotók).
- **Igazolatlan:** a kijelző gyártója és a kapcsolópanel-kiosztás. Egy közösségi SimHub-replika létezik ([overtake.gg](https://www.overtake.gg/downloads/hyundai-i20-n-rally2-dashboard-ea-sports-wrc.65630/)), de az a játék kijelzőjét másolja, nem gyári forrás.
- **Szükséges:** a játékbeli `WB_GaugeHyundaiI20NRally2` képernyőképe és közeli konzolfotó.

### 4. Volkswagen Polo GTI R5 (2018)

- **Forrás:** [VW Newsroom – Polo GTI R5](https://www.volkswagen-newsroom.com/en/the-new-polo-gti-driving-presentation-2512/the-new-polo-gti-r5-gti-goes-rallying-2567), [Wikipedia](https://en.wikipedia.org/wiki/Volkswagen_Polo_GTI_R5), Racemarket-hirdetések (fotók).
- **Játékból:** saját fordulatszám-textúra (`T_PoloGaugeRpm`) és UV-referencia. A kijelző tehát egyedi, ívelt fordulatszám-skálás.
- **Igazolatlan:** a kijelző gyártója, a konzol feliratai. **Szükséges:** játékbeli képernyőkép.

### 5. Peugeot 206 WRC (1999)

- **Forrás:** [Wikipedia](https://en.wikipedia.org/wiki/Peugeot_206_WRC), [L'argus – Grönholm-féle 2001-es C31](https://www.largus.fr/actualite-automobile/une-peugeot-206-wrc-pilotee-par-marcus-gronholm-en-vente-10316395.html), [Rallyssimo](https://www.rallyssimo.it/2020/04/13/peugeot-206-wrc-il-proiettile-dargento/).
- **Igazolt:** a műszerfal-alapforma részben a széria 206-osé, minden más át van építve. A Magneti Marelli volt a korszak Peugeot Sport-elektronikai partnere.
- **Játékból:** saját LCD-textúra (`T_Peugeot206WRCLCD_B`). A kijelző tehát korhű, monokróm LCD jellegű.
- **Figyelem:** a játék 1999-es autót modellez, a 2001-es fotók eltérhetnek.

### 6. Subaru Impreza 555 Group A (1993)

- **Forrás:** [impreza555 technikai adatok (ISDC fórumon idézve)](https://isdc.ie/forum/threads/subaru-impreza-555-group-a-technical-specifications-and-stats-impreza555-com.42273/), [impreza555.nl/specs](https://impreza555.nl/specs.htm).
- **Igazolt műszerek:** **Stack ST400 analóg fordulatszámmérő, 0–8000/min**; **VDO vízhőmérő**; Coralba tripmaster; GEMS adatgyűjtő; FHI/STI motorvezérlés.
- **Tervezés:** ez az egyetlen **analóg** műszerfal a hatból (mutatós fordulatszámmérő, kerek kiegészítő műszerek, billenőkapcsoló-sor). Ez a 6. pontban kért korhű analóg megvalósítás.

## Hiányzó referenciák – kérés a felhasználóhoz

Autónként a játékból, cockpit-kamerával, a HUD kikapcsolásával:

1. Teljes műszerfal és konzol nappal, majd éjjel bekapcsolt világítással.
2. A kijelző közelről: gyújtás, alapjárat, limiter (váltásjelző-LED-ek).
3. A világítás minden `CycleLights`-lépése (hány állapot van?), a távfény, az ablaktörlő minden állapota.

## Képkeresési találatok (vizuális tájékozódás)

Gyártói és kereskedői fotók: Škoda Storyboard / Škoda Motorsport, Racemarket.net, Racecarsdirect, Mikado Racing, Supercar-hirdetések (206 WRC Evo 2), impreza555. Ezeket csak elrendezés-referenciaként használjuk.
