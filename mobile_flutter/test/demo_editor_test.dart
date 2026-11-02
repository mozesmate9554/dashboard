import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sim_control_studio/connection.dart';
import 'package:sim_control_studio/demo.dart';
import 'package:sim_control_studio/display.dart';
import 'package:sim_control_studio/premium_controls.dart';
import 'package:sim_control_studio/editor.dart';
import 'package:sim_control_studio/layout_geometry.dart';
import 'package:sim_control_studio/models.dart';
import 'package:sim_control_studio/storage.dart';
import 'package:sim_control_studio/main.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late StudioStore store;
  late Directory directory;
  setUp(() async {
    SharedPreferences.setMockInitialValues({'role': 'panel', 'haptic': false});
    directory = await Directory.systemTemp.createTemp('sim-control-test-');
    store = StudioStore(); await store.load(documentsDirectory: directory);
  });
  tearDown(() async { store.dispose(); await directory.delete(recursive: true); });
  test('Local DEMO commands change only simulated state and never send network messages', () async {
    final connection = BridgeConnection(store);
    await connection.setDemo(true);
    expect(connection.telemetry.value!.isDemo, true);
    expect(connection.telemetry.value!.fields.values.every((v) => v.source.startsWith('demo:')), true);
    connection.command('lights');
    expect(connection.telemetry.value!.value('lights'), true);
    connection.command('radio', phase: 'down');
    expect(connection.telemetry.value!.value('radioActive'), true);
    connection.releaseAll(); connection.command('camera');
    expect(connection.telemetry.value!.value('radioActive'), false);
    expect(connection.commandHistory.last['stage'], 'simulated');
    expect(connection.outboundMessageCount, 0);
    connection.didChangeAppLifecycleState(AppLifecycleState.paused);
    expect(connection.mayControl, false);
    connection.didChangeAppLifecycleState(AppLifecycleState.resumed);
    await store.set('role', 'dashboard'); connection.command('lights');
    expect(connection.commandHistory.last['stage'], 'rejected');
    await connection.setDemo(false); expect(connection.telemetry.value, null);
    connection.dispose();
  });
  test('DEMO freshness requires an explicit mode and releases expired holds', () {
    final demo = DemoSimulator();
    demo.apply('radio', 'down', 0);
    expect(demo.frame(100).value('radioActive'), true);
    expect(demo.frame(3101).value('radioActive'), false);
    expect(TelemetryFrame(1, 1, 'demo', 'demo', null, {}).fresh, false);
  });
  test('Alignment keeps group spacing and original layout; opacity validates', () {
    final base = store.vehicle.dashboard, before = jsonEncode(store.vehicle.dashboard.data);
    final copy = base.personalCopy(newId(), 'Alignment');
    final first = copy.elements(0).first;
    first['group'] = 'test'; final second = copy.elements(0)[1]; second['group'] = 'test';
    final separation = (first['x'] as num) - (second['x'] as num);
    alignToCanvas(copy, 0, first['id'] as String, 'right');
    expect((first['x'] as num) - (second['x'] as num), closeTo(separation, .01));
    first['opacity'] = 1.1; expect(copy.validate, throwsFormatException);
    first['opacity'] = .4; copy.validate();
    expect(jsonEncode(store.vehicle.dashboard.data), before);
  });
  test('Personal layout survives save, load and delete; broken file remains intact', () async {
    final copy = store.vehicle.dashboard.personalCopy(newId(), 'Saved');
    copy.elements(0).first['opacity'] = .5;
    await store.saveLayout(copy); await store.selectLayout(copy);
    final reload = StudioStore(); await reload.load(documentsDirectory: directory);
    expect(reload.selected('dashboard').elements(0).first['opacity'], .5);
    await reload.deleteLayout(copy.id); expect(reload.personal, isEmpty); reload.dispose();
    final file = File('${directory.path}/personal-layouts.json');
    await file.writeAsString('damaged');
    final broken = StudioStore(); await broken.load(documentsDirectory: directory);
    expect(broken.loadError, isNotNull);
    await expectLater(broken.saveLayout(copy), throwsFormatException);
    await expectLater(broken.deleteLayout(copy.id), throwsFormatException);
    expect(await file.readAsString(), 'damaged'); broken.dispose();
  });
  testWidgets('Changing panel page releases a held action and never renews it', (tester) async {
    final connection = BridgeConnection(store); await connection.setDemo(true);
    Map<String,dynamic> page(String id) => {'id':id,'name':id,'elements':[
      {'id':'$id-hold','kind':'hold','label':'START','action':'starter','x':20,'y':20,'w':300,'h':200}]};
    final layout = StudioLayout({'schemaVersion':1,'id':'two-page-test','name':'Two pages','vehicleId':'skoda-fabia-rs-rally2','role':'panel',
      'isBase':true,'version':'0.4.0','revision':1,'width':800,'height':480,'pages':[page('p1'),page('p2')]});
    final index = layout.elements(0).indexWhere((e) => e['kind'] == 'hold');
    expect(index, greaterThanOrEqualTo(0));
    final id = layout.elements(0)[index]['id'];
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: LayoutCanvas(layout: layout, page: 0, frame: connection.telemetry.value, connection: connection))));
    final action = layout.elements(0)[index]['action'];
    final finder = find.byWidgetPredicate((w) => w is PanelControl && w.element['id'] == id);
    final gesture = await tester.startGesture(tester.getCenter(finder)); await tester.pump(const Duration(milliseconds: 150));
    expect(connection.commandHistory.where((c) => c['action'] == action && c['phase'] == 'down').length, 1);
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: LayoutCanvas(layout: layout, page: 1, frame: connection.telemetry.value, connection: connection))));
    await gesture.up(); await tester.pump(const Duration(seconds: 2));
    expect(connection.commandHistory.where((c) => c['action'] == action && c['phase'] == 'down').length, 1);
    await tester.pumpWidget(const SizedBox()); connection.dispose();
  });
  testWidgets('Three and multi-position selectors bound requests without inventing game state', (tester) async {
    final connection = BridgeConnection(store); await connection.setDemo(true);
    for (final kind in ['threeState', 'multiState']) {
      final maximum = kind == 'threeState' ? 2 : 3;
      final before = connection.commandHistory.length;
      final element = <String,dynamic>{'id':kind,'kind':kind,'label':'ABS','action':'absUp','minusAction':'absDown','field':'absLevel','positions':4};
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: Center(child: SizedBox(width:300,height:160,
        child: PanelControl(key: ValueKey(kind), element:element, frame:connection.telemetry.value, connection:connection))))));
      for (var i=0; i<6; i++) { await tester.tap(find.text('+')); await tester.pump(); }
      expect(connection.commandHistory.length - before, maximum);
      expect(find.text('kért pozíció: ${maximum+1}/${maximum+1}'), findsOneWidget);
    }
    await tester.pumpWidget(const SizedBox()); connection.dispose();
  });
  testWidgets('All main navigation screens fit portrait and landscape phones in DEMO', (tester) async {
    final connection = BridgeConnection(store); await connection.setDemo(true);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize); addTearDown(tester.view.resetDevicePixelRatio);
    for (final size in [const Size(360,800), const Size(900,420)]) {
      tester.view.physicalSize = size;
      await tester.pumpWidget(MaterialApp(theme:ThemeData.dark(), home:StudioShell(key:ValueKey(size),store:store,connection:connection)));
      await tester.pump(); expect(tester.takeException(),isNull,reason:'Home at $size');
      for (final page in ['Műszerfalak','Kezelőpanelek','Autóprofilok','Szerkesztő','Játékok','Csatlakozás','Eszközök','Telemetria','Beállítások']) {
        await tester.tap(find.byIcon(Icons.menu)); await tester.pump(const Duration(milliseconds:300));
        final link = find.descendant(of:find.byType(Drawer),matching:find.text(page));
        await tester.ensureVisible(link); await tester.pump();
        await tester.tap(link); await tester.pump(const Duration(milliseconds:300));
        expect(tester.takeException(),isNull,reason:'$page at $size');
      }
    }
    await tester.pumpWidget(const SizedBox()); connection.dispose();
  });
  testWidgets('Editor touch move, resize, undo and save preserve the shipped base layout', (tester) async {
    tester.view.devicePixelRatio = 1; tester.view.physicalSize = const Size(1400, 900);
    addTearDown(tester.view.resetPhysicalSize); addTearDown(tester.view.resetDevicePixelRatio);
    final connection = BridgeConnection(store); await connection.setDemo(true);
    final base = store.vehicle.dashboard, original = jsonEncode(store.vehicle.dashboard.data);
    await tester.pumpWidget(MaterialApp(theme: ThemeData.dark(), home: LayoutEditor(store: store, connection: connection, layout: base)));
    final field = base.elements(0).firstWhere((e) => e['field'] == 'speed');
    final instrument = find.byWidgetPredicate((w) => w is Instrument && w.element['id'] == field['id']);
    final finder = find.ancestor(of: instrument, matching: find.byType(GestureDetector)).first;
    await tester.tap(finder); await tester.pump();
    final before = tester.widget<LayoutCanvas>(find.byType(LayoutCanvas)).layout.elements(0).firstWhere((e) => e['id'] == field['id'])['x'];
    await tester.drag(finder, const Offset(30, 0)); await tester.pump();
    expect(tester.widget<LayoutCanvas>(find.byType(LayoutCanvas)).layout.elements(0).firstWhere((e) => e['id'] == field['id'])['x'], isNot(before));
    await tester.tap(find.byTooltip('Visszavonás')); await tester.pump();
    expect(tester.widget<LayoutCanvas>(find.byType(LayoutCanvas)).layout.elements(0).firstWhere((e) => e['id'] == field['id'])['x'], before);
    await tester.tap(finder); await tester.pump();
    final oldWidth = tester.widget<LayoutCanvas>(find.byType(LayoutCanvas)).layout.elements(0).firstWhere((e) => e['id'] == field['id'])['w'];
    await tester.drag(find.byIcon(Icons.open_in_full), const Offset(60, 60)); await tester.pump();
    expect(tester.widget<LayoutCanvas>(find.byType(LayoutCanvas)).layout.elements(0).firstWhere((e) => e['id'] == field['id'])['w'], isNot(oldWidth));
    await tester.runAsync(() async {
      await tester.tap(find.byTooltip('Mentés'));
      for (var i = 0; i < 100 && store.personal.isEmpty; i++) { await Future<void>.delayed(const Duration(milliseconds: 20)); }
    });
    await tester.pump();
    expect(store.personal.single.isBase, false);
    expect(jsonEncode(store.vehicle.dashboard.data), original);
    expect(find.byType(DemoBadge), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox()); connection.dispose();
  });
  testWidgets('Every Skoda 0.3.0 vector control (kept as a variant) sends its bound DEMO action and volume directions remain distinct',(tester)async{
    tester.view.devicePixelRatio=1;tester.view.physicalSize=const Size(1100,1450);
    addTearDown(tester.view.resetPhysicalSize);addTearDown(tester.view.resetDevicePixelRatio);
    await store.set('vehicleId','skoda-fabia-rs-rally2');
    final connection=BridgeConnection(store);await connection.setDemo(true);
    final layout=store.vehicle.variants.firstWhere((l)=>l.id=='skoda-fabia-rs-rally2-panel');
    await tester.pumpWidget(MaterialApp(theme:ThemeData.dark(),home:Scaffold(body:LayoutCanvas(layout:layout,connection:connection,frame:connection.telemetry.value))));
    await tester.pump();
    for(final e in layout.elements(0).where((e)=>e['action']!=null)){
      final finder=find.byWidgetPredicate((w)=>w is PanelControl && w.element['id']==e['id']);
      final rect=tester.getRect(finder);
      final kind=e['kind'];
      final point=kind=='stepper'?Offset(rect.center.dx,rect.top+rect.height*.25):kind=='rotary'?Offset(rect.left+rect.width*.75,rect.center.dy):rect.center;
      final before=connection.commandHistory.length;
      await tester.tapAt(point);await tester.pump();
      expect(connection.commandHistory.length,before+1,reason:e['id'] as String);
      expect(connection.commandHistory.last['action'],e['action']);expect(connection.commandHistory.last['stage'],'simulated');
      if(e['minusAction']!=null){
        await tester.tapAt(kind=='stepper'?Offset(rect.center.dx,rect.top+rect.height*.75):Offset(rect.left+rect.width*.25,rect.center.dy));await tester.pump();
        expect(connection.commandHistory.last['action'],e['minusAction']);
      }
    }
    expect(connection.outboundMessageCount,0);expect(tester.takeException(),isNull);
    await tester.pumpWidget(const SizedBox());connection.dispose();
  });

  testWidgets('Every 0.4.0 mechanical control sends real DEMO commands; LED never claims game confirmation',(tester)async{
    tester.view.devicePixelRatio=1;tester.view.physicalSize=const Size(1600,900);
    addTearDown(tester.view.resetPhysicalSize);addTearDown(tester.view.resetDevicePixelRatio);
    for(final car in store.vehicles.where((v)=>v.panel.data['adaptive']=='preserve')){
      await store.set('vehicleId',car.id);
      final connection=BridgeConnection(store);await connection.setDemo(true);
      final layout=car.panel;
      await tester.pumpWidget(MaterialApp(theme:ThemeData.dark(),home:Scaffold(body:LayoutCanvas(layout:layout,connection:connection,frame:connection.telemetry.value))));
      await tester.pump();
      for(final e in layout.elements(0).where((e)=>{'rocker','pushButton','guarded','rotarySwitch','cycleButton'}.contains(e['kind']))){
        final finder=find.byWidgetPredicate((w)=>w is PremiumControl && w.element['id']==e['id']);
        expect(finder,findsOneWidget,reason:'${car.id} ${e['id']}');
        final rect=tester.getRect(finder);
        final face=Offset(rect.center.dx,rect.top+(rect.height-42)/2);
        final before=connection.commandHistory.length;
        if(e['action']==null){
          await tester.tapAt(face);await tester.pump(const Duration(milliseconds:200));
          expect(connection.commandHistory.length,before,reason:'Display-only key ${e['id']} must not send anything');
          continue;
        }
        if(e['kind']=='guarded'){
          await tester.tapAt(face);await tester.pump(const Duration(milliseconds:300));
          expect(connection.commandHistory.length,before,reason:'Opening the safety cover must not send ${e['action']}');
        }
        if(e['kind']=='rotarySwitch'){
          await tester.tapAt(Offset(rect.left+rect.width*.8,face.dy));await tester.pump(const Duration(milliseconds:200));
          expect(connection.commandHistory.last['action'],e['action'],reason:e['id'] as String);
          await tester.tapAt(Offset(rect.left+rect.width*.2,face.dy));await tester.pump(const Duration(milliseconds:200));
          expect(connection.commandHistory.last['action'],e['minusAction'],reason:e['id'] as String);
          continue;
        }
        await tester.tapAt(face);await tester.pump(const Duration(milliseconds:200));
        final sent=connection.commandHistory.skip(before).toList();
        expect(sent.map((c)=>c['action']).toSet(),{e['action']},reason:'${car.id} ${e['id']}');
        expect(sent.every((c)=>c['stage']=='simulated'),true);
        if(e['hold']==true){expect(sent.map((c)=>c['phase']).toList(),['down','up'],reason:'Hold controls must release on lift');}
        expect(find.descendant(of:finder,matching:find.text('JÁTÉK IGAZOLTA')),findsNothing,reason:'DEMO/Bridge acks are not game confirmation (${e['id']})');
      }
      expect(connection.outboundMessageCount,0);expect(tester.takeException(),isNull);
      await tester.pumpWidget(const SizedBox());connection.dispose();
    }
  });
}
