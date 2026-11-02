import 'dart:convert';
import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:share_plus/share_plus.dart';
import 'connection.dart';
import 'display.dart';
import 'models.dart';
import 'premium_controls.dart';
import 'storage.dart';
import 'layout_geometry.dart';

Future<void> shareJson(BuildContext context, StudioStore store, String name, Object json) async {
  final file = File('${store.directory.path}/$name');
  await file.writeAsString(const JsonEncoder.withIndent('  ').convert(json));
  if (!context.mounted) return;
  final box = context.findRenderObject() as RenderBox?;
  await SharePlus.instance.share(ShareParams(files: [XFile(file.path)],
    sharePositionOrigin: box == null ? const Rect.fromLTWH(0, 0, 1, 1) : box.localToGlobal(Offset.zero) & box.size));
}

class LayoutEditor extends StatefulWidget {
  final StudioStore store;
  final BridgeConnection connection;
  final StudioLayout layout;
  const LayoutEditor({super.key, required this.store, required this.connection, required this.layout});
  @override State<LayoutEditor> createState() => _LayoutEditorState();
}
class _LayoutEditorState extends State<LayoutEditor> {
  late StudioLayout _layout;
  final List<Map<String, dynamic>> _undo = [], _redo = [];
  Map<String, dynamic>? _dragBefore;
  String? _selected;
  int _page = 0;
  bool _snap = true, _dirty = false;
  Map<String, dynamic>? get selected => _layout.elements(_page).where((e) => e['id'] == _selected).firstOrNull;
  @override void initState() {
    super.initState();
    _layout = widget.layout.isBase ? widget.layout.personalCopy(newId(), '${widget.layout.name} · Saját') : StudioLayout(widget.layout.data);
    _dirty = widget.layout.isBase;
  }
  void _record(Map<String, dynamic> before) {
    _undo.add(before); if (_undo.length > 30) _undo.removeAt(0); _redo.clear(); _dirty = true;
  }
  void _change(VoidCallback action) {
    final before = deepCopy(_layout.data);
    try {
      action();
      _layout.data['supportedFields'] = _layout.pages.expand((p) => (p['elements'] as List).cast<Map<String,dynamic>>())
          .map((e) => e['field']).whereType<String>().where((field) => field.isNotEmpty).toSet().toList();
      _layout.validate(); _record(before); setState(() {});
    }
    catch (error) { _layout = StudioLayout(before); _error(error); }
  }
  void _error(Object error) {
    if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error.toString())));
  }
  void _history(bool redo) {
    final source = redo ? _redo : _undo, destination = redo ? _undo : _redo;
    if (source.isEmpty) return;
    destination.add(deepCopy(_layout.data));
    setState(() { _layout = StudioLayout(source.removeLast()); _page = _page.clamp(0, _layout.pages.length - 1).toInt(); _selected = null; _dirty = true; });
  }
  void _move(Map<String, dynamic> element, Offset delta) {
    final group = element['group'];
    final items = _layout.elements(_page).where((e) => e['locked'] != true && (group == null ? e['id'] == element['id'] : e['group'] == group)).toList();
    if (items.isEmpty) return;
    final minX = items.map((e) => (e['x'] as num).toDouble()).reduce((a,b) => a < b ? a : b);
    final minY = items.map((e) => (e['y'] as num).toDouble()).reduce((a,b) => a < b ? a : b);
    final maxX = items.map((e) => (e['x'] as num) + (e['w'] as num)).reduce((a,b) => a > b ? a : b);
    final maxY = items.map((e) => (e['y'] as num) + (e['h'] as num)).reduce((a,b) => a > b ? a : b);
    final dx = delta.dx.clamp(-minX, _layout.width - maxX), dy = delta.dy.clamp(-minY, _layout.height - maxY);
    setState(() { for (final e in items) { e['x'] = (e['x'] as num) + dx; e['y'] = (e['y'] as num) + dy; } });
  }
  void _resize(Map<String, dynamic> e, Offset delta) {
    setState(() {
      e['w'] = ((e['w'] as num) + delta.dx).clamp(12, _layout.width - (e['x'] as num));
      e['h'] = ((e['h'] as num) + delta.dy).clamp(12, _layout.height - (e['y'] as num));
    });
  }
  void _endDrag() {
    final before = _dragBefore; _dragBefore = null;
    if (before == null || jsonEncode(before) == jsonEncode(_layout.data)) return;
    if (_snap && selected != null && selected!['locked'] != true) {
      final e = selected!;
      _move(e, Offset((((e['x'] as num) / 20).round() * 20 - (e['x'] as num)).toDouble(),
          (((e['y'] as num) / 20).round() * 20 - (e['y'] as num)).toDouble()));
    }
    try { _layout.validate(); _record(before); setState(() {}); }
    catch (error) { setState(() => _layout = StudioLayout(before)); _error(error); }
  }
  void _add(String kind) {
    final e = <String, dynamic>{'id': newId(), 'kind': kind, 'x': 100.0, 'y': 100.0, 'w': 240.0,
      'h': kind == 'leds' ? 48.0 : 160.0, 'label': kind.toUpperCase(), 'field': kind == 'gear' ? 'gear' : kind == 'leds' || kind == 'analog' ? 'rpm' : 'speed',
      'color': '#ef3340', 'fontSize': 56, 'z': _layout.elements(_page).length + 1};
    if (['button','hold','toggle','threeState','multiState','rotary','stepper','slider','icon'].contains(kind)) {
      e['field'] = ''; e['action'] = 'lights'; e['fontSize'] = 22;
      if (['threeState','multiState','rotary','stepper','slider'].contains(kind)) { e['action'] = 'brakeBiasUp'; e['minusAction'] = 'brakeBiasDown'; }
    }
    _change(() { _layout.elements(_page).add(e); _selected = e['id'] as String; });
  }
  Future<void> _asset() async {
    try {
      final result = await FilePicker.platform.pickFiles(type: FileType.custom, allowedExtensions: ['svg','png'], withData: false);
      if (result == null || !mounted) return;
      final item = result.files.single;
      if (item.size > 4 * 1024 * 1024) throw const FormatException('A kép túl nagy.');
      final bytes = item.bytes ?? await File(item.path!).readAsBytes();
      final type = item.extension?.toLowerCase() ?? '';
      validateAsset(type, bytes); final id = newId();
      _change(() {
        final assets = _layout.data.putIfAbsent('assets', () => <String, dynamic>{}) as Map<String, dynamic>;
        assets[id] = {'type': type, 'base64': base64Encode(bytes)};
        final e = <String, dynamic>{'id': newId(), 'kind': type == 'png' ? 'image' : 'svg', 'x': 60.0, 'y': 60.0, 'w': 400.0, 'h': 300.0,
          'label': item.name, 'field': '', 'assetId': id, 'border': false, 'z': _layout.elements(_page).length};
        _layout.elements(_page).add(e); _selected = e['id'] as String;
      });
    } catch (e) { _error(e); }
  }
  Future<void> _save() async {
    try {
      _layout.data['revision'] = ((_layout.data['revision'] as num?)?.toInt() ?? 0) + 1;
      await widget.store.saveLayout(_layout); await widget.store.selectLayout(_layout);
      if (mounted) { setState(() => _dirty = false); ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Profil helyben mentve.'))); }
    } catch (e) { _error(e); }
  }
  Future<void> _rename() async {
    final controller = TextEditingController(text: _layout.name);
    final name = await showDialog<String>(context: context, builder: (context) => AlertDialog(title: const Text('Profil neve'),
      content: TextField(controller: controller, maxLength: 120), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Mégse')),
        FilledButton(onPressed: () => Navigator.pop(context, controller.text.trim()), child: const Text('Átnevezés'))]));
    if (name != null && name.isNotEmpty) _change(() => _layout.data['name'] = name);
    controller.dispose();
  }
  Future<void> _canvasSettings() async {
    final background = TextEditingController(text: _layout.data['background'] as String? ?? '#080a0c');
    final pageName = TextEditingController(text: _layout.pages[_page]['name'] as String);
    final result = await showDialog<bool>(context: context, builder: (context) => AlertDialog(title: const Text('Vászon és oldal'),
      content: Column(mainAxisSize: MainAxisSize.min, children: [TextField(controller: background, decoration: const InputDecoration(labelText: 'Vászon háttérszíne #RRGGBB')),
        const SizedBox(height: 12), TextField(controller: pageName, maxLength: 80, decoration: const InputDecoration(labelText: 'Aktuális oldal neve'))]),
      actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Mégse')), FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Alkalmazás'))]));
    if (result == true) _change(() { _layout.data['background'] = background.text.trim(); _layout.pages[_page]['name'] = pageName.text.trim(); });
    background.dispose(); pageName.dispose();
  }
  Future<void> _inspect() async {
    if (selected == null) return;
    await showModalBottomSheet<void>(context: context, isScrollControlled: true, builder: (context) =>
      StatefulBuilder(builder: (context, localSetState) => Padding(padding: EdgeInsets.only(bottom: MediaQuery.viewInsetsOf(context).bottom),
        child: SizedBox(height: MediaQuery.sizeOf(context).height * .85, child: SingleChildScrollView(padding: const EdgeInsets.all(20),
          child: _properties(() => localSetState(() {})))))));
  }
  Widget _properties(VoidCallback refresh) {
    final e = selected;
    if (e == null) return const Text('Válassz egy elemet. Húzd a helyére, a kék fogantyúval méretezd át.');
    void update(String key, Object? value) { _change(() { if (value == null) { e.remove(key); } else { e[key] = value; } }); refresh(); }
    Widget input(String label, String key, {bool numeric = false}) => Padding(padding: const EdgeInsets.symmetric(vertical: 5),
      child: TextFormField(key: ValueKey('${e['id']}:$key:${e[key]}'), initialValue: e[key]?.toString() ?? '',
        decoration: InputDecoration(labelText: label), keyboardType: numeric ? const TextInputType.numberWithOptions(decimal: true, signed: true) : TextInputType.text,
        onFieldSubmitted: (text) {
          if (numeric) { final value = double.tryParse(text); if (value != null) update(key, value); }
          else { update(key, text); }
        }));
    Widget choose(String label, String key, List<String> values) => Padding(padding: const EdgeInsets.symmetric(vertical: 5),
      child: DropdownButtonFormField<String>(isExpanded:true,initialValue: values.contains(e[key]) ? e[key] as String : null, decoration: InputDecoration(labelText: label),
        items: values.map((value) => DropdownMenuItem(value: value, child: Text(value,maxLines:1,overflow:TextOverflow.ellipsis))).toList(), onChanged: (value) => update(key, value)));
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      const Text('MŰSZERELEM', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
      choose('Típus', 'kind', widgetKinds.toList()..sort()), input('Felirat', 'label'), input('Adatmező (pl. speed, rpm, stageTime)', 'field'),
      Row(children: [Expanded(child: input('X', 'x', numeric: true)), const SizedBox(width: 8), Expanded(child: input('Y', 'y', numeric: true))]),
      Row(children: [Expanded(child: input('Szélesség', 'w', numeric: true)), const SizedBox(width: 8), Expanded(child: input('Magasság', 'h', numeric: true))]),
      input('Forgatás °', 'rotation', numeric: true), input('Rétegsorrend', 'z', numeric: true), input('Csoport neve', 'group'),
      Text('Átlátszatlanság ${(((e['opacity'] as num?)?.toDouble() ?? 1) * 100).round()}%'),
      Slider(value: (e['opacity'] as num?)?.toDouble() ?? 1, min: 0, max: 1, divisions: 20, onChanged: (v) => update('opacity', v)),
      Wrap(spacing: 4, children: [for (final (alignment, icon) in [('left', Icons.align_horizontal_left), ('center', Icons.align_horizontal_center), ('right', Icons.align_horizontal_right), ('top', Icons.align_vertical_top), ('middle', Icons.align_vertical_center), ('bottom', Icons.align_vertical_bottom)])
        IconButton(tooltip: 'Vászonhoz igazítás: $alignment', onPressed: e['locked'] == true ? null : () { _change(() => alignToCanvas(_layout, _page, e['id'] as String, alignment)); refresh(); }, icon: Icon(icon))]),
      input('Kiemelőszín #RRGGBB', 'color'), input('Szövegszín #RRGGBB', 'foreground'), input('Háttérszín #RRGGBB', 'background'),
      input('Betűméret', 'fontSize', numeric: true), choose('Betűstílus', 'font', ['monospace', 'sans','factory']),
      choose('Saját gombgrafika', 'assetId', ((_layout.data['assets'] as Map<String,dynamic>?)?.keys.toList() ?? [])),
      choose('Forma', 'shape', ['rectangle','rounded','circle','square']),
      if ({'rocker','pushButton','guarded','rotarySwitch','cycleButton'}.contains(e['kind'])) ...[
        choose('Kapcsolóhang', 'sound', SwitchSounds.files.keys.toList()), input('LED-szín #RRGGBB', 'ledColor'),
        choose('Anyag', 'material', ['brushed','alu','carbon','plastic','rubber','glass']), input('Gravírozott felirat', 'engraving'),
      ],
      input('Skála maximum', 'max', numeric: true), input('Tizedesek', 'decimals', numeric: true),
      input('Választó pozícióinak száma (2–12)', 'positions', numeric: true),
      input('Figyelmeztetés e fölött', 'warningAbove', numeric: true),
      SwitchListTile(title: const Text('Figyelmeztetés villogása'), value: e['animate'] == true, onChanged: (v) => update('animate', v)),
      SwitchListTile(title: const Text('Elem zárolása'), value: e['locked'] == true, onChanged: (v) => update('locked', v)),
      choose('Művelet / növelés', 'action', actions.toList()..sort()), choose('Csökkentés', 'minusAction', actions.toList()..sort()),
      input('Javasolt PC-billentyű (pl. CTRL+L)', 'keys'),
      const Text('A billentyűjavaslatot a PC kiosztás exporttal vidd át, majd a Bridge-ben importáld. A játékban ugyanazt a billentyűt rendeld hozzá.', style: TextStyle(color: Colors.white54, fontSize: 12)),
      const SizedBox(height: 16), OutlinedButton(onPressed: () => _condition(e, 'visibleWhen', refresh), child: const Text('Feltételes láthatóság')),
      OutlinedButton(onPressed: () => _condition(e, 'enabledWhen', refresh), child: const Text('Vezérlő engedélyezési feltétele')),
      Row(children: [Expanded(child: OutlinedButton.icon(onPressed: () {
        _change(() { final copy = deepCopy(e); copy['id'] = newId(); copy['x'] = ((copy['x'] as num) + 20).clamp(0, _layout.width - (copy['w'] as num));
          _layout.elements(_page).add(copy); _selected = copy['id'] as String; }); refresh();
      }, icon: const Icon(Icons.copy), label: const Text('Másolat'))), const SizedBox(width: 8), Expanded(child: OutlinedButton.icon(onPressed: () {
        _change(() { _layout.elements(_page).removeWhere((item) => item['id'] == _selected); _selected = null; }); refresh();
      }, icon: const Icon(Icons.delete_outline), label: const Text('Törlés')))]),
    ]);
  }
  Future<void> _condition(Map<String, dynamic> e, String key, VoidCallback refresh) async {
    final rule = e[key] as Map<String, dynamic>? ?? {};
    final field = TextEditingController(text: rule['field'] as String? ?? 'rpm');
    final threshold = TextEditingController(text: rule['value']?.toString() ?? '5000');
    var op = rule['op'] as String? ?? '>';
    final result = await showDialog<String>(context: context, builder: (context) => AlertDialog(title: const Text('Adatfeltétel'),
      content: Column(mainAxisSize: MainAxisSize.min, children: [TextField(controller: field, decoration: const InputDecoration(labelText: 'Adatmező')),
        DropdownButtonFormField<String>(initialValue: op, items: ['>','<','>=','<=','=='].map((value) => DropdownMenuItem(value: value, child: Text(value,maxLines:1,overflow:TextOverflow.ellipsis))).toList(), onChanged: (value) => op = value!),
        TextField(controller: threshold, decoration: const InputDecoration(labelText: 'Határérték'), keyboardType: TextInputType.number)]),
      actions: [TextButton(onPressed: () => Navigator.pop(context, 'remove'), child: const Text('Törlés')), FilledButton(onPressed: () => Navigator.pop(context, 'save'), child: const Text('Alkalmazás'))]));
    if (result == 'remove') { _change(() => e.remove(key)); }
    if (result == 'save' && double.tryParse(threshold.text) != null) {
      _change(() => e[key] = {'field': field.text.trim(), 'op': op, 'value': double.parse(threshold.text)});
    }
    field.dispose(); threshold.dispose(); refresh();
  }
  Future<void> _exportKeys() async {
    final map = <String, dynamic>{};
    for (final page in _layout.pages) {
      for (final e in (page['elements'] as List).cast<Map<String, dynamic>>()) {
        if (e['action'] is String && e['keys'] is String && (e['keys'] as String).trim().isNotEmpty) {
          map[e['action'] as String] = {'keys': e['keys'], 'mode': e['kind'] == 'hold' ? 'hold' : 'press', 'durationMs': 80, 'repeatMs': 150};
        }
      }
    }
    final game = widget.connection.gameId.isEmpty || widget.connection.isDemo ? 'acr' : widget.connection.gameId;
    await shareJson(context, widget.store, 'sim-control-bindings.json', {'schemaVersion': 2, 'bindings': <String,dynamic>{}, 'profileBindings': {'$game/${_layout.vehicleId}': map}});
  }
  @override Widget build(BuildContext context) {
    final wide = MediaQuery.sizeOf(context).width > 1000;
    return PopScope(canPop: !_dirty, onPopInvokedWithResult: (popped, _) async {
      if (popped) return;
      final leave = await showDialog<bool>(context: context, builder: (context) => AlertDialog(title: const Text('Nem mentett módosítások'), content: const Text('Elhagyod a szerkesztőt a módosítások mentése nélkül?'),
        actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Maradok')), FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Elhagyás'))]));
      if (leave == true && context.mounted) { setState(() => _dirty = false); Navigator.pop(context); }
    }, child: Scaffold(appBar: AppBar(title: Text('${_dirty ? '• ' : ''}${_layout.name}'), actions: [
      IconButton(onPressed: _undo.isEmpty ? null : () => _history(false), tooltip: 'Visszavonás', icon: const Icon(Icons.undo)),
      IconButton(onPressed: _redo.isEmpty ? null : () => _history(true), tooltip: 'Ismétlés', icon: const Icon(Icons.redo)),
      IconButton(onPressed: _save, tooltip: 'Mentés', icon: const Icon(Icons.save_outlined)),
      PopupMenuButton<String>(onSelected: (value) async {
        if (value == 'rename') { await _rename(); return; }
        if (value == 'export') await shareJson(context, widget.store, 'sim-control-profile.json', _layout.data);
        if (value == 'keys') await _exportKeys();
        if (value == 'canvas') await _canvasSettings();
      }, itemBuilder: (_) => [const PopupMenuItem(value: 'rename', child: Text('Átnevezés')), const PopupMenuItem(value: 'canvas', child: Text('Vászon és oldal')), const PopupMenuItem(value: 'export', child: Text('Profil export JSON')), const PopupMenuItem(value: 'keys', child: Text('PC kiosztás export'))]),
    ]), body: Column(children: [
      SingleChildScrollView(scrollDirection: Axis.horizontal, child: Row(children: [
        PopupMenuButton<String>(tooltip: 'Elem hozzáadása', onSelected: _add, itemBuilder: (_) => widgetKinds.map((kind) => PopupMenuItem(value: kind, child: Text(kind))).toList(), child: const Padding(padding: EdgeInsets.all(12), child: Row(children: [Icon(Icons.add), Text('Elem')]))),
        IconButton(onPressed: _asset, tooltip: 'SVG / PNG import', icon: const Icon(Icons.add_photo_alternate_outlined)),
        IconButton(onPressed: selected == null ? null : _inspect, tooltip: 'Tulajdonságok', icon: const Icon(Icons.tune)),
        FilterChip(label: const Text('Rács 20'), selected: _snap, onSelected: (v) => setState(() => _snap = v)), const SizedBox(width: 10),
        DropdownButton<int>(value: _page, items: List.generate(_layout.pages.length, (i) => DropdownMenuItem(value: i, child: Text(_layout.pages[i]['name'] as String))), onChanged: (value) => setState(() { _page = value!; _selected = null; })),
        IconButton(onPressed: _layout.pages.length >= 8 ? null : () => _change(() {
          _layout.pages.add({'id': newId(), 'name': 'Oldal ${_layout.pages.length + 1}', 'elements': <Map<String,dynamic>>[]}); _page = _layout.pages.length - 1; _selected = null;
        }), tooltip: 'Új oldal', icon: const Icon(Icons.post_add)),
        IconButton(onPressed: _layout.pages.length == 1 ? null : () => _change(() { _layout.pages.removeAt(_page); _page = 0; _selected = null; }), tooltip: 'Oldal törlése', icon: const Icon(Icons.delete_sweep_outlined)),
      ])),
      if (widget.connection.isDemo) const DemoBadge(),
      Expanded(child: Row(children: [Expanded(child: AnimatedBuilder(animation: Listenable.merge([widget.connection.telemetry, widget.connection.ticks]), builder: (context, _) => Listener(
        onPointerDown: (_) => _dragBefore = deepCopy(_layout.data), onPointerUp: (_) => _endDrag(), onPointerCancel: (_) => _endDrag(),
        child: LayoutCanvas(layout: _layout, page: _page, editing: true, frame: widget.connection.telemetry.value,
          selectedId: _selected, onSelect: (e) => setState(() => _selected = e['id'] as String), onMove: _move, onResize: _resize)))),
        if (wide) SizedBox(width: 310, child: SingleChildScrollView(padding: const EdgeInsets.all(16), child: _properties(() {}))),
      ])),
      Padding(padding: const EdgeInsets.all(8), child: Text('SZEMÉLYES MÁSOLAT · ${_layout.elements(_page).length} elem · ${_layout.width.toInt()} × ${_layout.height.toInt()} · Húzás / sarokfogantyú', style: const TextStyle(color: Colors.white38, fontSize: 11))),
    ])));
  }
}
