import 'dart:convert';
import 'dart:io';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'models.dart';
import 'hybrid.dart';

class StudioStore extends ChangeNotifier {
  late SharedPreferences prefs;
  late Directory directory;
  List<VehicleProfile> vehicles = [];
  List<Map<String, dynamic>> games = [];
  List<StudioLayout> personal = [];
  String? loadError;
  Future<void> load() async {
    prefs = await SharedPreferences.getInstance();
    directory = await getApplicationDocumentsDirectory();
    final catalog = jsonDecode(await rootBundle.loadString('assets/catalog.json')) as Map<String, dynamic>;
    vehicles = (catalog['vehicles'] as List).map((v) => VehicleProfile(v as Map<String, dynamic>)).toList();
    games = (catalog['games'] as List).cast<Map<String, dynamic>>();
    final file = File('${directory.path}/personal-layouts.json');
    if (await file.exists()) {
      try {
        final list = jsonDecode(await file.readAsString()) as List;
        personal = list.map((v) => StudioLayout(v as Map<String, dynamic>)).toList();
      } catch (e) { loadError = 'A személyes profilok nem tölthetők be. Az eredeti fájl megmaradt. $e'; }
    }
    // Eagerly validate every shipped profile, rather than deferring a failure until track use.
    for (final vehicle in vehicles) { vehicle.dashboard.validate(); vehicle.panel.validate(); }
    notifyListeners();
  }
  String get language => prefs.getString('language') ?? 'hu';
  String get role => prefs.getString('role') ?? 'dashboard';
  String get vehicleId => prefs.getString('vehicleId') ?? 'skoda-fabia-rs-rally2';
  int get hz => prefs.getInt('hz') ?? 30;
  bool get haptic => prefs.getBool('haptic') ?? true;
  bool get suggestions => prefs.getBool('suggestions') ?? true;
  VehicleProfile get vehicle => vehicles.firstWhere((v) => v.id == vehicleId, orElse: () => vehicles.first);
  Future<void> set(String key, Object value) async {
    if (value is String) { await prefs.setString(key, value); }
    if (value is bool) { await prefs.setBool(key, value); }
    if (value is int) { await prefs.setInt(key, value); }
    notifyListeners();
  }
  Future<void> saveLayout(StudioLayout layout) async {
    if (layout.isBase) throw const FormatException('Az alapprofil csak személyes másolatként menthető.');
    layout.validate();
    if (loadError != null) throw const FormatException('Előbb exportáld vagy javítsd a sérült személyes profilt.');
    final next = [...personal.where((p) => p.id != layout.id), layout];
    final file = File('${directory.path}/personal-layouts.json');
    final temporary = File('${file.path}.tmp');
    await temporary.writeAsString(jsonEncode(next.map((p) => p.data).toList()), flush: true);
    if (await file.exists()) await file.copy('${file.path}.bak');
    await temporary.rename(file.path);
    personal = next; notifyListeners();
  }
  Future<void> deleteLayout(String id) async {
    personal = personal.where((p) => p.id != id).toList();
    final file = File('${directory.path}/personal-layouts.json');
    final temporary = File('${file.path}.tmp');
    await temporary.writeAsString(jsonEncode(personal.map((p) => p.data).toList()), flush: true);
    await temporary.rename(file.path); notifyListeners();
  }
  StudioLayout selected(String role) {
    final personalId = prefs.getString('layout:$role:$vehicleId');
    final saved = personal.where((p) => p.id == personalId && p.vehicleId == vehicleId && p.role == role);
    if (saved.isNotEmpty) return saved.first;
    if (role == 'hybrid') return composeHybrid(vehicleId, vehicle.name, selected('dashboard'), selected('panel'));
    return role == 'panel' ? vehicle.panel : vehicle.dashboard;
  }
  Future<void> selectLayout(StudioLayout layout) => set('layout:${layout.role}:${layout.vehicleId}', layout.id);
}
