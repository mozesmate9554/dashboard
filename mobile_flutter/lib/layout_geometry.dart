import 'models.dart';

/// Align an unlocked element, or its unlocked group, to the canvas bounds.
void alignToCanvas(StudioLayout layout, int page, String id, String alignment) {
  final selected = layout.elements(page).firstWhere((e) => e['id'] == id);
  if (selected['locked'] == true) return;
  final group = selected['group'];
  final items = layout.elements(page).where((e) => e['locked'] != true &&
    (group == null || group == '' ? e['id'] == id : e['group'] == group)).toList();
  final left = items.map((e) => (e['x'] as num).toDouble()).reduce((a,b) => a < b ? a : b);
  final top = items.map((e) => (e['y'] as num).toDouble()).reduce((a,b) => a < b ? a : b);
  final right = items.map((e) => (e['x'] as num) + (e['w'] as num)).reduce((a,b) => a > b ? a : b);
  final bottom = items.map((e) => (e['y'] as num) + (e['h'] as num)).reduce((a,b) => a > b ? a : b);
  final dx = switch (alignment) { 'left' => -left, 'center' => (layout.width - right - left) / 2, 'right' => layout.width - right, _ => 0.0 };
  final dy = switch (alignment) { 'top' => -top, 'middle' => (layout.height - bottom - top) / 2, 'bottom' => layout.height - bottom, _ => 0.0 };
  for (final e in items) { e['x'] = (e['x'] as num) + dx; e['y'] = (e['y'] as num) + dy; }
  layout.validate();
}
