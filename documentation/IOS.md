# iPhone / iPad build és aláírás

Az iOS projekt a `mobile_flutter/ios/Runner.xcodeproj`, a CocoaPods workspace a `Runner.xcworkspace`. iPhone és iPad céleszközcsalád beállítva; minimum iOS 15.5 a QR-kódkönyvtár feltételei miatt. Portré és fekvő megjelenítés engedélyezett.

**Nem készült aláírt IPA és nem futott Xcode build.** A kiadási környezet Linux volt, macOS, Xcode és Apple aláírási környezet nélkül. A saját generálású PBX projekt objektumhivatkozásai és az XML fájlok statikusan ellenőrizve lettek; ez nem Xcode-fordítás.

## Saját macOS gépen

1. Telepíts kompatibilis Flutter stable SDK-t, Xcode-ot és CocoaPodsot. Futtasd a `flutter doctor -v` parancsot.
2. A `mobile_flutter` könyvtárban: `flutter pub get`, `flutter analyze`, `flutter test`.
3. `cd ios && pod install`. A Flutter által előállított `Generated.xcconfig` és `GeneratedPluginRegistrant` fájlok buildtermékek, nem kitaláltan előre kitöltött SDK-útvonalak.
4. Nyisd meg a `Runner.xcworkspace` fájlt. A Runner → Signing & Capabilities lapon válaszd ki a saját fejlesztői Teamet, és állíts be egyedi Bundle Identifiert. Ha ezt módosítod, frissítsd a `Runner.entitlements` Keychain csoportját is.
5. Csatlakoztasd az iPhone-t/iPadet; Development buildhez engedélyezd a készüléken a fejlesztői módot és a saját aláírásodat az Apple feltételei szerint.
6. Indíts Xcode-ból vagy `flutter run` paranccsal. Kiadáshoz `flutter build ipa --release` és saját provisioning szükséges. A buildszkript `tools/build-ios.sh`; aláírás nélküli fordításhoz `SIMCONTROL_IOS_NO_CODESIGN=1` állítható be. Az így elkészülő `.app` nem telepíthető aláírt IPA-ként.

## Helyi hálózat

A plist tartalmazza a helyi hálózat és kamera érthető indoklását. A kapcsolat TLS és tanúsítványrögzítés alapú. Nincs általános `NSAllowsArbitraryLoads` kivétel vagy HTTP-n továbbított készüléktitok.

Az UDP broadcast felderítés iOS-en Apple multicast jogosultságot igényelhet. Ezt a projekt nem állítja automatikusan megszerzettnek. Az alap párosítási út a QR/kézi IPv4; ezt teszteld először. A helyi hálózati engedélyt a készülék beállításai között engedélyezd.

Az iOS Keychain a Bridge hitelesítési titkát tárolja. A projekt nem küld adatot Apple vagy más felhőszolgáltatásba. Az aláírás és a build eszközeinek hálózati igénye különbözik a futó alkalmazás működésétől.
