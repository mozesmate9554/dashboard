# Adapter bővítési pontok

A közös C# interfész `IGameAdapter`: `GameId`, `Health`, `PollAsync(CancellationToken)` és `Dispose`. A forrás csak egyszer olvasódik, a Bridge ugyanazt a változtathatatlan normalizált keretet osztja szét minden kliensnek.

Egy új adaptert a Bridge.Core alatt vagy arra hivatkozó osztálykönyvtárban valósíts meg. Az `AdapterFactory` és `BridgeConfiguration` engedélyezett játéklistájába, a Windows listaválasztóba és a mobil katalógusba fel kell venni. A mobil hálózati és widgetrétegét nem kell átírni, ha a meglévő normalizált mezőket használja. Futás közben betöltött idegen DLL-ekhez nincs ellenőrizetlen pluginloader.

| Játék | Kódolt állapot | Következő megalapozandó interfész |
|---|---|---|
| Assetto Corsa Rally | shared memory, tesztelt dekóder/transport; éles teszt hiányzik | játékverzió és mezők fizikai igazolása |
| Assetto Corsa EVO | bővítési pont | aktuális hivatalos/shared-memory szerződés ellenőrzése |
| Assetto Corsa | shared memory; strukturális mintateszt | AC-verzió és session teszt |
| BeamNG.drive | OutGauge loopback UDP; csomagteszt | aktuális OutGauge bekapcsolás/csomag ellenőrzése |
| ACC | shared memory; strukturális dekóder | autómezők, sessionek, online szabályok igazolása |
| iRacing | bővítési pont | hivatalos SDK és felhasználási feltételek |
| Automobilista 2 | bővítési pont | dokumentált PCARS-család telemetria, konkrét verzió |
| rFactor 2 | bővítési pont | engedélyezett shared-memory plugin és licence |
| Le Mans Ultimate | bővítési pont | az adott játék saját engedélyezett interfésze |
| EA SPORTS F1 | bővítési pont | évjáratonként verziózott UDP-protokoll |
| EA SPORTS WRC | bővítési pont | hivatalos UDP-konfiguráció és csomagséma |
| DiRT Rally 2.0 | bővítési pont | dokumentált extradata UDP és konfiguráció |
| RaceRoom | bővítési pont | gyártói shared-memory SDK |
| Forza Motorsport / Horizon | bővítési pont | Data Out, külön játékváltozat és sémaverzió |
| Project CARS | bővítési pont | konkrét címhez dokumentált UDP/shared memory |
| ETS2 / ATS | bővítési pont | SCS Telemetry SDK és megengedett plugin |

A táblázat utolsó oszlopa kutatási irány, nem ellenőrzött licenc-/protokollígéret. Játékfolyamat-injektálás, anti-cheat megkerülés, memóriamódosítás és automatikus vezetés nem része a rendszernek.

Új mezőnél rögzítsd az egységet, közvetlen/számított forrást, timestampet és az érvényességet. Az ismeretlen mezőt hagyd `unsupported` értékkel, ne nullával kitöltött élő állapotként. A frame időpontja és a mintasorszám csak új valódi forrásmintánál léphet előre.

Az adapterteszthez kis, dokumentált bináris fixture használható a `tests/` alatt. Ne regisztráld szimulátorként a termékbe, és ne nevezd a fixture-rel mért működést fizikailag igazolt játékkompatibilitásnak.
