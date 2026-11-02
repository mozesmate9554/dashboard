# GAME_ASSET_REFERENCE_REPORT – SIM CONTROL STUDIO 0.4.0 Alpha

Állapot: **1. lépés – eszközleltár (2026-11-02)**. Grafikai exportálás még **nem történt**.

## Forrás és módszer

- Telepítés: `H:\SteamLibrary\steamapps\common\Assetto Corsa Rally` (Steam app 3917090), csak olvasási hozzáféréssel.
- Motor: Unreal Engine 5.4 (a csomagolt `XeSS_UE5.4_Plugin_v2.0.10` alapján), IoStore-csomagolás (`.pak` + `.utoc` + `.ucas`, kb. 11,6 GB fő csomag).
- Forrásfájl: a játék saját `Manifest_UFSFiles_Win64.txt` listája (90 469 bejegyzés). Ez **csak eszközneveket** ad, tartalmat nem.
- A `.pak/.utoc/.ucas` fájlokat nem nyitottuk meg és nem módosítottuk. FModel nincs telepítve; a telepítéséhez külön engedély kell, és a kicsomagolhatóság (titkosítás/AES) még ellenőrizetlen.
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
- **Hiányzik:** maguk a textúrák/geometria (exportálás nem történt), a kapcsolók feliratai, a LED-színek.
- **Pontosság:** azonosítás igazolt; megjelenés nem igazolt.
- **Szükséges képek:** cockpit-nézet nappal és éjjel; a kijelző motor áll / gyújtás / járó motor / váltásjelzés állapotban; a kapcsolópanel közelről; a kormány.
- **Terv:** saját SVG/Flutter-rajz a referenciák alapján; a kijelző elrendezése a `WB_Gauge*` widget élő képe szerint.

### Škoda Fabia RS Rally2 (`SkodaFabiaRSRally2`)

- **Referencia forrása:** a játék eszközlistája (csak nevek).
- **Kijelző (dinamikus UMG-widget):** `Data/UI/Widgets_Gauges/WB_GaugeSkodaFabiaRS`, `Data/UI/Widgets_Gauges/PH_ReferenceTextures/UV_SkodaFabiaRSRally2`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_hadbrake`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_hadbrake_lights_add`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_hadbrake_lights_broken`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_hadbrake_lights_off`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_hadbrake_lights_on`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_wipers_fast`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_wipers_int`, `Data/UI/Widgets_Gauges/SkodaFabiaRs/t_Skodafabia_gauge_wipers_slow`
- **Utastér/kezelőszervek (név szerint):** `AB_InternalSkodaFabia`, `AB_Wipers`, `AS_SkodaFabiaRS_gear_down`, `AS_SkodaFabiaRS_gear_up`, `AS_SkodaFabiaRS_handbrake`, `AS_Wipers`, `MI_AluminiumCockpit`, `MI_CarbonFiberCockpit`, `MI_DecalsCockpit`, `MI_DecalsCockpit_UserLivery`, `MI_DetailsCockpit`, `MI_FabricBlackCockpit`, `MI_FabricHandleCockpit`, `MI_FullBlackCockpit`, `MI_GripTapeCockpit`, `MI_InternalWindow`, `MI_InternalWindowFront`, `MI_InternalWindowFrontSimulated`, `MI_InternalWindowPoly`, `MI_InternalWindowSimulatedPoly`, `MI_InternalWindowStickers`, `MI_InternalWindowStickers_UserLivery`, `MI_LCD`, `MI_LightGlassInternal`, `MI_PaintBlackMatteCockpit`, `MI_PaintBlackMatteCockpit_UserLivery`, `MI_PaintBlackSatinCockpit`, `MI_PaintRedCockpit`, `MI_PaintSilverCockpit`, `MI_PaintSilverCockpit_UserLivery`, `MI_PlasticBlackSatinCockpit`, `MI_PlasticDarkGreyCockpit`, `MI_RollcagePaddingCockpit`, `MI_RubberCockpit`, `MI_SafetyFoamCockpit`, `MI_SuedeCockpit`, `MI_SuedeDashCockpit`, `MI_WeldsBlackCockpit`, `MI_WeldsBlackCockpit_UserLivery`, `MI_WeldsSilverCockpit` …
- **Hiányzik:** maguk a textúrák/geometria (exportálás nem történt), a kapcsolók feliratai, a LED-színek.
- **Pontosság:** azonosítás igazolt; megjelenés nem igazolt.
- **Szükséges képek:** cockpit-nézet nappal és éjjel; a kijelző motor áll / gyújtás / járó motor / váltásjelzés állapotban; a kapcsolópanel közelről; a kormány.
- **Terv:** saját SVG/Flutter-rajz a referenciák alapján; a kijelző elrendezése a `WB_Gauge*` widget élő képe szerint.

### Hyundai i20 N Rally2 (`HyundaiI20NRally2`)

- **Referencia forrása:** a játék eszközlistája (csak nevek).
- **Kijelző (dinamikus UMG-widget):** `Data/UI/Widgets_Gauges/WB_GaugeHyundaiI20NRally2`
- **Utastér/kezelőszervek (név szerint):** `AB_HyundaiI20NHandbrake`, `AB_HyundaiI20NRally2Internal`, `AB_Wipers`, `AS_Wipers`, `AS_i20_HandBrake`, `MI_AluminiumCockpit`, `MI_CarbonGlossyCockpit`, `MI_CarbonYellowGlossyCockpit`, `MI_DecalsCockpit`, `MI_DetailsCockpit`, `MI_HeatWiresCockpit`, `MI_InternalWindow`, `MI_InternalWindowFront`, `MI_InternalWindowFrontSimulated`, `MI_InternalWindowSimulated`, `MI_InternalWindowStickers`, `MI_LCD`, `MI_PaintBlackCockpit`, `MI_PaintCockpit`, `MI_PaintCockpit_UserLivery`, `MI_PaintRedCockpit`, `MI_PlasticBlackCockpit`, `MI_PlasticGreyCockpit`, `MI_RollcagePaddingCockpit`, `MI_RubberCockpit`, `MI_WeldsBlackCockpit`, `MI_WeldsPaintedCockpit`, `MI_WeldsPaintedCockpit_UserLivery`, `SK_Interior`, `SK_Lights_FL`, `SK_Lights_FR`, `SK_Lights_RL`, `SK_Lights_RR`, `SK_Wipers`, `S_Interior`, `S_Lights_FL`, `S_Lights_FR`, `S_Lights_RL`, `S_Lights_RR`, `S_Wipers` …
- **Hiányzik:** maguk a textúrák/geometria (exportálás nem történt), a kapcsolók feliratai, a LED-színek.
- **Pontosság:** azonosítás igazolt; megjelenés nem igazolt.
- **Szükséges képek:** cockpit-nézet nappal és éjjel; a kijelző motor áll / gyújtás / járó motor / váltásjelzés állapotban; a kapcsolópanel közelről; a kormány.
- **Terv:** saját SVG/Flutter-rajz a referenciák alapján; a kijelző elrendezése a `WB_Gauge*` widget élő képe szerint.

### Volkswagen Polo GTI R5 (`VWPoloGTIR5`)

- **Referencia forrása:** a játék eszközlistája (csak nevek).
- **Kijelző (dinamikus UMG-widget):** `Data/UI/Widgets_Gauges/WB_GaugeVolkswagenPoloGTIR5`, `Data/UI/Widgets_Gauges/PH_ReferenceTextures/UV_VWPoloGTIR5`
- **Utastér/kezelőszervek (név szerint):** `AB_Internal_VWPolo`, `AB_Internal_VWPoloLayers`, `AB_Wipers`, `AS_WWPoloGTIR5_gear_bwd`, `AS_WWPoloGTIR5_gear_fwd`, `AS_WWPoloGTIR5_handbrake`, `AS_Wipers`, `MI_AluFoilCockpit`, `MI_AluminiumCockpit`, `MI_CarbonFiberCockpit`, `MI_DecalsCockpit`, `MI_DetailsCockpit`, `MI_FabricBlackCockpit`, `MI_FabricGreyCockpit`, `MI_FabricHandleCockpit`, `MI_FabricStrapCockpit`, `MI_FoamCockpit`, `MI_GlassClearCockpit`, `MI_GrilleFabricCockpit`, `MI_GripTapeCockpit`, `MI_InternalWindow`, `MI_InternalWindowFront`, `MI_InternalWindowFrontSimulated`, `MI_InternalWindowPoly`, `MI_InternalWindowSimulated`, `MI_InternalWindowSimulatedPoly`, `MI_InternalWindowStickers`, `MI_LCD`, `MI_LightGlassInternal`, `MI_MetalBlackSatinCockpit`, `MI_PaintBlackSatinCockpit`, `MI_PaintMetalBlackWeldsCockpit`, `MI_PaintMetalCockpit`, `MI_PaintMetalCockpit_UserLivery`, `MI_PaintMetalWeldsCockpit`, `MI_PaintMetalWeldsCockpit_UserLivery`, `MI_PlasticBlackGlossCockpit`, `MI_PlasticBlackSatinCockpit`, `MI_PlasticGrainCockpit`, `MI_PlasticGreyMatteCockpit` …
- **Hiányzik:** maguk a textúrák/geometria (exportálás nem történt), a kapcsolók feliratai, a LED-színek.
- **Pontosság:** azonosítás igazolt; megjelenés nem igazolt.
- **Szükséges képek:** cockpit-nézet nappal és éjjel; a kijelző motor áll / gyújtás / járó motor / váltásjelzés állapotban; a kapcsolópanel közelről; a kormány.
- **Terv:** saját SVG/Flutter-rajz a referenciák alapján; a kijelző elrendezése a `WB_Gauge*` widget élő képe szerint.

### Peugeot 206 WRC (`Peugeot206WRC`)

- **Referencia forrása:** a játék eszközlistája (csak nevek).
- **Kijelző (dinamikus UMG-widget):** `Data/UI/Widgets_Gauges/WB_GaugePeugeot206`, `Data/UI/Widgets_Gauges/Peugeot206WRC/T_Peugeot206WRCLCD_B`, `Data/UI/Widgets_Gauges/PH_ReferenceTextures/UV_Peugeot206`
- **Utastér/kezelőszervek (név szerint):** `AB_Internal_Peugeot206`, `AB_Internal_Peugeot206Layers`, `AB_Wipers`, `AS_Peugeot206_Handbrake`, `AS_Peugeot206_gear_bwd`, `AS_Peugeot206_gear_fwd`, `AS_Wipers`, `MI_CarbonCockpit`, `MI_DecalsCockpit`, `MI_DecalsCockpit_UserLivery`, `MI_DetailsCockpit`, `MI_FabricBlackCockpit`, `MI_FabricDotsCockpit`, `MI_FlockBlackCockpit`, `MI_FlockGreyCockpit`, `MI_FoamCockpit`, `MI_GripTapeCockpit`, `MI_InternalWindow`, `MI_InternalWindowFront`, `MI_InternalWindowFrontSimulated`, `MI_InternalWindowSimulated`, `MI_InternalWindowStickers`, `MI_KevlarYellowCockpit`, `MI_LCD`, `MI_LightGlassInternal`, `MI_PaintBlackGlossCockpit`, `MI_PaintBlackMatteCockpit`, `MI_PaintMetalBlackWeldsCockpit`, `MI_PaintMetalCockpit`, `MI_PaintMetalCockpit_UserLivery`, `MI_PaintMetalWeldsCockpit`, `MI_PaintMetalWeldsCockpit_UserLivery`, `MI_PlasticBlackGlossCockpit`, `MI_PlasticBlackMatteCockpit`, `MI_RubberCockpit`, `MI_SteelCockpit`, `MI_SteelYellowCockpit`, `MI_SuedeCockpit`, `SK_Interior`, `SK_Wipers` …
- **Hiányzik:** maguk a textúrák/geometria (exportálás nem történt), a kapcsolók feliratai, a LED-színek.
- **Pontosság:** azonosítás igazolt; megjelenés nem igazolt.
- **Szükséges képek:** cockpit-nézet nappal és éjjel; a kijelző motor áll / gyújtás / járó motor / váltásjelzés állapotban; a kapcsolópanel közelről; a kormány.
- **Terv:** saját SVG/Flutter-rajz a referenciák alapján; a kijelző elrendezése a `WB_Gauge*` widget élő képe szerint.

### Subaru Impreza S3 (`SubaruImprezaS3`)

- **Referencia forrása:** a játék eszközlistája (csak nevek).
- **Kijelző (dinamikus UMG-widget):** `Data/UI/Widgets_Gauges/WB_GaugeSubaruImprezaS3`, `Data/UI/Widgets_Gauges/PH_ReferenceTextures/UV_SubaruImprezaS3`
- **Utastér/kezelőszervek (név szerint):** `AB_Internal_ImprezaS3`, `AB_Internal_ImprezaS3Layers`, `AB_Wipers`, `AS_SubaruImprezaS3_Handbrake`, `AS_SubaruImprezaS3_gear_1_to_2`, `AS_SubaruImprezaS3_gear_3_to_4`, `AS_SubaruImprezaS3_gear_5_to_6`, `AS_SubaruImprezaS3_gear_N_to_1`, `AS_SubaruImprezaS3_gear_N_to_2`, `AS_SubaruImprezaS3_gear_N_to_3`, `AS_SubaruImprezaS3_gear_N_to_4`, `AS_SubaruImprezaS3_gear_N_to_5`, `AS_SubaruImprezaS3_gear_N_to_6`, `AS_SubaruImprezaS3_gear_N_to_R`, `AS_Wipers`, `MI_AluminiumCockpit`, `MI_CarbonSatinCockpit`, `MI_DecalsCockpit`, `MI_DecalsCockpit_UserLivery`, `MI_DetailsCockpit`, `MI_FabricBlackCockpit`, `MI_FabricDotsCockpit`, `MI_FabricStripesCockpit`, `MI_FlockCockpit`, `MI_GripTapeCockpit`, `MI_InternalWindowFrontSimulated`, `MI_InternalWindowSimulated`, `MI_InternalWindowStickers`, `MI_LCD`, `MI_LightGlassInternal`, `MI_MetalBlackBrushedCockpit`, `MI_MetalBlackMatteCockpit`, `MI_PaintMetalCockpit`, `MI_PaintMetalCockpit_UserLivery`, `MI_PaintMetalWeldsCockpit`, `MI_PaintMetalWeldsCockpit_UserLivery`, `MI_PlasticBlackGlossCockpit`, `MI_PlasticBlackGrainCockpit`, `MI_PlasticBlackSatinCockpit`, `MI_RubberCockpit` …
- **Hiányzik:** maguk a textúrák/geometria (exportálás nem történt), a kapcsolók feliratai, a LED-színek.
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
