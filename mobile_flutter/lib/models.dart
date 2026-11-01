import 'dart:convert';
import 'dart:typed_data';

const appVersion = '0.2.0';
const widgetKinds = <String>{
  'number', 'gear', 'bar', 'leds', 'analog', 'pedals', 'gForce', 'tyres',
  'text', 'image', 'svg', 'button', 'hold', 'toggle', 'threeState', 'multiState',
  'rotary', 'stepper', 'slider', 'indicator', 'icon',
};
const actions = <String>{
  'ignition', 'starter', 'lights', 'flash', 'wiper', 'radio', 'intercom', 'camera',
  'pitLimiter', 'brakeBiasUp', 'brakeBiasDown', 'absUp', 'absDown', 'tcUp', 'tcDown',
  'diffUp', 'diffDown', 'engineMapUp', 'engineMapDown', 'drs', 'ers', 'p2p', 'neutral',
  'reverse', 'displayNext', 'displayPrevious', 'acknowledge', 'drink', 'fan', 'rainLight',
};

class TelemetryDatum {
  final Object? value;
  final String unit, source, validity;
  final int timestampMs;
  final bool derived;
  const TelemetryDatum(this.value, this.unit, this.source, this.timestampMs,
      this.validity, this.derived);
  factory TelemetryDatum.fromJson(Map<String, dynamic> json) => TelemetryDatum(
    json['value'], json['unit'] as String? ?? '', json['source'] as String? ?? '',
    (json['timestampMs'] as num?)?.toInt() ?? 0,
    json['validity'] as String? ?? 'unsupported', json['derived'] == true,
  );
}

class TelemetryFrame {
  static final Stopwatch _arrivalClock = Stopwatch()..start();
  final int sequence, timestampMs;
  final String gameId, state, mode;
  final String? vehicleId;
  final Map<String, TelemetryDatum> fields;
  final int receivedAtTicks;
  TelemetryFrame(this.sequence, this.timestampMs, this.gameId, this.state,
      this.vehicleId, this.fields, {this.mode = 'live'}) : receivedAtTicks = _arrivalClock.elapsedMilliseconds;
  factory TelemetryFrame.fromJson(Map<String, dynamic> json) => TelemetryFrame(
    (json['sequence'] as num).toInt(), (json['timestampMs'] as num).toInt(),
    json['gameId'] as String, json['state'] as String,
    json['vehicleId'] as String?, (json['fields'] as Map<String, dynamic>).map(
      (key, value) => MapEntry(key, TelemetryDatum.fromJson(value as Map<String, dynamic>))),
    mode: json['mode'] as String? ?? 'live',
  );
  bool get isDemo => mode == 'demo';
  bool get fresh => (state == 'live' || isDemo && state == 'demo') && _arrivalClock.elapsedMilliseconds - receivedAtTicks <= 600;
  Object? value(String field) => fresh && fields[field]?.validity == 'valid' ? fields[field]?.value : null;
  double? number(String field) => value(field) is num ? (value(field) as num).toDouble() : null;
  String formatted(String field, {int decimals = 0}) {
    final data = value(field);
    if (data == null) return '—';
    if (field == 'gear' && data is num) return data == -1 ? 'R' : data == 0 ? 'N' : data.toInt().toString();
    if ((field.startsWith('lap') || field == 'stageTime') && data is num && field != 'lap' && field != 'lapsRemaining') {
      final ms = data.toInt();
      return '${ms ~/ 60000}:${((ms ~/ 1000) % 60).toString().padLeft(2, '0')}.${(ms % 1000).toString().padLeft(3, '0')}';
    }
    return data is num ? data.toStringAsFixed(decimals) : data.toString();
  }
}

Map<String, dynamic> deepCopy(Map<String, dynamic> value) {
  Object? copy(Object? item) => switch (item) {
    Map<String, dynamic> map => map.map((key, v) => MapEntry(key, copy(v))),
    List list => list.map(copy).toList(), _ => item,
  };
  return copy(value) as Map<String, dynamic>;
}

class StudioLayout {
  final Map<String, dynamic> data;
  StudioLayout(Map<String, dynamic> value) : data = deepCopy(value) { validate(); }
  String get id => data['id'] as String;
  String get name => data['name'] as String;
  String get vehicleId => data['vehicleId'] as String;
  String get role => data['role'] as String;
  bool get isBase => data['isBase'] == true;
  double get width => (data['width'] as num).toDouble();
  double get height => (data['height'] as num).toDouble();
  List<Map<String, dynamic>> get pages => (data['pages'] as List).cast<Map<String, dynamic>>();
  List<Map<String, dynamic>> elements(int page) => (pages[page]['elements'] as List).cast<Map<String, dynamic>>();
  StudioLayout personalCopy(String newId, String newName) {
    final copy = deepCopy(data);
    copy['id'] = newId; copy['name'] = newName; copy['isBase'] = false;
    copy['parentId'] = id; copy['revision'] = 1;
    return StudioLayout(copy);
  }
  void validate() {
    if (data['schemaVersion'] != 1 || data['id'] is! String || id.isEmpty || id.length > 100 ||
        data['name'] is! String || name.length > 120 || data['vehicleId'] is! String ||
        !{'dashboard', 'panel', 'hybrid'}.contains(role) ||
        width < 320 || width > 4096 || height < 200 || height > 4096 ||
        !width.isFinite || !height.isFinite || pages.isEmpty || pages.length > 8) {
      throw const FormatException('Érvénytelen vagy nem támogatott profil.');
    }
    final ids = <String>{};
    var count = 0;
    for (final page in pages) {
      for (final e in (page['elements'] as List).cast<Map<String, dynamic>>()) {
        count++;
        if (count > 250 || !widgetKinds.contains(e['kind']) || e['id'] is! String || !ids.add(e['id'] as String)) {
          throw const FormatException('Hibás, ismétlődő vagy túl sok műszerelem.');
        }
        for (final key in ['x', 'y', 'w', 'h']) {
          if (e[key] is! num || !(e[key] as num).toDouble().isFinite) throw const FormatException('Hibás geometria.');
        }
        final x = (e['x'] as num).toDouble(), y = (e['y'] as num).toDouble();
        final w = (e['w'] as num).toDouble(), h = (e['h'] as num).toDouble();
        if (x < 0 || y < 0 || w < 12 || h < 12 || x + w > width + .01 || y + h > height + .01) {
          throw const FormatException('A műszerelem a vásznon kívülre került.');
        }
        for (final key in ['action', 'minusAction']) {
          if (e[key] != null && !actions.contains(e[key])) throw const FormatException('Ismeretlen vezérlőművelet.');
        }
        if (e['rotation'] != null && (e['rotation'] is! num || !(e['rotation'] as num).toDouble().isFinite)) {
          throw const FormatException('Hibás forgatás.');
        }
        if (e['opacity'] != null && (e['opacity'] is! num || !(e['opacity'] as num).toDouble().isFinite || (e['opacity'] as num) < 0 || (e['opacity'] as num) > 1)) {
          throw const FormatException('Az átlátszóság 0 és 1 közötti érték lehet.');
        }
        if (e['positions'] != null && (e['positions'] is! int || (e['positions'] as int) < 2 || (e['positions'] as int) > 12)) {
          throw const FormatException('A választó pozícióinak száma 2 és 12 közötti egész szám lehet.');
        }
        for (final key in ['label', 'field', 'assetId', 'font', 'group']) {
          if (e[key] != null && (e[key] is! String || (e[key] as String).length > 200)) {
            throw const FormatException('Hibás műszerfelirat vagy adatkapcsolat.');
          }
        }
        for (final key in ['fontSize', 'max', 'z', 'warningAbove', 'count', 'decimals']) {
          if (e[key] != null && (e[key] is! num || !(e[key] as num).toDouble().isFinite)) {
            throw const FormatException('Érvénytelen műszerparaméter.');
          }
        }
        if (e['fontSize'] is num && ((e['fontSize'] as num) < 1 || (e['fontSize'] as num) > 500) ||
            e['max'] is num && (e['max'] as num) <= 0 ||
            e['count'] is num && ((e['count'] as num) < 1 || (e['count'] as num) > 64) ||
            e['decimals'] is num && ((e['decimals'] as num) < 0 || (e['decimals'] as num) > 5)) {
          throw const FormatException('A skála, betűméret vagy pontosság tartományon kívül van.');
        }
        for (final key in ['visibleWhen', 'enabledWhen']) {
          if (e[key] == null) continue;
          final rule = e[key];
          if (rule is! Map<String, dynamic> || rule['field'] is! String ||
              !{'>','<','>=','<=','=='}.contains(rule['op']) || rule['value'] is! num ||
              !(rule['value'] as num).toDouble().isFinite) {
            throw const FormatException('Érvénytelen megjelenítési feltétel.');
          }
        }
      }
    }
    final assets = data['assets'] as Map<String, dynamic>? ?? {};
    if (assets.length > 25) throw const FormatException('Túl sok importált kép.');
    var assetBytes = 0;
    for (final item in assets.values) {
      final asset = item as Map<String, dynamic>;
      final bytes = base64Decode(asset['base64'] as String);
      assetBytes += bytes.length;
      validateAsset(asset['type'] as String, bytes);
    }
    if (assetBytes > 12 * 1024 * 1024) throw const FormatException('A profil képei összesen legfeljebb 12 MB méretűek lehetnek.');
  }
}

void validateAsset(String type, Uint8List bytes) {
  if (bytes.length > 4 * 1024 * 1024 || bytes.isEmpty) throw const FormatException('A kép legfeljebb 4 MB lehet.');
  if (type == 'png') {
    if (bytes.length < 24 || !bytes.take(8).toList().toString().contains('137, 80, 78, 71, 13, 10, 26, 10')) {
      throw const FormatException('Nem PNG fájl.');
    }
    final data = ByteData.sublistView(bytes);
    final width = data.getUint32(16), height = data.getUint32(20);
    if (width == 0 || height == 0 || width > 8192 || height > 8192 || width * height > 16000000) {
      throw const FormatException('A PNG felbontása túl nagy.');
    }
  } else if (type == 'svg') {
    if (bytes.length > 1024 * 1024) throw const FormatException('Az SVG legfeljebb 1 MB lehet.');
    final text = utf8.decode(bytes);
    if (!text.contains('<svg') || RegExp(r'<!DOCTYPE|<!ENTITY|<script|<foreignObject', caseSensitive: false).hasMatch(text) ||
        RegExp('(?:href|src)\\s*=\\s*["\'](?!#|data:)', caseSensitive: false).hasMatch(text) ||
        RegExp(r'url\(\s*(?!#|data:)', caseSensitive: false).hasMatch(text)) {
      throw const FormatException('Az SVG csak önálló, külső hivatkozás nélküli grafika lehet.');
    }
  } else { throw const FormatException('Csak PNG vagy SVG használható.'); }
}

class VehicleProfile {
  final Map<String, dynamic> data;
  VehicleProfile(this.data);
  String get id => data['id'] as String;
  String get name => data['name'] as String;
  String get category => data['category'] as String;
  String get fidelity => data['fidelity'] as String;
  StudioLayout get dashboard => StudioLayout(data['dashboard'] as Map<String, dynamic>);
  StudioLayout get panel => StudioLayout(data['panel'] as Map<String, dynamic>);
}
