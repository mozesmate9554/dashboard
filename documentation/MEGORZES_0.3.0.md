# A meglévő rendszer megőrzése – 0.3.0

A 0.3.0 a meglévő repository történetét folytatja. Az eredeti 0.1.0 forrás, a 0.2.0 állapot és az auditok a Git-előzményben és a history mappában megmaradtak.

Összehasonlítási alap: `cfa4b0d72d266c5112ddf67fd4c76856762147dc`.

## Rally és Windows-bemenet

| Fájl | SHA-256 a 0.2.0 és 0.3.0 forrásban | Egyezés |
|---|---|---|
| `windows_bridge/Bridge.Core/GameAdapters.cs` | `432d34a21b6c257222a26c768c5853040412fb1477e6bf113adaa502135d562a` | Bájtazonos |
| `windows_bridge/Bridge.Core/InputControl.cs` | `7e261cd689afcc671aaee52d560d14f3ef425023bc4016dbecf505ab5164ba06` | Bájtazonos |

A Rally bináris dekódolása, a fókusz-/engedélykapuk és a Windows input-életciklus ezen fájlokban maradt. A verziószám, az opcionális mezők/konfigurálható logikai parancsok katalógusa és az elkülönített DEMO bővült. A v1 hálózati szerződés és a korábbi műveletnevek változatlanok. Az új gombok nem kapnak kitalált alapértelmezett játékbillentyűt.

A 22 viselkedési Bridge-regresszió között szerepel a Rally-minta dekódolása, elavulás, fokozatok, jogosultságok, több kliens, TLS/pin, visszacsatlakozás, tartott gomb, megszakítás és a DEMO valódi bemenetének tiltása. A kiadási STATUS.json a végleges futás tényleges eredményét tartalmazza.

## Autóprofilok

Az összes 20 azonosító és mind a 40 alapelrendezés-azonosító megmaradt. A Škoda két alapja frissült, és további alkalmazás-telemetriaoldalak őrzik a korábbi adatmezőket. A többi 19 profilfájl teljes tartalma változatlan:

| Profil | Változatlan SHA-256 |
|---|---|
| `toyota-yaris-rally1` | `22925e30ed90a4eefc89fec109b5653372c6e602b0792aa626cfb02d3f612f78` |
| `ford-puma-rally1` | `c7d9fbe503cf731766588ebdb1578b8b64e4c9e2b7eddc7cd19ab4b25a662289` |
| `mclaren-720s-gt3-evo` | `3a9b58dd733951e377758d9eeadaaa023a25a90023270ee5e07e240a52b988cb` |
| `bmw-m4-gt3` | `3171cfc3f1f818006791057309b1b279c17e65eb3ba49000a8b25fd61ce9353b` |
| `corvette-z06-gt3r` | `c00f6145a7cb72208d4c4b095cea687ee57a612918906ce8fc449a072aac738d` |
| `lexus-rcf-gt3` | `6414c562fd77c073d6b3c55b2f5493e65bc8c430249487060306ed179df9f39a` |
| `bmw-m-hybrid-v8` | `86114ff2080d5b33eccc326c702de9b92f08540b4dc8f480de387a9d827492d1` |
| `ferrari-296-gt3` | `f0691155377b834fe1f69b3f3a7bb22064fa70c2ae4f5d34807726a9250f786a` |
| `aston-vantage-gt3` | `aeda8436c02728908da71efa0b8a20c2d033236b2c38853f0a3aed92b6e5272d` |
| `ferrari-499p` | `4c3718b0567bfb42b7476ae423e8ddd47347883c379f7d7fb0d85ebda8c86b92` |
| `audi-r8-lms-gt3` | `f15abc8fb3c6977a322c4a022339c2846ac04dd290943312c73aa29059ba86c0` |
| `lamborghini-huracan-gt3-evo2` | `9f022e47f8365329768302f1b61abfb9314f55dd752cf47d05ef338d14e47f54` |
| `mercedes-amg-gt3` | `65a3c3bfde9706e2ca20a2f82829d53f06b3bc0d7bddaf7df9c5a161794dba51` |
| `porsche-992-gt3-r` | `0015d108ff37f7fa788355684929d9cda309af7c2a5fd04ae63c45899fceba43` |
| `toyota-gr010` | `5320a564235bb436596d38c2cc4dc8650bbfc0ab6b8fc6e649fe46fec199b124` |
| `hyundai-i20-rally1` | `20a6058d475de0ce98192b119054fa84b7e6c3692946df702ea50af7ea22b76f` |
| `cadillac-v-series-r` | `ef87403cc2af80db95f63e70f958745125d56a9a105e143736b6aa53c26141a9` |
| `dallara-ir18` | `39866e64c07045afb72487bada5d5a26862bc0693cf02ae67de21c0c52c6bc72` |
| `porsche-963` | `0fc83537d9249990f2fc51c318e0109bee83e5b2854edd20f5507e561fede5bc` |

A katalógus és a profilfájlok azonosságát, a kötéseket és a 19 hash-t a tests/validate_profiles.py minden buildben újra ellenőrzi. A mobilos adaptív megjelenítés ideiglenes másolatból dolgozik; a mentett koordinátákat nem írja át.

## Személyes adatok és frissítés

A saját másolatok, importok és kiválasztások sémája megmaradt. A galéria Használat gombja az új alapot választhatóvá teszi; a régi személyes másolatot nem törli. A személyes fájl sérülése esetén az alkalmazás megőrzi az eredetit.

A Windows Bridge beállításai a felhasználói adatmappában maradnak; telepítés előtt zárd be a korábbi Bridge-et. Androidon eltérő preview-aláírás esetén a rendszer nem enged helyben frissíteni: **előbb exportálj minden személyes elrendezést**, majd kövesd az ANDROID.md újratelepítési és párosítási lépéseit. Az eltávolítás az app saját adatait törli; ezt a kockázatot nem szabad automatikus adatmegőrzésnek nevezni.

A felhasználó már működő éles Android–Windows–Rally rendszerről számolt be. Az új 0.3.0 fizikai telefonos/játékos elfogadása külön felhasználói próba; a forrásazonosság és az automatizált regresszió erős bizonyíték, de nem egy új, megfigyelt fizikai játékmenet.
