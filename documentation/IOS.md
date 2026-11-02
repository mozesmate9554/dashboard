# iPhone / iPad – 0.3.0 build és telepítés

A 0.3.0 valódi macOS/Xcode-fordítást használ. Az első sikeres ellenőrzés Xcode 16.4 (16F6), Flutter 3.35.7, iPhone 16 Pro / iOS 18.5 szimulátoron futott. A kiadott változat pontos forráscommitját, az ismételt ellenőrzés eredményét és környezetét a kiadási csomag `Tests/iOS-CI/` könyvtára és `Documentation/STATUS.json` tartalmazza. Minimum iOS 15.5; iPhone és iPad céleszközcsalád.

**Fizikai iPhone-teszt nem történt. Aláírt IPA és TestFlight nincs:** a projekthez jelenleg nincs Apple Developer-tagság és App Store Connect-alkalmazás. A szimulátoros TLS/Keychain/telemetria/érintéses parancs/visszacsatlakozás ellenőrzés valódi natív futás, de loopback hálózaton, egyértelműen jelölt DEMO-forrással. Nem bizonyítja a Wi-Fi, a QR-kamera vagy a fizikai kijelző működését.

## Letölthető iOS-állományok

Kiadás: https://github.com/mozesmate9554/dashboard/releases/tag/v0.3.0

- `SIM_CONTROL_STUDIO_0.3.0_iOS_Simulator.zip`: ténylegesen fordított, szimulátoron telepített és elindított `Runner.app`. Csak kompatibilis macOS/Xcode/iOS Simulator környezetben fut.
- `SIM_CONTROL_STUDIO_0.3.0_iOS_Unsigned_NotInstallable.zip`: tényleges ARM64 release `.app`, aláírás nélkül. **Nem iPhone-ra telepíthető IPA**, és nem adható TestFlightnak.
- A teljes kiadási ZIP tartalmazza a forrást, az iOS-projektet, buildnaplókat és tesztbizonyítékot.

## Szimulátoros telepítés Macen

Xcode és az iOS 18.5 szimulátor futtatókörnyezete szükséges. A `Simulator` alkalmazásban indíts egy kompatibilis iPhone-t. Csomagold ki a Simulator ZIP-et, majd:

```sh
xcrun simctl install booted /teljes/utvonal/Runner.app
xcrun simctl launch booted hu.simcontrol.studio
```

Vagy húzd a `Runner.app` fájlt a szimulátor ablakára. Apple-fiók és fizetős tagság ehhez nem kell. Ha az adott Mac architektúrája vagy SDK-ja eltér, a forrásból fordítsd újra:

```sh
cd mobile_flutter
flutter pub get
flutter build ios --simulator --debug
```

## Saját iPhone-ra Xcode-ból

1. Macen telepíts Xcode-ot, CocoaPodsot és Flutter **3.35.7**-et; `flutter doctor -v` jelezze a kész környezetet.
2. A forrás `mobile_flutter` könyvtárában futtasd: `flutter pub get`, `flutter analyze`, `flutter test`, majd `cd ios && pod install`.
3. Nyisd meg a **Runner.xcworkspace** fájlt. A Runner → Signing & Capabilities alatt válassz saját Teamet, kapcsold be az automatikus aláírást, és szükség esetén adj meg egyedi Bundle Identifiert. A Keychain-csoport a Team és Bundle Identifier változóiból képződik.
4. Csatlakoztasd és bízd meg az iPhone-t; a készülék és Xcode utasításai szerint engedélyezd a Developer Mode-ot és a fejlesztői aláírást.
5. Válaszd ki a készüléket és indíts **Run**-t. Személyes Apple ID-val az Apple által megengedett ideiglenes fejlesztői telepítés használható; annak idő- és eszközkorlátait az Xcode jelzi. A projekt ezt nem kerüli meg.
6. Első induláskor DEMO-ban ellenőrizd mindhárom nézetet, majd engedélyezd a helyi hálózatot és párosíts a PC Bridge-dzsel. A kamerás QR opcionális; kézi IP/pin/token-párosítás is van.

Az aláírás nélküli kiadási `.app` helyett a saját Teameddel fordított alkalmazást telepítsd. Más Team vagy Bundle Identifier új Keychain-hozzáférést jelenthet: ilyenkor párosíts újra.

## TestFlight később

Aktív Apple Developer-tagság, saját Bundle ID, megfelelő App Store Connect-szerepkör és létrehozott alkalmazás szükséges. Xcode → Product → Archive → Distribute App → App Store Connect, vagy saját provisioning mellett `flutter build ipa --release`. Az App Store Connect feldolgozás és szükséges megfelelőségi adatok után a TestFlight lapon lehet tesztelőket meghívni; külső teszteléshez Apple-ellenőrzés is kellhet. A tagság/aláírás beállítása után kell ténylegesen elvégezni ezt a kiadást. Privát kulcsot és jelszót ne helyezz a repositoryba.

## Hálózat és teljes képernyő

A kapcsolat privát IPv4-en, tanúsítványhoz rögzített TLS/WebSocketen működik; a készüléktitok Keychainbe kerül. A plist helyi hálózati és opcionális kameraindoklást tartalmaz; nincs általános `NSAllowsArbitraryLoads` kivétel. Az UDP-broadcast iOS-en külön multicast-jogosultságot igényelhet: **QR vagy kézi IP az elsődleges párosítás**. A szimulátoros teszt nem ellenőrzi az éles hálózati engedélykérő ablakot.

A műszerfal a státuszsáv elrejtését és a Home-jelző automatikus elhalványítását kéri. Az iOS gesztusra visszahozhatja a rendszerjelzőt; ez rendszerkorlát. A kivágás és a biztonságos érintési terület szabadon marad. iPad multitasking felülírhat tájolási kéréseket. Részletek: [TELJES_KEPERNYO_0.3.0.md](TELJES_KEPERNYO_0.3.0.md).
