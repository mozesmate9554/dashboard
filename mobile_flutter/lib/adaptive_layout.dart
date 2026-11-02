import 'dart:math' as math;
import 'package:flutter/widgets.dart';
import 'models.dart';

const controlKinds = {'button','hold','toggle','threeState','multiState','rotary','stepper','slider','icon',
  'rocker','pushButton','guarded','rotarySwitch','cycleButton'};

/// A temporary presentation derived from a saved layout. Saved geometry never changes.
StudioLayout adaptLayout(StudioLayout source, int page, Size viewport) {
  // Reference-drawn 0.4.0 button boxes keep their exact proportions; they are only scaled uniformly.
  if (source.data['adaptive'] == 'preserve') return source;
  final factor = math.max(320 / viewport.width, 200 / viewport.height).clamp(1.0, 10.0).toDouble();
  final width = (viewport.width * factor).clamp(320.0,4096.0).toDouble();
  final height = (viewport.height * factor).clamp(200.0,4096.0).toDouble();
  final data = deepCopy(source.data);
  final items = source.elements(page).map(deepCopy).toList();
  void scaleOriginal() {
    for (final e in items) {
      e['x'] = (e['x'] as num) / source.width * width;
      e['y'] = (e['y'] as num) / source.height * height;
      e['w'] = math.max(12.0, (e['w'] as num) / source.width * width);
      e['h'] = math.max(12.0, (e['h'] as num) / source.height * height);
      e['x'] = (e['x'] as num).clamp(0,width-(e['w'] as num));
      e['y'] = (e['y'] as num).clamp(0,height-(e['h'] as num));
    }
  }
  final List<Map<String,dynamic>> visible = items;
  List<List<Map<String,dynamic>>>? mobilePages;
  if (source.role == 'panel') {
    final controls = items.where((e)=>controlKinds.contains(e['kind'])).toList();
    if (controls.isEmpty) { scaleOriginal(); }
    else { mobilePages = _controlPages(controls,Rect.fromLTWH(8,8,width-16,height-16)); }
  } else if (source.role == 'hybrid') {
    final controls=items.where((e)=>controlKinds.contains(e['kind'])).toList();
    final instruments=items.where((e)=>!controlKinds.contains(e['kind']) && !{'text','svg','image'}.contains(e['kind'])).toList();
    if (controls.isEmpty || instruments.isEmpty) { scaleOriginal(); }
    else {
      final instrumentArea=height>width?Rect.fromLTWH(8,8,width-16,height*.48-12):Rect.fromLTWH(8,8,width*.62-12,height-16);
      final controlArea=height>width?Rect.fromLTWH(8,height*.48+4,width-16,height*.52-12):Rect.fromLTWH(width*.62+4,8,width*.38-12,height-16);
      final controlPages=_controlPages(controls,controlArea);
      final instrumentPages=_instrumentPages(instruments,instrumentArea,repeatPrimary:true);
      mobilePages=[];
      for(var i=0;i<math.max(controlPages.length,instrumentPages.length);i++){
        final copy=instrumentPages[i%instrumentPages.length].map(deepCopy).toList();
        for(final e in copy) { e['id']='${e['id']}@mobile$i'; }
        _dashboard(copy,instrumentArea,height>width);
        final controlsCopy=controlPages[i%controlPages.length].map(deepCopy).toList();
        for(final e in controlsCopy){e['id']='${e['id']}@group$i';}
        mobilePages.add([...copy,...controlsCopy]);
      }
    }
  } else {
    final instruments=items.where((e)=>!{'text','svg','image'}.contains(e['kind'])).toList();
    if (instruments.isEmpty) { scaleOriginal(); }
    else {
      final area=Rect.fromLTWH(8,8,width-16,height-16);
      mobilePages=_instrumentPages(instruments,area);
      for(final group in mobilePages){_dashboard(group,area,height>width);}
    }
  }
  data['width']=width;data['height']=height;
  data['pages']=[for(var i=0;i<(mobilePages?.length??1);i++) {'id':'${source.pages[page]['id']}@mobile$i','name':source.pages[page]['name'],'elements':mobilePages?[i]??visible}];
  data['presentation']='adaptive';
  return StudioLayout(data);
}

List<List<Map<String,dynamic>>> _instrumentPages(List<Map<String,dynamic>> items, Rect area,{bool repeatPrimary=false}){
  final columns=math.max(1,(area.width/148).floor());
  final rows=math.max(1,((area.height-26)/100).floor());
  final capacity=math.max(columns*rows,(items.length/8).ceil());
  final pages=<List<Map<String,dynamic>>>[];
  if(repeatPrimary && items.length>capacity){
    final primary=items.where((e)=>{'gear','speed','rpm'}.contains(e['field'])).toList();
    final rest=items.where((e)=>!primary.contains(e)).toList();
    final chunk=math.max(2,math.max(capacity-primary.length,(rest.length/8).ceil()));
    for(var offset=0;offset<rest.length;offset+=chunk){
      pages.add([...primary,...rest.sublist(offset,math.min(rest.length,offset+chunk))]);
    }
    return pages.isEmpty?[items]:pages;
  }
  for(var offset=0;offset<items.length;offset+=capacity){
    pages.add(items.sublist(offset,math.min(items.length,offset+capacity)));
  }
  return pages;
}

List<List<Map<String,dynamic>>> _controlPages(List<Map<String,dynamic>> controls, Rect area){
  final columns=math.max(1,((area.width+8)/148).floor());
  final rows=math.max(1,((area.height+8)/108).floor());
  final capacity=math.max(columns*rows,(controls.length/8).ceil());
  final pages=<List<Map<String,dynamic>>>[];
  for(var offset=0;offset<controls.length;offset+=capacity){
    final group=controls.sublist(offset,math.min(controls.length,offset+capacity));
    _grid(group,area);pages.add(group);
  }
  return pages;
}

void _place(Map<String,dynamic> item, Rect rect) {
  item['x']=rect.left;item['y']=rect.top;item['w']=rect.width;item['h']=rect.height;
  item['rotation']=0; // Adaptive reading orientation; original rotation stays in the saved layout.
  item['fontSize']=(item['fontSize'] as num? ?? (controlKinds.contains(item['kind'])?20:48)).clamp(14,140);
  if(item['style']=='factoryReadout')item['style']='adaptiveReadout';
  if(item['style']=='factoryMap')item['style']='adaptiveMap';
}
void _grid(List<Map<String,dynamic>> items, Rect area) {
  if (items.isEmpty) return;
  const gap=8.0;
  final ideal=math.sqrt(items.length*area.width/area.height).ceil();
  final columns=ideal.clamp(1,math.max(1,(area.width/140).floor())).toInt();
  final rows=(items.length/columns).ceil();
  final cellW=(area.width-gap*(columns-1))/columns;
  final cellH=(area.height-gap*(rows-1))/rows;
  for(var i=0;i<items.length;i++) {
    _place(items[i],Rect.fromLTWH(area.left+(i%columns)*(cellW+gap),area.top+(i~/columns)*(cellH+gap),cellW,cellH));
  }
}
void _dashboard(List<Map<String,dynamic>> items, Rect area, bool portrait) {
  final leds=items.where((e)=>e['kind']=='leds').toList();
  final rest=items.where((e)=>e['kind']!='leds').toList();
  double top=area.top;
  for(final led in leds) {
    _place(led,Rect.fromLTWH(area.left,top,area.width,20)); led['vertical']=false;led['rows']=1; top+=26;
  }
  if(area.height<420){
    _grid(rest,Rect.fromLTWH(area.left,top,area.width,area.bottom-top));
    return;
  }
  final primary=rest.where((e)=>{'gear','speed','rpm'}.contains(e['field']) && {'gear','number','analog'}.contains(e['kind'])).toList();
  final secondary=rest.where((e)=>!primary.contains(e)).toList();
  final available=area.bottom-top;
  final hero=secondary.isEmpty?available:available*(portrait ? .46 : .6);
  if(primary.isNotEmpty) {
    final gear=primary.where((e)=>e['field']=='gear').firstOrNull;
    if(gear!=null && primary.length<=3) {
      _place(gear,Rect.fromLTWH(area.left,top,area.width*.5-4,hero-8));
      final others=primary.where((e)=>e!=gear).toList();
      for(var i=0;i<others.length;i++) { _place(others[i],Rect.fromLTWH(area.left+area.width*.5+4,top+i*hero/others.length,area.width*.5-4,hero/others.length-8)); }
    } else { _grid(primary,Rect.fromLTWH(area.left,top,area.width,hero-8)); }
  }
  _grid(secondary,Rect.fromLTWH(area.left,primary.isEmpty?top:top+hero,area.width,primary.isEmpty?available:available-hero));
}
