# Android build és telepítés

## Az átadott állapot

Natív Flutter Android projekt: `mobile_flutter/android`. Kiadási verzió `0.1.0+1`, application ID `hu.simcontrol.studio`, minimum Android API 24. A QR-kamera opcionális, a hálózat és kézi párosítás kamera nélkül is használható.

**APK nem készült.** A futtatókörnyezetben nem volt Flutter/Dart/Android SDK. A hivatalos Flutter SDK `storage.googleapis.com` letöltését a felügyelt környezet kimenő hálózati szabályzata HTTP 403-mal tiltotta; az általános hálózati engedély ezt a célállomás-szabályt nem változtatta meg. Nem került megkerülésre a tiltás, nem lett hamis APK vagy sikeres mobilteszt jelentve.

## Build saját gépen

1. Telepíts kompatibilis Flutter stable SDK-t (legalább 3.35 / Dart 3.9), JDK 17+-t és az Android SDK-t. Az első dependency-letöltés internetet igényel; az alkalmazás használata nem.
2. Futtasd: `flutter doctor -v` és `flutter doctor --android-licenses`.
3. A projekt gyökerében PowerShellből futtasd: `./tools/build-android.ps1`.
4. Az első kiadáshoz a szkript saját helyi keystore-t hoz létre. A jelszót helyben, rejtett bevitellel kéri. Őrizd meg a kulcsot és a jelszót; ezek nélkül ugyanaz a telepítés nem frissíthető.
5. A szkript sorban futtatja a `flutter pub get`, `flutter analyze`, `flutter test`, `flutter build apk --release` parancsokat, és csak sikeres lépések után másolja az APK-t a `releases/Android` könyvtárba. Hibánál leáll; a jelen kiadást nem nyilvánítja visszamenőleg sikeresen fordítottnak.

Meglévő kulcs esetén állítsd be helyben a `SIMCONTROL_KEYSTORE` és `SIMCONTROL_KEYSTORE_PASSWORD` környezeti változókat. A kulcsalias `simcontrol`. Titkot ne írj a forrásba vagy a kiosztás-exportba.

Kézi build esetén:

```powershell
cd mobile_flutter
flutter pub get
flutter analyze
flutter test
flutter build apk --release
```

Az `android/app/build.gradle.kts` a környezeti változókból olvassa az aláírást. A kiadási projekt nem a debug kulcsot használja.

## Telepítés és frissítés

A tényleges build után másold az APK-t a telefonra és engedélyezd a telepítést a saját fájlkezelődből, vagy használd az `adb install -r` parancsot. Az alkalmazásnak helyi hálózati és opcionális kameraengedély szükséges. Nem kér névjegy-, SMS- vagy mikrofonhozzáférést. Az interkomgomb a PC felé küldött játékparancs, nem hangfelvétel.

A gyártó által korlátozott Wi-Fi / vendéghálózat esetén az automatikus felderítés helyett használd a QR-kódot és a kézi IP-címet. Előtérben a teljes képernyős megjelenítés ébren tartja a készüléket. Háttérbe lépéskor a kliens felengedést küld és bontja a vezérlőkapcsolatot; visszatéréskor újracsatlakozik.

Az éles ellenőrzések listája: `TESZTELES.md`. Az itt mellékelt Dart- és widgettesztek jelenleg nem futtatott tesztek.
