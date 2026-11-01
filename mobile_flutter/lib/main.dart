import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'connection.dart';
import 'display.dart';
import 'editor.dart';
import 'models.dart';
import 'storage.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    final store = StudioStore(); await store.load();
    final connection = BridgeConnection(store); await connection.initialize();
    runApp(StudioApp(store: store, connection: connection));
  } catch (error) {
    runApp(MaterialApp(theme: ThemeData.dark(), home: Scaffold(body: SafeArea(child: Padding(
      padding: const EdgeInsets.all(24), child: SelectableText('A SIM CONTROL STUDIO nem indítható.\n$error\nA személyes fájlok nem kerültek törlésre.'))))));
  }
}

class StudioApp extends StatelessWidget {
  final StudioStore store;
  final BridgeConnection connection;
  const StudioApp({super.key, required this.store, required this.connection});
  @override Widget build(BuildContext context) => AnimatedBuilder(animation: store, builder: (context, _) =>
    MaterialApp(title: 'SIM CONTROL STUDIO', debugShowCheckedModeBanner: false,
      theme: ThemeData(brightness: Brightness.dark, useMaterial3: true, scaffoldBackgroundColor: const Color(0xff101216),
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xffed3044), brightness: Brightness.dark,
          primary: const Color(0xffed3044), surface: const Color(0xff191d24)),
        appBarTheme: const AppBarTheme(backgroundColor: Color(0xff101216)),
        inputDecorationTheme: const InputDecorationTheme(border: OutlineInputBorder()),
        cardTheme: const CardThemeData(color: Color(0xff1a1e25), elevation: 0, margin: EdgeInsets.zero),
        filledButtonTheme: FilledButtonThemeData(style: FilledButton.styleFrom(minimumSize: const Size(48, 48)))),
      home: store.prefs.getBool('onboarded') == true ? StudioShell(store: store, connection: connection)
        : FirstRunWizard(store: store, connection: connection)));
}

class StudioShell extends StatefulWidget {
  final StudioStore store;
  final BridgeConnection connection;
  const StudioShell({super.key, required this.store, required this.connection});
  @override State<StudioShell> createState() => _StudioShellState();
}
class _StudioShellState extends State<StudioShell> {
  int _page = 0;
  StudioStore get store => widget.store;
  BridgeConnection get connection => widget.connection;
  static const _hu = ['Kezdőlap','Műszerfalak','Kezelőpanelek','Autóprofilok','Szerkesztő','Játékok','Csatlakozás','Eszközök','Telemetria','Beállítások'];
  static const _en = ['Home','Dashboards','Button boxes','Vehicles','Editor','Games','Connection','Devices','Telemetry','Settings'];
  static const _icons = [Icons.space_dashboard_outlined,Icons.speed,Icons.grid_view,Icons.sports_motorsports_outlined,Icons.tune,Icons.sports_esports_outlined,
    Icons.wifi,Icons.devices,Icons.monitor_heart_outlined,Icons.settings_outlined];
  String tr(String hu,String en) => store.language == 'en' ? en : hu;
  void _error(Object error) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error.toString()))); }
  Future<void> _use(VehicleProfile vehicle, String role, {bool open = true}) async {
    await store.set('vehicleId', vehicle.id); await store.set('role', role);
    if (connection.connected) await connection.refreshSettings();
    connection.selectProfile(vehicle.id);
    if (open && mounted) await Navigator.push(context, MaterialPageRoute<void>(builder: (_) => LiveDisplay(store: store, connection: connection, role: role)));
  }
  Future<void> _edit(StudioLayout layout) async {
    connection.releaseAll();
    await Navigator.push(context, MaterialPageRoute<void>(builder: (_) => LayoutEditor(store: store, connection: connection, layout: layout)));
    if (mounted) setState(() {});
  }
  Future<void> _import() async {
    try {
      final result = await FilePicker.platform.pickFiles(type: FileType.custom, allowedExtensions: ['json'], withData: false);
      if (result == null) return;
      final item = result.files.single;
      if (item.size > 18 * 1024 * 1024) throw const FormatException('A profil legfeljebb 18 MB lehet.');
      final bytes = item.bytes ?? await File(item.path!).readAsBytes();
      final map = jsonDecode(utf8.decode(bytes)) as Map<String, dynamic>;
      map['id'] = newId(); map['isBase'] = false;
      final layout = StudioLayout(map);
      if (!store.vehicles.any((v) => v.id == layout.vehicleId)) throw const FormatException('A profil autóazonosítója nincs a katalógusban.');
      await store.saveLayout(layout); if (mounted) setState(() {});
    } catch (error) { _error(error); }
  }
  Future<void> _newLayout(String role) async {
    final layout = StudioLayout({'schemaVersion':1,'id':newId(),'version':'0.2.0','revision':1,'name':role == 'panel' ? 'Új kezelőpanel' : 'Új műszerfal',
      'vehicleId':store.vehicleId,'role':role,'isBase':false,'width':1200,'height':700,'background':'#080a0c','supportedFields':<String>[],
      'pages':[{'id':newId(),'name':'Főoldal','elements':<Map<String,dynamic>>[]}]});
    await _edit(layout);
  }
  @override Widget build(BuildContext context) {
    final wide = MediaQuery.sizeOf(context).width >= 1050 && MediaQuery.sizeOf(context).height >= 800;
    final names = store.language == 'en' ? _en : _hu;
    return AnimatedBuilder(animation: connection, builder: (context, _) => Scaffold(
      appBar: AppBar(title: Row(children: [const _BrandMark(), const SizedBox(width: 12), Expanded(child: Text(names[_page], maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w700)))]),
        actions: [if (connection.isDemo) const DemoBadge() else Padding(padding: const EdgeInsets.only(right: 14), child: Chip(avatar: Icon(connection.connected ? Icons.link : Icons.link_off,
          size: 16, color: connection.connected ? Colors.greenAccent : Colors.amber), label: Text(connection.connected ? '${connection.latencyMs} ms' : tr('Nincs kapcsolat','Disconnected'))))]),
      drawer: wide ? null : Drawer(child: SafeArea(child: ListView(children: [const Padding(padding: EdgeInsets.all(20), child: Text('SIM CONTROL\nSTUDIO', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900))),
        for (var i = 0; i < names.length; i++) ListTile(selected: i == _page, leading: Icon(_icons[i]), title: Text(names[i]),
          onTap: () { setState(() => _page = i); Navigator.pop(context); })]))),
      body: Row(children: [if (wide) NavigationRail(selectedIndex: _page, labelType: NavigationRailLabelType.all,
        onDestinationSelected: (index) => setState(() => _page = index), destinations: [
          for (var i=0;i<names.length;i++) NavigationRailDestination(icon: Icon(_icons[i]), label: Text(names[i], style: const TextStyle(fontSize: 11))),
        ]), Expanded(child: switch (_page) {
          0 => _home(), 1 => _gallery('dashboard'), 2 => _gallery('panel'), 3 => _gallery('vehicle'), 4 => _editors(),
          5 => _games(), 6 => ConnectionPage(store: store, connection: connection), 7 => _devices(), 8 => _telemetry(), _ => _settings(),
        })]),
    ));
  }
  Widget _scroll(List<Widget> children) => ListView(padding: const EdgeInsets.all(22), children: children);
  Widget _title(String overline,String title,[String? subtitle]) => Padding(padding: const EdgeInsets.only(bottom: 22), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Text(overline, style: const TextStyle(color: Color(0xffed3044), fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 3)), const SizedBox(height: 8),
    Text(title, style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w800, height: 1.1)), if (subtitle != null) Padding(padding: const EdgeInsets.only(top: 10), child: Text(subtitle, style: const TextStyle(color: Colors.white54))),
  ]));
  Widget _home() => _scroll([
    SwitchListTile(title: const Text('DEMO mód'), subtitle: const Text('Szimulált adatok · PC és játék nélkül kipróbálható'), value: connection.localDemo, onChanged: connection.setDemo),
    _title('SIM CONTROL STUDIO / 0.2.0', tr('A pilótafülkéd. Minden kijelzőn.','Your cockpit. Every display.'), tr('Helyi hálózat. Élő telemetria. Saját elrendezések.','Local network. Live telemetry. Your layouts.')),
    LayoutBuilder(builder: (context,constraints) => Wrap(spacing: 12, runSpacing: 12, children: [
      for (final (title,value,icon) in [
        (tr('PC BRIDGE','PC BRIDGE'),connection.connected ? connection.bridgeVersion : '—',Icons.computer),
        (tr('KÉSLELTETÉS','LATENCY'),connection.connected ? '${connection.latencyMs} ms' : '—',Icons.network_check),
        (tr('ADATFORRÁS','SOURCE'),connection.gameId.isEmpty ? '—' : connection.gameId.toUpperCase(),Icons.sensors),
      ]) SizedBox(width: constraints.maxWidth < 600 ? constraints.maxWidth : (constraints.maxWidth - 24) / 3,
        child: Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [Icon(icon,color: Colors.white38,size:20), const SizedBox(width: 8), Text(title,style: const TextStyle(color: Colors.white54,fontSize:11,letterSpacing:2))]),
          const SizedBox(height: 15), Text(value, style: const TextStyle(fontSize: 25,fontWeight: FontWeight.w700,fontFamily:'monospace')),
        ])))),
    ])), const SizedBox(height: 24),
    if (connection.suggestedProfile != null && connection.suggestedProfile != store.vehicleId)
      Card(child: ListTile(leading: const Icon(Icons.devices,color:Colors.greenAccent), title: Text(tr('Profilajánlás másik készülékről','Profile suggestion')),
        subtitle: Text(store.vehicles.where((v)=>v.id==connection.suggestedProfile).firstOrNull?.name ?? connection.suggestedProfile!),
        trailing: FilledButton(onPressed: () async {
          final profile = store.vehicles.where((v)=>v.id==connection.suggestedProfile).firstOrNull;
          if (profile != null) await _use(profile,store.role,open:false); connection.dismissSuggestion();
        }, child: Text(tr('Elfogadás','Accept'))))),
    const SizedBox(height: 14),
    Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(tr('AKTÍV AUTÓPROFIL','ACTIVE VEHICLE'),style: const TextStyle(color:Colors.white54,letterSpacing:2,fontSize:11)),const SizedBox(height:8),
      Text(store.vehicle.name,style: const TextStyle(fontSize:24,fontWeight:FontWeight.w800)),const SizedBox(height:8),
      Text('${store.vehicle.data['modelYear']} · ${store.vehicle.category} · ${store.vehicle.data['fidelityLabel']}',style:const TextStyle(color:Colors.white54,fontSize:12)),
      const SizedBox(height:16), SizedBox(height:210,child: ValueListenableBuilder<TelemetryFrame?>(valueListenable:connection.telemetry,builder:(context,frame,_)=>LayoutCanvas(layout:store.selected(store.role),frame:frame))),
      const SizedBox(height:16), Wrap(spacing:10,runSpacing:10,children:[
        for (final (role,label,icon) in [('dashboard',tr('Műszerfal','Dashboard'),Icons.speed),('panel',tr('Kezelőpanel','Button box'),Icons.grid_view),('hybrid',tr('Hibrid','Hybrid'),Icons.view_column_outlined)])
          FilledButton.tonalIcon(onPressed:()=>_use(store.vehicle,role),icon:Icon(icon),label:Text(label)),
      ]),
    ]))), const SizedBox(height:18),
    if (!connection.connected) OutlinedButton.icon(onPressed:()=>setState(()=>_page=6),icon:const Icon(Icons.qr_code_scanner),label:Text(tr('PC Bridge csatlakoztatása','Connect PC Bridge'))),
    if (connection.lastError.isNotEmpty) Padding(padding:const EdgeInsets.only(top:12),child:Text(connection.lastError,style:const TextStyle(color:Colors.amber,fontSize:12))),
    const SizedBox(height:24), Text(tr('A kijelző csak friss, fogadott adatot mutat. A hiányzó adat helyén — látható.','Only fresh received values are shown. Unavailable data appears as —.'),style:const TextStyle(color:Colors.white38,fontSize:12)),
  ]);
  Widget _gallery(String role) => CustomScrollView(slivers:[
    SliverPadding(padding:const EdgeInsets.all(22),sliver:SliverToBoxAdapter(child:_title('20 AUTÓ / 40 ALAPELRENDEZÉS',role=='panel'?tr('Kezelőpanelek','Button boxes'):role=='dashboard'?tr('Műszerfalak','Dashboards'):tr('Autóprofilok','Vehicle profiles'),
      tr('Minden profil önállóan szerkeszthető. A referenciaállapotot a részletek mutatják.','Editable profiles with documented reference status.')))),
    SliverPadding(padding:const EdgeInsets.fromLTRB(22,0,22,22),sliver:SliverLayoutBuilder(builder:(context,constraints){
      final columns=constraints.crossAxisExtent>1100?3:constraints.crossAxisExtent>650?2:1;
      return SliverGrid(delegate:SliverChildBuilderDelegate((context,index){
        final vehicle=store.vehicles[index];final layout=role=='panel'?vehicle.panel:vehicle.dashboard;
        return Card(child:Padding(padding:const EdgeInsets.all(14),child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
          Expanded(child:ValueListenableBuilder<TelemetryFrame?>(valueListenable:connection.telemetry,builder:(context,frame,_)=>LayoutCanvas(layout:layout,frame:connection.localDemo?frame:null))),const SizedBox(height:10),Text(vehicle.name,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontWeight:FontWeight.w700,fontSize:16)),
          Text('${vehicle.category} / ${vehicle.data['modelYear']} · ${vehicle.fidelity=='partial_reference'?'Részleges referencia':'Autó által inspirált'}',style:const TextStyle(color:Colors.white38,fontSize:11)),
          const SizedBox(height:10),Row(children:[Expanded(child:FilledButton.tonal(onPressed:()=>_use(vehicle,role=='panel'?'panel':'dashboard'),child:Text(tr('Használat','Use')))),
            IconButton(onPressed:()=>_edit(layout),icon:const Icon(Icons.edit_outlined),tooltip:tr('Szerkesztés másolatként','Edit copy')),
            IconButton(onPressed:()=>_details(vehicle),icon:const Icon(Icons.info_outline),tooltip:tr('Referenciák','References'))]),
        ])));
      },childCount:store.vehicles.length),gridDelegate:SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount:columns,mainAxisSpacing:14,crossAxisSpacing:14,mainAxisExtent:330));
    })),
  ]);
  void _details(VehicleProfile vehicle) => showDialog<void>(context:context,builder:(context)=>AlertDialog(title:Text(vehicle.name),
    content:SizedBox(width:650,child:SingleChildScrollView(child:SelectableText([
      '${vehicle.data['modelYear']} · ${vehicle.data['fidelityLabel']}',
      'A gyári pixelgeometria és teljes kapcsolókiosztás nincs hitelesítve.',
      for(final ref in vehicle.data['references'] as List) '${ref['url']}\n${ref['scope']}\n${ref['status'] ?? ''}',
      ...(vehicle.data['knownLimitations'] as List).cast<String>(),
    ].join('\n\n')))),actions:[TextButton(onPressed:()=>Navigator.pop(context),child:const Text('Bezárás'))]));
  Widget _editors()=>_scroll([
    _title('LAYOUT STUDIO',tr('Építsd a saját kijelződet.','Build your own display.'),tr('Érintéses elrendezés, adatkapcsolatok, SVG és PNG.','Touch editing, telemetry bindings, SVG and PNG.')),
    Wrap(spacing:12,runSpacing:12,children:[FilledButton.icon(onPressed:()=>_newLayout('dashboard'),icon:const Icon(Icons.add),label:Text(tr('Új műszerfal','New dashboard'))),
      FilledButton.tonalIcon(onPressed:()=>_newLayout('panel'),icon:const Icon(Icons.add),label:Text(tr('Új kezelőpanel','New button box'))),
      FilledButton.tonalIcon(onPressed:()=>_edit(store.selected('hybrid')),icon:const Icon(Icons.view_column_outlined),label:Text(tr('Hibrid szerkesztése','Edit hybrid'))),
      OutlinedButton.icon(onPressed:_import,icon:const Icon(Icons.file_open_outlined),label:const Text('Import JSON'))]),
    const SizedBox(height:24),Text(tr('Kiválasztott autó alapprofiljai','Base profiles for the selected vehicle'),style:const TextStyle(fontSize:20,fontWeight:FontWeight.bold)),const SizedBox(height:12),
    for(final layout in [store.vehicle.dashboard,store.vehicle.panel]) Card(child:ListTile(title:Text(layout.name),subtitle:Text(tr('Szerkesztéskor személyes másolat készül.','Editing creates a personal copy.')),trailing:const Icon(Icons.chevron_right),onTap:()=>_edit(layout))),
    const SizedBox(height:24),Text(tr('Személyes profilok','Personal profiles'),style:const TextStyle(fontSize:20,fontWeight:FontWeight.bold)),const SizedBox(height:12),
    if(store.loadError!=null)Text(store.loadError!,style:const TextStyle(color:Colors.amber)),
    if(store.personal.isEmpty)Text(tr('Még nincs mentett saját profil.','No personal profiles yet.'),style:const TextStyle(color:Colors.white54)),
    for(final layout in store.personal) Card(child:ListTile(title:Text(layout.name),subtitle:Text('${layout.role} · ${layout.data['revision']}'),onTap:()=>_edit(layout),trailing:IconButton(icon:const Icon(Icons.file_upload_outlined),onPressed:()=>shareJson(context,store,'sim-control-profile.json',layout.data)))),
  ]);
  Widget _games()=>_scroll([
    _title('GAME ADAPTERS',tr('A forrás határozza meg az adatokat.','The source determines the data.'),tr('Valós játékban még egyik integráció sem kapott tesztigazolást ebben a kiadásban.','No physical game verification has been performed for this release.')),
    for(final game in store.games)Card(child:ListTile(leading:Icon(game['implemented']==true?Icons.cable:Icons.extension_outlined,color:game['implemented']==true?Colors.greenAccent:Colors.white24),title:Text(game['name'] as String),
      subtitle:Text(game['status'] as String),trailing:game['implemented']==true?const Chip(label:Text('Éles teszt szükséges')):null)),
    const SizedBox(height:18),const Text('A játékválasztást és a PC-billentyűkiosztást a Bridge felületén állítsd be. Az internetes és online módok támogatása csak az adott játék által kiadott telemetriára terjedhet ki.',style:TextStyle(color:Colors.white54)),
  ]);
  Widget _devices()=>_scroll([
    _title('MULTI DEVICE',tr('Egy PC. Több szerepkör.','One PC. Multiple roles.')),
    Card(child:ListTile(leading:const Icon(Icons.smartphone),title:Text(store.prefs.getString('deviceName')??'Ez a készülék'),subtitle:Text('${store.role} · ${store.vehicle.name}\n${connection.connected?'Csatlakoztatva':'Nincs kapcsolat'}'),isThreeLine:true)),
    const SizedBox(height:18),const Text('Műszerfalhoz olvasási jogosultság elegendő. A kezelőpanel vezérlését a PC-n eszközönként kell engedélyezni.',style:TextStyle(color:Colors.white54)),
    const SizedBox(height:18),for(final role in ['dashboard','panel','hybrid'])ListTile(title:Text(role),leading:Icon(store.role==role?Icons.radio_button_checked:Icons.radio_button_off),onTap:()async{await store.set('role',role);await connection.refreshSettings();}),
    for(final device in connection.clients)Card(child:ListTile(leading:const Icon(Icons.devices), title:Text(device['name']?.toString()??''),subtitle:Text('${device['role']} · ${device['profileId']} / ${device['layoutId']??'—'} · ${device['hz']} Hz · ${device['latencyMs']??'—'} ms · ${device['connectionQuality']}'))),
    const SizedBox(height:12),SwitchListTile(title:Text(tr('Profilajánlások más készülékektől','Profile suggestions')),value:store.suggestions,onChanged:(v)=>store.set('suggestions',v)),
    const SizedBox(height:18),const Text('Az összes párosított készülék kezelése és a jogosultságok visszavonása a Windows Bridge Eszközök oldalán érhető el.'),
  ]);
  Widget _telemetry()=>AnimatedBuilder(animation:connection.ticks,builder:(context,_) {
    final frame=connection.telemetry.value;
    return _scroll([_title('LIVE DATA / DIAGNOSTICS',tr('Telemetria','Telemetry'),'${connection.gameId} · ${connection.health['state']??'waiting'} · ${frame?.fresh==true?'FRISS':'NINCS FRISS ADAT'}'),
      Wrap(spacing:12,children:[OutlinedButton.icon(onPressed:()=>shareJson(context,store,'sim-control-mobile-diagnostics.json',connection.diagnosticReport()),icon:const Icon(Icons.download_outlined),label:Text(tr('Jelentés exportálása','Export report'))),
        Text('Bridge ${connection.bridgeVersion.isEmpty?'—':connection.bridgeVersion} / ${connection.latencyMs} ms')]),const SizedBox(height:16),
      if(frame==null)const Padding(padding:EdgeInsets.all(24),child:Text('Még nem érkezett telemetriacsomag. Indíts valódi játékmenetet és ellenőrizd a Bridge diagnosztikáját.')),
      if(frame!=null)for(final entry in frame.fields.entries)Card(child:ListTile(title:Text('${entry.key}  ${frame.value(entry.key)??'—'} ${entry.value.unit}',style:const TextStyle(fontFamily:'monospace',fontSize:13)),
        subtitle:Text('${entry.value.source}\n${entry.value.validity} · ${entry.value.derived?'számított':'forrásadat'} · ${entry.value.timestampMs} ms UTC',style:const TextStyle(fontSize:11)),isThreeLine:true)),
      const SizedBox(height:24),Text(tr('Parancs-visszaigazolások','Command acknowledgments'),style:const TextStyle(fontSize:20,fontWeight:FontWeight.bold)),
      for(final command in connection.commandHistory.reversed.take(20))ListTile(title:Text('${command['action']} · ${command['stage']}'),subtitle:Text(command['reason']?.toString()??'A PC-bemenet elküldése nem igazolja önmagában a játék állapotváltozását.')),
    ]);
  });
  Widget _settings()=>_scroll([
    SwitchListTile(title: const Text('DEMO mód'), subtitle: const Text('Szimulált forrás; nem küld PC-bemenetet'), value: connection.localDemo, onChanged: connection.setDemo),
    _title('SETTINGS',tr('A saját eszközödre hangolva.','Tune your device.')),
    DropdownButtonFormField<String>(initialValue:store.language,decoration:const InputDecoration(labelText:'Nyelv / Language'),items:const[DropdownMenuItem(value:'hu',child:Text('Magyar')),DropdownMenuItem(value:'en',child:Text('English'))],onChanged:(value)=>store.set('language',value!)),const SizedBox(height:18),
    DropdownButtonFormField<int>(initialValue:store.hz,decoration:InputDecoration(labelText:tr('Kért telemetria-gyakoriság','Requested telemetry rate')),items:[20,30,60].map((hz)=>DropdownMenuItem(value:hz,child:Text('$hz Hz'))).toList(),onChanged:(value)async{await store.set('hz',value!);await connection.refreshSettings();}),
    const SizedBox(height:18),TextFormField(initialValue:store.prefs.getString('deviceName')??'',maxLength:60,decoration:InputDecoration(labelText:tr('Készülék neve','Device name')),onFieldSubmitted:(value)async{if(value.trim().isNotEmpty){await store.set('deviceName',value.trim());await connection.refreshSettings();}}),
    SwitchListTile(title:Text(tr('Érintéses rezgés','Haptic feedback')),value:store.haptic,onChanged:(value)=>store.set('haptic',value)),
    const SizedBox(height:24),const Text('SIM CONTROL STUDIO 0.2.0\nNatív Flutter / helyi TLS-kapcsolat\nNincs regisztráció, előfizetés vagy felhőszolgáltatás.',style:TextStyle(color:Colors.white54)),
    const SizedBox(height:18),OutlinedButton(onPressed:()async{await store.set('onboarded',false);if(mounted){Navigator.pushReplacement(context,MaterialPageRoute<void>(builder:(_)=>FirstRunWizard(store:store,connection:connection)));}},child:Text(tr('Konfigurációs varázsló újraindítása','Run setup wizard'))),
  ]);
}

class _BrandMark extends StatelessWidget {
  const _BrandMark();
  @override Widget build(BuildContext context)=>Transform(transform:Matrix4.skewX(-.22),child:Row(mainAxisSize:MainAxisSize.min,children:[
    Container(width:7,height:26,color:const Color(0xffed3044)),const SizedBox(width:4),Container(width:12,height:26,color:const Color(0xffed3044))]));
}

class ConnectionPage extends StatefulWidget {
  final StudioStore store;final BridgeConnection connection;
  const ConnectionPage({super.key,required this.store,required this.connection});
  @override State<ConnectionPage> createState()=>_ConnectionPageState();
}
class _ConnectionPageState extends State<ConnectionPage> {
  final _uri=TextEditingController(),_host=TextEditingController(),_port=TextEditingController(text:'19760'),_pin=TextEditingController(),_token=TextEditingController();
  bool _busy=false;String _error='';
  Future<void> _pair(BridgeTarget target)async{
    final confirmed=await showDialog<bool>(context:context,builder:(context)=>AlertDialog(title:const Text('PC Bridge ellenőrzése'),
      content:SingleChildScrollView(child:SelectableText('${target.host}:${target.port}\n\nSHA-256\n${target.pin}\n\nA teljes ujjlenyomat egyezzen a PC Bridge felületén látható értékkel.')),
      actions:[TextButton(onPressed:()=>Navigator.pop(context,false),child:const Text('Mégse')),FilledButton(onPressed:()=>Navigator.pop(context,true),child:const Text('Egyezik · Párosítás'))]));
    if(confirmed!=true)return;
    setState(()=>_busy=true);
    try{await widget.connection.pair(target);}catch(e){if(mounted)setState(()=>_error=e.toString());}
    finally{if(mounted)setState(()=>_busy=false);}
  }
  Future<void> _scan()async{
    final result=await Navigator.push<String>(context,MaterialPageRoute(builder:(_)=>const _Scanner()));
    if(result!=null&&mounted){_uri.text=result;try{await _pair(BridgeTarget.fromUri(result));}catch(e){setState(()=>_error=e.toString());}}
  }
  Future<void> _discover()async{
    setState(()=>_busy=true);
    try{
      final results=await discoverBridges();
      if(!mounted)return;
      if(results.isEmpty){setState(()=>_error='Nem érkezett válasz. Használd a QR-kódot vagy a kézi IP-címet.');return;}
      final target=await showDialog<BridgeTarget>(context:context,builder:(context)=>SimpleDialog(title:const Text('Elérhető Bridge-ek'),children:[
        for(final t in results)SimpleDialogOption(onPressed:()=>Navigator.pop(context,t),child:Text('${t.host}:${t.port}\n${t.pin.substring(0,16)}…'))]));
      if(target!=null){_host.text=target.host;_port.text=target.port.toString();_pin.text=target.pin;setState(()=>_error='A felderítés önmagában nem hitelesítés. Hasonlítsd össze az ujjlenyomatot, és másold át a PC-n megnyitott párosítási tokent.');}
    }catch(e){if(mounted)setState(()=>_error='A hálózat nem támogatja a felderítést: $e');}
    finally{if(mounted)setState(()=>_busy=false);}
  }
  @override Widget build(BuildContext context)=>AnimatedBuilder(animation:widget.connection,builder:(context,_)=>ListView(padding:const EdgeInsets.all(22),children:[
    const Text('PC BRIDGE / PÁROSÍTÁS',style:TextStyle(color:Color(0xffed3044),letterSpacing:3,fontWeight:FontWeight.w700)),const SizedBox(height:12),
    Text(widget.connection.connected?'Kapcsolódva':'Csatlakozz a PC-hez.',style:const TextStyle(fontSize:30,fontWeight:FontWeight.w800)),const SizedBox(height:10),
    Text(widget.connection.target==null?'A PC és a mobil ugyanazon elérhető helyi hálózaton legyen.': '${widget.connection.target!.host}:${widget.connection.target!.port}',style:const TextStyle(color:Colors.white54)),
    const SizedBox(height:20),Wrap(spacing:12,runSpacing:12,children:[FilledButton.icon(onPressed:_busy?null:_scan,icon:const Icon(Icons.qr_code_scanner),label:const Text('QR-kód beolvasása')),
      OutlinedButton.icon(onPressed:_busy?null:_discover,icon:const Icon(Icons.radar),label:const Text('Automatikus felderítés'))]),
    const SizedBox(height:20),TextField(controller:_uri,maxLines:3,decoration:const InputDecoration(labelText:'Teljes párosítási hivatkozás',hintText:'simcontrol://pair?host=…')),
    const SizedBox(height:12),FilledButton.tonal(onPressed:_busy?null:()async{try{await _pair(BridgeTarget.fromUri(_uri.text));}catch(e){setState(()=>_error=e.toString());}},child:const Text('Csatlakozás hivatkozással')),
    const SizedBox(height:18),ExpansionTile(title:const Text('Manuális IP-cím és port'),children:[
      TextField(controller:_host,decoration:const InputDecoration(labelText:'PC IPv4-címe',hintText:'192.168.1.20'),keyboardType:TextInputType.url),const SizedBox(height:12),
      TextField(controller:_port,decoration:const InputDecoration(labelText:'TLS port'),keyboardType:TextInputType.number),const SizedBox(height:12),
      TextField(controller:_pin,decoration:const InputDecoration(labelText:'Tanúsítvány teljes SHA-256 ujjlenyomata')),const SizedBox(height:12),
      TextField(controller:_token,decoration:const InputDecoration(labelText:'Párosítási token (120 másodpercig érvényes)'),obscureText:true),const SizedBox(height:12),
      FilledButton(onPressed:_busy?null:()async{try{await _pair(BridgeTarget(_host.text.trim(),int.tryParse(_port.text)??0,_pin.text.trim(),token:_token.text.trim().isEmpty?null:_token.text.trim()));}catch(e){setState(()=>_error=e.toString());}},child:const Text('Manuális csatlakozás')),
    ]),const SizedBox(height:12),if(_busy)const LinearProgressIndicator(),
    if(_error.isNotEmpty)Padding(padding:const EdgeInsets.symmetric(vertical:12),child:Text(_error,style:const TextStyle(color:Colors.amber))),
    if(widget.connection.lastError.isNotEmpty)Text(widget.connection.lastError,style:const TextStyle(color:Colors.amber,fontSize:12)),
    const SizedBox(height:18),if(widget.connection.target!=null)Wrap(spacing:12,runSpacing:12,children:[OutlinedButton(onPressed:()=>widget.connection.refreshSettings(),child:const Text('Újracsatlakozás')),
      TextButton(onPressed:()=>widget.connection.forget(),child:const Text('Mentett kapcsolat elfelejtése'))]),
    const SizedBox(height:24),const Text('A PC vezetékes Etherneten is kapcsolódhat. Vendéghálózati elkülönítés és VPN megakadályozhatja a helyi elérést. A QR-kód internet nélkül használható.',style:TextStyle(color:Colors.white38,fontSize:12)),
  ]));
  @override void dispose(){for(final controller in [_uri,_host,_port,_pin,_token]){controller.dispose();}super.dispose();}
}

class _Scanner extends StatefulWidget {
  const _Scanner();
  @override State<_Scanner> createState()=>_ScannerState();
}
class _ScannerState extends State<_Scanner>{
  bool _returned=false;
  @override Widget build(BuildContext context)=>Scaffold(appBar:AppBar(title:const Text('PC Bridge QR-kód')),body:MobileScanner(onDetect:(capture){
    if(_returned)return;
    for(final code in capture.barcodes){if(code.rawValue?.startsWith('simcontrol://pair?')==true){_returned=true;Navigator.pop(context,code.rawValue);break;}}
  },errorBuilder:(context,error)=>Center(child:Padding(padding:const EdgeInsets.all(24),child:Text('A kamera nem elérhető. Engedélyezd a kamerát, vagy használd a kézi párosítást.\n$error')))));
}

class FirstRunWizard extends StatefulWidget{
  final StudioStore store;final BridgeConnection connection;
  const FirstRunWizard({super.key,required this.store,required this.connection});
  @override State<FirstRunWizard> createState()=>_FirstRunWizardState();
}
class _FirstRunWizardState extends State<FirstRunWizard>{
  int _step=0;
  Future<void> _finish()async{
    await widget.store.set('onboarded',true);
    if(mounted)Navigator.pushReplacement(context,MaterialPageRoute<void>(builder:(_)=>StudioShell(store:widget.store,connection:widget.connection)));
  }
  @override Widget build(BuildContext context)=>Scaffold(appBar:AppBar(title:const Text('SIM CONTROL STUDIO / Beállítás')),
    body:Column(children:[LinearProgressIndicator(value:(_step+1)/4),Expanded(child:switch(_step){
      0=>ListView(padding:const EdgeInsets.all(24),children:[const Text('Üdv a pilótafülkében.',style:TextStyle(fontSize:32,fontWeight:FontWeight.w800)),const SizedBox(height:18),
        const Text('Válassz nyelvet. A teljes rendszer helyi hálózaton működik, regisztráció nélkül.'),const SizedBox(height:24),
        for(final (id,name) in [('hu','Magyar'),('en','English')])ListTile(leading:Icon(widget.store.language==id?Icons.radio_button_checked:Icons.radio_button_off),title:Text(name),onTap:()async{await widget.store.set('language',id);if(mounted)setState((){});})]),
      1=>Column(children:[ListTile(title:const Text('Kipróbálás PC nélkül'),trailing:FilledButton(onPressed:()async{await widget.connection.setDemo(true);if(mounted)setState(()=>_step=2);},child:const Text('DEMO'))),Expanded(child:ConnectionPage(store:widget.store,connection:widget.connection))]),
      2=>ListView(padding:const EdgeInsets.all(24),children:[const Text('A készülék szerepe és autója',style:TextStyle(fontSize:26,fontWeight:FontWeight.bold)),const SizedBox(height:20),
        for(final (id,label) in [('dashboard','Műszerfal'),('panel','Kezelőpanel'),('hybrid','Hibrid')])ListTile(leading:Icon(widget.store.role==id?Icons.radio_button_checked:Icons.radio_button_off),title:Text(label),onTap:()async{await widget.store.set('role',id);if(mounted)setState((){});}),
        const SizedBox(height:24),DropdownButtonFormField<String>(initialValue:widget.store.vehicleId,isExpanded:true,items:widget.store.vehicles.map((v)=>DropdownMenuItem(value:v.id,child:Text(v.name,overflow:TextOverflow.ellipsis))).toList(),onChanged:(v)async{await widget.store.set('vehicleId',v!);setState((){});}),
        const SizedBox(height:18),Text('Műszerfal: ${widget.store.vehicle.dashboard.name}\nKezelőpanel: ${widget.store.vehicle.panel.name}\nA profilpár később külön is módosítható.',style:const TextStyle(color:Colors.white54))]),
      _=>ListView(padding:const EdgeInsets.all(24),children:[const Text('Első telemetriateszt',style:TextStyle(fontSize:28,fontWeight:FontWeight.w800)),const SizedBox(height:18),
        const Text('Indítsd el a Bridge-et és a játék valódi játékmenetét. A kijelzőn a sebességnek, fordulatszámnak és fokozatnak követnie kell a játékot.\n\nA kezelőpanelhez a PC-n engedélyezd ezt az eszközt, majd rendeld hozzá a játék billentyűit.'),
        const SizedBox(height:20),FilledButton.icon(onPressed:()async{await widget.connection.refreshSettings();if(context.mounted)await Navigator.push(context,MaterialPageRoute<void>(builder:(_)=>LiveDisplay(store:widget.store,connection:widget.connection,role:widget.store.role)));},icon:const Icon(Icons.play_arrow),label:const Text('Kijelző megnyitása')),
        const SizedBox(height:18),const Text('Kapcsolat nélkül a műszerek — jelet mutatnak. A tesztet később is elvégezheted.',style:TextStyle(color:Colors.white54))]),
    }),SafeArea(top:false,child:Padding(padding:const EdgeInsets.all(16),child:Row(children:[if(_step>0)TextButton(onPressed:()=>setState(()=>_step--),child:const Text('Vissza')),const Spacer(),
      FilledButton(onPressed:_step==3?_finish:()=>setState(()=>_step++),child:Text(_step==3?'Beállítás befejezése':'Tovább'))])))]));
}
