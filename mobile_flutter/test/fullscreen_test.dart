import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sim_control_studio/adaptive_layout.dart';
import 'package:sim_control_studio/connection.dart';
import 'package:sim_control_studio/demo.dart';
import 'package:sim_control_studio/display.dart';
import 'package:sim_control_studio/fullscreen.dart';
import 'package:sim_control_studio/hybrid.dart';
import 'package:sim_control_studio/models.dart';
import 'package:sim_control_studio/storage.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  final catalog=jsonDecode(File('assets/catalog.json').readAsStringSync()) as Map<String,dynamic>;
  test('Adaptive presentations preserve all 20 saved profiles and action identities',(){
    for(final json in catalog['vehicles'] as List){
      final car=VehicleProfile(json as Map<String,dynamic>);
      for(final layout in [car.dashboard,car.panel,composeHybrid(car.id,car.name,car.dashboard,car.panel)]){
        final before=jsonEncode(layout.data);
        for(var page=0;page<layout.pages.length;page++){
          for(final size in [const Size(360,680),const Size(844,300),const Size(1024,1280)]){
            final adaptive=adaptLayout(layout,page,size);adaptive.validate();
            expect(adaptive.width/adaptive.height,closeTo(size.width/size.height,.001));
            final originalActions=layout.elements(page).where((e)=>e['action']!=null).map((e)=>e['action']).toList()..sort();
            final shownActions=adaptive.pages.expand((p)=>(p['elements'] as List).cast<Map<String,dynamic>>()).where((e)=>e['action']!=null).map((e)=>e['action']).toList()..sort();
            expect(shownActions,originalActions,reason:'${layout.id} page $page');
            for(final e in adaptive.pages.expand((p)=>(p['elements'] as List).cast<Map<String,dynamic>>()).where((e)=>controlKinds.contains(e['kind']))){
              expect((e['w'] as num).toDouble(),greaterThanOrEqualTo(48));
              expect((e['h'] as num).toDouble(),greaterThanOrEqualTo(48));
            }
          }
        }
        expect(jsonEncode(layout.data),before);
      }
    }
  });
  testWidgets('Adaptive pages render with fresh DEMO data in portrait and landscape',(tester)async{
    final errors=<String>[];
    tester.view.devicePixelRatio=1;
    addTearDown(tester.view.resetPhysicalSize);addTearDown(tester.view.resetDevicePixelRatio);
    for(final size in [const Size(360,680),const Size(844,300)]){
      tester.view.physicalSize=size;
      for(final json in catalog['vehicles'] as List){
        final car=VehicleProfile(json as Map<String,dynamic>);
        for(final source in [car.dashboard,car.panel,composeHybrid(car.id,car.name,car.dashboard,car.panel)]){
          for(var page=0;page<source.pages.length;page++){
            final layout=adaptLayout(source,page,size);
            for(var mobilePage=0;mobilePage<layout.pages.length;mobilePage++){
              await tester.pumpWidget(MaterialApp(theme:ThemeData.dark(),home:Scaffold(body:LayoutCanvas(layout:layout,page:mobilePage,frame:DemoSimulator().frame(5000)))));
              await tester.pump();final error=tester.takeException();if(error!=null)errors.add('${source.id} page $page/$mobilePage at $size: $error');
            }
          }
        }
      }
    }
    expect(errors,isEmpty,reason:errors.join('\n'));
  });
  testWidgets('All cockpit roles respect iPhone safe areas and keep an exit reachable',(tester)async{
    SharedPreferences.setMockInitialValues({'haptic':false});
    final directory=(await tester.runAsync(()=>Directory.systemTemp.createTemp('studio-fullscreen-')))!;
    final store=StudioStore();await tester.runAsync(()=>store.load(documentsDirectory:directory));
    final connection=BridgeConnection(store);await connection.setDemo(true);
    tester.view.devicePixelRatio=1;tester.view.physicalSize=const Size(393,852);
    addTearDown(tester.view.resetPhysicalSize);addTearDown(tester.view.resetDevicePixelRatio);
    try{
      for(final role in ['dashboard','panel','hybrid']){
        await store.set('role',role);
        await tester.pumpWidget(MaterialApp(theme:ThemeData.dark(),home:MediaQuery(data:const MediaQueryData(size:Size(393,852),padding:EdgeInsets.only(top:59,bottom:34),viewPadding:EdgeInsets.only(top:59,bottom:34)),child:LiveDisplay(key:ValueKey(role),store:store,connection:connection,role:role))));
        await tester.pump();
        final rect=tester.getRect(find.byType(LayoutCanvas));
        expect(rect.top,greaterThanOrEqualTo(59));expect(rect.bottom,lessThanOrEqualTo(818));
        expect(find.byKey(const ValueKey('cockpit-options')),findsOneWidget);
        expect(find.text('DEMO · SZIMULÁLT ADATOK'),findsOneWidget);
        expect(tester.takeException(),isNull,reason:role);
      }
    }finally{
      await tester.pumpWidget(const SizedBox());connection.dispose();store.dispose();
      await tester.runAsync(()=>directory.delete(recursive:true));
    }
  });
  test('Fullscreen enter and leave call the native Android API and restore system UI',()async{
    final calls=<MethodCall>[];
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(StudioFullscreen.channel,(call)async{calls.add(call);return null;});
    final fullscreen=StudioFullscreen(platform:TargetPlatform.android);
    await fullscreen.enter();await fullscreen.leave();
    expect(calls.where((c)=>c.method=='setFullscreen').map((c)=>(c.arguments as Map)['enabled']),[true,false]);
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(StudioFullscreen.channel,null);
  });
}
