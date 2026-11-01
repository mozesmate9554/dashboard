# Mobil szerkesztő és profilok

A szerkesztő a natív Flutter alkalmazás része. Az alapprofilok másolatként nyílnak meg, így a 40 szállított elrendezés megmarad. Saját név, azonosító, verzió, revízió, autóazonosító és szerepkör tartozik minden mentéshez.

## Használat

- A Szerkesztő oldalon hozz létre új műszerfalat/kezelőpanelt, vagy nyisd meg egy autó alapprofilját.
- Elem: érintéssel kijelölés, húzással mozgatás, kék sarokfogantyúval átméretezés. A 20 egységes rács elengedéskor illeszti az elemet.
- Tulajdonságok: telefonon a hangoló ikon nyitja a szerkesztőlapot; széles kijelzőn külön oldalsó felület jelenik meg. A szövegmező módosítását a billentyűzet bevitel/enter gombja alkalmazza.
- X/Y/méret, forgatás, rétegsorrend, zárolás, szín, háttér, felirat, betűméret, monospace/sans betűstílus, adatmező, figyelmeztetés, animáció és művelet megadható.
- Azonos csoportnevet adva több elemnek a húzás együtt mozgatja őket. A zárolt elemek nem mozdulnak.
- Visszavonás/ismétlés: legfeljebb 30 szerkesztési állapot. A műveletsor a munkameneten belül él; a profil tartósan a Mentés gombbal rögzül.
- Több oldal: legfeljebb 8 oldal/profil; az élő kijelző réteg gombja lapoz. A menü Vászon és oldal pontja állítja a háttérszínt és oldalnevét.

## Adatkapcsolatok

Példák: `speed`, `rpm`, `gear`, `throttle`, `brake`, `stageTime`, `tyrePressure`, `waterTemp`. A teljes mezőjegyzék a Bridge `TelemetryCatalog` osztályában és a protokolldokumentációban van. Egy widget hozzárendelése nem teszi elérhetővé a forrásban hiányzó adatot: ilyenkor — jelenik meg.

Figyelmeztetés e fölött: numerikus határérték; opcionálisan villogó piros megjelenítés. Feltételes láthatóság és engedélyezés: adatmező, összehasonlítás és numerikus határérték. Ismeretlen/elavult adat nem teljesíti a feltételt.

Műszerek: digitális adat, fokozat, skálás csík, analóg mutató, RPM LED-sor, pedálok, G-vektor, négy kerék értékei, jelzőfény, statikus szöveg, PNG/SVG. Az RPM LED-ek skálája tervezési beállítás; ha a forrás érvényes `rpmLimit` mezőt ad, az elsőbbséget élvez. A G-vektor X/Z ábrázolás nyers tengelyeket jelent, nem önkényesen kitalált Rally-tengelykonvenciót.

Vezérlők: nyomógomb, tartás, kapcsoló, relatív többállású/forgó/+− vezérlő, relatív csúszka, ikon. A kért lépésszám külön jelenik meg a valódi telemetriából visszaolvasott értéktől. Nincs hamis bekapcsolt lámpa csak azért, mert elküldtünk egy gombot.

## Grafikák és JSON

PNG/SVG import a kép ikonnal. Az SVG vektorosan jelenik meg. Külső hivatkozás, script, DTD és beágyazott HTML nem engedélyezett. Egy PNG legfeljebb 4 MB, SVG 1 MB; a profil összes képe legfeljebb 12 MB. A képek Base64 adatként a profilba kerülnek, ezért az export hordozható. Háttérképként helyezd a képet alsó rétegre, állítsd a vászon méretére és zárold.

A Profil export JSON a kész elrendezést viszi másik eszközre. A fő Szerkesztő oldalon importálható, új saját azonosítóval. A gyári jellegű alapadatot soha nem írja felül.

A billentyű-javaslat mező a mobilon szerkeszthető. A PC kiosztás export a játékhoz tartozó kiosztás-JSON-t készíti, amelyet a Bridge Játékvezérlés lapján lehet importálni. Ez helyi PC-engedélyezési lépés: a hálózati kliens nem állíthat be ellenőrizetlen tetszőleges Windows-billentyűket.

## Aktuális ellenőrzési korlát

A Dart forrás szintaktikai ellenőrzése és az összes JSON-profil geometriai/adatkapcsolati tesztje lefutott. Flutter analyze, widgetteszt, érintéses szerkesztés és mobilos fájlmegosztás fizikai ellenőrzése még nem történt; nem minősül készre tesztelt mobilfunkciónak. A mellékelt widgetteszt minden alapoldalt telefon- és tabletméretben ellenőriz, amikor rendelkezésre áll a Flutter SDK.

## 0.2.0

Az elem tulajdonságai között az átlátszatlanság 0–100%-os csúszkával állítható. A hat igazító ikon a vászon bal/közép/jobb, illetve felső/közép/alsó határához igazít; név szerinti csoport esetén a zárolatlan csoport együtt mozog. Ezek a műveletek visszavonhatók.

Az előnézet a beérkező telemetriát követi. PC nélkül a Kezdőlapon kapcsold be a DEMO módot, majd nyisd meg a szerkesztőt: a DEMO felirat itt is látható. A szerkesztés közben a vezérlőgomb nem küld játékparancsot. A PC kiosztás export a 2-es JSON-sémában az adott autóhoz kötött hozzárendeléseket adja át.
