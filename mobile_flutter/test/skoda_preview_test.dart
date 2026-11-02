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

void main(){
  testWidgets('Export the two editable Skoda reconstructions through the actual Flutter renderer',(tester)async{
    final loader=FontLoader('OemCondensed')..addFont(rootBundle.load('assets/fonts/BarlowCondensed-Regular.ttf'));
    await loader.load();
    final json=jsonDecode(File('assets/catalog.json').readAsStringSync()) as Map<String,dynamic>;
    final car=VehicleProfile((json['vehicles'] as List).cast<Map<String,dynamic>>().firstWhere((v)=>v['id']=='skoda-fabia-rs-rally2'));
    final out=Directory('../preview-build')..createSync(recursive:true);
    tester.view.devicePixelRatio=1;
    addTearDown(tester.view.resetPhysicalSize);addTearDown(tester.view.resetDevicePixelRatio);
    for(final layout in [car.dashboard,car.panel]){
      tester.view.physicalSize=Size(layout.width,layout.height+88);
      final key=GlobalKey();
      await tester.pumpWidget(MaterialApp(theme:ThemeData.dark(),home:Scaffold(body:RepaintBoundary(key:key,child:Column(children:[
        SizedBox(height:50,child:Center(child:Text('ŠKODA FABIA RS RALLY2 / ${layout.role=='dashboard'?'DRIVER DISPLAY':'CENTRAL CONSOLE'}',style:const TextStyle(fontSize:23,letterSpacing:3)))),
        Expanded(child:LayoutCanvas(layout:layout,frame:DemoSimulator().frame(8500))),
        const SizedBox(height:38,child:Center(child:Text('PHOTO-DERIVED RECONSTRUCTION · DEMO / SYNTHETIC DATA · EDITABLE CONTROLS',style:TextStyle(fontSize:16,color:Colors.amber,letterSpacing:1)))),
      ])))));
      await tester.pumpAndSettle();
      expect(tester.takeException(),isNull);
      final boundary=key.currentContext!.findRenderObject()! as RenderRepaintBoundary;
      final image=await boundary.toImage(pixelRatio:2);
      final bytes=await image.toByteData(format:ui.ImageByteFormat.png);
      File('${out.path}/SKODA_${layout.role.toUpperCase()}_0.3.0.png').writeAsBytesSync(bytes!.buffer.asUint8List());
      image.dispose();
      final copy=layout.personalCopy('preview-edit-${layout.role}','Editable');
      final element=copy.elements(0).firstWhere((e)=>e['locked']!=true);
      element['x']=(element['x'] as num)+1;copy.validate();
      expect(element['x'],isNot(layout.elements(0).firstWhere((e)=>e['id']==element['id'])['x']));
    }
  });
}
