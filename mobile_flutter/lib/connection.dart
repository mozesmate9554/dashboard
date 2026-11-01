import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'models.dart';
import 'storage.dart';
import 'demo.dart';

String newId() {
  final random = Random.secure();
  final b = List<int>.generate(16, (_) => random.nextInt(256));
  b[6] = (b[6] & 15) | 64; b[8] = (b[8] & 63) | 128;
  final hex = b.map((n) => n.toRadixString(16).padLeft(2, '0')).join();
  return '${hex.substring(0, 8)}-${hex.substring(8, 12)}-${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20)}';
}

bool privateAddress(String host) {
  final address = InternetAddress.tryParse(host);
  if (address == null || address.type != InternetAddressType.IPv4) return false;
  final b = address.rawAddress;
  return b[0] == 10 || b[0] == 127 || b[0] == 192 && b[1] == 168 ||
      b[0] == 172 && b[1] >= 16 && b[1] <= 31 || b[0] == 169 && b[1] == 254;
}

class BridgeTarget {
  final String host, pin;
  final int port;
  final String? token;
  BridgeTarget(this.host, this.port, String fingerprint, {this.token}) : pin = fingerprint.toLowerCase().replaceAll(':', '') {
    if (!privateAddress(host) || port < 1024 || port > 65535 || !RegExp(r'^[0-9a-f]{64}$').hasMatch(pin) ||
        token != null && !RegExp(r'^[0-9a-fA-F]{48}$').hasMatch(token!)) {
      throw const FormatException('Hibás helyi IP-cím, port, tanúsítvány vagy párosítási token.');
    }
  }
  factory BridgeTarget.fromUri(String value) {
    final uri = Uri.parse(value.trim());
    if (uri.scheme != 'simcontrol' || uri.host != 'pair' || uri.queryParameters['v'] != '1') {
      throw const FormatException('Ez nem SIM CONTROL STUDIO v1 párosítókód.');
    }
    return BridgeTarget(uri.queryParameters['host'] ?? '', int.tryParse(uri.queryParameters['port'] ?? '') ?? 0,
        uri.queryParameters['pin'] ?? '', token: uri.queryParameters['token']);
  }
  Map<String, dynamic> toJson() => {'host': host, 'port': port, 'pin': pin};
}

class BridgeConnection extends ChangeNotifier with WidgetsBindingObserver {
  final StudioStore store;
  final _secure = const FlutterSecureStorage(aOptions: AndroidOptions(encryptedSharedPreferences: true));
  final telemetry = ValueNotifier<TelemetryFrame?>(null);
  final ticks = ValueNotifier<int>(0);
  final Stopwatch _watch = Stopwatch()..start();
  WebSocket? _socket;
  HttpClient? _client;
  Timer? _ping, _retry, _freshness;
  Timer? _demoTimer;
  DemoSimulator? _demo;
  String mode = 'live';
  int outboundMessageCount = 0;
  List<Map<String, dynamic>> clients = [];
  BridgeTarget? target;
  String deviceId = '', status = 'disconnected', lastError = '', bridgeVersion = '', gameId = '';
  bool canControl = false, mobileControlEnabled = false, _wantConnection = false, _connecting = false, _paused = false, _disposed = false;
  int latencyMs = 0, _attempt = 0, _generation = 0, _sequence = 0, _lastServerMs = 0;
  Set<String> supportedActions = {};
  Map<String, dynamic> health = {};
  final List<Map<String, dynamic>> commandHistory = [];
  String? suggestedProfile;
  String? suggestionSource;
  BridgeConnection(this.store) { WidgetsBinding.instance.addObserver(this); }
  bool get connected => status == 'connected';
  bool get isDemo => mode == 'demo';
  bool get localDemo => _demo != null;
  bool get mayControl => (localDemo || connected && (isDemo || canControl && mobileControlEnabled)) && store.role != 'dashboard' && !_paused;
  Future<void> setDemo(bool enabled) async {
    releaseAll();
    _generation++; _retry?.cancel(); _ping?.cancel(); _demoTimer?.cancel();
    await _socket?.close(); _socket = null; _client?.close(force: true); _connecting = false;
    telemetry.value = null; canControl = false; mobileControlEnabled = false;
    clients = []; health = {}; supportedActions = {}; lastError = '';
    mode = enabled ? 'demo' : 'live'; _demo = enabled ? DemoSimulator() : null;
    status = enabled ? 'demo' : 'disconnected'; gameId = enabled ? 'demo' : '';
    if (enabled) { supportedActions = {...actions}; _startDemo(); }
    else if (_wantConnection) { unawaited(connect()); }
    notifyListeners();
  }
  void _startDemo() {
    _demoTimer?.cancel();
    if (_paused || _demo == null) return;
    void update() { telemetry.value = _demo!.frame(_watch.elapsedMilliseconds); ticks.value++; }
    update();
    _demoTimer = Timer.periodic(Duration(microseconds: (1000000 / store.hz).round()), (_) => update());
  }
  String get secretKey => 'bridge:${target?.pin}:$deviceId';
  Future<void> initialize() async {
    deviceId = store.prefs.getString('deviceId') ?? newId();
    await store.prefs.setString('deviceId', deviceId);
    final saved = store.prefs.getString('bridgeTarget');
    if (saved != null) {
      try {
        final json = jsonDecode(saved) as Map<String, dynamic>;
        target = BridgeTarget(json['host'] as String, json['port'] as int, json['pin'] as String);
        _wantConnection = true; unawaited(connect());
      } catch (e) { lastError = 'A mentett kapcsolat nem tölthető be: $e'; }
    }
    _freshness = Timer.periodic(const Duration(milliseconds: 200), (_) {
      ticks.value++;
      if (connected && _watch.elapsedMilliseconds - _lastServerMs > 5000) {
        _socket?.close(); _lost('A Bridge nem válaszol.');
      }
    });
  }
  Future<void> pair(BridgeTarget value) async {
    if (localDemo) { _wantConnection = false; await setDemo(false); }
    _wantConnection = false; _generation++; _socket?.close(); _client?.close(force: true);
    _retry?.cancel(); _ping?.cancel(); target = value; _attempt = 0; _connecting = false;
    _wantConnection = true; await connect();
  }
  Future<void> connect() async {
    if (localDemo || _connecting || _paused || _disposed || !_wantConnection || target == null) return;
    _retry?.cancel(); _connecting = true; status = 'connecting'; lastError = ''; notifyListeners();
    final generation = ++_generation;
    try {
      final t = target!;
      final http = HttpClient(context: SecurityContext(withTrustedRoots: false));
      http.findProxy = (_) => 'DIRECT';
      http.badCertificateCallback = (certificate, host, port) => host == t.host && port == t.port && sha256.convert(certificate.der).toString() == t.pin;
      _client = http;
      final socket = await WebSocket.connect('wss://${t.host}:${t.port}/ws', customClient: http).timeout(const Duration(seconds: 6));
      if (_disposed || generation != _generation) { await socket.close(); http.close(force: true); return; }
      _socket = socket; _lastServerMs = _watch.elapsedMilliseconds;
      final secret = await _secure.read(key: secretKey);
      if (_disposed || generation != _generation) { await socket.close(); return; }
      _send({'protocol': 1, 'deviceId': deviceId, 'name': store.prefs.getString('deviceName') ?? 'Mobil ${deviceId.substring(0, 4)}',
        'role': store.role, 'profileId': store.vehicleId, 'hz': store.hz, 'secret': secret, if (secret == null) 'pairingToken': t.token});
      socket.listen((event) {
        if (generation == _generation) unawaited(_message(event, generation));
      }, onError: (Object error) {
        if (generation == _generation) _lost('Kapcsolati hiba: $error');
      }, onDone: () {
        if (generation == _generation) {
          final auth = socket.closeCode == WebSocketStatus.policyViolation;
          if (auth) _wantConnection = false;
          _lost(auth ? 'A párosítás sikertelen vagy visszavont. Nyiss új párosítást a PC-n.' : 'Megszakadt a kapcsolat.');
        }
      }, cancelOnError: true);
      _ping?.cancel();
      _ping = Timer.periodic(const Duration(seconds: 1), (_) => _send({'type': 'ping', 'sentMs': _watch.elapsedMilliseconds}));
      // A successful TLS connection is not an authenticated protocol session.
      Future<void>.delayed(const Duration(seconds: 6), () {
        if (generation == _generation && !connected && !_disposed) { _socket?.close(); _lost('Nem érkezett párosítási visszaigazolás.'); }
      });
    } catch (e) {
      if (generation == _generation) _lost('Nem érhető el a Bridge. Ellenőrizd az IP-címet, tűzfalat és tanúsítványt. $e');
    } finally { if (generation == _generation) _connecting = false; }
  }
  Future<void> _message(Object? raw, int generation) async {
    if (_disposed || generation != _generation) return;
    if (raw is! String || raw.length > 128 * 1024) { _socket?.close(); return; }
    try {
      final json = jsonDecode(raw) as Map<String, dynamic>;
      _lastServerMs = _watch.elapsedMilliseconds;
      switch (json['type']) {
        case 'welcome':
          if (json['protocol'] != 1 || json['deviceId'] != deviceId) throw const FormatException('Eltérő protokoll vagy eszköz.');
          if (json['secret'] is String) await _secure.write(key: secretKey, value: json['secret'] as String);
          if (_disposed || generation != _generation) return;
          await store.prefs.setString('bridgeTarget', jsonEncode(target!.toJson()));
          if (_disposed || generation != _generation) return;
          // Never retain the temporary pairing token after authentication.
          target = BridgeTarget(target!.host, target!.port, target!.pin);
          bridgeVersion = json['bridgeVersion'] as String? ?? ''; gameId = json['gameId'] as String? ?? '';
          mode = json['mode'] as String? ?? 'live';
          canControl = json['canControl'] == true; mobileControlEnabled = json['mobileControlEnabled'] == true;
          supportedActions = (json['supportedActions'] as List? ?? []).cast<String>().toSet();
          suggestedProfile = json['suggestedProfile'] as String?; status = 'connected'; _attempt = 0;
          break;
        case 'telemetry':
          final frame = TelemetryFrame.fromJson(json['frame'] as Map<String, dynamic>);
          telemetry.value = frame;
          return;
        case 'health':
          mode = json['mode'] as String? ?? 'live';
          clients = (json['clients'] as List? ?? []).cast<Map<String, dynamic>>();
          health = json['health'] as Map<String, dynamic>; canControl = json['canControl'] == true;
          mobileControlEnabled = json['mobileControlEnabled'] == true;
          supportedActions = (json['supportedActions'] as List? ?? []).cast<String>().toSet();
          break;
        case 'pong':
          latencyMs = (_watch.elapsedMilliseconds - (json['sentMs'] as num).toInt()).clamp(0, 60000).toInt();
          _send({'type': 'latency', 'ms': latencyMs});
          break;
        case 'ack':
          final index = commandHistory.indexWhere((c) => c['id'] == json['id']);
          if (index >= 0) { commandHistory[index] = {...commandHistory[index], ...json,
            '${json['stage']}AtBridgeMs': json['timestampMs']}; }
          break;
        case 'profileSuggestion':
          if (store.suggestions && json['sourceDevice'] != deviceId) {
            suggestedProfile = json['profileId'] as String?; suggestionSource = 'paired-device';
          }
          break;
      }
      notifyListeners();
    } catch (e) { lastError = 'Hibás Bridge-üzenet: $e'; notifyListeners(); }
  }
  bool _send(Map<String, dynamic> json) {
    try {
      if (_socket?.readyState != WebSocket.open) return false;
      _socket!.add(jsonEncode(json)); outboundMessageCount++; return true;
    } on WebSocketException { return false; }
      on StateError { return false; }
  }
  String command(String action, {String phase = 'press'}) {
    final id = newId();
    final permitted = actions.contains(action) && (phase == 'up' || mayControl && supportedActions.contains(action));
    final entry = <String, dynamic>{'id': id, 'action': action, 'phase': phase,
      'timestampMs': DateTime.now().millisecondsSinceEpoch, 'stage': permitted ? 'requested' : 'rejected',
      'requestedAtMs': DateTime.now().millisecondsSinceEpoch,
      if (!permitted) 'reason': supportedActions.contains(action) ? 'device_read_only' : 'unsupported_or_unmapped'};
    commandHistory.add(entry); if (commandHistory.length > 100) commandHistory.removeAt(0);
    if (localDemo) {
      if (permitted) {
        _demo!.apply(action, phase, _watch.elapsedMilliseconds);
        entry['stage'] = 'simulated'; entry['mode'] = 'demo';
        entry['detail'] = 'Csak helyi DEMO-állapot; nem küld PC-bemenetet.';
        telemetry.value = _demo!.frame(_watch.elapsedMilliseconds);
      }
      notifyListeners(); return id;
    }
    if (permitted) {
      final sent = _send({'type': 'command', 'id': id, 'sequence': ++_sequence, 'action': action, 'phase': phase});
      if (!sent) { entry['stage'] = 'rejected'; entry['reason'] = 'disconnected'; notifyListeners(); return id; }
      entry['stage'] = 'sent';
      entry['sentAtMs'] = DateTime.now().millisecondsSinceEpoch;
      Future<void>.delayed(const Duration(seconds: 4), () {
        if (_disposed) return;
        final index = commandHistory.indexWhere((c) => c['id'] == id);
        if (index >= 0 && ['sent', 'received'].contains(commandHistory[index]['stage'])) {
          commandHistory[index] = {...commandHistory[index], 'stage': 'timeout'}; notifyListeners();
        }
      });
    }
    notifyListeners(); return id;
  }
  void releaseAll() { if (localDemo) { _demo!.releaseAll(); } else { _send({'type': 'releaseAll'}); } }
  void selectProfile(String profileId) { if (!localDemo) { _send({'type': 'profile', 'profileId': profileId}); } }
  Future<void> refreshSettings() async {
    if (localDemo) { releaseAll(); _startDemo(); notifyListeners(); return; }
    releaseAll(); _generation++; _socket?.close(); _client?.close(force: true); _ping?.cancel(); _connecting = false;
    telemetry.value = null; status = 'disconnected'; _wantConnection = target != null; await connect();
  }
  void dismissSuggestion() { suggestedProfile = null; notifyListeners(); }
  void _lost(String reason) {
    if (_disposed || localDemo) return;
    status = 'disconnected'; lastError = reason; canControl = false; mobileControlEnabled = false;
    telemetry.value = null; _ping?.cancel(); _client?.close(force: true); _connecting = false; notifyListeners();
    if (_wantConnection && !_paused && _retry?.isActive != true) {
      _retry = Timer(Duration(seconds: min(30, 1 << min(_attempt++, 5))), () => unawaited(connect()));
    }
  }
  Future<void> forget() async {
    _wantConnection = false; releaseAll(); _generation++; _retry?.cancel(); _ping?.cancel();
    await _socket?.close(); _client?.close(force: true);
    await _secure.delete(key: secretKey); await store.prefs.remove('bridgeTarget');
    target = null; status = 'disconnected'; telemetry.value = null; notifyListeners();
  }
  @override void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) { _paused = false; if (localDemo) { _startDemo(); notifyListeners(); } else if (_wantConnection) { unawaited(connect()); } }
    else if (state == AppLifecycleState.inactive || state == AppLifecycleState.paused || state == AppLifecycleState.detached) {
      _paused = true; releaseAll(); _generation++; _socket?.close(); _ping?.cancel(); _retry?.cancel();
      _demoTimer?.cancel(); _connecting = false; status = localDemo ? 'demo' : 'disconnected'; telemetry.value = null; notifyListeners();
    }
  }
  Map<String, dynamic> diagnosticReport() => {'application': 'SIM CONTROL STUDIO', 'version': appVersion,
    'bridgeVersion': bridgeVersion, 'exportedAt': DateTime.now().toUtc().toIso8601String(), 'state': status,
    'mode': mode, 'latencyMs': localDemo ? null : latencyMs, 'health': health, 'clients': clients, 'commands': commandHistory, 'lastError': lastError,
    'fields': telemetry.value?.fields.map((key, d) => MapEntry(key, {'value': d.value, 'source': d.source,
      'timestampMs': d.timestampMs, 'validity': d.validity, 'derived': d.derived, 'unit': d.unit}))};
  @override void dispose() {
    _disposed = true; _wantConnection = false; releaseAll(); _generation++;
    WidgetsBinding.instance.removeObserver(this); _socket?.close(); _client?.close(force: true);
    _ping?.cancel(); _retry?.cancel(); _freshness?.cancel(); _demoTimer?.cancel(); telemetry.dispose(); ticks.dispose(); super.dispose();
  }
}

Future<List<BridgeTarget>> discoverBridges({int port = 19761}) async {
  final socket = await RawDatagramSocket.bind(InternetAddress.anyIPv4, 0);
  final nonce = newId(); final results = <String, BridgeTarget>{};
  try {
    socket.broadcastEnabled = true;
    final subscription = socket.listen((event) {
      if (event != RawSocketEvent.read) return;
      final packet = socket.receive(); if (packet == null || packet.data.length > 2048) return;
      try {
        final json = jsonDecode(utf8.decode(packet.data)) as Map<String, dynamic>;
        if (json['service'] == 'simcontrol' && json['protocol'] == 1 && json['nonce'] == nonce) {
          final target = BridgeTarget(packet.address.address, json['port'] as int, json['pin'] as String);
          if (results.length < 16) results[target.host] = target;
        }
      } catch (_) { /* Untrusted LAN broadcast; discard invalid replies. */ }
    });
    socket.send(ascii.encode('SIMCONTROL_DISCOVER_V1 $nonce'), InternetAddress('255.255.255.255'), port);
    await Future<void>.delayed(const Duration(seconds: 2));
    await subscription.cancel(); return results.values.toList();
  } finally { socket.close(); }
}
