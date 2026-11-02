# BUTTON_MAPPING – SIM CONTROL STUDIO 0.4.0 Alpha

A telefon gombja **nem közvetlenül a játékot kapcsolja**. Az útvonal:

```
Telefon gomb → Bridge (Windows) → billentyűleütés → Assetto Corsa Rally billentyűkiosztás → játékfunkció
```

Ezért minden gombhoz **két helyen ugyanazt a billentyűt** kell beállítani: a játék *Controls* menüjében és a Bridge **Játékvezérlés** lapján.

## A világítás hibájának oka és javítása

A játékfájlok bemeneti listája szerint az ACR-ben a világításhoz ezek a műveletek tartoznak:

| Játékbeli akció | Működés | 0.4.0 művelet a Bridge-ben |
|---|---|---|
| `IA_CycleLights` | **léptet**: minden nyomás a következő fényállapotra vált | `lights` |
| `IA_ToggleHighBeams` | távfény be/ki | `highBeam` (új) |
| `IA_ToggleLeftIndicatorLight` | bal index | `indicatorLeft` (új) |
| `IA_ToggleRightIndicatorLight` | jobb index | `indicatorRight` (új) |
| `IA_CycleWipers` | ablaktörlő léptetése | `wiper` |
| `IA_StartStopEngine` | motor indítás/leállítás | `starter` (tartott gomb) |
| `IA_HandBrake` | kézifék | `handbrake` (új, tartott gomb) |
| `IA_Respawn` | visszahelyezés | `respawn` (új) |
| `IA_Increase/DecreaseEngineMap` | motortérkép | `engineMapUp` / `engineMapDown` |

**A 0.3.0 hibája:** a „Világítás” kétállású BE/KI kapcsoló volt, a játékban viszont a világítás **körbeléptet**. A telefon BE/KI-t mutatott, a játék közben egy másik fényállapotban volt, és a kettő elcsúszott egymástól. A 0.4.0-ban a világítás **léptetőgomb**. A LED a *kért lépést* jelzi, nem állítja, hogy a játékban be van kapcsolva.

### Ha a világítás gomb továbbra sem reagál

1. **Játék:** a *Controls* menüben keresd meg a „Cycle Lights” (fények léptetése) sort, és rendelj hozzá egy egyszerű billentyűt, például `L`-t.
2. **Bridge → Játékvezérlés:** a `lights` sorban ugyanazt a billentyűt add meg (`L`), **mód: `press`**, **lenyomás: 150 ms**. A 80 ms-os alapérték egy-egy képkocka-kiesésnél rövid lehet.
3. Ha a profiloknál **autónkénti kiosztást** mentettél (például a Škodához), az **felülírja** a játék alapértelmezését. Ilyenkor a `lights` sornak az autó saját kiosztásában is szerepelnie kell, különben a gomb a telefonon szürke marad.
4. Kattints a `lights` sorra, majd a **„Kijelölt parancs tesztje · 3 s”** gombra, és 3 másodpercen belül hozd előtérbe a játékot. Ha a fény vált, a kiosztás jó.
5. A Bridge **Rally diagnosztika** lapján a `local_input_test` sor mutatja, hogy a parancs `executed` lett-e.

## A LED-ek jelentése (minden új kezelőpanelen)

| LED | Jelentés |
|---|---|
| sötét | nincs kérés |
| villogó sárga | **elküldve**, még nincs Bridge-visszaigazolás |
| félig világít, sötét közép | **a Bridge végrehajtotta**: a billentyű leütése megtörtént, a játékállapot **feltételezett** |
| teljes fény, fényudvar | **a játék telemetriája igazolta** (csak ahol a játék ad ilyen adatot) |
| szürke, üreges | **ismeretlen**: nincs kapcsolat, nincs kiosztás vagy nincs engedélyezve |
| villogó piros | **hiba**: elutasítva vagy időtúllépés |

DEMO módban a felirat „DEMO · SZIMULÁLT ÁLLAPOT”, nem „JÁTÉK IGAZOLTA”.

## Javasolt billentyűk (mind a játékban, mind a Bridge-ben azonosan)

Ezek javaslatok, nem gyári ACR-alapértékek. Ütközés esetén válassz másikat.

| Művelet | Billentyű | Mód | ms |
|---|---|---|---|
| `starter` | `S` | hold | – |
| `lights` | `L` | press | 150 |
| `highBeam` | `K` | press | 100 |
| `indicatorLeft` / `indicatorRight` | `Q` / `E` | press | 100 |
| `wiper` | `W` | press | 150 |
| `handbrake` | `SPACE` | hold | – |
| `respawn` | `R` | press | 100 |
| `engineMapUp` / `engineMapDown` | `PAGEUP` / `PAGEDOWN` | press | 100 |
| `hazards`, `fogLights`, `demist`, `fan`, `electricalMaster`, `ignition`, `fireExtinguisher` | szabadon | press | 100 |

Megjegyzés: a `hazards`, `fogLights`, `demist`, `fan`, `ignition` és `electricalMaster` gomboknak a játékfájlokban **nincs külön akciójuk**. Ezek csak akkor hatnak, ha a játékban valamilyen funkcióhoz rendeled őket, például a `ComboKey1/2`-höz. Egyébként csak kijelzési/kényelmi gombok.

## Biztonság

- Kapcsolatvesztés, a telefon képernyőjének lezárása, autóváltás vagy a fókusz elvesztése esetén a Bridge **minden lenyomott billentyűt felenged**. Ezt az automatikus Bridge-teszt a kéziféknél külön ellenőrzi.
- A tartott gombok (indító, kézifék) másodpercenként megújítják a lenyomást; 3 s megújítás nélkül a Bridge magától felengedi őket.
- A Bridge csak akkor küld billentyűt, ha a mobilvezérlés engedélyezve van **és** a játék van előtérben.
