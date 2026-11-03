# GAME_ASSET_REFERENCE_REPORT – SIM CONTROL STUDIO 0.4.0 Alpha

Állapot: **2. lépés – tényleges, csak olvasó exportálás megtörtént (2026-11-03)**. Az 1. lépés (2026-11-02, eszközleltár) szövege lejjebb változatlanul megmaradt; az ott szereplő „exportálás nem történt” és „UE 5.4” állítást ez a szakasz helyesbíti.

## 2. lépés – mi történt ténylegesen

- **Motor:** Unreal Engine **5.6** (FModel csak `GAME_UE5_6` beállítással nyitja meg; az 1. lépésben a plugin neve alapján becsült 5.4 téves volt).
- **Titkosítás:** az IoStore-csomagok **nem titkosítottak** (AES-kulcs nem kellett). Védelmet nem kerültünk meg.
- **Eszköz:** FModel (felhasználói engedéllyel, a felhasználó gépén). A csomagok „unversioned properties” formátumúak, ezért kellett egy nyilvános mapping-fájl: `5.6.1-0+UE5-acr.usmap` (a felhasználó töltötte le az overtake.gg-ről).
- **Csak olvasás:** a játék mappájában semmi nem változott; minden kimenet a `Downloads\FModel\FModel\Output\Exports` mappába került.
- **Ténylegesen exportált tartalom:**
  - autónként a `Vehicles/<osztály>/<autó>/Textures` mappa (köztük a kapcsolópanel-atlasz `T_IntDetails_B`);
  - `Data/UI/Widgets_Gauges`: 27 textúra PNG-ben és **47 JSON** (a `WB_Gauge*` UMG-widgetek, LED-widgetek, anyagok, textúra-leírók).
- **Mi NEM került be az alkalmazásba:** egyetlen játékbeli textúra, betűtípus vagy kép sem. Az exportok a felhasználó gépén maradtak, nincsenek a repóban és a kiadásban.
- **Amit felhasználtunk belőlük:** csak **méreteket, pozíciókat, színkódokat, láthatóságot és fordulatszám-küszöböket** (tények), illetve a kapcsolópanel-atlaszok gombsorrendjét és feliratait. Minden grafikát a `tools/build_040*.py` rajzol.
- **Nem exportálható:** a widgetek Blueprint-logikája (a bájtkód-szerializálás ki volt kapcsolva, és nem is cél). Ezért a futás közben beállított színek és a váltásjelző küszöbök egy része **feltételezés**; ezeket az elemek `referenceNote` mezője jelöli.

## A hat kijelző-widget tartalma (JSON-exportból)

| Autó | Widget | Fő kijelző (játék) | Rejtett a játékban |
|---|---|---|---|
| Škoda Fabia RS Rally2 | `WB_GaugeSkodaFabiaRS` | 880×491 fekete kijelző, 20 px lekerekítés; nagy fokozatszám (NotoSans Bold 327), piros (F74D4A) váltásjelző felület; alsó sáv: „Map” + zöld (31B87F) érték, kézifék-ikon, világítás-ikon | ablaktörlő-ikon |
| Peugeot 208 Rally4 | `WB_GaugePeugeot208Rally4` + `WB_208MultiPhaseRPMLed` | 10 LED: 1–4. fokozatban 5200→6100 rpm között fokozatosan, 6100 felett mind, 6150 felett villog; 930×512 kijelző: fokozat, RPM-doboz, Speed (5DC6EE); külön GPS-tripmeter (DBE0F1 háttér, MENU/MODE, CLR, km) | Map (ECF831), OilP, OilT, WaterT |
| Hyundai i20 N Rally2 | `WB_GaugeHyundaiI20NRally2` | 855×535: kék „RPM” + érték, ciánkék (02FEFF) fokozat 350 px, sebesség; teljes képernyős váltásjelzés: zöld oldalsávok (00FF79), sárga (FFC90D), piros középsáv (C90E05) | tWater, pWater, tOil, pOil, TExh, Emerg, Map, Boost, Shift (0 átlátszatlanság) |
| VW Polo GTI R5 | `WB_GaugeVolkswagenPoloGTIR5` | két képernyő: felső (874×504: 5 lekerekített doboz, időmérő, gyújtás, ívelt RPM-sávok zöld/narancs/piros, sárga fokozat) és alsó (840×480: 3×4 doboz – fokozat+RPM, idő, sebesség, Trip [part.]/[total]) | – |
| Peugeot 206 WRC | `WB_GaugePeugeot206` | LCD: 760×53 RPM-sáv, 3 váltásjelző LED (6700+, 7000–7300; az elsőé 19999 rpm, tehát gyakorlatilag nem világít), 300×460 fokozatmező (A5A58F, piros 7-szegmens), jobb oldalon piros távolság / napszak / szakaszhossz; zöld (48C579) LCD-mezők: GEAR, FUEL, RACE/WARM UP/PRACTICE | WATER T, OIL T, OIL P |
| Subaru Impreza S3 | `WB_GaugeSubaruImprezaS3` | csak a tripmeter: sötét (252402) ház, piros LCD (2D0000), három piros 7-szegmens kijelző: napszak, megtett táv, szakaszhossz. Az analóg műszerek 3D-modellek | – |

Az alkalmazás mind a hat műszerfalat ezek alapján építi fel (`tools/build_040_gauges.py`). A játékban rejtett mezők külön „Rejtett mezők” oldalra kerültek, és ezt az oldal felirata jelzi. A szakaszhossz (`DistanceFinal`) mezőt az ACR-adapter nem adja, ezért „—” jelenik meg.

## 1. lépés – eszközleltár (2026-11-02, eredeti szöveg)

- Telepítés: `H:\SteamLibrary\steamapps\common\Assetto Corsa Rally` (Steam app 3917090), csak olvasási hozzáféréssel.
- Motor (1. lépésbeli becslés, **téves**, lásd fent): Unreal Engine 5.4 a csomagolt `XeSS_UE5.4_Plugin_v2.0.10` alapján. IoStore-csomagolás (`.pak` + `.utoc` + `.ucas`, kb. 11,6 GB fő csomag).
- Forrásfájl: a játék saját `Manifest_UFSFiles_Win64.txt` listája (90 469 bejegyzés). Ez csak eszközneveket ad.
- Felhasználási jog: a játék eredeti grafikái a kiadásba nem kerülhetnek be. Referenciaként használhatók, a végleges grafika saját rajzolású.

## Kritikus vezérlési lelet (világítás)

A játék bemeneti akciói (`Data/Input/...`):

| Csoport | Akciók |
|---|---|
| Világítás | `IA_CycleLights` (körbeléptető), `IA_ToggleHighBeams`, `IA_ToggleLeftIndicatorLight`, `IA_ToggleRightIndicatorLight` |
| Ablaktörlő | `IA_CycleWipers` (körbeléptető) |
| Motor | `IA_StartStopEngine`; külön gyújtásakció nincs, csak `DA_CarIgnitionOption` beállítás és `WB_CarIgnition` widget |
| Vezetés | `IA_HandBrake`, `IA_GearUp/Down`, `IA_Gear1–7`, `IA_GearN`, `IA_GearR`, `IA_Clutch` |
| Beállítás | `IA_Increase/Decrease` + `Abs`, `Tc`, `TcCut`, `BrakeBias`, `EngineMap` |
| Egyéb | `IA_Respawn`, `IA_ComboKey1/2`, `IA_CycleCamera`, `IA_Look*` |

**Következtetés:** a 0.3.0 Škoda-panelen a „Világítás” `toggle` típusú, `lights` akcióval. A játékban viszont a világítás **több állapoton léptet körbe**, nem be/ki kapcsoló. Egy kétállású BE/KI kapcsoló ezért egy-két nyomás után elcsúszik a játék tényleges állapotától. Ez a világításhiba legvalószínűbb oka. A pontos ciklust (állapotok száma, sorrend) még élő játékban kell ellenőrizni. A 0.4.0 javítási terve: `lightsCycle` léptető kezelőszerv, külön `highBeam` és `indicatorLeft/Right` akciók, a LED pedig csak „feltételezett” állapotot mutat, amíg a telemetria nem igazolja.

## A hat autó játékbeli azonosítói

| Autó | Játékbeli azonosító | Eszközmappa | Eszközök | Kijelző-widget |
|---|---|---|---|---|
| Peugeot 208 Rally4 | `Peugeot208Rally4` | `Vehicles/Rally4/Peugeot208` | 219 | `WB_GaugePeugeot208Rally4` |
| Škoda Fabia RS Rally2 | `SkodaFabiaRSRally2` | `Vehicles/Rally2/SkodaFabiaRS` | 236 | `WB_GaugeSkodaFabiaRS` |
| Hyundai i20 N Rally2 | `HyundaiI20NRally2` | `Vehicles/Rally2/HyundaiI20` | 227 | `WB_GaugeHyundaiI20NRally2` |
| Volkswagen Polo GTI R5 | `VWPoloGTIR5` | `Vehicles/R5/VWPoloGTI` | 235 | `WB_GaugeVolkswagenPoloGTIR5` |
| Peugeot 206 WRC | `Peugeot206WRC` | `Vehicles/WRC/Peugeot206` | 221 | `WB_GaugePeugeot206` |
| Subaru Impreza S3 | `SubaruImprezaS3` | `Vehicles/GroupA/SubaruImprezaS3` | 229 | `WB_GaugeSubaruImprezaS3` |

Megjegyzés: a Subaru a játékban `SubaruImprezaS3`, a **GroupA** osztályban szerepel. A pontos évjáratot élő képernyőképpel kell megerősíteni. A Hyundai a játékban **i20 N Rally2**.

## Autónkénti részletek

### Peugeot 208 Rally4 (`Peugeot208Rally4`)

- **Referencia forrása:** a játék eszközlistája (csak nevek).
- **Kijelző (dinamikus UMG-widget):** `Data/UI/Widgets_Gauges/WB_GaugePeugeot208Rally4`, `Data/UI/Widgets_Gauges/Materials/M_Peugeot208RPMLed`
- **Utastér/kezelőszervek (név szerint):** `AB_InternalPeugeot208`, `AB_Wipers`, `AS_Peugeot208Rally4_handbrake`, `AS_Wipers`, `MI_AluminiumCockpit`, `MI_CarpetBlackCockpit`, `MI_DecalsCockpit`, `MI_DecalsCockpit_UserLivery`, `MI_DetailsCockpit`, `MI_DuctCockpit`, `MI_FabricBlackCockpit`, `MI_FabricDotsCockpit`, `MI_FabricStrapCockpit`, `MI_InternalWindow`, `MI_InternalWindowFront`, `MI_InternalWindowFrontSimulated`, `MI_InternalWindowSimulated`, `MI_InternalWindowStickers`, `MI_LCD`, `MI_LightGlassInternal`, `MI_MetalBrushedCockpit`, `MI_PaintBlackGlossCockpit`, `MI_PaintBlackGlossCockpit_UserLivery`, `MI_PaintBlackGlossWeldsCockpit`, `MI_PaintBlackGlossWeldsCockpit_UserLivery`, `MI_PaintSilverCockpit`, `MI_PaintSilverCockpit_UserLivery`, `MI_PaintSilverWeldsCockpit`, `MI_PaintSilverWeldsCockpit_UserLivery`, `MI_PlasticBlackGrainCockpit`, `MI_PlasticBlackSatinCockpit`, `MI_RollcagePaddingCockpit`, `MI_RubberCockpit`, `MI_SuedeBlackCockpit`, `SK_AuxLights_Skeleton1`, `SK_Interior`, `SK_Wipers`, `S_Interior`, `S_Wipers`, `T_Cockpit_AO` …
- **Hiányzott (1. lépés):** textúrák, feliratok, LED-színek. **2. lépés:** a textúrák és a kijelző-widget exportálva, lásd fent.
- **Pontosság:** azonosítás igazolt; megjelenés nem igazolt.
- **Szükséges képek:** cockpit-nézet nappal és éjjel; a kijelző motor áll / gyújtás / járó motor / váltásjelzés állapotban; a kapcsolópanel közelről; a kormány.
- **Terv:** saját SVG/Flutter-rajz a referenciák alapján; a kijelző elrendezése a `WB_Gauge*` widget élő képe szerint.

### Škoda Fabia RS Rally2 (`SkodaFabiaRSRally2`)

- **Referencia forrása:** a játék eszközlistája (csak nevek).
- **Kijelző (dinamikus UMG-widget):** `Data/UI/Widgets_Gauges/WB_GaugeSkodaFabiaRS`, `Data/UI/Widgets_Gauges/PH_ReferenceTextures/UV_SkodaFabiaRSRally2`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_hadbrake`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_hadbrake_lights_add`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_hadbrake_lights_broken`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_hadbrake_lights_off`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_hadbrake_lights_on`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_wipers_fast`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_wipers_int`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_wipers_slow`
- **Utastér/kezelőszervek (név szerint):** `AB_InternalSkodaFabia`, `AB_Wipers`, `AS_SkodaFabiaRS_gear_down`, `AS_SkodaFabiaRS_gear_up`, `AS_SkodaFabiaRS_handbrake`, `AS_Wipers`, `MI_AluminiumCockpit`, `MI_CarbonFiberCockpit`, `MI_DecalsCockpit`, `MI_DecalsCockpit_UserLivery`, `MI_DetailsCockpit`, `MI_FabricBlackCockpit`, `MI_FabricHandleCockpit`, `MI_FullBlackCockpit`, `MI_GripTapeCockpit`, `MI_InternalWindow`, `MI_InternalWindowFront`, `MI_InternalWindowFrontSimulated`, `MI_InternalWindowPoly`, `MI_InternalWindowSimulatedPoly`, `MI_InternalWindowStickers`, `MI_InternalWindowStickers_UserLivery`, `MI_LCD`, `MI_LightGlassInternal`, `MI_PaintBlackMatteCockpit`, `MI_PaintBlackMatteCockpit_UserLivery`, `MI_PaintBlackSatinCockpit`, `MI_PaintRedCockpit`, `MI_PaintSilverCockpit`, `MI_PaintSilverCockpit_UserLivery`, `MI_PlasticBlackSatinCockpit`, `MI_PlasticDarkGreyCockpit`, `MI_RollcagePaddingCockpit`, `MI_RubberCockpit`, `MI_SafetyFoamCockpit`, `MI_SuedeCockpit`, `MI_SuedeDashCockpit`, `MI_WeldsBlackCockpit`, `MI_WeldsBlackCockpit_UserLivery`, `MI_WeldsSilverCockpit` …
- **Hiányzott (1. lépés):** textúrák, feliratok, LED-színek. **2. lépés:** a textúrák és a kijelző-widget exportálva, lásd fent.
- **Pontosság:** azonosítás igazolt; megjelenés nem igazolt.
- **Szükséges képek:** cockpit-nézet nappal és éjjel; a kijelző motor áll / gyújtás / járó motor / váltásjelzés állapotban; a kapcsolópanel közelről; a kormány.
- **Terv:** saját SVG/Flutter-rajz a referenciák alapján; a kijelző elrendezése a `WB_Gauge*` widget élő képe szerint.

### Hyundai i20 N Rally2 (`HyundaiI20NRally2`)

- **Referencia forrása:** a játék eszközlistája (csak nevek).
- **Kijelző (dinamikus UMG-widget):** `Data/UI/Widgets_Gauges/WB_GaugeHyundaiI20NRally2`
- **Utastér/kezelőszervek (név szerint):** `AB_HyundaiI20NHandbrake`, `AB_HyundaiI20NRally2Internal`, `AB_Wipers`, `AS_Wipers`, `AS_i20_HandBrake`, `MI_AluminiumCockpit`, `MI_CarbonGlossyCockpit`, `MI_CarbonYellowGlossyCockpit`, `MI_DecalsCockpit`, `MI_DetailsCockpit`, `MI_HeatWiresCockpit`, `MI_InternalWindow`, `MI_InternalWindowFront`, `MI_InternalWindowFrontSimulated`, `MI_InternalWindowSimulated`, `MI_InternalWindowStickers`, `MI_LCD`, `MI_PaintBlackCockpit`, `MI_PaintCockpit`, `MI_PaintCockpit_UserLivery`, `MI_PaintRedCockpit`, `MI_PlasticBlackCockpit`, `MI_PlasticGreyCockpit`, `MI_RollcagePaddingCockpit`, `MI_RubberCockpit`, `MI_WeldsBlackCockpit`, `MI_WeldsPaintedCockpit`, `MI_WeldsPaintedCockpit_UserLivery`, `SK_Interior`, `SK_Lights_FL`, `SK_Lights_FR`, `SK_Lights_RL`, `SK_Lights_RR`, `SK_Wipers`, `S_Interior`, `S_Lights_FL`, `S_Lights_FR`, `S_Lights_RL`, `S_Lights_RR`, `S_Wipers` …
- **Hiányzott (1. lépés):** textúrák, feliratok, LED-színek. **2. lépés:** a textúrák és a kijelző-widget exportálva, lásd fent.
- **Pontosság:** azonosítás igazolt; megjelenés nem igazolt.
- **Szükséges képek:** cockpit-nézet nappal és éjjel; a kijelző motor áll / gyújtás / járó motor / váltásjelzés állapotban; a kapcsolópanel közelről; a kormány.
- **Terv:** saját SVG/Flutter-rajz a referenciák alapján; a kijelző elrendezése a `WB_Gauge*` widget élő képe szerint.

### Volkswagen Polo GTI R5 (`VWPoloGTIR5`)

- **Referencia forrása:** a játék eszközlistája (csak nevek).
- **Kijelző (dinamikus UMG-widget):** `Data/UI/Widgets_Gauges/WB_GaugeVolkswagenPoloGTIR5`, `Data/UI/Widgets_Gauges/PH_ReferenceTextures/UV_VWPoloGTIR5`
- **Utastér/kezelőszervek (név szerint):** `AB_Internal_VWPolo`, `AB_Internal_VWPoloLayers`, `AB_Wipers`, `AS_WWPoloGTIR5_gear_bwd`, `AS_WWPoloGTIR5_gear_fwd`, `AS_WWPoloGTIR5_handbrake`, `AS_Wipers`, `MI_AluFoilCockpit`, `MI_AluminiumCockpit`, `MI_CarbonFiberCockpit`, `MI_DecalsCockpit`, `MI_DetailsCockpit`, `MI_FabricBlackCockpit`, `MI_FabricGreyCockpit`, `MI_FabricHandleCockpit`, `MI_FabricStrapCockpit`, `MI_FoamCockpit`, `MI_GlassClearCockpit`, `MI_GrilleFabricCockpit`, `MI_GripTapeCockpit`, `MI_InternalWindow`, `MI_InternalWindowFront`, `MI_InternalWindowFrontSimulated`, `MI_InternalWindowPoly`, `MI_InternalWindowSimulated`, `MI_InternalWindowSimulatedPoly`, `MI_InternalWindowStickers`, `MI_LCD`, `MI_LightGlassInternal`, `MI_MetalBlackSatinCockpit`, `MI_PaintBlackSatinCockpit`, `MI_PaintMetalBlackWeldsCockpit`, `MI_PaintMetalCockpit`, `MI_PaintMetalCockpit_UserLivery`, `MI_PaintMetalWeldsCockpit`, `MI_PaintMetalWeldsCockpit_UserLivery`, `MI_PlasticBlackGlossCockpit`, `MI_PlasticBlackSatinCockpit`, `MI_PlasticGrainCockpit`, `MI_PlasticGreyMatteCockpit` …
- **Hiányzott (1. lépés):** textúrák, feliratok, LED-színek. **2. lépés:** a textúrák és a kijelző-widget exportálva, lásd fent.
- **Pontosság:** azonosítás igazolt; megjelenés nem igazolt.
- **Szükséges képek:** cockpit-nézet nappal és éjjel; a kijelző motor áll / gyújtás / járó motor / váltásjelzés állapotban; a kapcsolópanel közelről; a kormány.
- **Terv:** saját SVG/Flutter-rajz a referenciák alapján; a kijelző elrendezése a `WB_Gauge*` widget élő képe szerint.

### Peugeot 206 WRC (`Peugeot206WRC`)

- **Referencia forrása:** a játék eszközlistája (csak nevek).
- **Kijelző (dinamikus UMG-widget):** `Data/UI/Widgets_Gauges/WB_GaugePeugeot206`, `Data/UI/Widgets_Gauges/Peugeot206WRC/T_Peugeot206WRCLCD_B`, `Data/UI/Widgets_Gauges/PH_ReferenceTextures/UV_Peugeot206`
- **Utastér/kezelőszervek (név szerint):** `AB_Internal_Peugeot206`, `AB_Internal_Peugeot206Layers`, `AB_Wipers`, `AS_Peugeot206_Handbrake`, `AS_Peugeot206_gear_bwd`, `AS_Peugeot206_gear_fwd`, `AS_Wipers`, `MI_CarbonCockpit`, `MI_DecalsCockpit`, `MI_DecalsCockpit_UserLivery`, `MI_DetailsCockpit`, `MI_FabricBlackCockpit`, `MI_FabricDotsCockpit`, `MI_FlockBlackCockpit`, `MI_FlockGreyCockpit`, `MI_FoamCockpit`, `MI_GripTapeCockpit`, `MI_InternalWindow`, `MI_InternalWindowFront`, `MI_InternalWindowFrontSimulated`, `MI_InternalWindowSimulated`, `MI_InternalWindowStickers`, `MI_KevlarYellowCockpit`, `MI_LCD`, `MI_LightGlassInternal`, `MI_PaintBlackGlossCockpit`, `MI_PaintBlackMatteCockpit`, `MI_PaintMetalBlackWeldsCockpit`, `MI_PaintMetalCockpit`, `MI_PaintMetalCockpit_UserLivery`, `MI_PaintMetalWeldsCockpit`, `MI_PaintMetalWeldsCockpit_UserLivery`, `MI_PlasticBlackGlossCockpit`, `MI_PlasticBlackMatteCockpit`, `MI_RubberCockpit`, `MI_SteelCockpit`, `MI_SteelYellowCockpit`, `MI_SuedeCockpit`, `SK_Interior`, `SK_Wipers` …
- **Hiányzott (1. lépés):** textúrák, feliratok, LED-színek. **2. lépés:** a textúrák és a kijelző-widget exportálva, lásd fent.
- **Pontosság:** azonosítás igazolt; megjelenés nem igazolt.
- **Szükséges képek:** cockpit-nézet nappal és éjjel; a kijelző motor áll / gyújtás / járó motor / váltásjelzés állapotban; a kapcsolópanel közelről; a kormány.
- **Terv:** saját SVG/Flutter-rajz a referenciák alapján; a kijelző elrendezése a `WB_Gauge*` widget élő képe szerint.

### Subaru Impreza S3 (`SubaruImprezaS3`)

- **Referencia forrása:** a játék eszközlistája (csak nevek).
- **Kijelző (dinamikus UMG-widget):** `Data/UI/Widgets_Gauges/WB_GaugeSubaruImprezaS3`, `Data/UI/Widgets_Gauges/PH_ReferenceTextures/UV_SubaruImprezaS3`
- **Utastér/kezelőszervek (név szerint):** `AB_Internal_ImprezaS3`, `AB_Internal_ImprezaS3Layers`, `AB_Wipers`, `AS_SubaruImprezaS3_Handbrake`, `AS_SubaruImprezaS3_gear_1_to_2`, `AS_SubaruImprezaS3_gear_3_to_4`, `AS_SubaruImprezaS3_gear_5_to_6`, `AS_SubaruImprezaS3_gear_N_to_1`, `AS_SubaruImprezaS3_gear_N_to_2`, `AS_SubaruImprezaS3_gear_N_to_3`, `AS_SubaruImprezaS3_gear_N_to_4`, `AS_SubaruImprezaS3_gear_N_to_5`, `AS_SubaruImprezaS3_gear_N_to_6`, `AS_SubaruImprezaS3_gear_N_to_R`, `AS_Wipers`, `MI_AluminiumCockpit`, `MI_CarbonSatinCockpit`, `MI_DecalsCockpit`, `MI_DecalsCockpit_UserLivery`, `MI_DetailsCockpit`, `MI_FabricBlackCockpit`, `MI_FabricDotsCockpit`, `MI_FabricStripesCockpit`, `MI_FlockCockpit`, `MI_GripTapeCockpit`, `MI_InternalWindowFrontSimulated`, `MI_InternalWindowSimulated`, `MI_InternalWindowStickers`, `MI_LCD`, `MI_LightGlassInternal`, `MI_MetalBlackBrushedCockpit`, `MI_MetalBlackMatteCockpit`, `MI_PaintMetalCockpit`, `MI_PaintMetalCockpit_UserLivery`, `MI_PaintMetalWeldsCockpit`, `MI_PaintMetalWeldsCockpit_UserLivery`, `MI_PlasticBlackGlossCockpit`, `MI_PlasticBlackGrainCockpit`, `MI_PlasticBlackSatinCockpit`, `MI_RubberCockpit` …
- **Hiányzott (1. lépés):** textúrák, feliratok, LED-színek. **2. lépés:** a textúrák és a kijelző-widget exportálva, lásd fent.
- **Pontosság:** azonosítás igazolt; megjelenés nem igazolt.
- **Szükséges képek:** cockpit-nézet nappal és éjjel; a kijelző motor áll / gyújtás / járó motor / váltásjelzés állapotban; a kapcsolópanel közelről; a kormány.
- **Terv:** saját SVG/Flutter-rajz a referenciák alapján; a kijelző elrendezése a `WB_Gauge*` widget élő képe szerint.

## Szükséges játékbeli képernyőképek (ha nincs exportálás)

Mind a hat autóhoz, cockpit-kamerával, 16:9-ben, a HUD kikapcsolásával:

1. Teljes műszerfal és középkonzol nappal.
2. Ugyanez éjjel, bekapcsolt világítással.
3. A kijelző közelről: motor álló helyzetben, alapjáraton és a fordulatszám-limitnél.
4. A világítás minden állapota (`CycleLights` lépésenként) és a távfény.
5. Az ablaktörlő minden állapota (Škodánál: int/slow/fast ikon).
6. Kézifék behúzva (Škodánál külön kézifék-kijelzőelem van).
