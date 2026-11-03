# SIM CONTROL STUDIO 0.4.0 Alpha – kiadási jegyzet

Ág: `feature/sim-control-studio-0.4.0-alpha` (a `main` és a `v0.3.0` változatlan).

## Új

- **Hat Assetto Corsa Rally autó saját műszerfallal és saját kezelőpanellel:** Škoda Fabia RS Rally2, Peugeot 208 Rally4, Hyundai i20 N Rally2, VW Polo GTI R5 (2018), Peugeot 206 WRC (1999), Subaru Impreza 555 Group A (1993). Kérésre csak ez a hat autó szerepel az alkalmazás listájában.
- **Játékhű műszerfalak (2026-11-03):** mind a hat kijelző a játék saját `WB_Gauge*` widgetjének elrendezését követi (méretek, pozíciók, színkódok, láthatóság, váltásjelző küszöbök – FModel JSON-export, csak olvasás). Új oldalak: 208 GPS-tripmeter, Polo alsó kijelző, Subaru tripmeter, és autónként „Rejtett mezők”. A Škodánál a játékbeli kijelző lett az 1. oldal, a 0.3.0 fotóalapú oldalak utána megmaradtak.
- **Játékhű kezelőpanelek:** a kapcsolópanelek gombsorrendje és feliratai az autók játékbeli `T_IntDetails_B` textúráját követik; a játékakció nélküli gombok csak kijelzők, parancsot nem küldenek.
- **Mechanikus kezelőszervek:** billenőkapcsoló, nyomógomb (gumi, üveg, fém), fedeles biztonsági kapcsoló (nyitás → kapcsolás → 6 s után automatikus zárás), fokozatos forgókapcsoló, léptetőgomb. Mindegyik animált, és részletes anyaghatásokkal (szálcsiszolt fém, matt alumínium, karbon, gumi, csavarok, gravírozás) rajzolt.
- **Kapcsolóhangok:** 7 saját, szintetizált hang (fém ON/OFF, műanyag gomb, reteszelő, forgó, fedél, indító). Indításkor előre betöltődnek. A Beállításokban ki- és bekapcsolhatók, a hangerő állítható.
- **Haptika:** Androidon és iOS-en a rezgés a kapcsolótípushoz igazodik (indítónál erősebb). A meglévő „Érintéses rezgés” kapcsolóval kikapcsolható.
- **Négyfokozatú LED-visszajelzés:** kért → elküldve → Bridge végrehajtotta (feltételezett) → játék igazolta. Mellette ismeretlen és hibaállapot is van. A parancs elküldését a program soha nem mutatja igazolt játékállapotként.
- **Nappali és éjszakai megvilágítás:** a kijelző beállításaiban váltható, háttérvilágított gravírozással és erősebb LED-fényudvarral.
- **Automatikus autófelismerés:** ha a Bridge a játéktól autóazonosítót kap, az alkalmazás felajánlja a hozzá tartozó profilt. Az azonosítók élesben még ellenőrizetlenek, a kézi választás megmarad.
- **Új játékvezérlések:** `highBeam`, `indicatorLeft`, `indicatorRight`, `handbrake` (tartott), `respawn`.

## Javítva

- **Világítás:** a játékban a világítás körbeléptető (`IA_CycleLights`), nem BE/KI kapcsoló. A 0.3.0 kétállású kapcsolója ezért elcsúszott a játék állapotától. Most léptetőgomb, és a távfény külön gombot kapott. Beállítás: `documentation/BUTTON_MAPPING.md`.
- A kezelőpanel elrendezése nem torzul: a 0.4.0 panelek arányosan skálázódnak.

## Megőrizve

- A Škoda 0.3.0 fotórekonstrukciós középkonzolja változatként elérhető: **Szerkesztő → Használat**.
- DEMO mód, profilszerkesztő, import/export, többeszközös kapcsolat, autónkénti Bridge-kiosztás.

## Korlátok

Lásd `DEVELOPMENT_STATUS.md` és `TEST_REPORT.md`. A legfontosabbak:
- A játékbeli hatást csak élő játékban lehet igazolni, ezt ma este a felhasználó teszteli.
- A játék grafikáit referenciaként exportáltuk (csak olvasás), de az alkalmazásba **nem** kerültek be: minden kép saját rajz. A játék betűtípusai helyett szabad betűtípusok szerepelnek.
- A futás közben beállított színek és néhány váltásjelző küszöb (i20, Polo, Škoda) nem exportálható; ezek feltételezések, az elemek `referenceNote` mezője jelöli őket.
- A szakaszhossz (`DistanceFinal`) mezőt az ACR-adapter nem adja, ezért „—” látszik.
- iPhone-on fizikai teszt nem volt.
