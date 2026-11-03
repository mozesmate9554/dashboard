# Telepítés – SIM CONTROL STUDIO 0.4.0 Alpha (ma esti Android-próba)

## 1. Letöltés

A letöltési linkek a `TEST_REPORT.md` „Letöltések” részében vannak (GitHub Actions artifactok, GitHub-bejelentkezés szükséges).

- **Android APK** – ZIP, benne az `app-release.apk`.
- **Windows Bridge** – ZIP, benne a telepítő (`SIM_CONTROL_STUDIO_0.4.0_Setup_x64.exe`) és a hordozható `SimControlStudio.Bridge.exe`.

## 2. Windows Bridge frissítése

1. Zárd be a futó 0.3.0 Bridge-et (tálca ikon → Kilépés).
2. Futtasd a 0.4.0 telepítőt. A beállítások, a párosított eszközök és a billentyűkiosztás megmaradnak (`%LOCALAPPDATA%\SimControlStudio`).
3. Indítsd el, válaszd az **Assetto Corsa Rally** adaptert, és kapcsold be a **Helyi hálózat engedélyezése** és a **Mobilvezérlés engedélyezése** opciót.
4. **Játékvezérlés** lap: állítsd be a billentyűket a `BUTTON_MAPPING.md` szerint. Az új sorok: `highBeam`, `indicatorLeft`, `indicatorRight`, `handbrake`, `respawn`. A `lights` sornál a lenyomás 150 ms legyen.

## 3. Android

1. **Előtte exportáld a saját elrendezéseidet:** Szerkesztő → export. A preview-aláírás buildenként változhat.
2. Ha a telepítés aláírási ütközés miatt nem sikerül, töröld a 0.3.0-t, majd telepítsd a 0.4.0 APK-t, és párosítsd újra QR-kóddal.
3. Indítás után: **Autóprofilok** → válaszd az autót → **Kezelőpanel** vagy **Műszerfal**. Fekvő tájolásban teljes képernyős a nézet.
   A műszerfalak oldalai (lapozás): Škoda – játékbeli kijelző, majd a 0.3.0 fotóalapú oldalak; 208 – kijelző, GPS-tripmeter, rejtett mezők; i20 – kijelző, rejtett mezők; Polo – felső és alsó kijelző; 206 – LCD, rejtett mezők; Subaru – analóg műszerek, tripmeter.
4. **Beállítások:** Kapcsolóhangok be/ki, hangerő, Érintéses rezgés.
5. A kijelző „…” menüjében: **Éjszakai megvilágítás**, eszköztár elrejtése.

## 4. Ma esti teszt-ellenőrzőlista

| # | Lépés | Elvárt |
|---|---|---|
| 1 | START gomb nyomva tartása | motor indul; felengedéskor a Bridge felengedi a billentyűt |
| 2 | LIGHT gomb nyomásonként | a játékban a fények léptetődnek; jegyezd fel, **hány lépés** a teljes kör |
| 3 | HIGH | távfény be/ki |
| 4 | « / » | irányjelzők |
| 5 | WIPE nyomásonként | ablaktörlő-fokozatok léptetése |
| 6 | Kézifék (tartsd) | behúzva marad, amíg nyomod |
| 7 | Wi-Fi kikapcsolása nyomott kéziféknél | a Bridge felengedi a kéziféket (nem ragad be) |
| 8 | Motortérkép forgatás | a térképérték változik a játék kijelzőjén |
| 9 | Váltásjelző: pörgesd fel a motort | 208: 10 LED 5200 rpm-től, 6100 felett mind piros; i20/Polo/Škoda: színes villanás (küszöb feltételezett, jegyezd fel, ha eltér a játéktól) |
| 10 | Autóváltás a játékban | megjelenik-e az autóprofil-ajánlás (a játék `vehicleId` értéke a Telemetria lapon látszik) |

A LED **félig világító, sötét közepű** állapota azt jelenti, hogy a Bridge végrehajtotta a parancsot. Ez **nem** igazolja a játékállapotot. A teljes fény csak akkor jelenik meg, ha a játék telemetriája igazolja az állapotot.
