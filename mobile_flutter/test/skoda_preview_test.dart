import 'dart:convert';
import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sim_control_studio/demo.dart';
import 'package:sim_control_studio/display.dart';
import 'package:sim_control_studio/models.dart';
import 'package:sim_control_studio/premium_controls.dart';

void main(){
  testWidgets('Export the 0.4.0 dashboards and button boxes (day and night) through the actual Flutter renderer',(tester)async{
    final loader=FontLoader('OemCondensed')..addFont(rootBundle.load('assets/fonts/BarlowCondensed-Regular.ttf'))..addFont(rootBundle.load('assets/fonts/BarlowCondensed-SemiBold.ttf'));
    await tester.runAsync(loader.load);
    final icons=FontLoader('MaterialIcons')..addFont(rootBundle.load('fonts/MaterialIcons-Regular.otf'));
    await tester.runAsync(icons.load);
    final json=jsonDecode(File('assets/catalog.json').readAsStringSync()) as Map<String,dynamic>;
    final out=Directory('../preview-build')..createSync(recursive:true);
    tester.view.devicePixelRatio=1;
    addTearDown(tester.view.resetPhysicalSize);addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(()=>CockpitLighting.night.value=false);
    final renders=<(VehicleProfile,StudioLayout,bool)>[];
    for(final data in (json['vehicles'] as List).cast<Map<String,dynamic>>()){
      final car=VehicleProfile(data);
      if(car.id=='skoda-fabia-rs-rally2'){renders.addAll([(car,car.dashboard,false),(car,car.variants.first,false)]);}
      if(car.panel.data['adaptive']=='preserve'){renders.addAll([(car,car.panel,false),(car,car.panel,true)]);}
      if(car.data['version']=='0.4.0' && car.id!='skoda-fabia-rs-rally2'){renders.add((car,car.dashboard,false));}
    }
    for(final (car,layout,night) in renders){
      CockpitLighting.night.value=night;
      tester.view.physicalSize=Size(layout.width,layout.height+88);
      final key=GlobalKey();
      await tester.pumpWidget(MaterialApp(theme:ThemeData.dark().copyWith(textTheme:ThemeData.dark().textTheme.apply(fontFamily:'OemCondensed')),home:Scaffold(body:RepaintBoundary(key:key,child:Column(children:[
        SizedBox(height:50,child:Center(child:Text('${car.name.toUpperCase()} / ${layout.role=='dashboard'?'DRIVER DISPLAY':'BUTTON BOX'}${night?' / NIGHT':''}',style:const TextStyle(fontSize:23,letterSpacing:3)))),
        Expanded(child:LayoutCanvas(layout:layout,frame:DemoSimulator().frame(8500))),
        const SizedBox(height:38,child:Center(child:Text('REFERENCE-BASED ORIGINAL ARTWORK · DEMO / SYNTHETIC DATA · EDITABLE CONTROLS',style:TextStyle(fontSize:16,color:Colors.amber,letterSpacing:1)))),
      ])))));
      await tester.runAsync(()async{
        for(final element in find.byType(Image).evaluate()){await precacheImage((element.widget as Image).image,element);}
      });
      await tester.pumpAndSettle();
      expect(tester.takeException(),isNull);
      final boundary=key.currentContext!.findRenderObject()! as RenderRepaintBoundary;
      final image=(await tester.runAsync(()=>boundary.toImage(pixelRatio:2)))!;
      final bytes=await tester.runAsync(()=>image.toByteData(format:ui.ImageByteFormat.png));
      File('${out.path}/${car.id}_${layout.id}${night?'_night':''}.png').writeAsBytesSync(bytes!.buffer.asUint8List());
      image.dispose();
      final copy=layout.personalCopy('preview-edit-${layout.role}','Editable');
      final element=copy.elements(0).firstWhere((e)=>e['locked']!=true);
      element['x']=(element['x'] as num)+1;copy.validate();
      expect(element['x'],isNot(layout.elements(0).firstWhere((e)=>e['id']==element['id'])['x']));
    }
  });
}
