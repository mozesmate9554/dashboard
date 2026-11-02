import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'adaptive_layout.dart';
import 'fullscreen.dart';
import 'connection.dart';
import 'models.dart';
import 'storage.dart';

Color studioColor(Object? hex, [Color fallback = const Color(0xffef3340)]) {
  if (hex is! String) return fallback;
  final value = int.tryParse(hex.replaceFirst('#', ''), radix: 16);
  return value == null ? fallback : Color(hex.replaceFirst('#', '').length <= 6 ? 0xff000000 | value : value);
}
bool visibleElement(Map<String, dynamic> element, TelemetryFrame? frame) {
  final rule = element['visibleWhen'];
  if (rule is! Map<String, dynamic>) return true;
  final value = frame?.number(rule['field'] as String? ?? '');
  if (value == null) return false;
  final threshold = (rule['value'] as num?)?.toDouble() ?? 0;
  return switch (rule['op']) { '>' => value > threshold, '<' => value < threshold,
    '>=' => value >= threshold, '<=' => value <= threshold, '==' => value == threshold, _ => false };
}

class LayoutCanvas extends StatelessWidget {
  final StudioLayout layout;
  final int page;
  final BridgeConnection? connection;
  final TelemetryFrame? frame;
  final bool editing;
  final String? selectedId;
  final void Function(Map<String, dynamic>)? onSelect;
  final void Function(Map<String, dynamic>, Offset)? onMove;
  final void Function(Map<String, dynamic>, Offset)? onResize;
  const LayoutCanvas({super.key, required this.layout, this.page = 0, this.connection,
    this.frame, this.editing = false, this.selectedId, this.onSelect, this.onMove, this.onResize});
  @override Widget build(BuildContext context) {
    final elements = [...layout.elements(page)]..sort((a, b) => ((a['z'] as num?) ?? 0).compareTo((b['z'] as num?) ?? 0));
    return LayoutBuilder(builder: (context, constraints) {
      final scale = math.min(constraints.maxWidth / layout.width, constraints.maxHeight / layout.height);
      return Center(child: SizedBox(width: layout.width * scale, height: layout.height * scale,
        child: FittedBox(fit: BoxFit.contain, child: SizedBox(width: layout.width, height: layout.height,
          child: ClipRect(child: ColoredBox(color: studioColor(layout.data['background'], const Color(0xff080a0c)),
            child: Stack(children: [
              if (editing) const Positioned.fill(child: CustomPaint(painter: _GridPainter())),
              for (final element in elements)
                if (editing || visibleElement(element, frame)) _position(context, element, scale),
              if (editing)
                for (final element in elements)
                  if (element['id'] == selectedId && element['locked'] != true)
                    Positioned(left: (element['x'] as num).toDouble(), top: (element['y'] as num).toDouble(),
                      width: (element['w'] as num).toDouble(), height: (element['h'] as num).toDouble(),
                      child: Transform.rotate(angle: ((element['rotation'] as num?)?.toDouble() ?? 0) * math.pi / 180,
                        child: Stack(clipBehavior: Clip.none, children: [Positioned(right: 0, bottom: 0, width: 44, height: 44,
                          child: GestureDetector(behavior: HitTestBehavior.opaque, dragStartBehavior: DragStartBehavior.down,
                            onPanUpdate: (d) => onResize?.call(element, d.delta),
                            child: const ColoredBox(color: Color(0xff53c9ff), child: Icon(Icons.open_in_full, color: Colors.black))))]))),
            ])))))));
    });
  }
  Widget _position(BuildContext context, Map<String, dynamic> e, double scale) {
    final selected = editing && selectedId == e['id'];
    final locked = e['locked'] == true;
    return Positioned(key: ValueKey('${layout.id}:$page:${e['id']}'), left: (e['x'] as num).toDouble(), top: (e['y'] as num).toDouble(),
      width: (e['w'] as num).toDouble(), height: (e['h'] as num).toDouble(),
      child: Transform.rotate(angle: ((e['rotation'] as num?)?.toDouble() ?? 0) * math.pi / 180,
        child: GestureDetector(behavior: HitTestBehavior.opaque,
          onTap: editing ? () => onSelect?.call(e) : null,
          onPanStart: editing ? (_) => onSelect?.call(e) : null,
          onPanUpdate: editing && !locked ? (details) => onMove?.call(e, details.delta) : null,
          child: Stack(clipBehavior: Clip.none, children: [
            Positioned.fill(child: IgnorePointer(ignoring: editing, child: Instrument(element: e,
              layout: layout, frame: frame, connection: connection))),
            if (selected) Positioned.fill(child: IgnorePointer(child: DecoratedBox(
              decoration: BoxDecoration(border: Border.all(color: const Color(0xff53c9ff), width: 3))))),
            if (selected && locked) const Positioned(right: 2, top: 2, child: Icon(Icons.lock, color: Colors.lightBlue, size: 22)),
          ]))));
  }
}

class Instrument extends StatelessWidget {
  final Map<String, dynamic> element;
  final StudioLayout layout;
  final TelemetryFrame? frame;
  final BridgeConnection? connection;
  const Instrument({super.key, required this.element, required this.layout, this.frame, this.connection});
  @override Widget build(BuildContext context) {
    final e = element, kind = e['kind'] as String;
    final field = e['field'] as String? ?? '';
    final value = frame?.number(field);
    final accent = studioColor(e['color']);
    final warning = value != null && e['warningAbove'] is num && value >= (e['warningAbove'] as num);
    final color = warning ? const Color(0xffff3f3f) : accent;
    final size = (e['fontSize'] as num?)?.toDouble() ?? (kind == 'gear' ? 140.0 : 54.0);
    final label = e['label'] as String? ?? '';
    final foreground = studioColor(e['foreground'], Colors.white);
    final unit = frame?.fields[field]?.unit ?? e['unit'] as String? ?? '';
    final text = e['format']=='minutesSeconds' && value!=null ? '${value.toInt()~/60000}:${((value.toInt()~/1000)%60).toString().padLeft(2,'0')}' : frame?.formatted(field, decimals: (e['decimals'] as num?)?.toInt() ?? 0) ?? '—';
    final font = e['font'] == 'factory' ? 'OemCondensed' : e['font'] == 'sans' ? null : 'monospace';
    final weight=FontWeight.values[(((e['fontWeight'] as num?)?.toInt() ?? (kind=='text'?400:800)) ~/ 100 - 1).clamp(0,8).toInt()];
    Widget child;
    switch (kind) {
      case 'text': child = Center(child: Text(label, textAlign: TextAlign.center, style: TextStyle(color: foreground, fontSize: size, letterSpacing: (e['letterSpacing'] as num?)?.toDouble() ?? 2, fontWeight:weight, fontFamily: font))); break;
      case 'number': case 'gear':
        if(e['style']=='factoryMap' || e['style']=='adaptiveMap'){
          if(value==null){child=const Center(child:Text('—',style:TextStyle(fontSize:38,color:Colors.white54)));break;}
          final row=Row(children:[for(var i=1;i<=5;i++) Expanded(child:Padding(padding:const EdgeInsets.all(2),child:Container(
            decoration:BoxDecoration(color:value==i?const Color(0xff9bd158):const Color(0xff34383b),borderRadius:BorderRadius.circular(6)),
            child:Center(child:FittedBox(child:Text('$i',style:TextStyle(fontFamily:font,fontSize:40,color:value==i?Colors.black:Colors.white54)))))))]);
          child=e['style']=='adaptiveMap'?Column(children:[const Text('Map',style:TextStyle(fontSize:14)),Expanded(child:row)]):row;break;
        }
        if(e['style']=='factoryReadout'){
          child=FittedBox(fit:BoxFit.contain,alignment:Alignment.center,child:Text(text,style:TextStyle(color:foreground,fontFamily:font,fontSize:size,fontWeight:weight,height:1)));break;
        }
        child = Padding(padding: const EdgeInsets.all(7), child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          if (label.isNotEmpty) FittedBox(fit:BoxFit.scaleDown, child:Text(label.toUpperCase(),maxLines:1,style: TextStyle(color: color, fontSize: 15, fontWeight: FontWeight.w700, letterSpacing: 2))),
          Expanded(child: FittedBox(fit: BoxFit.contain, child: Text(text, style: TextStyle(color: warning ? color : foreground, fontSize: size, height: 1, fontWeight:weight, fontFamily: font)))),
          if (kind != 'gear' && unit.isNotEmpty) FittedBox(fit:BoxFit.scaleDown,child:Text(unit,maxLines:1,style: const TextStyle(color: Colors.white54, fontSize: 14))),
        ])); break;
      case 'bar':
        final maximum = (e['max'] as num?)?.toDouble() ?? 1.0;
        child = Padding(padding: const EdgeInsets.all(10), child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          FittedBox(fit:BoxFit.scaleDown,child:Text('$label  $text',maxLines:1,style: TextStyle(color: foreground, fontSize: 18))), const SizedBox(height: 8),
          LinearProgressIndicator(value: value == null ? 0 : (value / maximum).clamp(0, 1).toDouble(), color: color, backgroundColor: Colors.white12, minHeight: 16),
        ])); break;
      case 'leds': child = CustomPaint(painter: _LedPainter(value, frame?.number('rpmLimit') ?? (e['max'] as num?)?.toDouble() ?? 8000,
          (e['count'] as num?)?.toInt() ?? 15, e['vertical'] == true, e['shape'] == 'circle', (e['rows'] as num?)?.toInt() ?? 1)); break;
      case 'analog': child = CustomPaint(painter: _AnalogPainter(value, (e['max'] as num?)?.toDouble() ?? 10000, color, text)); break;
      case 'pedals':
        child = Padding(padding: const EdgeInsets.all(8), child: Row(children: [
          for (final (key, name, tint) in [('throttle', 'GÁZ', Colors.greenAccent), ('brake', 'FÉK', Colors.redAccent), ('clutch', 'KU', Colors.lightBlueAccent)])
            Expanded(child: Padding(padding: const EdgeInsets.all(5), child: Column(children: [
              Expanded(child: RotatedBox(quarterTurns: 3, child: LinearProgressIndicator(value: (frame?.number(key) ?? 0).clamp(0, 1).toDouble(), color: tint, backgroundColor: Colors.white10, minHeight: 18))),
              Text(frame?.number(key) == null ? '—' : name, style: const TextStyle(fontSize: 12)),
            ]))),
        ])); break;
      case 'gForce': child = CustomPaint(painter: _GForcePainter(frame?.number('gX'), frame?.number('gZ'), color)); break;
      case 'tyres':
        final values = frame?.value(field);
        child = Column(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [
          FittedBox(fit:BoxFit.scaleDown,child:Text(label,maxLines:1,style: TextStyle(color: color, fontSize: 15))),
          for (var row = 0; row < 2; row++) Expanded(child:Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [
            for (var column = 0; column < 2; column++) Expanded(child:FittedBox(fit:BoxFit.scaleDown,child:Text('${['FL', 'FR', 'RL', 'RR'][row * 2 + column]}\n${values is List && values.length == 4 && values[row * 2 + column] is num ? (values[row * 2 + column] as num).toStringAsFixed(1) : '—'}', textAlign: TextAlign.center, style: const TextStyle(fontSize: 22, fontFamily: 'monospace')))),
          ])),
        ]); break;
      case 'indicator':
        final actual = frame?.value(field);
        if(e['style']=='factorySymbol'){
          final bytes=layout.assetBytes(e['assetId'] as String?);
          final active=e['activeBelow'] is num?value!=null && value<(e['activeBelow'] as num):actual==true;
          child=bytes==null?const SizedBox():SvgPicture.memory(bytes,fit:BoxFit.contain,colorFilter:ColorFilter.mode(active?accent:Colors.white24,BlendMode.srcIn));break;
        }
        child = Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          Icon(Icons.circle, color: actual == true || actual is num && actual != 0 ? color : Colors.white12, size: 28),
          Text(actual == null ? '$label · —' : label, style: const TextStyle(fontSize: 14)),
        ]); break;
      case 'image': case 'svg':
        final assets = layout.data['assets'] as Map<String, dynamic>?;
        final asset = assets?[e['assetId']] as Map<String, dynamic>?;
        if (asset == null) { child = const Center(child: Icon(Icons.image_outlined, color: Colors.white24)); }
        else {
          final bytes = layout.assetBytes(e['assetId'] as String)!;
          child = kind == 'svg' ? SvgPicture.memory(bytes, fit: BoxFit.contain,
            errorBuilder: (_, _, _) => const Center(child: Icon(Icons.broken_image))) : Image.memory(bytes, fit: BoxFit.contain,
            errorBuilder: (_, _, _) => const Center(child: Icon(Icons.broken_image)));
        }
        break;
      default:
        final artwork=(layout.data['assets'] as Map<String,dynamic>?)?[e['assetId']] as Map<String,dynamic>?;
        if(e['artwork']==true && artwork!=null){
          final bytes=layout.assetBytes(e['assetId'] as String)!;
          child=Stack(fit:StackFit.expand,children:[
            artwork['type']=='svg'?SvgPicture.memory(bytes,fit:BoxFit.contain):Image.memory(bytes,fit:BoxFit.contain),
            PanelControl(element:e,frame:frame,connection:connection),
          ]);break;
        }
        child = LayoutBuilder(builder: (context, constraints) => FittedBox(fit: BoxFit.contain,
          child: SizedBox(width: math.max(220.0, constraints.maxWidth), height: math.max(110.0, constraints.maxHeight),
            child: PanelControl(element: e, frame: frame, connection: connection))));
        break;
    }
    final shape = e['shape'] as String? ?? 'rectangle';
    final faded = warning && e['animate'] == true && (connection?.ticks.value ?? 0).isEven;
    return Opacity(opacity: ((e['opacity'] as num?)?.toDouble() ?? 1) * (faded ? .5 : 1), child: Container(
      decoration: BoxDecoration(color: studioColor(e['background'], Colors.transparent),
        borderRadius: BorderRadius.circular(shape == 'circle' ? 200 : shape == 'rounded' ? 20 : 3),
        border: e['border'] == false || kind == 'leds' || kind == 'text' ? null : Border.all(color: color.withValues(alpha: .5), width: 1.5)),
      child: ClipRect(child: child)));
  }
}

class PanelControl extends StatefulWidget {
  final Map<String, dynamic> element;
  final TelemetryFrame? frame;
  final BridgeConnection? connection;
  const PanelControl({super.key, required this.element, this.frame, this.connection});
  @override State<PanelControl> createState() => _PanelControlState();
}
class _PanelControlState extends State<PanelControl> {
  bool _pressed = false;
  int _requested = 0;
  double _steps = 0;
  Timer? _renew;
  int? _holdPointer;
  String get _kind => widget.element['kind'] as String;
  String get _action => widget.element['action'] as String? ?? '';
  bool get _enabled => widget.connection?.mayControl == true && widget.connection!.supportedActions.contains(_action) &&
      (widget.element['enabledWhen'] == null || visibleElement({'visibleWhen': widget.element['enabledWhen']}, widget.frame));
  void _emit(String action, [String phase = 'press']) {
    if (widget.connection?.store.haptic == true) unawaited(HapticFeedback.selectionClick());
    widget.connection?.command(action, phase: phase);
  }
  void _down() {
    if (!_enabled) return;
    setState(() => _pressed = true); _emit(_action, 'down');
    _renew?.cancel(); _renew = Timer.periodic(const Duration(seconds: 1), (_) => _emit(_action, 'down'));
  }
  void _up() {
    if (!_pressed) return;
    _renew?.cancel(); _pressed = false; _emit(_action, 'up'); if (mounted) setState(() {});
  }
  @override void didUpdateWidget(covariant PanelControl oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (_pressed && (!_enabled || oldWidget.element['id'] != widget.element['id'] || oldWidget.element['action'] != _action || oldWidget.connection != widget.connection)) {
      _renew?.cancel(); _pressed = false; oldWidget.connection?.releaseAll();
    }
  }
  @override Widget build(BuildContext context) {
    final label = widget.element['label'] as String? ?? '';
    final color = studioColor(widget.element['color']);
    final actual = widget.frame?.formatted(widget.element['field'] as String? ?? '');
    final artwork=widget.element['artwork']==true;
    if(artwork && ['stepper','rotary'].contains(_kind)){
      final minus=widget.element['minusAction'] as String? ?? '';
      Widget region(String action,String name)=>Expanded(child:Semantics(button:true,label:'$label $name',child:Material(color:Colors.transparent,child:InkWell(onTap:_enabled && widget.connection!.supportedActions.contains(action)?(){_emit(action);setState(()=>_requested++);}:null))));
      final parts=[region(_action,'növelés'),region(minus,'csökkentés')];
      return Tooltip(message:'$label · kért lépések: $_requested · visszaolvasott: ${actual??'—'}',child:_kind=='stepper'?Column(children:parts):Row(children:parts.reversed.toList()));
    }
    Widget button(String text, VoidCallback? tap, {IconData? icon}) => Expanded(child: Material(color: Colors.transparent,
      child: InkWell(onTap: tap, child: Center(child: icon != null ? Icon(icon, color: _enabled ? color : Colors.white24, size: 28)
        : Text(text, textAlign: TextAlign.center, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: _enabled ? Colors.white : Colors.white24))))));
    Widget child;
    if (['rotary', 'stepper', 'threeState', 'multiState'].contains(_kind)) {
      final minus = widget.element['minusAction'] as String? ?? '';
      final selector = _kind == 'threeState' || _kind == 'multiState';
      final maximum = _kind == 'threeState' ? 2 : ((widget.element['positions'] as num?)?.toInt() ?? 6) - 1;
      child = Column(children: [
        Text(label, style: TextStyle(fontSize: 15, color: color, fontWeight: FontWeight.w700)),
        Expanded(child: Row(children: [button('−', _enabled && (!selector || _requested > 0) && widget.connection!.supportedActions.contains(minus) ? () { _emit(minus); setState(() => _requested--); } : null),
          Expanded(child: FittedBox(fit: BoxFit.scaleDown, child: Column(mainAxisSize: MainAxisSize.min, mainAxisAlignment: MainAxisAlignment.center, children: [
            if (_kind == 'rotary') Icon(Icons.tune, color: color),
            Text(actual == null || actual == '—' ? '—' : actual, style: const TextStyle(fontSize: 24, fontFamily: 'monospace')),
            Text(selector ? 'kért pozíció: ${_requested + 1}/${maximum + 1}' : 'kért lépés: $_requested', style: const TextStyle(color: Colors.white38, fontSize: 10)),
          ]))), button('+', _enabled && (!selector || _requested < maximum) ? () { _emit(_action); setState(() => _requested++); } : null)])),
      ]);
    } else if (_kind == 'slider') {
      child = Column(mainAxisAlignment: MainAxisAlignment.center, children: [Text(label, style: TextStyle(color: color)),
        Slider(value: _steps, min: -5, max: 5, divisions: 10, label: '${_steps.toInt()} lépés',
          onChanged: _enabled ? (value) => setState(() => _steps = value) : null,
          onChangeEnd: _enabled ? (value) async {
            final count = value.toInt(); final action = count < 0 ? widget.element['minusAction'] as String? ?? '' : _action;
            setState(() => _steps = 0);
            for (var i = 0; i < count.abs(); i++) { if (!mounted || !_enabled) break; _emit(action); await Future<void>.delayed(const Duration(milliseconds: 160)); }
          } : null), const Text('RELATÍV LÉPTETÉS', style: TextStyle(fontSize: 11, color: Colors.white38)),
      ]);
    } else {
      final holding = _kind == 'hold';
      final observed = widget.frame?.value(widget.element['field'] as String? ?? '');
      child = Material(color: _pressed ? color.withValues(alpha: .35) : artwork ? Colors.transparent : observed == true ? color.withValues(alpha: .2) : Colors.transparent,
        child: Listener(behavior: HitTestBehavior.opaque,
          onPointerDown: holding ? (event) { if (_holdPointer == null) { _holdPointer = event.pointer; _down(); } } : null,
          onPointerUp: holding ? (event) { if (_holdPointer == event.pointer) { _holdPointer = null; _up(); } } : null,
          onPointerCancel: holding ? (event) { if (_holdPointer == event.pointer) { _holdPointer = null; _up(); } } : null,
          child: InkWell(onTap: !holding && _enabled ? () {
            _emit(_action); setState(() => _requested++);
          } : null, child: Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
            if (_kind == 'icon') Icon(_action == 'lights' ? Icons.lightbulb_outline : _action == 'radio' ? Icons.mic : Icons.sports_motorsports, size: 30, color: _enabled ? color : Colors.white24),
            if(!artwork) Flexible(child:FittedBox(fit:BoxFit.scaleDown,child:Text(label,maxLines:1,textAlign: TextAlign.center, style: TextStyle(color: _enabled ? Colors.white : Colors.white24, fontSize: (widget.element['fontSize'] as num?)?.toDouble() ?? 20, fontWeight: FontWeight.w800, letterSpacing: 1)))),
            if (_kind == 'toggle' && !artwork) Text(observed == null ? 'ÁLLAPOT: —' : observed == true ? 'BE' : 'KI', style: const TextStyle(fontSize: 10, color: Colors.white38)),
          ])))));
    }
    return Tooltip(message: _enabled ? (artwork?'$label · Rekonstrukció, szerkeszthető funkciókiosztás.':label) : 'Ez a funkció ebben a játékban nem érhető el, nincs kiosztva vagy nincs engedélyezve.', child: child);
  }
  @override void dispose() { _renew?.cancel(); if (_pressed) widget.connection?.releaseAll(); super.dispose(); }
}

class LiveDisplay extends StatefulWidget {
  final StudioStore store;
  final BridgeConnection connection;
  final String role;
  final StudioLayout? layout;
  const LiveDisplay({super.key, required this.store, required this.connection, required this.role, this.layout});
  @override State<LiveDisplay> createState() => _LiveDisplayState();
}
class _LiveDisplayState extends State<LiveDisplay> {
  int _page = 0, _mobilePage = 0, _interactionEpoch = 0;
  String? _roleOverride;
  late bool _adaptive, _toolbar;
  final _fullscreen = StudioFullscreen();
  StudioLayout? _cachedPresentation;
  String? _presentationKey;
  String get _role => _roleOverride ?? widget.role;
  @override void initState() {
    super.initState();
    _adaptive=widget.store.prefs.getBool('displayAdaptive') ?? true;
    _toolbar=widget.store.prefs.getBool('displayToolbar') ?? true;
    unawaited(_fullscreen.enter());
    widget.connection.selectProfile(widget.store.vehicleId, layoutId: (widget.layout ?? widget.store.selected(_role)).id);
  }
  void _releaseContext() { widget.connection.releaseAll(); setState(()=>_interactionEpoch++); }
  Future<void> _options() async {
    _releaseContext();
    final choice=await showModalBottomSheet<String>(context:context,isScrollControlled:true,useSafeArea:true,builder:(sheetContext)=>
      SizedBox(height:MediaQuery.sizeOf(sheetContext).height*.78,child:ListView(padding:const EdgeInsets.all(16),children:[
        const ListTile(title:Text('Kijelző beállításai',style:TextStyle(fontWeight:FontWeight.bold,fontSize:22))),
        ListTile(leading:const Icon(Icons.close),title:const Text('Kijelző bezárása'),onTap:()=>Navigator.pop(sheetContext,'close')),
        ListTile(leading:Icon(_adaptive?Icons.check_circle:Icons.crop_free),title:const Text('Adaptív mobilnézet'),subtitle:const Text('Nagyobb műszerek és gombok; kitölti a biztonságos kijelzőterületet.'),onTap:()=>Navigator.pop(sheetContext,'adaptive')),
        ListTile(leading:Icon(!_adaptive?Icons.check_circle:Icons.aspect_ratio),title:const Text('Eredeti arány és elrendezés'),subtitle:const Text('Az autó referenciához rajzolt vagy a saját szerkesztett geometriája.'),onTap:()=>Navigator.pop(sheetContext,'original')),
        ListTile(leading:const Icon(Icons.visibility),title:Text(_toolbar?'Eszköztár elrejtése':'Eszköztár megjelenítése'),onTap:()=>Navigator.pop(sheetContext,'toolbar')),
        if(widget.layout==null) ...[
          const Divider(),
          for(final (role,label) in [('dashboard','Műszerfal'),('panel','Kezelőpanel'),('hybrid','Hibrid')])
            ListTile(leading:Icon(_role==role?Icons.radio_button_checked:Icons.radio_button_off),title:Text(label),onTap:()=>Navigator.pop(sheetContext,'role:$role')),
        ],
        const Divider(),
        if(_role!='dashboard') ListTile(leading:const Icon(Icons.touch_app),title:const Text('Alkalmazás gyorsvezérlői'),subtitle:const Text('Indító, ablaktörlő, rádió és interkom · külön az autó grafikájától.'),onTap:()=>Navigator.pop(sheetContext,'quick')),
        for(final (value,label) in [('auto','Automatikus tájolás'),('portrait','Álló helyzet'),('landscape','Fekvő helyzet')])
          ListTile(leading:const Icon(Icons.screen_rotation),title:Text(label),onTap:()=>Navigator.pop(sheetContext,'orientation:$value')),
      ])));
    if(!mounted || choice==null)return;
    if(choice=='close'){Navigator.pop(context);return;}
    if(choice=='quick'){await _quickControls();return;}
    if(choice=='adaptive' || choice=='original'){
      setState((){_adaptive=choice=='adaptive';_mobilePage=0;});await widget.store.set('displayAdaptive',_adaptive);
    } else if(choice=='toolbar'){
      setState(()=>_toolbar=!_toolbar);await widget.store.set('displayToolbar',_toolbar);
    } else if(choice.startsWith('orientation:')){
      await _fullscreen.orientation(choice.substring(12));
    } else if(choice.startsWith('role:')){
      final role=choice.substring(5);
      await widget.store.set('role',role);await widget.connection.refreshSettings();
      if(!mounted)return;
      setState((){_roleOverride=role;_page=0;_mobilePage=0;_interactionEpoch++;});
      widget.connection.selectProfile(widget.store.vehicleId,layoutId:widget.store.selected(role).id);
    }
  }
  Future<void> _quickControls() async {
    await showModalBottomSheet<void>(context:context,isScrollControlled:true,useSafeArea:true,builder:(sheetContext)=>
      FractionallySizedBox(heightFactor:.8,child:ListView(padding:const EdgeInsets.all(16),children:[
        const ListTile(title:Text('Alkalmazás gyorsvezérlői'),subtitle:Text('Saját alkalmazásvezérlők; nem a gyári középkonzol rekonstrukciójának részei.')),
        for(final (action,label,kind) in [('starter','INDÍTÓ','hold'),('wiper','ABLAKTÖRLŐ','button'),('intercom','INTERKOM','hold'),('radio','RÁDIÓ','hold'),('engineMapUp','MOTOR MAP +','button'),('engineMapDown','MOTOR MAP −','button')])
          Padding(padding:const EdgeInsets.symmetric(vertical:6),child:SizedBox(height:90,child:PanelControl(element:{'id':'quick-$action','kind':kind,'action':action,'label':label,'color':'#8fceab'},frame:widget.connection.telemetry.value,connection:widget.connection))),
      ])));
    widget.connection.releaseAll();
  }
  @override void dispose() {
    widget.connection.releaseAll();unawaited(_fullscreen.leave());super.dispose();
  }
  @override Widget build(BuildContext context) {
    final layout=widget.layout ?? widget.store.selected(_role);
    return Scaffold(backgroundColor:studioColor(layout.data['background'],Colors.black),body:SafeArea(child:LayoutBuilder(builder:(context,constraints){
      final size=Size(constraints.maxWidth,constraints.maxHeight-26-(_toolbar?48:0));
      if(size.width<=0 || size.height<100)return const SizedBox();
      final key='${layout.id}:${layout.data['revision']}:$_page:${size.width}:${size.height}:$_adaptive';
      if(key!=_presentationKey){
        _cachedPresentation=_adaptive?adaptLayout(layout,_page,size):layout;
        _presentationKey=key;
      }
      final presentation=_cachedPresentation!;
      _mobilePage=_mobilePage.clamp(0,presentation.pages.length-1).toInt();
      return AnimatedBuilder(animation:Listenable.merge([widget.connection,widget.connection.telemetry,widget.connection.ticks]),builder:(context,_){
        final frame=widget.connection.telemetry.value;
        return Column(children:[
          if(_toolbar) SizedBox(height:48,child:Row(children:[
            IconButton(tooltip:'Kijelző bezárása',onPressed:()=>Navigator.pop(context),icon:const Icon(Icons.close)),
            Expanded(child:Text(layout.name,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:12,color:Colors.white54))),
            if(layout.pages.length>1 || _adaptive && presentation.pages.length>1) IconButton(tooltip:'Következő oldal',onPressed:(){
              _releaseContext();
              setState((){
                if(_adaptive && _mobilePage+1<presentation.pages.length){_mobilePage++;}
                else{_mobilePage=0;_page=(_page+1)%layout.pages.length;}
              });
            },icon:const Icon(Icons.layers_outlined)),
            IconButton(key:const ValueKey('cockpit-options'),tooltip:'Kijelző beállításai',onPressed:_options,icon:const Icon(Icons.more_horiz)),
          ])),
          Expanded(child:Stack(children:[
            Positioned.fill(child:LayoutCanvas(key:ValueKey('$_role:$_page:$_mobilePage:$_interactionEpoch'),layout:presentation,page:_adaptive?_mobilePage:_page,frame:frame,connection:widget.connection)),
            if(!_toolbar) Positioned(top:0,right:0,child:IconButton.filledTonal(key:const ValueKey('cockpit-options'),tooltip:'Kijelző beállításai',onPressed:_options,icon:const Icon(Icons.more_horiz))),
          ])),
          SizedBox(height:26,child:Center(child:Text(widget.connection.isDemo?'DEMO · SZIMULÁLT ADATOK':frame?.fresh==true?'ÉLŐ TELEMETRIA · ${widget.connection.latencyMs} ms':'NINCS FRISS TELEMETRIA',
            style:TextStyle(fontSize:11,fontWeight:FontWeight.w700,letterSpacing:1,color:widget.connection.isDemo?Colors.amber:frame?.fresh==true?Colors.greenAccent:Colors.amber)))),
        ]);
      });
    })));
  }

}

class DemoBadge extends StatelessWidget {
  const DemoBadge({super.key});
  @override Widget build(BuildContext context) => const Chip(backgroundColor: Color(0xff633b00),
    avatar: Icon(Icons.science_outlined, color: Colors.amber),
    label: Text('DEMO · SZIMULÁLT', style: TextStyle(color: Colors.amber, fontWeight: FontWeight.bold)));
}

class _GridPainter extends CustomPainter {
  const _GridPainter();
  @override void paint(Canvas canvas, Size size) {
    final p = Paint()..color = Colors.white10..strokeWidth = 1;
    for (double x = 0; x < size.width; x += 20) { canvas.drawLine(Offset(x, 0), Offset(x, size.height), p); }
    for (double y = 0; y < size.height; y += 20) { canvas.drawLine(Offset(0, y), Offset(size.width, y), p); }
  }
  @override bool shouldRepaint(covariant _GridPainter oldDelegate) => false;
}
class _LedPainter extends CustomPainter {
  final double? value; final double maximum; final int count; final bool vertical, round; final int rows;
  _LedPainter(this.value, this.maximum, this.count, this.vertical, this.round, this.rows);
  @override void paint(Canvas canvas, Size size) {
    final fraction = value == null || maximum <= 0 ? 0 : (value! / maximum).clamp(0, 1);
    for (var i = 0; i < count; i++) {
      final color = i < count * .6 ? const Color(0xff43e078) : i < count * .8 ? const Color(0xffffd640) : const Color(0xffff3a4b);
      final p = Paint()..color = i < fraction * count ? color : const Color(0xff20252a);
      final columns=(count/rows).ceil();
      final w = rows>1?size.width/columns-4:vertical ? size.width - 4 : size.width / count - 4;
      final h = rows>1?size.height/rows-4:vertical ? size.height / count - 4 : size.height - 4;
      final rect = Rect.fromLTWH(rows>1?(i%columns)*size.width/columns+2:vertical ? 2 : i * size.width / count + 2, rows>1?(i~/columns)*size.height/rows+2:vertical ? size.height - (i + 1) * size.height / count + 2 : 2, math.max(1, w), math.max(1, h));
      if(rows>1 && round){canvas.drawCircle(rect.center,math.max(1,math.min(w,h)/2),p);}
      else{canvas.drawRRect(RRect.fromRectAndRadius(rect, Radius.circular(round ? math.min(w, h) / 2 : 2)), p);}
    }
  }
  @override bool shouldRepaint(covariant _LedPainter oldDelegate) => true;
}
class _AnalogPainter extends CustomPainter {
  final double? value; final double maximum; final Color color; final String text;
  _AnalogPainter(this.value, this.maximum, this.color, this.text);
  @override void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2); final radius = math.min(size.width, size.height) * .42;
    final p = Paint()..style = PaintingStyle.stroke..strokeWidth = 8..color = const Color(0xff303640);
    canvas.drawArc(Rect.fromCircle(center: center, radius: radius), math.pi * .75, math.pi * 1.5, false, p);
    if (value != null) {
      final angle = math.pi * .75 + (value! / maximum).clamp(0, 1) * math.pi * 1.5;
      p..color = color..strokeWidth = 5;
      canvas.drawLine(center, center + Offset(math.cos(angle), math.sin(angle)) * radius * .85, p);
    }
    final painter = TextPainter(text: TextSpan(text: text, style: const TextStyle(color: Colors.white, fontSize: 34, fontFamily: 'monospace')), textDirection: TextDirection.ltr)..layout();
    painter.paint(canvas, center + Offset(-painter.width / 2, radius * .55));
  }
  @override bool shouldRepaint(covariant _AnalogPainter oldDelegate) => true;
}
class _GForcePainter extends CustomPainter {
  final double? x, z; final Color color;
  _GForcePainter(this.x, this.z, this.color);
  @override void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2); final r = math.min(size.width, size.height) * .4;
    final p = Paint()..color = Colors.white24..style = PaintingStyle.stroke;
    canvas.drawCircle(center, r, p); canvas.drawCircle(center, r / 2, p);
    canvas.drawLine(center - Offset(r, 0), center + Offset(r, 0), p); canvas.drawLine(center - Offset(0, r), center + Offset(0, r), p);
    if (x != null && z != null) { p..style = PaintingStyle.fill..color = color; canvas.drawCircle(center + Offset(x!.clamp(-3, 3) / 3 * r, -z!.clamp(-3, 3) / 3 * r), 7, p); }
  }
  @override bool shouldRepaint(covariant _GForcePainter oldDelegate) => true;
}
