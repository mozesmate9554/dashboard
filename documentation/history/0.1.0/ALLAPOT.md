# Fejlesztési állapot 0.1.0

A teljes specifikáció elfogadási feltétele **még nem teljesült**. Futó Rally és két fizikai mobil nem állt rendelkezésre. A Windows kiadás lefordult, APK/IPA nem készült.

Automatizált ellenőrzések: 18 Bridge + 25 adat/projekt, 9 Dart fájl szintaxis. A Dart szintaxis nem Flutter analyzer vagy futtatott widgetteszt.

| Funkció | Állapot |
|---|---|
| Önálló Windows x64 Bridge | Elkészült, valós eszközön még tesztelendő |
| Assetto Corsa Rally valódi shared-memory adapter | Elkészült, valós eszközön még tesztelendő |
| Egységes mezőmodell és elavulás | Elkészült és automatizáltan tesztelt |
| Többklienses kétirányú kapcsolat, bontás és újracsatlakozás | Elkészült és automatizáltan tesztelt |
| TLS, párosítás, hash-tárolás, visszavonás, sebességkorlát | Elkészült és automatizáltan tesztelt |
| Billentyűk, kombinációk, hold/repeat, fókusz- és beragadásvédelem | Elkészült és automatizáltan tesztelt |
| Windows felület, tálca, QR, kiosztásimport és diagnosztika | Elkészült, valós eszközön még tesztelendő |
| Natív Flutter Android/iOS kliens | Részlegesen elkészült |
| Műszerfal, kezelőpanel és külön menthető hibrid | Részlegesen elkészült |
| 20 autó / 40 eltérő, verziózott alapelrendezés | Elkészült és automatizáltan tesztelt |
| Gyári műszerfalak és kapcsolópanelek hű rekonstrukciója | Részlegesen elkészült |
| Más készüléktől érkező profilajánlás | Elkészült és automatizáltan tesztelt |
| Játékazonosítóból automatikus autóprofil-váltás | Nem készült el |
| Érintéses vizuális szerkesztő, csoport, réteg, undo/redo és feltételek | Részlegesen elkészült |
| JSON/SVG/PNG import-export és helyi mentés | Részlegesen elkészült |
| Assetto Corsa, ACC és BeamNG OutGauge adapterek | Részlegesen elkészült |
| A többi megnevezett játék integrációja | Nem készült el |
| Minden játékmód és online használat igazolása | Nem készült el |
| Android release APK | Nem készült el |
| Aláírt iOS IPA | Nem készült el |
| Magyar felület és angol nyelv | Részlegesen elkészült |
| Magyar útmutatók, napló és gépi állapotjelentés | Elkészült és automatizáltan tesztelt |

Részletek és a bizonyítékok határai: `STATUS.json`. A 40 elrendezésből 1 részleges referencia, 19 inspirált; nincs 20 hitelesített gyári replika készre jelentve.

Az Android build hiányának konkrét oka: a hivatalos Flutter SDK célállomását a környezet hálózati szabályzata 403-mal tiltotta. Az iOS buildhez macOS, Xcode és aláírás hiányzott. A forrás és a natív projektek átadásra kerülnek.
