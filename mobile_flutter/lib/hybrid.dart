import 'models.dart';

/// A composed editable hybrid, not an additional claimed factory layout.
StudioLayout composeHybrid(String vehicleId, String name, StudioLayout dashboard, StudioLayout panel) {
  final elements = <Map<String, dynamic>>[];
  final assets = <String, dynamic>{};
  void add(StudioLayout source, String prefix, double left, double width, int page) {
    final sx = width / source.width, sy = 700 / source.height;
    final scale = sx < sy ? sx : sy;
    final dx = left + (width - source.width * scale) / 2;
    final dy = (700 - source.height * scale) / 2;
    for (final entry in (source.data['assets'] as Map<String, dynamic>? ?? {}).entries) {
      assets['$prefix:${entry.key}'] = entry.value;
    }
    for (final original in source.elements(page)) {
      final e = deepCopy(original);
      e['id'] = '$prefix:${e['id']}';
      e['w'] = ((e['w'] as num) * scale).clamp(12, width).toDouble();
      e['h'] = ((e['h'] as num) * scale).clamp(12, 700).toDouble();
      e['x'] = (dx + (e['x'] as num) * scale).clamp(left, left + width - (e['w'] as num)).toDouble();
      e['y'] = (dy + (e['y'] as num) * scale).clamp(0, 700 - (e['h'] as num)).toDouble();
      if (e['fontSize'] is num) e['fontSize'] = ((e['fontSize'] as num) * scale).clamp(1, 500).toDouble();
      if (e['assetId'] is String) e['assetId'] = '$prefix:${e['assetId']}';
      if (e['group'] is String) e['group'] = '$prefix:${e['group']}';
      elements.add(e);
    }
  }
  add(dashboard, 'dash', 0, 1200, 0);
  add(panel, 'panel', 1200, 800, panel.pages.length >= 3 ? 2 : 0);
  return StudioLayout({'schemaVersion': 1, 'id': '$vehicleId-hybrid', 'name': '$name · Hibrid', 'vehicleId': vehicleId,
    'role': 'hybrid', 'version': '0.3.0', 'revision': 1, 'isBase': true, 'width': 2000, 'height': 700,
    'background': '#080a0c', 'assets': assets, 'supportedFields': elements.map((e) => e['field']).whereType<String>().where((v) => v.isNotEmpty).toSet().toList(),
    'pages': [{'id': '$vehicleId-hybrid-main', 'name': 'Hibrid', 'elements': elements}]});
}
