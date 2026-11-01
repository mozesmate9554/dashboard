import 'dart:math' as math;
import 'models.dart';

/// Entirely local simulation. This class has no transport or OS input access.
class DemoSimulator {
  int _sequence = 0;
  final Map<String, Object> _state = {
    'ignition': true, 'engineRunning': true, 'lights': false, 'pitLimiter': false,
    'drs': false, 'ers': false, 'p2p': false, 'rainLight': false, 'fan': false,
    'tcLevel': 3, 'absLevel': 4, 'brakeBias': 55.0, 'differential': 3, 'engineMap': 2, 'wiperLevel': 0,
  };
  final Map<String, int> _heldUntil = {};
  void releaseAll() => _heldUntil.clear();
  void apply(String action, String phase, int nowMs) {
    if (!actions.contains(action) || !{'press', 'down', 'up'}.contains(phase)) {
      throw const FormatException('Ismeretlen DEMO parancs.');
    }
    if (phase == 'up') { _heldUntil.remove(action); return; }
    if (phase == 'down') {
      _heldUntil[action] = nowMs + 3000;
      if (action == 'starter' && _state['ignition'] == true) _state['engineRunning'] = true;
      return;
    }
    switch (action) {
      case 'starter': if (_state['ignition'] == true) _state['engineRunning'] = true; break;
      case 'ignition':
        _state['ignition'] = _state['ignition'] != true;
        if (_state['ignition'] != true) _state['engineRunning'] = false;
        break;
      case 'wiper': _state['wiperLevel'] = ((_state['wiperLevel'] as int) + 1) % 4; break;
      case 'tcUp': case 'tcDown': _step('tcLevel', action.endsWith('Up') ? 1 : -1, 0, 12); break;
      case 'absUp': case 'absDown': _step('absLevel', action.endsWith('Up') ? 1 : -1, 0, 12); break;
      case 'diffUp': case 'diffDown': _step('differential', action.endsWith('Up') ? 1 : -1, 0, 12); break;
      case 'engineMapUp': case 'engineMapDown': _step('engineMap', action.endsWith('Up') ? 1 : -1, 1, 12); break;
      case 'brakeBiasUp': case 'brakeBiasDown': _step('brakeBias', action.endsWith('Up') ? .5 : -.5, 40, 70); break;
      case 'lights': case 'pitLimiter': case 'drs': case 'ers': case 'p2p': case 'rainLight': case 'fan':
        _state[action] = _state[action] != true; break;
      default: _heldUntil[action] = nowMs + 400;
    }
  }
  void _step(String field, num amount, num min, num max) => _state[field] = ((_state[field] as num) + amount).clamp(min, max);
  TelemetryFrame frame(int elapsedMs, {int? timestampMs}) {
    _heldUntil.removeWhere((_, expiry) => expiry < elapsedMs);
    final t = elapsedMs / 1000, cycle = t % 20;
    final speed = _state['engineRunning'] == true ? (cycle < 10 ? cycle : 20 - cycle) * 16 : 0.0;
    final gear = _heldUntil.containsKey('neutral') ? 0 : _heldUntil.containsKey('reverse') ? -1 : (speed / 35).floor().clamp(1, 6);
    final rpm = _state['engineRunning'] == true ? 1100 + speed % 35 * 165 : 0.0;
    final now = timestampMs ?? DateTime.now().millisecondsSinceEpoch;
    final values = <String, Object>{
      ..._state, 'lights': _state['lights'] == true || _heldUntil.containsKey('flash'),
      'speed': speed, 'gear': gear, 'rpm': rpm, 'rpmLimit': 7500,
      'throttle': cycle < 10 ? .72 : .12, 'brake': cycle < 10 ? 0.0 : .45,
      'clutch': 0.0, 'handbrake': 0.0, 'steering': math.sin(t / 2) * .3,
      'gX': math.sin(t) * .8, 'gY': .0, 'gZ': cycle < 10 ? .45 : -.65,
      'fuel': 42 - (t / 60) % 30, 'waterTemp': 88 + math.sin(t / 4) * 4,
      'oilTemp': 104 + math.sin(t / 5) * 5, 'oilPressure': 4.5,
      'tyrePressure': [26.1, 26.3, 25.8, 26.0], 'tyreTempMiddle': [85.0, 87.0, 82.0, 84.0],
      'lap': 3, 'lapsRemaining': 8, 'lapCurrent': elapsedMs % 92000,
      'lapLast': 92451, 'lapBest': 91802, 'delta': math.sin(t / 3) * 400,
      'stageTime': elapsedMs, 'distance': t * 18, 'stageDistance': t * 18,
      'battery': .72 + math.sin(t / 4) * .12, 'hybridEnergy': 420.0, 'ersDeploy': 35.0,
      'tyreTempInner': [85, 87, 82, 84], 'tyreTempOuter': [81, 83, 80, 82],
      'tyreWear': [.95, .94, .96, .95], 'brakeTemp': [420, 430, 340, 350],
      'consumption': 32.4, 'range': 139, 'turbo': .6, 'gearboxTemp': 89,
      'damage': [0, 0, 0, 0, 0], 'faults': 'none', 'sessionStatus': 'demo',
      'stageState': 'synthetic_demo', 'stageId': 'DEMO-STAGE', 'vehicleId': 'DEMO-SYNTHETIC',
      'navigation': 'Szimulált bemutató', 'absActive': cycle > 15, 'tcActive': cycle < 4,
      'timeRemaining': 1200 - t % 1200, 'inPit': _state['pitLimiter'] == true, 'pitLimit': 60,
      'wheelLock': false, 'wheelSpeed': [10.0, 10.0, 10.0, 10.0], 'wheelSlip': [.01, .02, .01, .02],
      'yaw': math.sin(t) * .1, 'pitch': .01, 'roll': .03, 'suspension': [.04, .05, .04, .05],
      'sectors': [28900, 30200, 29720], 'stageSplits': [30120, 32040],
      'flags': 'DEMO', 'position': 4, 'camera': _heldUntil.containsKey('camera') ? 2 : 1,
      'radioActive': _heldUntil.containsKey('radio'), 'intercomActive': _heldUntil.containsKey('intercom'),
      'starterActive': _heldUntil.containsKey('starter'), 'flash': _heldUntil.containsKey('flash'),
    };
    String unit(String key) => switch (key) {
      'speed' => 'km/h', 'rpm' || 'rpmLimit' => 'rpm', 'fuel' => 'L',
      'waterTemp' || 'oilTemp' || 'tyreTempMiddle' => '°C', 'tyrePressure' => 'psi',
      'lapCurrent' || 'lapLast' || 'lapBest' || 'stageTime' => 'ms',
      'distance' || 'stageDistance' => 'm', 'brakeBias' || 'battery' => '%', _ => '',
    };
    return TelemetryFrame(++_sequence, now, 'demo', 'demo', 'DEMO-SYNTHETIC',
      values.map((key, value) => MapEntry(key, TelemetryDatum(value, unit(key), 'demo:local:synthetic:v1', now, 'valid', false))), mode: 'demo');
  }
}
