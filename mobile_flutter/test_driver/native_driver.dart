import 'dart:convert';
import 'dart:io';
import 'package:integration_test/integration_test_driver_extended.dart';

Future<void> main() => integrationDriver(
  onScreenshot:(String name,List<int> bytes,[Map<String,Object?>? args])async{
    if(!RegExp(r'^[a-zA-Z0-9_-]+$').hasMatch(name) || bytes.isEmpty)return false;
    final file=File('../${Platform.environment['STUDIO_NATIVE_OUTPUT']??'ios-ci'}/$name.png');await file.parent.create(recursive:true);await file.writeAsBytes(bytes);return true;
  },
  responseDataCallback:(data)async{
    final file=File('../${Platform.environment['STUDIO_NATIVE_OUTPUT']??'ios-ci'}/native-integration-results.json');await file.parent.create(recursive:true);
    await file.writeAsString(jsonEncode({'allTestsPassed':true,'scope':'Native simulator/emulator; loopback TLS with explicit DEMO fixture; not physical phone or live game',
      'screenshots':(data?['screenshots'] as List? ?? []).map((s)=>(s as Map)['screenshotName']).toList()}));
  },
);
