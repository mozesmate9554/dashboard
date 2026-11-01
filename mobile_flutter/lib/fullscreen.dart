import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:wakelock_plus/wakelock_plus.dart';

/// Owns fullscreen only for the lifetime of one cockpit route.
class StudioFullscreen with WidgetsBindingObserver {
  static const channel = MethodChannel('hu.simcontrol.studio/fullscreen');
  final TargetPlatform platform;
  bool _active = false;
  int _epoch = 0;
  String? lastError;
  StudioFullscreen({TargetPlatform? platform}) : platform = platform ?? defaultTargetPlatform;
  Future<void> enter() async {
    if (!_active) WidgetsBinding.instance.addObserver(this);
    _active = true;
    await _apply(++_epoch);
  }
  Future<void> _apply(int epoch) async {
    try { await WakelockPlus.enable(); } catch (e) { lastError = 'wakelock: $e'; }
    if (!_active || epoch != _epoch) return;
    try {
      // iOS supports status-bar hiding and Home-indicator auto-hide through this API.
      await SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
      if (!_active || epoch != _epoch) return;
      if (platform == TargetPlatform.android) {
        // Flutter's legacy modes are ignored with target API 36; use public native insets APIs.
        await channel.invokeMethod<void>('setFullscreen', {'enabled': true});
      }
    } catch (e) { lastError = 'fullscreen: $e'; }
  }
  Future<void> orientation(String value) async {
    if (!_active) return;
    await SystemChrome.setPreferredOrientations(switch(value) {
    'portrait' => [DeviceOrientation.portraitUp],
    'landscape' => [DeviceOrientation.landscapeLeft,DeviceOrientation.landscapeRight],
    _ => [],
  });
  }
  Future<Map<String,dynamic>> inspect() async {
    if (platform != TargetPlatform.android) return {'requested':_active,'platform':platform.name,'homeIndicator':'OS-controlled auto-hide'};
    return Map<String,dynamic>.from(await channel.invokeMethod<Map>('getState') ?? {});
  }
  Future<void> leave() async {
    _active = false; _epoch++;
    WidgetsBinding.instance.removeObserver(this);
    try {
      if (platform == TargetPlatform.android) await channel.invokeMethod<void>('setFullscreen', {'enabled':false});
    } catch (e) { lastError = 'native restore: $e'; }
    try {
      await SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
      await SystemChrome.setPreferredOrientations([]);
      await WakelockPlus.disable();
    } catch (e) { lastError = 'restore: $e'; }
  }
  @override void didChangeAppLifecycleState(AppLifecycleState state) {
    if (!_active) return;
    if (state == AppLifecycleState.resumed) { unawaited(_apply(++_epoch)); }
    if (state == AppLifecycleState.paused || state == AppLifecycleState.inactive) {
      _epoch++; unawaited(WakelockPlus.disable().catchError((Object e) { lastError='wakelock: $e'; }));
    }
  }
}
