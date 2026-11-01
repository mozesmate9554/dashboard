import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sim_control_studio/models.dart';
import 'package:sim_control_studio/display.dart';
import 'package:sim_control_studio/demo.dart';
import 'package:sim_control_studio/hybrid.dart';

void main() {
  testWidgets('Every base page renders at phone and tablet sizes with unavailable data', (tester) async {
    final json = jsonDecode(File('assets/catalog.json').readAsStringSync()) as Map<String, dynamic>;
    for (final size in [const Size(360, 800), const Size(900, 420), const Size(1366, 1024)]) {
      tester.view.devicePixelRatio = 1;
      tester.view.physicalSize = size;
      for (final vehicle in json['vehicles'] as List) {
        for (final layout in [StudioLayout(vehicle['dashboard'] as Map<String,dynamic>), StudioLayout(vehicle['panel'] as Map<String,dynamic>), composeHybrid(vehicle['id'] as String, vehicle['name'] as String, StudioLayout(vehicle['dashboard'] as Map<String,dynamic>), StudioLayout(vehicle['panel'] as Map<String,dynamic>))]) {
          for (var page = 0; page < layout.pages.length; page++) {
            for (final frame in [null, DemoSimulator().frame(4500)]) {
            await tester.pumpWidget(MaterialApp(theme: ThemeData.dark(), home: Scaffold(body: LayoutCanvas(layout: layout, page: page, frame: frame))));
            await tester.pump();
            expect(tester.takeException(), isNull, reason: '${layout.id} page $page at $size');
            }
          }
        }
      }
    }
    addTearDown(tester.view.resetPhysicalSize); addTearDown(tester.view.resetDevicePixelRatio);
  });
}
