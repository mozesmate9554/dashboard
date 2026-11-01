# Tesztelési állapot és felhasználói átvétel

## Ténylegesen futtatva

- C# Bridge.Core és Bridge.Headless Release build .NET 10 SDK-val: sikeres, 0 figyelmeztetés/hiba.
- Windows WinForms Release build és self-contained win-x64 publish: sikeres; a kiadáshoz tartozó napló `Tests/windows-build.log`.
- **18 Bridge-teszt**, Linux x64 .NET futtatással, determinisztikus bináris tesztmintákkal és valódi helyi TLS/WebSocket kapcsolatokkal. Eredmény: `bridge-tests.json`.
- **25 statikus adat/projektellenőrzés**: 20 autó/40 azonosító, minden elrendezés határai, mezői, vezérlőműveletei, különböző geometriai aláírása, SVG-k, Škoda nézetek, Android/iOS XML, PBX hivatkozások, verziók. Eredmény: `profile-tests.json`.
- Dart fájlok tree-sitter szintaktikai ellenőrzése: `dart-syntax.json`. Ez nem típusellenőrzés és nem futtatott Flutter-teszt.

## Nem futtatva

- Dart analyzer, Flutter unit/widget tesztek, Android APK build/telepítés.
- Xcode build, iOS aláírás és telepítés.
- Windows EXE grafikus futtatás; valódi Windows named mapping / SendInput.
- Futó Assetto Corsa Rally, annak konkrét játékverziója, tényleges billentyűhatás.
- Két fizikai telefon/tablet, valós Wi-Fi-késleltetés, 20/30/60 Hz-es fizikai teljesítménymérés.
- Online, replay, spectator vagy további játékmód ellenőrzése.

Ezekhez nem tartozik kitalált sikeres eredmény. A mobiltesztek forrása mellékelve van, de státuszuk `not_run`.

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
