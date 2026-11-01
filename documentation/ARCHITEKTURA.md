# Modulhatárok és működés

```text
Játék megengedett API-ja
  → IGameAdapter (C#, egy olvasó)
  → TelemetryFrame / Datum (egység, forrás, timestamp, validity)
  → legfrissebb közös keret
  → TLS/WebSocket több külön mobilkliensnek
  → Flutter Canvas / műszerek / kezelőpanel

Mobilparancs → session-ellenőrzés → jogosultság + fókusz + helyi kiosztás
  → ControlEngine tulajdonolt billentyűk → Windows SendInput
  → received/executed/rejected visszaigazolás

Játék tényleges állapota → külön telemetriamező, nem az ACK-ból kitalált állapot
```

## PC

`Bridge.Core` platformfüggetlen normalizálást, hálózatot, regisztert és vezérlőlogikát tartalmaz. A platformhatárokat `IGameProbe`, `IMemorySource`, `IKeySink`, `IGameAdapter` interfészek választják el. A Windows-specifikus megvalósítás csak Windows alatt nyit named mappinget vagy hív SendInputot. A tesztek a saját könyvtárukban adnak determinisztikus bináris mintát és billentyűnaplózó sinket; ezek nem kapcsolhatók be termékadapterként.

`BridgeRuntime` egyszerre egy forrásadaptert olvas 20/30/60 Hz ütemezéssel. Minden mobil saját küldési ciklust kap, legfeljebb a kért ütemben, a közös legutóbbi mintából. Nincs kliensenként ismételt játékmemória-olvasás vagy korlátlan csomagsor. A párhuzamos WebSocket-küldést session-szemafor rendezi; a lassú írás időkorlátos.

`Bridge.Windows` a felhasználó fiókjában futó WinForms alkalmazás. QR-kód, tálca, engedélyek, kiosztás, teszt és diagnosztika itt kezelhető. A portable self-contained win-x64 kiadás mellé NSIS telepítő kerül, felhasználói telepítéssel, Start menüvel és eltávolítóval. Nincs szolgáltatás, automatikus rendszerindítás vagy önkényesen megnyitott tűzfalszabály.

## Mobil

`models.dart`: telemetria és validált, másolható JSON-elrendezés. `storage.dart`: verziózott alapprofilok és helyi személyes profilok. `connection.dart`: certificate pinning, secure storage, heartbeat, exponenciális újracsatlakozás és parancsnapló. `display.dart`: natív Flutter widgetek, CustomPainter műszerek és érintéses vezérlők. `editor.dart`: azonos JSON-modellt módosító érintéses szerkesztő. `main.dart`: varázsló és 10 fő oldal.

A gyakori telemetriafrissítés külön ValueNotifieren érkezik; a főnavigáció nem épül újra minden 60 Hz-es mintára. Az élő kijelző kilépési és lapozási gombot tartalmaz, elrejti a rendszernavigációt és ébren tartja a készüléket. Az elavulást a mobil a PC órájától független érkezési stopperrel ellenőrzi.

A képek és SVG-k a személyes JSON-ba ágyazva exportálhatók. Bemeneti méret-, geometria-, feltétel- és eszközparaméter-korlátok védik a betöltést. Egy hibás személyes JSON nem íródik felül automatikusan.

## Bővítés

Új autóhoz új, verziózott `vehicle_profiles/<id>/profile.json`, referenciajegyzék és katalógusbejegyzés készül. A generátor minden elrendezést kifejezett kompozíciós listából állít elő. Új widgethez a típusvalidátort, az Instrument/PanelControl renderelőt és a szerkesztő tulajdonságait kell bővíteni. Új játékhoz a GameAdapter modulhatár használható; a mobil hálózati rétege marad.

A jelenleg gyáriként nem igazolt elrendezésrészeknek külön referenciaállapota van. Működő telemetriamező, működő játékparancs, gyári grafikai hűség és fizikai eszközteszt négy eltérő bizonyítékkategória; az állapotjelentés nem vonja őket össze.

## A 0.2.0 kiegészítései

A valós adapterek mellett explicit `DemoAdapter` és mobilos `DemoSimulator` van. Mindkettő `mode=demo` és `demo:` forrásmegjelölést ad; a DEMO-parancs `simulated` ACK-ja különbözik a Windows-bemenet `executed` állapotától. A mobilos DEMO leválasztja a socketet, megőrzi a párosítási célt, és nem hívja a hálózati küldést. A PC DEMO-adapter nem kap `IKeySink` referenciát; a ControlEngine ezenfelül tiltja a `gameId=demo` bemenetét.

A press parancsok futása nem blokkolja a WebSocket fogadóhurkát; a session legfeljebb 16 folyamatban lévő műveletet tart. Azonos művelet impulzusai sorba rendeződnek, a tulajdonos megszűnése a várakozókat is megszakítja. Autóprofil-váltás felengedi az előző kontextust. A fizikai gomb/Windows ACK és a telemetriából olvasott állapot továbbra is külön útvonal.

A profilkiosztás kulcsa `gameId/vehicleId`; hiányzó autókiosztásnál a játékalapértelmezés érvényes, üres autókiosztásnál semmi. A 2-es kiosztásséma mindkét szintet exportálja/importálja, a régi játékszintű JSON is olvasható. A telemetriakeret UTF-8 kódolása megosztható a kliensek között, nincs felhalmozódó mintasor. Az elavulás monotón érkezési idővel működik.

A szerkesztő azonos vásznon élő ValueNotifier-frissítést kap, és személyes másolatot módosít. Az igazítás az elem vagy zárolatlan csoport határolóját igazítja a vászonhoz; a csoport belső távolságai megmaradnak. Átlátszatlanság 0–1, forgatás fokban. A többoldalas vezérlők stabil elem- és oldalkulccsal rendelkeznek, és a tartás pointer-felengedéskor, megszakításkor vagy eltávolításkor megszűnik.
