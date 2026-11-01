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

`Bridge.Windows` a felhasználó fiókjában futó WinForms alkalmazás. QR-kód, tálca, engedélyek, kiosztás, teszt és diagnosztika itt kezelhető. A portable self-contained win-x64 kiadás mellé opcionális, felhasználói Start menü parancsikont készítő PowerShell telepítő kerül. Nincs szolgáltatás, automatikus rendszerindítás vagy önkényesen megnyitott tűzfalszabály.

## Mobil

`models.dart`: telemetria és validált, másolható JSON-elrendezés. `storage.dart`: verziózott alapprofilok és helyi személyes profilok. `connection.dart`: certificate pinning, secure storage, heartbeat, exponenciális újracsatlakozás és parancsnapló. `display.dart`: natív Flutter widgetek, CustomPainter műszerek és érintéses vezérlők. `editor.dart`: azonos JSON-modellt módosító érintéses szerkesztő. `main.dart`: varázsló és 10 fő oldal.

A gyakori telemetriafrissítés külön ValueNotifieren érkezik; a főnavigáció nem épül újra minden 60 Hz-es mintára. Az élő kijelző kilépési és lapozási gombot tartalmaz, elrejti a rendszernavigációt és ébren tartja a készüléket. Az elavulást a mobil a PC órájától független érkezési stopperrel ellenőrzi.

A képek és SVG-k a személyes JSON-ba ágyazva exportálhatók. Bemeneti méret-, geometria-, feltétel- és eszközparaméter-korlátok védik a betöltést. Egy hibás személyes JSON nem íródik felül automatikusan.

## Bővítés

Új autóhoz új, verziózott `vehicle_profiles/<id>/profile.json`, referenciajegyzék és katalógusbejegyzés készül. A generátor minden elrendezést kifejezett kompozíciós listából állít elő. Új widgethez a típusvalidátort, az Instrument/PanelControl renderelőt és a szerkesztő tulajdonságait kell bővíteni. Új játékhoz a GameAdapter modulhatár használható; a mobil hálózati rétege marad.

A jelenleg gyáriként nem igazolt elrendezésrészeknek külön referenciaállapota van. Működő telemetriamező, működő játékparancs, gyári grafikai hűség és fizikai eszközteszt négy eltérő bizonyítékkategória; az állapotjelentés nem vonja őket össze.
