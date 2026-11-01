# SIM CONTROL STUDIO LAN protocol v1

Transport: TLS-encrypted WebSocket at `wss://<private-ip>:19760/ws`. The native client uses an empty trust store and accepts only the SHA-256 DER certificate fingerprint verified from the PC pairing screen. Plain WebSocket, HTTP token URLs, browser origins and arbitrary public destinations are not supported.

The v1 maximum client JSON message is 16,384 UTF-8 bytes. Text messages only; timeout for the initial handshake is 5 seconds. A maximum of 16 registered devices is supported. A device's secret is returned only once over pinned TLS, stored in Android secure storage / iOS Keychain, and hashed in the PC registry.

## Pairing

The PC opens a 120-second window with a random 192-bit token. Its QR content:

```text
simcontrol://pair?host=192.168.1.20&port=19760&pin=<64-hex-sha256>&token=<48-hex-token>&v=1
```

First WebSocket message (no `type` is required for the initial message):

```json
{
  "protocol": 1,
  "deviceId": "38de573f-7b62-4c06-849c-d164af5f030a",
  "name": "My tablet",
  "role": "panel",
  "profileId": "skoda-fabia-rs-rally2",
  "layoutId": "skoda-fabia-rs-rally2-panel",
  "hz": 30,
  "pairingToken": "<48-hex-token>"
}
```

Reconnect uses `secret` instead of `pairingToken`. `deviceId` must be a UUID, role must be dashboard/panel/hybrid, and Hz must be 20/30/60. New devices start read-only. A profile ID never grants keyboard privileges.

The welcome contains protocol, bridgeVersion, deviceId, a new secret only on first pairing, canControl, mobileControlEnabled, gameId, supportedActions and optional suggestedProfile. The secret must never be copied into a diagnostic report or shared profile JSON.

## Telemetry

```json
{
  "type": "telemetry",
  "frame": {
    "sequence": 1,
    "timestampMs": 1000,
    "gameId": "acr",
    "adapter": "acr:shared-memory:v1",
    "state": "live",
    "fields": {
      "speed": {"value": 137.25, "unit": "km/h", "source": "acr:shared-memory:v1", "timestampMs": 1000, "validity": "valid", "derived": false},
      "gear": {"value": 4, "unit": "gear", "source": "acr:shared-memory:v1", "timestampMs": 1000, "validity": "valid", "derived": true},
      "fuel": {"unit": "L", "source": "acr:shared-memory:v1", "timestampMs": 1000, "validity": "unsupported", "derived": false}
    }
  }
}
```

This example is a **synthetic protocol test vector**, not a captured live Rally session. `value` is omitted for unavailable fields by the .NET serializer. Validity is `valid`, `stale`, `unsupported` or `invalid`. Stale fields retain their original sample timestamp. Derived values identify explicit unit/gear conversions, not guessed sensor measurements. Arrays use FL/FR/RL/RR ordering.

Each session samples the single latest shared frame at its requested maximum rate. Slow clients cannot accumulate an unbounded telemetry queue. The shared adapter is read once per Bridge tick, regardless of the number of devices. ActualHz is measured at the Bridge delivery read loop, not the game's internal physics frequency.

`health` arrives about once a second with adapter state, game detection, memory availability, optional memoryBlocks, actualHz, lastPacketMs, error and current command permissions. New games may add fields without changing the mobile renderer. Unsupported fields must remain explicitly unavailable.

## Controls

```json
{"type":"command","id":"request-unique-id","sequence":1,"action":"lights","phase":"press"}
```

Only registered action IDs are accepted; no keycodes, executable paths, arbitrary scripts or macros are accepted from the network. Phases: press, down, up. The PC maps action IDs to locally reviewed keys. Down requires a hold/repeat binding; up always releases this session's corresponding lease. A session's sequence must increase, IDs must not repeat. The command token bucket allows 30/s with a 30-command burst; key-up is exempt from rate limiting.

Acknowledgments distinguish `received`, `executed`, `released` and `rejected`. The mobile separately shows `requested`, `sent` and timeout. An executed SendInput request is **not** proof that the game accepted it; real state feedback is the separate telemetry channel.

The Bridge requires global local arming, a controller-enabled paired device, panel/hybrid role, a running selected game and that game's foreground window. Key ownership is tracked per socket session and per virtual key, including shared modifiers. Revocation, disconnect, focus loss, Bridge shutdown and 3-second hold expiry release owned keys. A 5-second client heartbeat expiry also aborts the session. A hold can renew its lease using down; configured repeat remains bounded to 3 seconds and requires release/re-arm.

```json
{"type":"releaseAll"}
{"type":"ping","sentMs":1234}
{"type":"profile","profileId":"skoda-fabia-rs-rally2"}
```

Pong echoes sentMs; the client computes RTT with a monotonic clock and sends `latency`. Profile changes broadcast a `profileSuggestion` with the source device; recipients accept explicitly and retain manual override. Unknown profile IDs are ignored. No verified game-car alias table is provided in 0.2.0.

## Discovery

Optional UDP request to port 19761: `SIMCONTROL_DISCOVER_V1 <nonce>`. Response contains service=simcontrol, protocol=1, port, name, pin and matching nonce. It contains neither pairing token nor device secret. Broadcast discovery is unauthenticated; the fingerprint must be checked against the PC screen. The bridge rate-limits replies per address. Manual IPv4 and QR work without discovery.

## Backward-compatible 0.2.0 fields

`mode` is `live` (default for old frames) or `demo`. A DEMO frame uses `state=demo`, `mode=demo`, `gameId=demo`, and `demo:` field sources. The mobile accepts a fresh DEMO only with the explicit mode, and displays a persistent badge. DEMO command acknowledgments have `stage=simulated`; they never claim Windows or game execution. Remote DEMO still requires pairing and panel/hybrid role, and cannot invoke `IKeySink`.

Hello and profile messages may include an opaque `layoutId` (1–100 characters, no control characters), identifying the actual base/personal layout. `profileId` remains the vehicle ID used for local keymap selection and cross-device suggestions. Health includes sanitized `clients` with deviceId, name, role, profileId, layoutId, requested Hz, nullable measured RTT and connection quality. It never includes pairing credentials.

Keymap schema 2: `{"schemaVersion":2,"bindings":{"acr":{}},"profileBindings":{"acr/vehicle-id":{}}}`. A present profile map completely overrides the game's default, including an intentionally empty map. Legacy game-map JSON remains importable. A mapping is local configuration, never supplied as a raw keyboard request over the socket.

Command receive loops do not await press duration. Each session has at most 16 pending commands; key-up stays exempt. Same-action pulses serialize; session release/profile change/permission loss cancels queued pulses as well as held leases.
