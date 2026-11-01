# Ismert korlátok – 0.2.0

- Assetto Corsa Rally nincs telepítve a fejlesztői környezetben. A pinned közösségi referencián alapuló adapter bináris mintákkal és helyi TLS-kliensekkel tesztelt; az aktuális játék mappingnevei, folyamatneve, fokozatkódja és G-tengelyei élő ellenőrzést igényelnek.
- Rally: a sebesség/RPM/fokozat/gáz/fék/nyers kormány/G-vektor, valamint a rendelkezésre álló statics mezők útvonala implementált. Üzemanyag, hőmérsékletek, kézifék, kuplung, ABS/TC/fékerőelosztás, szakaszidő és világításállapot ebből az adapterből nem kap kitalált értéket. DEMO-ban lehetnek szimulált értékeik.
- A Windows-bemenet játékhatása és két fizikai telefon Wi-Fi-n nincs igazolva. A `received` átvétel, az `executed` elküldött Windows-bemenet; egyik sem bizonyítja a játék állapotát. A `simulated` kizárólag DEMO-visszajelzés.
- Nincs minden autóhoz gyári billentyűkiosztás: a játékban és a Bridge-ben ugyanazokat a ténylegesen támogatott parancsokat állítsd be. Az autónkénti kiosztás a teljes játékalapértelmezést felülírja; az üres autókiosztás tudatos letiltás.
- A három-/többállású választó és csúszka növelő/csökkentő műveletet küld. A kért pozíció nem abszolút játékállapot. Közvetlen játékállapot-írás nincs.
- A gyári grafikai geometria nincs hitelesítve. Škoda Fabia RS Rally2: részleges referencia; a többi 19 inspirált. Az alapelrendezések saját geometriával készültek, de nem pontos gyári replikák.
- Mobil FPS és valódi Wi-Fi-késleltetés nincs mérve. A kétklienses benchmark loopback TLS-t mér szimulált forrással, és külön közli a kapott Hz-et, RTT-t, CPU-t és allokációt.
- iOS natív forrás és konfiguráció van; aláírt IPA, Xcode-build és fizikai iPhone/iPad-teszt nincs. Az iOS broadcast-felderítéshez külön Apple multicast-jogosultság kellhet; QR/kézi IP használható.
- A preview Android-aláírás futásonként változhat. Frissítés előtt profil-export szükséges; a tartós signing secret beállítása az ANDROID.md-ben szerepel.
- A Windows telepítő nincs külső kiadói tanúsítvánnyal aláírva. A telepítés felhasználónként történik, a Bridge adatai eltávolításkor megmaradnak.
- Valódi kamera, mobil Keystore/Keychain, rendszerfájlválasztó és megosztás nincs fizikai eszközön végigtesztelve. Az angol fordítás a fő navigációra terjed ki, a szerkesztő és több részletes szöveg magyar.
- Játékból automatikus autóváltáshoz nincs hiteles aliaslista. A kézi profilválasztás és a másik készülék profilajánlása elérhető. További játékok és online munkamenetek tesztje nincs készre jelentve.
