# Teljes képernyő és képernyőméretek – 0.3.0

A Műszerfal, Kezelőpanel és Hibrid élő nézet ugyanazt a natív teljesképernyő-kezelőt használja. A nézet megnyitásakor bekapcsol az ébren tartás, elrejtést kérnek a rendszerjelzők; kilépéskor visszaáll az alkalmazás szokásos rendszerfelülete és a szabad tájolás. Háttérbe lépéskor az ébren tartás megszűnik, visszatéréskor a teljes képernyő ismét érvényesül. Nézet-, oldal- és menüváltáskor a tartott vezérlések felengednek.

A jobb felső **…** gomb mindig elérhető, az eszköztár elrejtése után is. Itt választható adaptív mobilnézet, eredeti geometria, álló/fekvő/automatikus tájolás, a három szerepkör, valamint kilépés. A panel és hibrid **Alkalmazás gyorsvezérlői** pontja őrzi az indító, ablaktörlő, rádió/interkom és motor-map műveleteket. Ezek alkalmazásgombok; nem gyári Škoda-kapcsolóhelyek.

## Adaptív vagy eredeti elrendezés

Az adaptív nézet az elérhető **biztonságos** területre szervezi a műszereket és gombokat. Kis kijelzőn külön mobiloldalakra bontja a túl sűrű adatot/vezérlést; a réteges oldalikon lapozza a további oldalakat. A hibrid álló helyzetben a műszerek alatt, fekvő helyzetben mellettük helyezi el a vezérlést. A feliratok egy sorban, a számok a maradék helyen skálázódnak. A gombok célterülete a vizsgált méreteken legalább 48 logikai pixel mindkét irányban.

Az **Eredeti arány és elrendezés** megőrzi a referencia alapján rajzolt autófelületet vagy a személyes szerkesztett geometriát. A 1280×800-as Škoda-kijelző és az 1100×1450-es konzol eltérő képarányú: eredeti módban az ettől eltérő képernyőn maradhat tér. Adaptív módban a mobil használhatósága kap elsőbbséget, ezért a kapcsolók elhelyezése nem a fotó perspektívája. A gyári felület összehasonlító előnézete az eredeti geometria tényleges Flutter-renderelése.

A program a megjelenítéshez ideiglenes elrendezést készít; a mentett profilok koordinátáit és a 19 másik autó grafikáját nem írja át. A személyes másolatok/importok és a meglévő kiválasztások megmaradnak. Az új Škoda alap a galéria **Használat** gombjával választható ki; ezzel a személyes változat nem törlődik.

## Rendszerkorlátok

- Android: a natív `WindowInsetsControllerCompat` rejti el a státusz- és navigációs sávot, ezért a Flutter legacy rendszer-UI módjának target API 36 melletti korlátozása nem akadályozza a kérést. A rendszersáv gesztussal ideiglenesen visszahívható. Nagy Android-kijelzőn a rendszer felülírhatja a tájolásrögzítést.
- iOS: státuszsáv-rejtés és Home-jelző auto-hide; a rendszer gesztussal újra megjelenítheti a jelzőt. Nincs ígéret a rendszer állandó kizárására. A notch/Dynamic Island, forgatott kivágás és biztonságos alsó érintési sáv figyelembe van véve.
- A DEMO vagy az élő/stale kapcsolatjelzés vékony, 26 logikai pixeles sávja látható marad; a szimulált adatot teljes képernyőn sem szabad élő játékadatnak nézni.

## Ellenőrzés

A widgettesztek minden 20 autó minden alapoldalát és hibridjét három alapméreten, az adaptív lapokat álló és fekvő méreten renderelik. Külön teszt vizsgálja a 393×852-es iPhone biztonságos területét és az Android natív csatorna belépés/kilépés hívását. A natív teszt szimulátoron/emulátoron ellenőrzi a tényleges tájolást, a három nézet renderelését és képernyőképet készít. Androidon a rendszersávok tényleges láthatóságát is lekérdezi. A kiadáshoz tartozó futás konkrét eredménye a `STATUS.json` és a csomag `Tests` mappája; fizikai készülékes ellenőrzés továbbra is szükséges.
