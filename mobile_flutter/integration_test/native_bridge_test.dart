import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:sim_control_studio/connection.dart';
import 'package:sim_control_studio/display.dart';
import 'package:sim_control_studio/fullscreen.dart';
import 'package:sim_control_studio/storage.dart';

void main() {
  final binding=IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('Native pinned TLS, secure pairing, telemetry, touch command and reconnect', (tester) async {
    final store = StudioStore(); await store.load();
    await store.set('role', 'panel'); await store.set('haptic', false);
    final connection = BridgeConnection(store); await connection.initialize();
    final http = HttpClient();
    try {
      final request = await http.getUrl(Uri.parse('http://127.0.0.1:19759/session'));
      final response = await request.close();
      final bootstrap = jsonDecode(await utf8.decoder.bind(response).join()) as Map<String,dynamic>;
      await connection.pair(BridgeTarget.fromUri(bootstrap['uri'] as String));
      Future<void> until(bool Function() ready) async {
        final clock = Stopwatch()..start();
        while (!ready() && clock.elapsed < const Duration(seconds: 15)) {
          await Future<void>.delayed(const Duration(milliseconds: 50));
        }
        expect(ready(), true, reason: connection.lastError);
      }
      await until(() => connection.connected && connection.telemetry.value?.fresh == true);
      expect(connection.telemetry.value!.isDemo, true);
      expect(connection.telemetry.value!.number('speed'), isNotNull);
      expect(connection.localDemo, false);
      final lights = store.vehicle.panel.pages.expand((p)=>(p['elements'] as List).cast<Map<String,dynamic>>()).firstWhere((e)=>e['action']=='lights');
      await tester.pumpWidget(MaterialApp(theme:ThemeData.dark(), home:Scaffold(body:Center(child:SizedBox(width:280,height:180,
        child:PanelControl(element:lights,frame:connection.telemetry.value,connection:connection))))));
      await tester.tap(find.byType(PanelControl));
      await until(() => connection.commandHistory.any((c)=>c['action']=='lights' && c['stage']=='simulated'));
      await until(() => connection.telemetry.value?.value('lights') == true);
      final identity = connection.deviceId;
      await connection.refreshSettings();
      await until(() => connection.connected && connection.telemetry.value?.fresh == true);
      expect(connection.deviceId, identity);
      expect(connection.target!.token, isNull); // Reconnect used persisted Keychain/Keystore credentials.
      if(Platform.isAndroid){await binding.convertFlutterSurfaceToImage();await tester.pump();}
      for(final (orientation,orientations) in [
        ('portrait',[DeviceOrientation.portraitUp]),
        ('landscape',[DeviceOrientation.landscapeLeft]),
      ]){
        for(final role in ['dashboard','panel','hybrid']){
          await tester.pumpWidget(const SizedBox());await Future<void>.delayed(const Duration(milliseconds:400));
          await SystemChrome.setPreferredOrientations(orientations);
          await store.set('role',role);await connection.refreshSettings();
          await until(()=>connection.connected && connection.telemetry.value?.fresh==true);
          await tester.pumpWidget(MaterialApp(theme:ThemeData.dark(),home:LiveDisplay(store:store,connection:connection,role:role)));
          await Future<void>.delayed(const Duration(milliseconds:1500));await tester.pump();
          expect(tester.takeException(),isNull,reason:'$role $orientation');
          final size=tester.view.physicalSize;
          expect(size.width>size.height,orientation=='landscape',reason:'Actual native orientation: $role $orientation / $size');
          expect(find.byKey(const ValueKey('cockpit-options')),findsOneWidget);
          if(Platform.isAndroid){
            final bars=await StudioFullscreen().inspect();
            expect(bars['requested'],true);expect(bars['statusBarVisible'],false);expect(bars['navigationBarVisible'],false);
          }
          await binding.takeScreenshot('${Platform.isIOS?'ios':'android'}-$role-$orientation');
        }
      }
      await tester.pumpWidget(const SizedBox());
    } finally { http.close(force:true); connection.dispose(); store.dispose(); }
  });
}
