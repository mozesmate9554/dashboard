# Tesztelési állapot – 0.2.0

A kiadáshoz tartozó pontos futás, forráscommit és eredmény: `STATUS.json`, `FUNKCIOMATRIX_0.2.0.md`, illetve a teljes csomag `Tests/Android-CI/provenance.json` fájlja.

Automatizált ellenőrzések: 22 Bridge-regresszió Linuxon és Windows CI-ben, 25 profil-/projektellenőrzés, Flutter analyzer és unit/widget tesztek, release APK és aláírásellenőrzés, Windows self-contained EXE és NSIS telepítő. A Windows CI csendes telepítést és a WinForms főablak megjelenését is ellenőrzi. A teljes interaktív felület vizsgálatát ez nem helyettesíti.

A Flutter teszt minden alapprofil minden oldalát és a 20 hibridet 360×800, 900×420 és 1366×1024 méreten rendereli, hiányzó és DEMO-adatokkal. További tesztek: hibás SVG/kép/geometria, alapok megőrzése, hibrid másolás, személyes mentés/visszatöltés/törlés, sérült fájl megőrzése, DEMO hálózati izoláció, szerepkörök, tartott gomb nézetváltása, szerkesztőbeli mozgatás/visszavonás/mentés.

A Bridge-tesztek valódi helyi TLS/WebSocket kapcsolatot használnak; a játékbájtok és a bemeneti sink tesztminták. A DEMO-s kétklienses benchmark 30 és 60 Hz kéréssel, 1 másodperc bemelegítéssel mér. Eredmény: `transport-benchmark.json`, Windows CI-n `windows-transport-benchmark.json`. Ezek nem fizikai telefonos FPS- vagy Wi-Fi-mérések.

Nem történt futó Assetto Corsa Rally-, két fizikai mobil-, valódi játékhatás-, iOS/Xcode/IPA- vagy online munkamenetteszt. A 0.1.0 audit és bizonyítékok a `history/0.1.0` mappában megmaradtak.

## A – Valódi Rally-telemetria (felhasználónál)

1. Jegyezd fel a Windows-verziót, a játék pontos verzióját és a futó EXE nevét.
2. Indítsd a Bridge-et, a Rallyt és a tényleges vezetést.
3. Ellenőrizd a diagnosztikában a physics/static/graphics elérhetőséget és az utolsó valódi packet idejét.
4. Hasonlítsd össze a sebességet, RPM-et és R/N/1.. fokozatot a játékkal.
5. Gázadás/fékezés/álló helyzet/menü/kilépés esetén se maradjon egy régi érték frissnek jelölve.
6. Exportálj Bridge és mobil diagnosztikát. Csak ez után lehet az adott játékverziót élesben ellenőrzöttnek nevezni.

## B – Két fizikai kliens

Egyik készülék műszerfal, másik kezelőpanel, ugyanaz az autó. Ellenőrizd az ajánlást, a folyamatos adatokat, a második kliens bontását és visszakapcsolódását. Az első kijelző nem állhat le. A mesterséges kétklienses hálózati teszt ezt a protokollviselkedést ellenőrizte, a fizikai hálózatot nem.

## C – Valódi vezérlés

Először egy egyértelmű, ártalmatlan, a játékban létező funkció billentyűjét konfiguráld. Ellenőrizd a `requested → sent → received → executed` utat és a játék tényleges reakcióját. Tarts lenyomva egy hold vezérlőt, majd engedd fel, bontsd a Wi-Fit, tedd háttérbe a mobilappot és válts fókuszt a PC-n. Az injektált billentyűnek mindig fel kell engednie. A meglévő fizikai kormány/pedál bemenetet a rendszer nem tiltja le.

A Bridge helyi parancsteszt gombja 3 másodpercet ad a játék előtérbe hozására. Ez is ugyanazt a fókusz- és engedélykaput használja, nem küld bemenetet tetszőleges alkalmazásnak.

## D / E – Profilok és szerkesztő

A Škoda műszerfal, kormány, konzol és kombinált nézet, majd mind a 20 autópár következzen. A valódi gyári hűséget külön ellenőrizd: a mellékelt profilok inspirált/részleges rekonstrukciók. Készíts másolatot, mozgasd/forgasd/csoportosítsd az elemeket, ments, indíts újra, exportálj/importálj. A saját hybrid is külön szerepként menthető. Ellenőrizd telefonon és tableten, portréban és fekvő helyzetben.

## F – Játékmódváltás

Csak a konkrét játékban ténylegesen létező munkameneteket vedd fel a mátrixba. Szakaszindítás, szakaszváltás, menü, autóváltás, játékbezárás és újraindítás ne igényeljen új párosítást. Replay/online adatot kizárólag akkor jelölj támogatottnak, ha a játék API-ja azt frissen szolgáltatta és használata engedélyezett.

## G – Hibakezelés

Próbáld a Bridge bezárását, Wi-Fi megszakítását, háttérbe lépést, ismeretlen mezőt, sérült profilt és hibás kiosztást. A korábbi személyes adatokat nem szabad felülírni sérült importtal. A program ne pótolja a hiányzó adatot szimulált számmal. A hibajelentésbe kerüljön pontos reprodukció, játék/app verzió, diagnosztikai export és az időpont; párosítási tokent, készüléktitkot, keystore-t vagy PFX-et ne csatolj.

## Megismételhetőség

`tools/verify.sh` / `tools/build-windows.ps1`. A hibaesetek determinisztikusak; a teszt-fixture kizárólag a `tests` projektben található. A Flutter-tesztek `flutter test` paranccsal futnak, amint rendelkezésre áll az SDK. A JSON státuszjelentés nem frissül önmagától egy később, más gépen végzett teszt után: őrizd meg az új eredményeket és azok környezetét is.
