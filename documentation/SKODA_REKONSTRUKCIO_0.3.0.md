# Škoda Fabia RS Rally2 – két fotóalapú felület

Kizárólag a **vezető digitális kijelzője** és a **különálló középkonzoli kezelőpanel** kapott részletes új grafikát. Kormány vagy kormánygombok rajza nem készült. A 2022–2024-es gyártói referenciafotókat használjuk; az eltérő, későbbi évjáratokhoz nem állítunk egyezést.

## Referenciák és bizonyíthatóság

| Felület | Elsődleges bizonyíték | Megfigyelt részlet | Rekonstrukció / korlát |
|---|---|---|---|
| Vezetői kijelző | [Škoda Motorsport cockpitfotó](https://skoda-motorsport.s3.amazonaws.com/com/2024/10/Rally2_steering_wheel.jpg) | Speed balra, Map mezők és ROAD középen, nagy Gear jobbra; LC Limiter, óra és Time lent; felső LED-mátrix és hőmérséklet-jel | A kis kijelző a teljes fotóban kevés pixel: LED-darabszám, küszöb, pontos font, bezel-méretek és ikonvonalak becslések |
| Középkonzol | [Škoda Storyboard 2022 fotó](https://cdn.skoda-storyboard.com/2022/10/02_FABIA_RS_Rally2_f0de083a.jpg) | Színes kupakok, forgó és billenő, servis menu, hívásgombok, két hangerősáv, vészvillogó/köd/ALL, FIRE fedél | Perspektívából síkba rajzolt geometria; felirat nélküli kapcsolók funkciói és az audio-csatornák hozzárendelése nem teljesen igazolt |
| Műszaki elhelyezés | [Gyártói alapinformáció](https://www.skoda-motorsport.com/en/skoda-fabia-rs-rally2/basic-information/) | Fő kijelző, középkonzoli érintőpanel és interkom; az indító a kormányon | Az alkalmazás indítógombja emiatt külön gyorsvezérlő, nem a konzolra kitalált gyári gomb |

A cockpitfotó középen lent látható nagyobb szervizmonitorja külön egység. A 0.3.0 vezetői felülete a kormányoszlop fölötti **kis kijelzőt** rekonstruálja. A fotóeredet és SHA-256 az autó `REFERENCES.md` / `profile.json` fájljában és a kiadás összehasonlító dokumentumában szerepel.

## Megvalósítás

A vezetői nézetben a bezel, skálázható számok, ötfokozatú Map-kijelzés, LED-mátrix és állapotikon külön szerkeszthető elem. A Barlow Condensed helyettesítő betűtípus, nem igazolt gyári font; OFL-licence a `documentation/licenses` mappában. Az alkalmazás két további telemetriaoldala megőrzi a korábbi motor/futómű adatokat; ezek kifejezetten **alkalmazásoldalak**, nem gyárinak állított képernyők.

A konzol 16 interaktív vezérlője saját SVG-rajzzal rendelkezik: kupak, perem, árnyék, ikon, billenő, hangerősáv és védőfedél. A grafika és a parancskötés ugyanazon az elemen van, így áthelyezéskor, forgatáskor, méretezéskor együtt marad. Az elemek másolhatók, csoportosíthatók, a parancs és saját grafika a szerkesztőben módosítható. A háttérlemez zárolt, de feloldható. A fotó nincs az alkalmazás hátterébe lapítva.

Az új logikai parancsokhoz **nincs automatikusan kitalált játékbillentyű**. A Bridge-ben az adott játék és autó támogatott műveleteihez rendelj kiosztást. Az `executed` Windows-bemenetet, a `simulated` DEMO-műveletet igazol; egyik sem gyári autófunkció-tanúsítás. A tűzoltófedél szimulátorbeli, szabadon kiosztható gomb, nem fizikai autóvezérlés.

A valós Rally-adapter új mezőket nem talál ki: a launch RPM limit, Map, óra, ROAD állapot, hőmérsékletek, szakaszidő és rádióhangerő csak támogatott érvényes mintából jelenhet meg. A launch limit külön mező, **nem azonos** a motor fordulatszám-határával. Hiányzó adat `—`, nem hamis nulla; a DEMO szintetikus értékeket ad, állandó jelöléssel.

## Előnézetek

- `SKODA_DASHBOARD_0.3.0.png`: 2560×1776, a tényleges Flutter-renderelővel.
- `SKODA_PANEL_0.3.0.png`: 2200×3076, a tényleges Flutter-renderelővel.
- `SKODA_REFERENCE_COMPARISON_0.3.0.pdf`: két felület, gyártói fotórészlettel, külön megfigyelt és rekonstruált részletekkel.
- Két nagy felbontású összehasonlító PNG és gépi eredetjegyzék a Skoda Previews ZIP-ben.

A képeken DEMO-adat szerepel, nem élő játék vagy fizikai iPhone-képernyő. A natív szimulátoros képernyőképek a teljes kiadás `Tests/iOS-CI` és `Tests/Android-native` mappáiban vannak. A grafika részletesebb fotóalapú rekonstrukció, **nem hitelesített gyári replika**.
