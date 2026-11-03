import 'dart:async';
import 'dart:io' show Platform;
import 'dart:math' as math;
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'connection.dart';
import 'models.dart';

/// Cockpit-wide lighting state (day / night backlighting). Persisted by the caller.
class CockpitLighting {
  static final night = ValueNotifier<bool>(false);
}

/// Short mechanical switch sounds, synthesised for this project (no third-party recordings).
/// Every player is created and loaded once at start-up so a tap never waits for disk I/O.
class SwitchSounds {
  SwitchSounds._();
  static final SwitchSounds instance = SwitchSounds._();
  static const files = <String, String>{
    'metalOn': 'sounds/metal_toggle_on.wav',
    'metalOff': 'sounds/metal_toggle_off.wav',
    'plastic': 'sounds/plastic_button.wav',
    'latch': 'sounds/latching_switch.wav',
    'rotary': 'sounds/rotary_detent.wav',
    'guard': 'sounds/safety_cover.wav',
    'starter': 'sounds/starter_button.wav',
  };
  double volume = .8;
  bool enabled = true;
  final Map<String, List<AudioPlayer>> _players = {};
  final Map<String, int> _next = {};
  bool _loading = false;
  static bool get available => !kIsWeb && !Platform.environment.containsKey('FLUTTER_TEST');

  Future<void> preload() async {
    if (!available || _loading) return;
    _loading = true;
    for (final entry in files.entries) {
      try {
        final players = <AudioPlayer>[];
        for (var i = 0; i < 3; i++) {
          final player = AudioPlayer(playerId: 'switch-${entry.key}-$i');
          await player.setReleaseMode(ReleaseMode.stop);
          await player.setPlayerMode(PlayerMode.lowLatency);
          await player.setSource(AssetSource(entry.value));
          players.add(player);
        }
        _players[entry.key] = players;
      } catch (_) {
        // Sound is optional feedback; the control and its command keep working without it.
      }
    }
  }

  void play(String? kind) {
    if (!available || !enabled || volume <= 0 || kind == null) return;
    final players = _players[kind];
    if (players == null || players.isEmpty) return;
    final index = (_next[kind] ?? 0) % players.length;
    _next[kind] = index + 1;
    final player = players[index];
    unawaited(() async {
      try {
        await player.stop();
        await player.setVolume(volume);
        await player.resume();
      } catch (_) {
        // A failed click sound must never block or fail the control command.
      }
    }());
  }
}

/// The four separately reported stages of a control command, plus local states.
enum LedStage { off, requested, sent, bridgeAck, confirmed, unknown, error }

String ledCaption(LedStage stage) => switch (stage) {
  LedStage.off => 'KI',
  LedStage.requested => 'KÉRT',
  LedStage.sent => 'ELKÜLDVE',
  LedStage.bridgeAck => 'BRIDGE OK · FELTÉTELEZETT',
  LedStage.confirmed => 'JÁTÉK IGAZOLTA',
  LedStage.unknown => 'ÁLLAPOT ISMERETLEN',
  LedStage.error => 'HIBA',
};

/// Derives the LED stage from the command log and telemetry. A sent or executed command is never
/// shown as confirmed: only a valid telemetry field can confirm the in-game state.
LedStage ledStageFor({required BridgeConnection? connection, required String? commandId,
    required bool requestedOn, required TelemetryFrame? frame, String? field, bool enabled = true}) {
  if (field != null && field.isNotEmpty) {
    final actual = frame?.value(field);
    if (actual is bool) return actual ? LedStage.confirmed : LedStage.off;
    if (actual is num) return actual != 0 ? LedStage.confirmed : LedStage.off;
  }
  if (!enabled) return LedStage.unknown;
  if (commandId == null || connection == null) return requestedOn ? LedStage.requested : LedStage.off;
  final entry = connection.commandHistory.where((c) => c['id'] == commandId).lastOrNull;
  if (entry == null) return requestedOn ? LedStage.requested : LedStage.off;
  return switch (entry['stage']) {
    'rejected' || 'timeout' => LedStage.error,
    'sent' || 'received' => requestedOn ? LedStage.sent : LedStage.off,
    'executed' || 'simulated' || 'released' => requestedOn ? LedStage.bridgeAck : LedStage.off,
    _ => requestedOn ? LedStage.requested : LedStage.off,
  };
}

Color _hex(Object? value, Color fallback) {
  if (value is! String) return fallback;
  final raw = value.replaceFirst('#', '');
  final parsed = int.tryParse(raw, radix: 16);
  if (parsed == null) return fallback;
  return Color(raw.length <= 6 ? 0xff000000 | parsed : parsed);
}

/// Mechanical button-box control: rocker, push button, guarded switch, rotary switch, cycle button.
class PremiumControl extends StatefulWidget {
  final Map<String, dynamic> element;
  final TelemetryFrame? frame;
  final BridgeConnection? connection;
  const PremiumControl({super.key, required this.element, this.frame, this.connection});
  @override State<PremiumControl> createState() => _PremiumControlState();
}

class _PremiumControlState extends State<PremiumControl> with TickerProviderStateMixin {
  late final AnimationController _motion = AnimationController(vsync: this, duration: const Duration(milliseconds: 110));
  late final AnimationController _cover = AnimationController(vsync: this, duration: const Duration(milliseconds: 260));
  late final AnimationController _pulse = AnimationController(vsync: this, duration: const Duration(milliseconds: 900));
  bool _on = false, _pressed = false, _coverOpen = false;
  int _position = 0;
  String? _commandId;
  Timer? _renew, _autoClose;
  int? _pointer;

  Map<String, dynamic> get e => widget.element;
  String get kind => e['kind'] as String;
  String get action => e['action'] as String? ?? '';
  String? get minusAction => e['minusAction'] as String?;
  bool get hold => e['hold'] == true;
  List<String> get states => (e['states'] as List?)?.cast<String>() ?? const [];
  int get positions => (e['positions'] as num?)?.toInt() ?? (states.isNotEmpty ? states.length : 6);
  bool _can(String? name) => name != null && name.isNotEmpty && widget.connection?.mayControl == true &&
      widget.connection!.supportedActions.contains(name);
  bool get enabled => _can(action);

  @override void initState() {
    super.initState();
    _position = (e['initialPosition'] as num?)?.toInt() ?? 0;
    widget.connection?.addListener(_changed);
  }
  @override void didUpdateWidget(covariant PremiumControl oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.connection != widget.connection) {
      oldWidget.connection?.removeListener(_changed);
      widget.connection?.addListener(_changed);
    }
    if (_pressed && (!enabled || oldWidget.element['id'] != e['id'])) { _release(); }
  }
  void _changed() { if (mounted) setState(() {}); }

  void _feedback(String? sound, {bool heavy = false}) {
    SwitchSounds.instance.play(sound ?? e['sound'] as String?);
    if (widget.connection?.store.haptic != false) {
      unawaited(heavy ? HapticFeedback.heavyImpact() : kind == 'rotarySwitch' ? HapticFeedback.selectionClick() : HapticFeedback.mediumImpact());
    }
  }
  void _send(String name, [String phase = 'press']) {
    final connection = widget.connection;
    if (connection == null) return;
    _commandId = connection.command(name, phase: phase);
    _syncPulse();
  }
  void _syncPulse() {
    final stage = _stage();
    final animate = stage == LedStage.sent || stage == LedStage.requested || stage == LedStage.error;
    if (animate && !_pulse.isAnimating) { _pulse.repeat(); }
    else if (!animate && _pulse.isAnimating) { _pulse.stop(); _pulse.value = 0; }
  }

  LedStage _stage() => ledStageFor(connection: widget.connection, commandId: _commandId,
      requestedOn: kind == 'pushButton' && !hold ? _commandId != null && _recent() : kind == 'cycleButton' || kind == 'rotarySwitch' ? _position != 0 : _on || _pressed,
      frame: widget.frame, field: e['field'] as String?, enabled: enabled);
  bool _recent() {
    final entry = widget.connection?.commandHistory.where((c) => c['id'] == _commandId).lastOrNull;
    final at = (entry?['requestedAtMs'] as num?)?.toInt();
    return at != null && DateTime.now().millisecondsSinceEpoch - at < 1500;
  }

  // ---- interactions -------------------------------------------------------------------------
  void _tapRocker() {
    if (!enabled) return;
    setState(() => _on = !_on);
    _on ? _motion.forward() : _motion.reverse();
    _feedback(_on ? 'metalOn' : 'metalOff');
    _send(action);
  }
  void _pushDown(PointerDownEvent event) {
    if (!enabled || _pointer != null) return;
    _pointer = event.pointer;
    setState(() => _pressed = true);
    _motion.forward();
    _feedback(action == 'starter' ? 'starter' : null, heavy: action == 'starter');
    if (hold) {
      _send(action, 'down');
      _renew?.cancel();
      _renew = Timer.periodic(const Duration(seconds: 1), (_) => widget.connection?.command(action, phase: 'down'));
    }
  }
  void _pushUp(PointerEvent event, {bool cancelled = false}) {
    if (_pointer != event.pointer) return;
    _pointer = null;
    if (hold) { _release(); return; }
    _motion.reverse();
    setState(() => _pressed = false);
    if (cancelled) return;
    if (kind == 'cycleButton') { _position = (_position + 1) % math.max(1, positions); }
    _send(action);
  }
  void _release() {
    _renew?.cancel(); _renew = null;
    if (_pressed && hold) widget.connection?.command(action, phase: 'up');
    _pressed = false; _pointer = null;
    _motion.reverse();
    if (mounted) setState(() {});
  }
  void _toggleCover() {
    setState(() => _coverOpen = !_coverOpen);
    _coverOpen ? _cover.forward() : _cover.reverse();
    _feedback('guard');
    _autoClose?.cancel();
    if (_coverOpen) {
      _autoClose = Timer(const Duration(seconds: 6), () { if (mounted && _coverOpen) _toggleCover(); });
    }
  }
  void _guardedSwitch() {
    if (!_coverOpen || !enabled) return;
    _autoClose?.cancel();
    setState(() => _on = !_on);
    _on ? _motion.forward() : _motion.reverse();
    _feedback(_on ? 'metalOn' : 'metalOff');
    _send(action);
    _autoClose = Timer(const Duration(seconds: 6), () { if (mounted && _coverOpen) _toggleCover(); });
  }
  void _rotate(int direction) {
    final name = direction > 0 ? action : minusAction;
    if (!_can(name)) return;
    final next = _position + direction;
    if (next < 0 || next >= positions) return;
    setState(() => _position = next);
    _feedback('rotary');
    _send(name!);
  }

  @override Widget build(BuildContext context) {
    final label = e['label'] as String? ?? '';
    final night = CockpitLighting.night.value;
    final stage = _stage();
    final demo = widget.connection?.isDemo == true || widget.frame?.isDemo == true;
    WidgetsBinding.instance.addPostFrameCallback((_) { if (mounted) _syncPulse(); });
    final led = _hex(e['ledColor'], const Color(0xff3cff7a));
    final accent = _hex(e['color'], const Color(0xffe8e8e8));
    final material = e['material'] as String? ?? 'plastic';
    Widget face;
    switch (kind) {
      case 'rocker':
        face = GestureDetector(behavior: HitTestBehavior.opaque, onTap: _tapRocker,
          child: AnimatedBuilder(animation: Listenable.merge([_motion, _pulse]), builder: (context, _) => CustomPaint(
            painter: _RockerPainter(_motion.value, stage, led, accent, night, material, _pulse.value, e['engraving'] as String? ?? 'I  O'))));
      case 'guarded':
        face = AnimatedBuilder(animation: Listenable.merge([_motion, _cover, _pulse]), builder: (context, _) => Stack(fit: StackFit.expand, children: [
          CustomPaint(painter: _RockerPainter(_motion.value, stage, led, accent, night, 'alu', _pulse.value, e['engraving'] as String? ?? '')),
          Positioned.fill(child: GestureDetector(behavior: HitTestBehavior.opaque, onTap: _coverOpen ? _guardedSwitch : _toggleCover)),
          Positioned.fill(child: IgnorePointer(child: CustomPaint(painter: _CoverPainter(_cover.value, _hex(e['coverColor'], const Color(0xffd0202a)), night)))),
          if (_coverOpen) Positioned(left: 0, right: 0, top: 0, height: 34, child: GestureDetector(behavior: HitTestBehavior.opaque, onTap: _toggleCover,
            child: const Center(child: Icon(Icons.keyboard_arrow_down, size: 26, color: Colors.white70)))),
        ]));
      case 'rotarySwitch':
        face = GestureDetector(behavior: HitTestBehavior.opaque,
          onTapUp: (details) {
            final box = context.findRenderObject() as RenderBox?;
            final width = box?.size.width ?? 1;
            _rotate(details.localPosition.dx >= width / 2 ? 1 : -1);
          },
          onHorizontalDragEnd: (details) { final v = details.primaryVelocity ?? 0; if (v.abs() > 80) _rotate(v > 0 ? 1 : -1); },
          child: TweenAnimationBuilder<double>(tween: Tween(end: _position.toDouble()), duration: const Duration(milliseconds: 140), curve: Curves.easeOutBack,
            builder: (context, value, _) => CustomPaint(painter: _RotaryPainter(value, positions, states, accent, night, enabled, material))));
      default: // pushButton, cycleButton
        face = Listener(behavior: HitTestBehavior.opaque, onPointerDown: _pushDown, onPointerUp: _pushUp,
          onPointerCancel: (event) => _pushUp(event, cancelled: true),
          child: AnimatedBuilder(animation: Listenable.merge([_motion, _pulse]), builder: (context, _) => CustomPaint(
            painter: material == 'touch' || material == 'outline' || material == 'label'
              ? _PanelKeyPainter(_motion.value, stage, led, accent, night, material, _pulse.value, e['engraving'] as String? ?? '',
                  panelIcons[e['icon']], (e['leds'] as num?)?.toInt() ?? 1, kind == 'cycleButton' ? _position : -1)
              : _PushPainter(_motion.value, stage, led, accent, night, material, _pulse.value,
                  e['engraving'] as String? ?? '', e['ring'] != false, e['shape'] == 'square'))));
    }
    final stateText = kind == 'cycleButton' && states.isNotEmpty ? 'kért: ${states[_position % states.length]}'
        : kind == 'rotarySwitch' ? 'kért: ${states.isNotEmpty ? states[_position.clamp(0, states.length - 1)] : _position + 1}'
        : demo && stage == LedStage.confirmed ? 'DEMO · SZIMULÁLT ÁLLAPOT' : ledCaption(stage);
    final captionColor = stage == LedStage.error ? const Color(0xffff4d4d) : stage == LedStage.confirmed ? const Color(0xff7dff9a) : Colors.white54;
    return Semantics(button: true, enabled: enabled, label: label,
      child: Tooltip(message: enabled ? '$label · ${ledCaption(stage)}' : '$label · nincs kiosztva, nincs engedélyezve vagy nincs kapcsolat',
        child: Opacity(opacity: enabled ? 1 : .55, child: LayoutBuilder(builder: (context, constraints) {
          // Very small presentations (hybrid / adaptive scaling) show the mechanical face only.
          if (constraints.maxHeight < 110 || e['caption'] == false) return SizedBox.expand(child: face);
          return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          Expanded(child: face),
          const SizedBox(height: 4),
          SizedBox(height: 22, child: FittedBox(fit: BoxFit.scaleDown, child: Text(label.toUpperCase(), maxLines: 1,
            style: TextStyle(fontFamily: 'OemCondensed', fontWeight: FontWeight.w600, fontSize: 20, letterSpacing: 1.5,
              color: night ? const Color(0xffffe0a0) : const Color(0xffe6e6e6),
              shadows: night ? const [Shadow(color: Color(0xaaffb040), blurRadius: 8)] : const [Shadow(color: Colors.black, offset: Offset(0, 1))])))),
          SizedBox(height: 16, child: FittedBox(fit: BoxFit.scaleDown, child: Text(stateText, maxLines: 1,
            style: TextStyle(fontSize: 13, letterSpacing: .8, color: captionColor)))),
        ]);
        }))));
  }

  @override void dispose() {
    widget.connection?.removeListener(_changed);
    if (_pressed && hold) widget.connection?.command(action, phase: 'up');
    _renew?.cancel(); _autoClose?.cancel();
    _motion.dispose(); _cover.dispose(); _pulse.dispose();
    super.dispose();
  }
}

// ---- painting --------------------------------------------------------------------------------

Paint _materialPaint(String material, Rect rect, bool night) {
  final List<Color> colors = switch (material) {
    'brushed' => [const Color(0xffd9dde2), const Color(0xff9aa0a8), const Color(0xffc9ced4), const Color(0xff7e848c)],
    'alu' => [const Color(0xffb8bcc2), const Color(0xff8b9097)],
    'carbon' => [const Color(0xff2b2e33), const Color(0xff131518)],
    'rubber' => [const Color(0xff2a2a2a), const Color(0xff141414)],
    'glass' => [const Color(0xff1d2630), const Color(0xff0b0f14)],
    _ => [const Color(0xff3a3d42), const Color(0xff1c1e21)],
  };
  final shaded = night ? colors.map((c) => Color.lerp(c, Colors.black, .55)!).toList() : colors;
  return Paint()..shader = LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: shaded).createShader(rect);
}

void _screw(Canvas canvas, Offset center, double radius, bool night) {
  final rect = Rect.fromCircle(center: center, radius: radius);
  canvas.drawCircle(center, radius, Paint()..shader = RadialGradient(colors: [
    night ? const Color(0xff606368) : const Color(0xffe8eaed), night ? const Color(0xff2a2c30) : const Color(0xff6c7178)]).createShader(rect));
  final slot = Paint()..color = const Color(0xff202226)..strokeWidth = radius * .28..strokeCap = StrokeCap.round;
  canvas.drawLine(center + Offset(-radius * .6, -radius * .25), center + Offset(radius * .6, radius * .25), slot);
}

void _bezel(Canvas canvas, Rect rect, double radius, bool night, {bool screws = true}) {
  final outer = RRect.fromRectAndRadius(rect, Radius.circular(radius));
  canvas.drawRRect(outer.shift(const Offset(0, 4)), Paint()..color = Colors.black.withValues(alpha: .55)..maskFilter = const MaskFilter.blur(BlurStyle.normal, 6));
  canvas.drawRRect(outer, _materialPaint('brushed', rect, night));
  canvas.drawRRect(outer.deflate(rect.shortestSide * .05), Paint()..color = night ? const Color(0xff0c0d0f) : const Color(0xff1a1c1f));
  if (screws) {
    final s = rect.shortestSide * .045;
    for (final c in [rect.topLeft + Offset(s * 2, s * 2), rect.topRight + Offset(-s * 2, s * 2),
      rect.bottomLeft + Offset(s * 2, -s * 2), rect.bottomRight + Offset(-s * 2, -s * 2)]) { _screw(canvas, c, s, night); }
  }
}

void _led(Canvas canvas, Offset center, double radius, LedStage stage, Color color, double pulse, bool night) {
  final lens = Rect.fromCircle(center: center, radius: radius);
  canvas.drawCircle(center, radius * 1.25, Paint()..color = const Color(0xff0a0a0a));
  final blink = (math.sin(pulse * math.pi * 2) + 1) / 2;
  final (Color base, double level, bool hollow) = switch (stage) {
    LedStage.confirmed => (color, 1.0, false),
    LedStage.bridgeAck => (color, .55, true),
    LedStage.sent => (const Color(0xffffb020), .35 + .5 * blink, false),
    LedStage.requested => (const Color(0xffffb020), .25 + .3 * blink, true),
    LedStage.error => (const Color(0xffff2020), blink > .5 ? 1.0 : .1, false),
    LedStage.unknown => (const Color(0xff8a8f96), .18, true),
    LedStage.off => (color, 0.0, false),
  };
  final dark = Color.lerp(base, Colors.black, .82)!;
  final lit = Color.lerp(dark, base, level)!;
  if (level > .3) {
    canvas.drawCircle(center, radius * (night ? 3.2 : 2.3), Paint()..color = base.withValues(alpha: .38 * level)..maskFilter = MaskFilter.blur(BlurStyle.normal, radius * 1.4));
  }
  canvas.drawCircle(center, radius, Paint()..shader = RadialGradient(center: const Alignment(-.3, -.35), colors: [
    Color.lerp(lit, Colors.white, level * .6)!, lit, Color.lerp(lit, Colors.black, .5)!], stops: const [0, .45, 1]).createShader(lens));
  if (hollow) {
    canvas.drawCircle(center, radius * .42, Paint()..color = const Color(0xdd0a0a0a));
  }
  canvas.drawCircle(center, radius, Paint()..style = PaintingStyle.stroke..strokeWidth = radius * .14..color = Colors.white24);
}

void _engrave(Canvas canvas, String text, Offset center, double size, bool night, {Color? color}) {
  if (text.isEmpty) return;
  final style = TextStyle(fontFamily: 'OemCondensed', fontWeight: FontWeight.w600, fontSize: size, letterSpacing: 1,
    color: color ?? (night ? const Color(0xffffd9a0) : const Color(0xffdcdcdc)),
    shadows: night ? [const Shadow(color: Color(0xccff9a30), blurRadius: 6)] : [const Shadow(color: Colors.black, offset: Offset(0, -1))]);
  final painter = TextPainter(text: TextSpan(text: text, style: style), textDirection: TextDirection.ltr, textAlign: TextAlign.center)..layout();
  painter.paint(canvas, center - Offset(painter.width / 2, painter.height / 2));
}

class _RockerPainter extends CustomPainter {
  final double t, pulse; final LedStage stage; final Color led, accent; final bool night; final String material, engraving;
  _RockerPainter(this.t, this.stage, this.led, this.accent, this.night, this.material, this.pulse, this.engraving);
  @override void paint(Canvas canvas, Size size) {
    final w = math.min(size.width, size.height * .62);
    final rect = Rect.fromCenter(center: Offset(size.width / 2, size.height * .5), width: w, height: size.height * .96);
    _bezel(canvas, rect, w * .12, night);
    final well = Rect.fromCenter(center: rect.center + Offset(0, rect.height * .08), width: w * .62, height: rect.height * .62);
    canvas.drawRRect(RRect.fromRectAndRadius(well, Radius.circular(w * .06)), Paint()..color = const Color(0xff050506));
    // Paddle: lit face moves from top half (OFF) to bottom half (ON) as it tilts.
    final tilt = (t - .5) * 2; // -1 = OFF (top pressed in), +1 = ON
    final paddle = well.deflate(w * .035);
    final paint = Paint()..shader = LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [
      Color.lerp(const Color(0xff4a4d52), const Color(0xff1b1c1f), (1 - tilt) / 2 * .9)!,
      const Color(0xff2a2c30),
      Color.lerp(const Color(0xff4a4d52), const Color(0xff1b1c1f), (1 + tilt) / 2 * .9)!,
    ]).createShader(paddle);
    canvas.drawRRect(RRect.fromRectAndRadius(paddle, Radius.circular(w * .05)), paint);
    final ridge = paddle.center.dy + tilt * paddle.height * .12;
    canvas.drawLine(Offset(paddle.left + 4, ridge), Offset(paddle.right - 4, ridge), Paint()..color = Colors.black54..strokeWidth = 2);
    final parts = engraving.split(RegExp(r'\s{2,}'));
    _engrave(canvas, parts.isNotEmpty ? parts.first : '', Offset(paddle.center.dx, paddle.top + paddle.height * .25), w * .13, night);
    if (parts.length > 1) _engrave(canvas, parts[1], Offset(paddle.center.dx, paddle.bottom - paddle.height * .25), w * .13, night);
    _led(canvas, Offset(rect.center.dx, rect.top + rect.height * .12), w * .07, stage, led, pulse, night);
  }
  @override bool shouldRepaint(covariant _RockerPainter old) => old.t != t || old.stage != stage || old.pulse != pulse || old.night != night;
}

class _CoverPainter extends CustomPainter {
  final double open; final Color color; final bool night;
  _CoverPainter(this.open, this.color, this.night);
  @override void paint(Canvas canvas, Size size) {
    final w = math.min(size.width, size.height * .62);
    final rect = Rect.fromCenter(center: Offset(size.width / 2, size.height * .5), width: w * .86, height: size.height * .9);
    // Hinge at the top: the cover rotates up and away (perspective foreshortening).
    final visible = (1 - open).clamp(0.0, 1.0);
    if (visible <= .02) {
      final hinge = Rect.fromLTWH(rect.left, rect.top - 6, rect.width, 14);
      canvas.drawRRect(RRect.fromRectAndRadius(hinge, const Radius.circular(4)), Paint()..color = Color.lerp(color, Colors.black, .35)!);
      return;
    }
    final cover = Rect.fromLTWH(rect.left, rect.top, rect.width, rect.height * visible);
    final base = night ? Color.lerp(color, Colors.black, .45)! : color;
    canvas.drawRRect(RRect.fromRectAndRadius(cover.shift(const Offset(0, 5)), Radius.circular(w * .1)), Paint()..color = Colors.black45..maskFilter = const MaskFilter.blur(BlurStyle.normal, 5));
    canvas.drawRRect(RRect.fromRectAndRadius(cover, Radius.circular(w * .1)), Paint()..shader = LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter,
      colors: [base.withValues(alpha: .92), Color.lerp(base, Colors.black, .4)!.withValues(alpha: .92)]).createShader(cover));
    canvas.drawRRect(RRect.fromRectAndRadius(cover.deflate(5), Radius.circular(w * .08)), Paint()..style = PaintingStyle.stroke..strokeWidth = 2..color = Colors.white30);
    if (visible > .5) {
      // Diagonal warning stripes stamped into the cover.
      canvas.save(); canvas.clipRRect(RRect.fromRectAndRadius(cover.deflate(8), Radius.circular(w * .07)));
      final stripe = Paint()..color = Colors.black.withValues(alpha: .25)..strokeWidth = w * .06;
      for (var x = cover.left - cover.height; x < cover.right; x += w * .16) {
        canvas.drawLine(Offset(x, cover.bottom), Offset(x + cover.height, cover.top), stripe);
      }
      canvas.restore();
      _engrave(canvas, 'NYITÁS', Offset(cover.center.dx, cover.bottom - 18), w * .1, night, color: Colors.white);
    }
  }
  @override bool shouldRepaint(covariant _CoverPainter old) => old.open != open || old.night != night;
}

class _PushPainter extends CustomPainter {
  final double t, pulse; final LedStage stage; final Color led, accent; final bool night, ring, square; final String material, engraving;
  _PushPainter(this.t, this.stage, this.led, this.accent, this.night, this.material, this.pulse, this.engraving, this.ring, this.square);
  @override void paint(Canvas canvas, Size size) {
    final side = math.min(size.width, size.height);
    final rect = Rect.fromCenter(center: Offset(size.width / 2, size.height / 2), width: side * .96, height: side * .96);
    _bezel(canvas, rect, square ? side * .1 : side * .48, night, screws: square);
    final depth = side * .05 * (1 - t);
    final cap = rect.deflate(side * (ring ? .2 : .14));
    final capShape = square ? RRect.fromRectAndRadius(cap, Radius.circular(side * .07)) : RRect.fromRectAndRadius(cap, Radius.circular(cap.width / 2));
    if (ring) {
      // Illuminated ring around the cap follows the LED stage.
      final lit = stage == LedStage.confirmed || stage == LedStage.bridgeAck || stage == LedStage.sent || stage == LedStage.error;
      final ringColor = stage == LedStage.error ? const Color(0xffff2020) : stage == LedStage.sent ? const Color(0xffffb020) : led;
      final level = stage == LedStage.confirmed ? 1.0 : stage == LedStage.bridgeAck ? .55 : lit ? .4 + .5 * ((math.sin(pulse * math.pi * 2) + 1) / 2) : 0.0;
      final ringRect = rect.deflate(side * .12);
      final ringShape = square ? RRect.fromRectAndRadius(ringRect, Radius.circular(side * .08)) : RRect.fromRectAndRadius(ringRect, Radius.circular(ringRect.width / 2));
      if (level > 0) canvas.drawRRect(ringShape, Paint()..color = ringColor.withValues(alpha: .5 * level)..maskFilter = MaskFilter.blur(BlurStyle.normal, side * .05));
      canvas.drawRRect(ringShape, Paint()..style = PaintingStyle.stroke..strokeWidth = side * .04
        ..color = Color.lerp(const Color(0xff1a1a1a), ringColor, level)!);
    }
    // Shadow under the cap shrinks as the button travels in.
    canvas.drawRRect(capShape.shift(Offset(0, depth + 1)), Paint()..color = Colors.black.withValues(alpha: .7)..maskFilter = MaskFilter.blur(BlurStyle.normal, 2 + depth));
    final face = capShape.shift(Offset(0, side * .03 * t));
    final capColor = accent;
    canvas.drawRRect(face, Paint()..shader = RadialGradient(center: const Alignment(-.25, -.4), radius: 1.1, colors: [
      Color.lerp(capColor, Colors.white, night ? .05 : .28)!, Color.lerp(capColor, Colors.black, night ? .65 : .25)!,
      Color.lerp(capColor, Colors.black, night ? .8 : .55)!]).createShader(face.outerRect));
    if (material == 'rubber') {
      // Fine grain on rubber caps.
      final grain = Paint()..color = Colors.black.withValues(alpha: .08)..strokeWidth = 1;
      for (var y = face.top + 4; y < face.bottom; y += 4) { canvas.drawLine(Offset(face.left + 4, y), Offset(face.right - 4, y), grain); }
    }
    canvas.drawRRect(face, Paint()..style = PaintingStyle.stroke..strokeWidth = 1.5..color = Colors.white.withValues(alpha: night ? .08 : .25));
    _engrave(canvas, engraving, face.center, side * (engraving.length > 5 ? .1 : .14), night,
      color: accent.computeLuminance() > .5 ? const Color(0xff1a1a1a) : null);
    if (!ring) _led(canvas, Offset(rect.right - side * .14, rect.top + side * .14), side * .045, stage, led, pulse, night);
  }
  @override bool shouldRepaint(covariant _PushPainter old) => old.t != t || old.stage != stage || old.pulse != pulse || old.night != night;
}

class _RotaryPainter extends CustomPainter {
  final double position; final int positions; final List<String> labels; final Color accent; final bool night, enabled; final String material;
  _RotaryPainter(this.position, this.positions, this.labels, this.accent, this.night, this.enabled, this.material);
  @override void paint(Canvas canvas, Size size) {
    final side = math.min(size.width, size.height);
    final center = Offset(size.width / 2, size.height / 2);
    final rect = Rect.fromCircle(center: center, radius: side * .48);
    _bezel(canvas, rect, side * .1, night);
    final sweep = math.pi * 1.5;
    final start = math.pi * .75;
    double angleFor(double p) => positions <= 1 ? -math.pi / 2 : start + sweep * p / (positions - 1);
    for (var i = 0; i < positions; i++) {
      final a = angleFor(i.toDouble());
      final inner = center + Offset(math.cos(a), math.sin(a)) * side * .3;
      final outer = center + Offset(math.cos(a), math.sin(a)) * side * .36;
      final active = i == position.round();
      canvas.drawLine(inner, outer, Paint()..strokeWidth = active ? 3 : 1.5..color = active ? accent : Colors.white38);
      final text = labels.length > i ? labels[i] : '${i + 1}';
      _engrave(canvas, text, center + Offset(math.cos(a), math.sin(a)) * side * .42, side * .065, night,
        color: active ? accent : (night ? const Color(0xffc8a878) : Colors.white60));
    }
    final knob = Rect.fromCircle(center: center, radius: side * .25);
    canvas.drawCircle(center + const Offset(0, 4), side * .25, Paint()..color = Colors.black54..maskFilter = const MaskFilter.blur(BlurStyle.normal, 6));
    canvas.drawCircle(center, side * .25, Paint()..shader = SweepGradient(colors: night
      ? const [Color(0xff3a3c40), Color(0xff15161a), Color(0xff2c2e33), Color(0xff15161a), Color(0xff3a3c40)]
      : const [Color(0xffd6d9de), Color(0xff6f747b), Color(0xffc3c7cd), Color(0xff6f747b), Color(0xffd6d9de)]).createShader(knob));
    // Knurled edge.
    final knurl = Paint()..color = Colors.black26..strokeWidth = 1.2;
    for (var i = 0; i < 48; i++) {
      final a = i * math.pi * 2 / 48;
      canvas.drawLine(center + Offset(math.cos(a), math.sin(a)) * side * .22, center + Offset(math.cos(a), math.sin(a)) * side * .25, knurl);
    }
    canvas.drawCircle(center, side * .17, Paint()..color = night ? const Color(0xff1d1f23) : const Color(0xff2b2e33));
    final pointer = angleFor(position);
    canvas.drawLine(center + Offset(math.cos(pointer), math.sin(pointer)) * side * .04, center + Offset(math.cos(pointer), math.sin(pointer)) * side * .2,
      Paint()..strokeWidth = side * .035..strokeCap = StrokeCap.round..color = enabled ? accent : Colors.white30);
  }
  @override bool shouldRepaint(covariant _RotaryPainter old) => old.position != position || old.night != night || old.enabled != enabled;
}


/// Symbols used on the reference panels (rendered from the bundled Material icon font).
const panelIcons = <String, IconData>{
  'phone': Icons.call, 'phoneEnd': Icons.call_end, 'hazard': Icons.change_history, 'fog': Icons.foggy,
  'volumeUp': Icons.volume_up, 'volumeDown': Icons.volume_down, 'all': Icons.movie_creation_outlined,
  'horn': Icons.campaign, 'demist': Icons.waves, 'power': Icons.flash_on, 'windowUp': Icons.arrow_upward,
  'windowDown': Icons.arrow_downward, 'light': Icons.light_mode, 'highBeam': Icons.highlight, 'wiper': Icons.water_drop,
  'left': Icons.arrow_back, 'right': Icons.arrow_forward, 'fire': Icons.local_fire_department, 'fan': Icons.air,
};

/// Flat panel keys as seen on the cars: navy touch keys (Škoda console) and black keys with a coloured
/// outline and LED dots (Peugeot Sport switch panel).
class _PanelKeyPainter extends CustomPainter {
  final double t, pulse; final LedStage stage; final Color led, accent; final bool night; final String material, engraving;
  final IconData? icon; final int leds, position;
  _PanelKeyPainter(this.t, this.stage, this.led, this.accent, this.night, this.material, this.pulse, this.engraving, this.icon, this.leds, this.position);
  @override void paint(Canvas canvas, Size size) {
    final rect = (Offset.zero & size).deflate(math.min(size.width, size.height) * .04);
    final side = math.min(rect.width, rect.height);
    final radius = Radius.circular(side * (material == 'touch' ? .16 : .12));
    final pressed = t;
    final lit = stage == LedStage.confirmed || stage == LedStage.bridgeAck || stage == LedStage.sent || stage == LedStage.error;
    final blink = (math.sin(pulse * math.pi * 2) + 1) / 2;
    final glowColor = stage == LedStage.error ? const Color(0xffff2020) : stage == LedStage.sent ? const Color(0xffffb020) : led;
    final inkLight = night ? const Color(0xffffe6b8) : const Color(0xffdfe3e8);
    // Outline keys are black faces: their engraving stays light whatever the rim colour (208 white/yellow keys).
    final dark = material == 'label' || material != 'outline' && accent.computeLuminance() > .45;
    final ink = dark ? (night ? const Color(0xff2a2410) : const Color(0xff1c1f1a)) : inkLight;
    if (material == 'touch' || material == 'label') {
      final base = night ? Color.lerp(accent, Colors.black, .45)! : accent;
      canvas.drawRRect(RRect.fromRectAndRadius(rect.shift(const Offset(0, 3)), radius), Paint()..color = Colors.black54..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4));
      canvas.drawRRect(RRect.fromRectAndRadius(rect, radius), Paint()..shader = LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter,
        colors: [Color.lerp(base, Colors.white, .08 - pressed * .05)!, Color.lerp(base, Colors.black, .18 + pressed * .15)!]).createShader(rect));
      if (lit) {
        canvas.drawRRect(RRect.fromRectAndRadius(rect.deflate(2), radius), Paint()..style = PaintingStyle.stroke..strokeWidth = side * .03
          ..color = glowColor.withValues(alpha: stage == LedStage.sent || stage == LedStage.error ? .3 + .6 * blink : stage == LedStage.confirmed ? .95 : .55));
      }
    } else {
      canvas.drawRRect(RRect.fromRectAndRadius(rect, radius), Paint()..color = Color.lerp(const Color(0xff141414), Colors.black, pressed * .6)!);
      canvas.drawRRect(RRect.fromRectAndRadius(rect.deflate(side * .05), radius), Paint()..style = PaintingStyle.stroke..strokeWidth = side * .035
        ..color = night ? Color.lerp(accent, Colors.white, .1)! : accent);
      for (var i = 0; i < leds; i++) {
        final center = Offset(rect.right - side * .1, leds == 1 ? rect.top + side * .1 : rect.top + side * .15 + i * (rect.height - side * .3) / math.max(1, leds - 1));
        final on = leds > 1 ? position == i && stage != LedStage.off && stage != LedStage.unknown : lit;
        canvas.drawCircle(center, side * .075, Paint()..color = const Color(0xff141414));
        canvas.drawCircle(center, side * .075, Paint()..style = PaintingStyle.stroke..strokeWidth = side * .03..color = accent);
        final level = !on ? 0.0 : stage == LedStage.confirmed ? 1.0 : stage == LedStage.bridgeAck ? .6 : .3 + .6 * blink;
        final color = stage == LedStage.error ? const Color(0xffff2020) : led;
        if (level > 0) canvas.drawCircle(center, side * .12, Paint()..color = color.withValues(alpha: .45 * level)..maskFilter = MaskFilter.blur(BlurStyle.normal, side * .05));
        canvas.drawCircle(center, side * .05, Paint()..color = Color.lerp(const Color(0xff4a3c10), color, level)!);
      }
    }
    final content = rect.center + Offset(0, pressed * side * .02);
    if (icon != null) {
      final painter = TextPainter(text: TextSpan(text: String.fromCharCode(icon!.codePoint), style: TextStyle(fontFamily: icon!.fontFamily, package: icon!.fontPackage,
        fontSize: side * (engraving.isEmpty ? .48 : .34), color: engraving.isEmpty && material == 'touch' ? ink : (material == 'outline' ? Colors.white : ink))), textDirection: TextDirection.ltr)..layout();
      painter.paint(canvas, content - Offset(painter.width / 2, engraving.isEmpty ? painter.height / 2 : painter.height * .85));
    }
    if (engraving.isNotEmpty) {
      final painter = TextPainter(text: TextSpan(text: engraving, style: TextStyle(fontFamily: 'OemCondensed', fontWeight: FontWeight.w600,
        fontSize: side * (engraving.length > 8 ? .14 : .18), height: 1.25, color: ink)), textDirection: TextDirection.ltr, textAlign: TextAlign.center)..layout(maxWidth: rect.width * .9);
      painter.paint(canvas, content + Offset(-painter.width / 2, icon != null ? side * .08 : -painter.height / 2));
    }
  }
  @override bool shouldRepaint(covariant _PanelKeyPainter old) => old.t != t || old.stage != stage || old.pulse != pulse || old.night != night || old.position != position;
}
