using System.Net;
using System.Text.Json;
using System.Net.NetworkInformation;
using System.Security.Cryptography.X509Certificates;
using QRCoder;

namespace SimControlStudio.Windows;

public sealed class MainForm : Form
{
    private readonly string _directory = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "SimControlStudio");
    private readonly BridgeConfiguration _config;
    private readonly DeviceRegistry _registry;
    private readonly X509Certificate2 _certificate;
    private BridgeRuntime? _bridge;
    private readonly NotifyIcon _tray;
    private readonly System.Windows.Forms.Timer _refresh = new() { Interval = 500 };
    private readonly ComboBox _game = new() { DropDownStyle = ComboBoxStyle.DropDownList, Width = 280 };
    private readonly ComboBox _address = new() { DropDownStyle = ComboBoxStyle.DropDownList, Width = 280 };
    private readonly ComboBox _hz = new() { DropDownStyle = ComboBoxStyle.DropDownList, Width = 100 };
    private readonly NumericUpDown _port = new() { Minimum = 1024, Maximum = 65535, Value = 19760, Width = 100 };
    private readonly CheckBox _lan = new() { Text = "Helyi hálózat engedélyezése", AutoSize = true };
    private readonly CheckBox _control = new() { Text = "Mobilvezérlés engedélyezése (csak az előtérben futó játékhoz)", AutoSize = true };
    private readonly Button _start = new() { Text = "Bridge indítása", AutoSize = true };
    private readonly Label _status = new() { AutoSize = true, MaximumSize = new Size(850, 0), Font = new Font("Segoe UI", 11) };
    private readonly PictureBox _qr = new() { Size = new Size(300, 300), SizeMode = PictureBoxSizeMode.Zoom, BackColor = Color.White };
    private readonly TextBox _pairUri = new() { ReadOnly = true, Multiline = true, Width = 580, Height = 85 };
    private readonly Label _pairTime = new() { AutoSize = true };
    private readonly ListBox _devices = new() { Width = 860, Height = 220 };
    private readonly DataGridView _bindings = new() { Dock = DockStyle.Fill, AllowUserToAddRows = true, AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill };
    private readonly TextBox _diagnostic = new() { ReadOnly = true, Multiline = true, ScrollBars = ScrollBars.Vertical, Dock = DockStyle.Fill, Font = new Font("Consolas", 10) };
    private readonly ComboBox _profileMap = new() { DropDownStyle = ComboBoxStyle.DropDownList, Width = 280 };
    private string? MappingProfile => _profileMap.SelectedIndex > 0 ? _profileMap.SelectedItem?.ToString() : null;
    private bool _exiting;
    private bool _starting;
    private readonly string[] _ids = ["acr", "ac", "acc", "beamng", "demo"];
    public MainForm()
    {
        Directory.CreateDirectory(_directory);
        try { _config = BridgeConfiguration.Load(ConfigPath); }
        catch (Exception e) when (e is ArgumentException or System.Text.Json.JsonException or InvalidDataException)
        {
            MessageBox.Show("A konfiguráció nem tölthető be. Az eredeti fájl megmarad.\n" + e.Message, "Konfigurációs hiba");
            _config = new();
        }
        _registry = new(Path.Combine(_directory, "devices.json"));
        _certificate = BridgeCertificate.LoadOrCreate(_directory);
        Text = "SIM CONTROL STUDIO 0.3.0 · PC Bridge";
        Size = new Size(1030, 780); MinimumSize = new Size(860, 650);
        BackColor = Color.FromArgb(19, 21, 25); ForeColor = Color.WhiteSmoke;
        Font = new Font("Segoe UI", 10);
        var tabs = new TabControl { Dock = DockStyle.Fill };
        Controls.Add(tabs);
        var connection = Page(tabs, "Kapcsolat");
        var flow = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.TopDown, WrapContents = false, AutoScroll = true, Padding = new Padding(18) };
        connection.Controls.Add(flow);
        flow.Controls.Add(new Label { Text = "PC BRIDGE / HELYI HÁLÓZAT", AutoSize = true, Font = new Font(Font.FontFamily, 19, FontStyle.Bold) });
        _game.Items.AddRange(["Assetto Corsa Rally", "Assetto Corsa", "Assetto Corsa Competizione", "BeamNG.drive · OutGauge", "DEMO · szimulált adatok (nincs PC-bemenet)"]);
        _game.SelectedIndex = Math.Max(0, Array.IndexOf(_ids, _config.GameId));
        _address.Items.Add("127.0.0.1");
        foreach (var ip in NetworkInterface.GetAllNetworkInterfaces().Where(n => n.OperationalStatus == OperationalStatus.Up)
            .SelectMany(n => n.GetIPProperties().UnicastAddresses).Select(a => a.Address)
            .Where(a => a.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork && !IPAddress.IsLoopback(a)).Distinct()) _address.Items.Add(ip.ToString());
        _address.SelectedItem = _address.Items.Contains(_config.BindAddress) ? _config.BindAddress : "127.0.0.1";
        _lan.Checked = _config.BindAddress != "127.0.0.1";
        _hz.Items.AddRange(["20", "30", "60"]); _hz.SelectedItem = _config.Hz.ToString(); _port.Value = _config.Port;
        AddRow(flow, new Label { Text = "Játékadapter", AutoSize = true, Width = 160 }, _game);
        AddRow(flow, new Label { Text = "PC hálózati címe", AutoSize = true, Width = 160 }, _address, _lan);
        AddRow(flow, new Label { Text = "TLS port / Hz", AutoSize = true, Width = 160 }, _port, _hz, _start);
        flow.Controls.Add(_control); flow.Controls.Add(_status);
        flow.Controls.Add(new Label { Text = "A tűzfalon csak a választott privát hálózathoz engedélyezd a bejövő TCP-portot.\nA párosítás és a forgalom internet nélkül működik.", AutoSize = true });
        var pair = new Button { Text = "QR-párosítás megnyitása · 120 másodperc", AutoSize = true };
        pair.Click += (_, _) => ShowPairing(); flow.Controls.Add(pair);
        AddRow(flow, _qr, _pairUri);
        flow.Controls.Add(_pairTime);
        var certificateLabel = new TextBox { Text = "Tanúsítvány SHA-256: " + BridgeCertificate.Fingerprint(_certificate), ReadOnly = true, Width = 880 };
        flow.Controls.Add(certificateLabel);
        var devices = Page(tabs, "Eszközök");
        var deviceFlow = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.TopDown, Padding = new Padding(16) };
        devices.Controls.Add(deviceFlow); deviceFlow.Controls.Add(_devices);
        var grant = new Button { Text = "Vezérlés engedélyezése a kijelölt eszköznek", AutoSize = true };
        var readonlyButton = new Button { Text = "Csak olvasás", AutoSize = true };
        var revoke = new Button { Text = "Párosítás visszavonása", AutoSize = true };
        grant.Click += (_, _) => Permission(true); readonlyButton.Click += (_, _) => Permission(false);
        revoke.Click += (_, _) => { if (SelectedDevice() is { } device) _registry.Revoke(device.Id); };
        AddRow(deviceFlow, grant, readonlyButton, revoke);
        deviceFlow.Controls.Add(new Label { Text = "Az új készülékek csak olvasási jogosultságot kapnak.\nA visszavonás az aktív kapcsolatot bezárja és a lenyomott billentyűket felengedi.", AutoSize = true });
        var mapping = Page(tabs, "Játékvezérlés");
        var mappingTools = new FlowLayoutPanel { Dock = DockStyle.Top, AutoSize = true };
        var saveMapping = new Button { Text = "Kiosztás mentése", AutoSize = true };
        var exportMapping = new Button { Text = "Export JSON", AutoSize = true };
        var importMapping = new Button { Text = "Import JSON", AutoSize = true };
        var release = new Button { Text = "MINDEN BILLENTYŰ FELENGEDÉSE", AutoSize = true };
        var testCommand = new Button { Text = "Kijelölt parancs tesztje · 3 s", AutoSize = true };
        _profileMap.Items.Add("Játék alapértelmezett kiosztása");
        var mappingProfiles = Path.Combine(AppContext.BaseDirectory, "profiles.json");
        if (File.Exists(mappingProfiles)) _profileMap.Items.AddRange(Protocol.Deserialize<string[]>(File.ReadAllText(mappingProfiles)) ?? []);
        _profileMap.SelectedIndex = 0;
        _profileMap.SelectedIndexChanged += (_, _) => LoadMappings();
        mappingTools.Controls.AddRange([_profileMap, saveMapping, exportMapping, importMapping, release, testCommand]);
        mapping.Controls.Add(_bindings); mapping.Controls.Add(mappingTools);
        _bindings.Columns.Add(new DataGridViewComboBoxColumn { Name = "Action", HeaderText = "Művelet", DataSource = ActionCatalog.Actions.Order().ToArray() });
        _bindings.Columns.Add("Keys", "Billentyűk (pl. CTRL+L)");
        _bindings.Columns.Add(new DataGridViewComboBoxColumn { Name = "Mode", HeaderText = "Mód", DataSource = new[] { "press", "hold", "repeat" } });
        _bindings.Columns.Add("Duration", "Lenyomás ms"); _bindings.Columns.Add("Repeat", "Ismétlés ms");
        _bindings.BackgroundColor = Color.FromArgb(32, 35, 42); _bindings.ForeColor = Color.Black;
        _bindings.DataError += (_, e) => { e.ThrowException = false; };
        saveMapping.Click += (_, _) => SaveMappings();
        exportMapping.Click += (_, _) => { if (SaveMappings()) ExportJson("bindings.json", new BindingBundle { Bindings = _config.Bindings, ProfileBindings = _config.ProfileBindings }); };
        importMapping.Click += (_, _) => ImportMappings();
        release.Click += (_, _) => _bridge?.Controls.ReleaseAll();
        testCommand.Click += async (_, _) =>
        {
            if (_bridge == null || !_config.MobileControlEnabled || _config.GameId == "demo")
            { MessageBox.Show("Indítsd el a Bridge-et és engedélyezd a mobilvezérlést. A teszt alatt vidd előtérbe a játékot."); return; }
            if (!SaveMappings() || _bindings.CurrentRow?.Cells[0].Value is not string action) return;
            var testBridge = _bridge; var testProfile = MappingProfile;
            testCommand.Enabled = false;
            try
            {
                for (var seconds = 3; seconds > 0; seconds--) { testCommand.Text = $"Vidd előtérbe a játékot · {seconds}"; await Task.Delay(1000); }
                if (_bridge == testBridge)
                {
                    var ack = await testBridge.Controls.ExecuteAsync("local-test", true, new(Guid.NewGuid().ToString("N"), 1, action, "press"), profileId: testProfile);
                    _bridge.Log("local_input_test", $"{action} / {ack.Stage} / {ack.Reason}");
                    testCommand.Text = ack.Stage == "executed" ? "Teszt elküldve" : $"Teszt: {ack.Reason}";
                }
            }
            finally { testCommand.Enabled = true; }
        };
        _game.SelectedIndexChanged += (_, _) => { _config.GameId = _ids[_game.SelectedIndex]; _control.Enabled = _config.GameId != "demo"; if (!_control.Enabled) _control.Checked = false; LoadMappings(); };
        LoadMappings();
        var diagnostics = Page(tabs, "Rally diagnosztika");
        var exportReport = new Button { Text = "Diagnosztikai jelentés exportálása", Dock = DockStyle.Top, Height = 42 };
        exportReport.Click += (_, _) => { if (_bridge != null) ExportJson("sim-control-diagnostics.json", _bridge.DiagnosticReport()); };
        diagnostics.Controls.Add(_diagnostic); diagnostics.Controls.Add(exportReport);
        _start.Click += async (_, _) => await ToggleAsync();
        _control.CheckedChanged += (_, _) => { _config.MobileControlEnabled = _control.Checked; if (!_control.Checked) _bridge?.Controls.ReleaseAll(); };
        _tray = new NotifyIcon { Text = "SIM CONTROL STUDIO", Icon = SystemIcons.Application, Visible = true };
        var menu = new ContextMenuStrip(); menu.Items.Add("Megnyitás", null, (_, _) => { Show(); WindowState = FormWindowState.Normal; Activate(); });
        menu.Items.Add("Billentyűk felengedése", null, (_, _) => _bridge?.Controls.ReleaseAll());
        menu.Items.Add("Kilépés", null, async (_, _) => await ExitAsync()); _tray.ContextMenuStrip = menu;
        _tray.DoubleClick += (_, _) => { Show(); WindowState = FormWindowState.Normal; };
        Resize += (_, _) => { if (WindowState == FormWindowState.Minimized) Hide(); };
        FormClosing += (_, e) => { if (!_exiting) { e.Cancel = true; Hide(); } };
        _refresh.Tick += (_, _) => RefreshState(); _refresh.Start();
        _status.Text = "A Bridge még nem fut. Válassz adaptert és hálózati címet, majd indítsd el.";
    }
    private string ConfigPath => Path.Combine(_directory, "bridge.json");
    private static TabPage Page(TabControl tabs, string name)
    {
        var page = new TabPage(name) { BackColor = Color.FromArgb(24, 27, 32), ForeColor = Color.WhiteSmoke };
        tabs.TabPages.Add(page); return page;
    }
    private static void AddRow(Control parent, params Control[] controls)
    {
        var row = new FlowLayoutPanel { AutoSize = true, WrapContents = false, Margin = new Padding(0, 8, 0, 8) };
        row.Controls.AddRange(controls); parent.Controls.Add(row);
    }
    private async Task ToggleAsync()
    {
        if (_starting) return; _starting = true; _start.Enabled = false;
        try
        {
            if (_bridge != null)
            {
                _control.Checked = false;
                await _bridge.DisposeAsync(); _bridge = null; _start.Text = "Bridge indítása";
            }
            else
            {
                _config.GameId = _ids[_game.SelectedIndex];
                _config.BindAddress = _lan.Checked ? _address.SelectedItem?.ToString() ?? "127.0.0.1" : "127.0.0.1";
                if (_lan.Checked && _config.BindAddress == "127.0.0.1") throw new ArgumentException("Helyi hálózati használathoz válaszd ki a PC Ethernet/Wi-Fi IP-címét.");
                _config.Port = (int)_port.Value; _config.Hz = int.Parse(_hz.SelectedItem!.ToString()!);
                _config.DiscoveryEnabled = _lan.Checked; _config.MobileControlEnabled = false; _control.Checked = false;
                _config.Save(ConfigPath);
                var probe = new WindowsGameProbe(_config.RallyProcessNames);
                var profilesFile = Path.Combine(AppContext.BaseDirectory, "profiles.json");
                var profiles = File.Exists(profilesFile) ? Protocol.Deserialize<string[]>(File.ReadAllText(profilesFile)) : [];
                var bridge = new BridgeRuntime(_config, _registry, _certificate, AdapterFactory.Create(_config, probe), probe, new WindowsKeySink(), profiles);
                try { await bridge.StartAsync(); _bridge = bridge; }
                catch { await bridge.DisposeAsync(); throw; }
                _start.Text = "Bridge leállítása";
            }
            _game.Enabled = _address.Enabled = _lan.Enabled = _port.Enabled = _hz.Enabled = _bridge == null;
        }
        catch (Exception e) when (e is IOException or ArgumentException or System.Net.Sockets.SocketException or InvalidOperationException)
        { MessageBox.Show(e.Message, "Bridge indítási hiba"); }
        finally { _starting = false; _start.Enabled = true; }
    }
    private void ShowPairing()
    {
        if (_bridge == null) { MessageBox.Show("Előbb indítsd el a Bridge-et."); return; }
        var uri = BridgeCertificate.PairingUri(_config.BindAddress, _config.Port, _bridge.Fingerprint, _registry.OpenPairingWindow());
        _pairUri.Text = uri;
        using var data = QRCodeGenerator.GenerateQrCode(uri, QRCodeGenerator.ECCLevel.M);
        using var png = new PngByteQRCode(data);
        using var stream = new MemoryStream(png.GetGraphic(5));
        using var bitmap = Image.FromStream(stream);
        var previous = _qr.Image; _qr.Image = new Bitmap(bitmap); previous?.Dispose();
    }
    private void RefreshState()
    {
        _pairTime.Text = $"Párosítási ablak: {_registry.PairingSecondsRemaining} másodperc";
        if (_registry.PairingSecondsRemaining == 0 && _pairUri.Text.Length > 0)
        { _pairUri.Clear(); var old = _qr.Image; _qr.Image = null; old?.Dispose(); }
        var selectedId = SelectedDevice()?.Id;
        var list = _registry.Devices.Select(d => new DeviceDisplay(d, _bridge?.Clients.FirstOrDefault(c => c.DeviceId == d.Id))).ToArray();
        if (!_devices.Items.Cast<DeviceDisplay>().Select(d => d.ToString()).SequenceEqual(list.Select(d => d.ToString())))
        { _devices.Items.Clear(); _devices.Items.AddRange(list); _devices.SelectedItem = list.FirstOrDefault(d => d.Device.Id == selectedId); }
        if (_bridge == null) { _status.Text = "Bridge leállítva."; return; }
        var h = _bridge.Health; var f = _bridge.Latest;
        string Value(string field) => f?.Fields.TryGetValue(field, out var datum) == true && datum.Validity == Validity.Valid ? datum.Value?.ToString() ?? "—" : "—";
        _status.Text = (_config.GameId == "demo" ? "DEMO · SZIMULÁLT ADATOK · NINCS PC-BEMENET\n" : "") + $"{h.GameId.ToUpperInvariant()} · játék: {(h.GameDetected ? "felismerve" : "nem fut")} · memória: {(h.MemoryAvailable ? "elérhető" : "nem elérhető")}\n" +
            $"{h.State} · {h.ActualHz:0.0} Hz · mobilok: {_bridge.Clients.Count} · utolsó adat: {h.LastPacketMs}\n" +
            $"Sebesség: {Value("speed")} km/h · RPM: {Value("rpm")} · fokozat: {Value("gear")}\n{h.Error}";
        _diagnostic.Text = System.Text.Json.JsonSerializer.Serialize(_bridge.DiagnosticReport(), new System.Text.Json.JsonSerializerOptions(Protocol.Json) { WriteIndented = true });
    }
    private PairedDevice? SelectedDevice() => (_devices.SelectedItem as DeviceDisplay)?.Device;
    private void Permission(bool enabled) { if (SelectedDevice() is { } device) _registry.SetPermission(device.Id, enabled); }
    private void LoadMappings()
    {
        _bindings.Rows.Clear();
        foreach (var (action, binding) in _config.ResolveBindings(MappingProfile))
            _bindings.Rows.Add(action, binding.Keys, binding.Mode, binding.DurationMs, binding.RepeatMs);
    }
    private bool SaveMappings()
    {
        try
        {
            _bindings.EndEdit();
            var map = new Dictionary<string, KeyBinding>();
            foreach (DataGridViewRow row in _bindings.Rows)
            {
                if (row.IsNewRow) continue;
                var action = row.Cells[0].Value?.ToString() ?? throw new ArgumentException("Válassz műveletet.");
                var binding = new KeyBinding(row.Cells[1].Value?.ToString() ?? "", row.Cells[2].Value?.ToString() ?? "press",
                    int.TryParse(row.Cells[3].Value?.ToString(), out var duration) ? duration : 80,
                    int.TryParse(row.Cells[4].Value?.ToString(), out var repeat) ? repeat : 150);
                binding.Validate(); if (!map.TryAdd(action, binding)) throw new ArgumentException("Egy művelet csak egyszer szerepelhet.");
            }
            _bridge?.Controls.ReleaseAll();
            if (MappingProfile is { } profile) _config.ProfileBindings = new(_config.ProfileBindings) { [_config.GameId + "/" + profile] = map };
            else _config.Bindings = new(_config.Bindings) { [_config.GameId] = map };
            _config.Save(ConfigPath);
            return true;
        }
        catch (ArgumentException e) { MessageBox.Show(e.Message, "Hibás kiosztás"); return false; }
    }
    private void ImportMappings()
    {
        using var dialog = new OpenFileDialog { Filter = "JSON|*.json" };
        if (dialog.ShowDialog() != DialogResult.OK) return;
        try
        {
            if (new FileInfo(dialog.FileName).Length > 1024 * 1024) throw new ArgumentException("A kiosztás legfeljebb 1 MB lehet.");
            var imported = BindingBundle.Parse(File.ReadAllText(dialog.FileName));
            _bridge?.Controls.ReleaseAll();
            foreach (var (game, map) in imported.Bindings) _config.Bindings[game] = map;
            foreach (var (profile, map) in imported.ProfileBindings) _config.ProfileBindings[profile] = map;
            _config.Save(ConfigPath); LoadMappings();
        }
        catch (Exception e) when (e is ArgumentException or System.Text.Json.JsonException or IOException) { MessageBox.Show(e.Message, "Importálási hiba"); }
    }
    private static void ExportJson(string filename, object value)
    {
        using var dialog = new SaveFileDialog { FileName = filename, Filter = "JSON|*.json" };
        if (dialog.ShowDialog() == DialogResult.OK) AtomicFile.Write(dialog.FileName, Protocol.Serialize(value));
    }
    private async Task ExitAsync()
    {
        _exiting = true; _refresh.Stop();
        if (_bridge != null) { await _bridge.DisposeAsync(); _bridge = null; }
        _tray.Visible = false; _tray.Dispose(); _certificate.Dispose(); Close();
    }
    private sealed record DeviceDisplay(PairedDevice Device, ConnectedDevice? Session)
    {
        public override string ToString() => $"{Device.Name} · {Device.Role} · {(Device.CanControl ? "vezérlés engedélyezve" : "csak olvasás")} · {Session?.ProfileId ?? Device.ProfileId} / {Session?.LayoutId ?? "—"} · {Session?.LatencyMs?.ToString() ?? "—"} ms · {Session?.ConnectionQuality ?? "offline"} · {Device.Id}";
    }
}
