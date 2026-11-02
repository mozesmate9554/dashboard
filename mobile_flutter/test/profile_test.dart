import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:sim_control_studio/models.dart';
import 'package:sim_control_studio/connection.dart';
import 'package:sim_control_studio/hybrid.dart';
import 'package:sim_control_studio/premium_controls.dart';

void main() {
  test('All base layouts and variants validate and remain unchanged when copied', () {
    final json = jsonDecode(File('assets/catalog.json').readAsStringSync()) as Map<String, dynamic>;
    expect((json['vehicles'] as List).length, 6);
    for (final data in json['vehicles'] as List) {
      final vehicle = VehicleProfile(data as Map<String, dynamic>);
      for (final base in [vehicle.dashboard, vehicle.panel, ...vehicle.variants]) {
        final original = jsonEncode(base.data);
        final copy = base.personalCopy(newId(), 'Personal');
        copy.elements(0).first['x'] = 0;
        expect(jsonEncode(base.data), original);
        expect(copy.isBase, false);
      }
    }
  });
  test('Missing and stale telemetry can never become a numeric zero', () {
    final frame = TelemetryFrame(1, 1, 'acr', 'stale', null, {
      'speed': const TelemetryDatum(120, 'km/h', 'fixture', 1, 'stale', false),
      'fuel': const TelemetryDatum(null, 'L', 'fixture', 1, 'unsupported', false),
    });
    expect(frame.formatted('speed'), '—'); expect(frame.number('speed'), null);
    expect(frame.formatted('fuel'), '—'); expect(frame.formatted('unknown'), '—');
  });
  test('Each hybrid is a separately editable role and preserves its source layouts', () {
    final json = jsonDecode(File('assets/catalog.json').readAsStringSync()) as Map<String, dynamic>;
    for (final data in json['vehicles'] as List) {
      final vehicle = VehicleProfile(data as Map<String, dynamic>);
      final dash = vehicle.dashboard, panel = vehicle.panel;
      final before = jsonEncode(dash.data);
      final hybrid = composeHybrid(vehicle.id, vehicle.name, dash, panel);
      expect(hybrid.role, 'hybrid'); expect(hybrid.elements(0).length, greaterThan(dash.elements(0).length));
      hybrid.elements(0).first['x'] = 0;
      expect(jsonEncode(dash.data), before);
    }
  });
  test('Unsafe remote pairing target and invalid certificate pins are rejected', () {
    expect(() => BridgeTarget('8.8.8.8', 19760, 'a' * 64), throwsFormatException);
    expect(() => BridgeTarget('192.168.1.2', 19760, 'a'), throwsFormatException);
    expect(BridgeTarget('192.168.1.2', 19760, 'a' * 64).host, '192.168.1.2');
    expect(() => BridgeTarget.fromUri('https://example.com/pair'), throwsFormatException);
  });
  test('SVG external references and oversized images are rejected', () {
    expect(() => validateAsset('svg', Uint8List.fromList(utf8.encode('<svg><image href="https://example.com/x"/></svg>'))), throwsFormatException);
    expect(() => validateAsset('svg', Uint8List.fromList(utf8.encode('<!DOCTYPE svg><svg/>'))), throwsFormatException);
    validateAsset('svg', Uint8List.fromList(utf8.encode('<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0L1 1"/></svg>')));
  });
  test('Invalid geometry, decimals and LED counts are rejected', () {
    final json = jsonDecode(File('assets/catalog.json').readAsStringSync()) as Map<String, dynamic>;
    final data = deepCopy((json['vehicles'] as List).first['dashboard'] as Map<String, dynamic>);
    final item = ((data['pages'] as List).first['elements'] as List).first as Map<String, dynamic>;
    item['count'] = 1000000; expect(() => StudioLayout(data), throwsFormatException);
    item['count'] = 16; item['decimals'] = 99; expect(() => StudioLayout(data), throwsFormatException);
    item['decimals'] = 1; item['x'] = -1; expect(() => StudioLayout(data), throwsFormatException);
  });
  test('LED stages: only valid telemetry confirms; Bridge execution stays an assumption', () {
    final frame = TelemetryFrame(1, DateTime.now().millisecondsSinceEpoch, 'acr', 'live', null, {
      'ignition': TelemetryDatum(true, '', 'fixture', 1, 'valid', false),
    });
    expect(ledStageFor(connection: null, commandId: null, requestedOn: true, frame: frame, field: 'ignition'), LedStage.confirmed);
    expect(ledStageFor(connection: null, commandId: null, requestedOn: true, frame: null, field: 'lights'), LedStage.requested);
    expect(ledStageFor(connection: null, commandId: null, requestedOn: false, frame: null, field: 'lights', enabled: false), LedStage.unknown);
  });
  test('Game car identifiers map to profiles only through explicit aliases', () {
    final json = jsonDecode(File('assets/catalog.json').readAsStringSync()) as Map<String, dynamic>;
    final vehicles = (json['vehicles'] as List).map((v) => VehicleProfile(v as Map<String, dynamic>)).toList();
    expect(detectVehicle(vehicles, 'SkodaFabiaRSRally2'), 'skoda-fabia-rs-rally2');
    expect(detectVehicle(vehicles, 'skoda_fabia_rs_rally2'), 'skoda-fabia-rs-rally2');
    expect(detectVehicle(vehicles, 'Unknown Car 9000'), isNull);
    expect(detectVehicle(vehicles, null), isNull);
  });
}
