using System.Buffers.Binary;
using System.Net;
using System.Net.Sockets;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using SimControlStudio;

var output = args.FirstOrDefault() ?? Path.Combine(AppContext.BaseDirectory, "test-results.json");
var results = new List<object>();
var failures = 0;
var temporary = Path.Combine(Path.GetTempPath(), "simcontrol-tests-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(temporary);
async Task Test(string name, Func<Task> test)
{
    var started = DateTimeOffset.UtcNow;
    try { await test(); results.Add(new { name, status = "passed", durationMs = (DateTimeOffset.UtcNow - started).TotalMilliseconds }); Console.WriteLine("PASS " + name); }
    catch (Exception e) { failures++; results.Add(new { name, status = "failed", error = e.ToString() }); Console.WriteLine("FAIL " + name + " / " + e.Message); }
}
static void Assert(bool condition, string detail = "Assertion failed") { if (!condition) throw new Exception(detail); }
static void Throws<T>(Action action) where T : Exception
{ try { action(); } catch (T) { return; } throw new Exception("Expected " + typeof(T).Name); }
static double Numeric(TelemetryFrame frame, string field) => Convert.ToDouble(frame.Fields[field].Value);
static byte[] Physics(int packet = 1)
{
    var bytes = new byte[800];
    PutInt(bytes, 0, packet); PutFloat(bytes, 4, .75f); PutFloat(bytes, 8, .125f); PutInt(bytes, 16, 5);
    PutInt(bytes, 20, 6432); PutFloat(bytes, 24, -12.5f); PutFloat(bytes, 28, 137.25f);
    PutFloat(bytes, 44, 1.2f); PutFloat(bytes, 48, -.4f); PutFloat(bytes, 52, 1f);
    return bytes;
}
static void PutInt(byte[] b, int o, int n) => BinaryPrimitives.WriteInt32LittleEndian(b.AsSpan(o, 4), n);
static void PutFloat(byte[] b, int o, float n) => PutInt(b, o, BitConverter.SingleToInt32Bits(n));
static Hello HelloFor(string? token = null, string role = "panel", string? secret = null, string? id = null) =>
    new(1, id ?? Guid.NewGuid().ToString(), "Integration device", role, "skoda-fabia-rs-rally2", 30, token, secret);

try
{
    await Test("Rally byte layout: speed/RPM/gear/pedals/G-force", () =>
    {
        var frame = AcMemoryDecoder.Decode(Physics(), null, null, "acr", 1000, 1);
        Assert(Numeric(frame, "speed") == 137.25 && Numeric(frame, "rpm") == 6432 && Numeric(frame, "gear") == 4);
        Assert(Numeric(frame, "throttle") == .75 && Numeric(frame, "brake") == .125 && Numeric(frame, "steering") == -12.5);
        Assert(Math.Abs(Numeric(frame, "gX") - 1.2) < 1e-5);
        Assert(frame.Fields["speed"].TimestampMs == 1000 && frame.Fields["gear"].Derived);
        return Task.CompletedTask;
    });
    await Test("Rally does not invent extended ACC or timing fields", () =>
    {
        var frame = AcMemoryDecoder.Decode(Physics(), new byte[784], new byte[176], "acr", 1000, 1);
        foreach (var key in new[] { "fuel", "absLevel", "tcLevel", "brakeBias", "stageTime", "battery", "waterTemp" })
            Assert(frame.Fields[key].Validity == Validity.Unsupported && frame.Fields[key].Value == null, key);
        return Task.CompletedTask;
    });
    await Test("Reverse and neutral wire convention", () =>
    {
        var p = Physics(); PutInt(p, 16, 0); Assert(Numeric(AcMemoryDecoder.Decode(p, null, null, "acr", 0, 0), "gear") == -1);
        PutInt(p, 16, 1); Assert(Numeric(AcMemoryDecoder.Decode(p, null, null, "acr", 0, 0), "gear") == 0);
        return Task.CompletedTask;
    });
    await Test("Short, NaN and impossible telemetry rejected", () =>
    {
        Throws<InvalidDataException>(() => AcMemoryDecoder.Decode(new byte[55], null, null, "acr", 0, 0));
        var p = Physics(); PutFloat(p, 28, float.NaN); Throws<InvalidDataException>(() => AcMemoryDecoder.Decode(p, null, null, "acr", 0, 0));
        PutFloat(p, 28, 1001); Throws<InvalidDataException>(() => AcMemoryDecoder.Decode(p, null, null, "acr", 0, 0));
        return Task.CompletedTask;
    });
    await Test("Statics UTF16 offsets and RPM limit", () =>
    {
        var bytes = new byte[784]; Encoding.Unicode.GetBytes("fabia_rs_test").CopyTo(bytes, 68);
        Encoding.Unicode.GetBytes("stage_test").CopyTo(bytes, 134); Encoding.Unicode.GetBytes("0.test").CopyTo(bytes, 30); PutInt(bytes, 412, 8000);
        var frame = AcMemoryDecoder.Decode(Physics(), bytes, null, "acr", 1, 1);
        Assert(frame.VehicleId == "fabia_rs_test" && Numeric(frame, "rpmLimit") == 8000 && frame.GameVersion == "0.test");
        return Task.CompletedTask;
    });
    await Test("Stale fields retain original sample timestamp", () =>
    {
        var frame = AcMemoryDecoder.Decode(Physics(), null, null, "acr", 1000, 1).Stale(1600);
        Assert(frame.State == "stale" && frame.Fields["speed"].Validity == Validity.Stale && frame.Fields["speed"].TimestampMs == 1000);
        Assert(frame.Fields["fuel"].Validity == Validity.Unsupported);
        return Task.CompletedTask;
    });
    await Test("First packet id zero, duplicates and game exit/restart", async () =>
    {
        var memory = new FixtureMemory { Packet = 0 }; var probe = new FixtureProbe();
        using var adapter = new AcSharedMemoryAdapter("acr", memory, probe);
        Assert(await adapter.PollAsync(default) != null);
        Assert(adapter.Health.MemoryBlocks?["physics"] == true && adapter.Health.MemoryBlocks["static"] == false);
        Assert(await adapter.PollAsync(default) == null);
        probe.Running = false; Assert(await adapter.PollAsync(default) == null && !adapter.Health.GameDetected);
        probe.Running = true; Assert(await adapter.PollAsync(default) != null);
        probe.Conflict = true; Assert(await adapter.PollAsync(default) == null && adapter.Health.Error != null);
    });
    await Test("Key binding validation prevents system commands", () =>
    {
        Assert(KeyNames.Parse("CTRL+SHIFT+L").Length == 3);
        Throws<ArgumentException>(() => KeyNames.Parse("ALT+F4")); Throws<ArgumentException>(() => KeyNames.Parse("WIN+R"));
        Throws<ArgumentException>(() => KeyNames.Parse("CTRL+ALT+DELETE")); Throws<ArgumentException>(() => new KeyBinding("A", DurationMs: 5000).Validate());
        return Task.CompletedTask;
    });
    await Test("Pairing, hashed persistence, wrong secret and revocation", () =>
    {
        var path = Path.Combine(temporary, "registry.json"); var registry = new DeviceRegistry(path); var token = registry.OpenPairingWindow();
        var hello = HelloFor(token); var auth = registry.Authenticate(hello)!;
        Assert(auth != null && auth.NewSecret != null && !auth.Device.CanControl);
        Assert(!File.ReadAllText(path).Contains(auth!.NewSecret!));
        Assert(registry.Authenticate(hello with { Secret = "wrong" }) == null);
        Assert(registry.Authenticate(hello with { Secret = auth.NewSecret, PairingToken = null }) != null);
        registry.Revoke(hello.DeviceId); registry.ClosePairingWindow(); Assert(registry.Authenticate(hello) == null);
        return Task.CompletedTask;
    });
    await Test("Session replay and throttling; key-up exempt", () =>
    {
        var guard = new SessionCommandGuard();
        Assert(guard.Validate(new("id", 1, "lights", "press")) == null);
        Assert(guard.Validate(new("id", 2, "lights", "press")) == "duplicate_or_out_of_order");
        var limited = false;
        for (var i = 2; i < 70; i++) limited |= guard.Validate(new("id" + i, i, "lights", "press")) == "rate_limited";
        Assert(limited); Assert(guard.Validate(new("up", 100, "lights", "up")) == null);
        return Task.CompletedTask;
    });
    await Test("Foreground, explicit arming and per-device permission", async () =>
    {
        var config = new BridgeConfiguration(); config.Bindings["acr"]["lights"] = new("L");
        var probe = new FixtureProbe(); var sink = new FixtureSink(); using var engine = new ControlEngine(config, probe, sink);
        Assert((await engine.ExecuteAsync("d", true, new("1", 1, "lights", "press"))).Stage == "rejected");
        config.MobileControlEnabled = true;
        Assert((await engine.ExecuteAsync("d", false, new("2", 2, "lights", "press"))).Stage == "rejected");
        probe.Foreground = false; Assert((await engine.ExecuteAsync("d", true, new("3", 3, "lights", "press"))).Stage == "rejected");
        probe.Foreground = true; Assert((await engine.ExecuteAsync("d", true, new("4", 4, "lights", "press"))).Stage == "executed");
        Assert(sink.Events.SequenceEqual(new[] { "down:76", "up:76" }));
    });
    await Test("Two devices share modifier ownership; disconnect and focus watchdog", async () =>
    {
        var config = new BridgeConfiguration { MobileControlEnabled = true };
        config.Bindings["acr"]["lights"] = new("CTRL+L", "hold"); config.Bindings["acr"]["wiper"] = new("CTRL+W", "hold");
        var probe = new FixtureProbe(); var sink = new FixtureSink(); using var engine = new ControlEngine(config, probe, sink);
        await engine.ExecuteAsync("a", true, new("1", 1, "lights", "down"));
        await engine.ExecuteAsync("b", true, new("2", 1, "wiper", "down"));
        engine.ReleaseOwner("a"); Assert(engine.HeldKeyCount == 2 && !sink.Events.Contains("up:17"));
        probe.Foreground = false; engine.Watchdog(); Assert(engine.HeldKeyCount == 0 && sink.Events.Contains("up:17"));
    });
    await Test("Repeat reports a failed first input honestly and stops on key-up", async () =>
    {
        var config = new BridgeConfiguration { MobileControlEnabled = true };
        config.Bindings["acr"]["lights"] = new("L", "repeat", 20, 50);
        using (var failing = new ControlEngine(config, new FixtureProbe(), new FailingSink()))
        {
            var ack = await failing.ExecuteAsync("d", true, new("r", 1, "lights", "down"));
            Assert(ack.Stage == "rejected" && ack.Reason == "input_failed" && failing.HeldKeyCount == 0);
        }
        var sink = new FixtureSink();
        using var engine = new ControlEngine(config, new FixtureProbe(), sink);
        Assert((await engine.ExecuteAsync("d", true, new("r", 1, "lights", "down"))).Stage == "executed");
        await Task.Delay(160);
        await engine.ExecuteAsync("d", true, new("u", 2, "lights", "up"));
        await Task.Delay(30);
        Assert(engine.HeldKeyCount == 0 && sink.Events.Count(e => e == "down:76") >= 2);
    });
    await Test("Read-only unsupported action and invalid phase never inject input", async () =>
    {
        var config = new BridgeConfiguration { MobileControlEnabled = true }; var sink = new FixtureSink();
        using var engine = new ControlEngine(config, new FixtureProbe(), sink);
        Assert((await engine.ExecuteAsync("d", true, new("1", 1, "absUp", "press"))).Reason == "unsupported_or_unmapped");
        Assert((await engine.ExecuteAsync("d", true, new("2", 2, "evil", "press"))).Reason == "invalid_command");
        Assert(sink.Events.Count == 0);
    });
    await Test("BeamNG OutGauge header, unit conversion and invalid packet", () =>
    {
        var bytes = new byte[92]; Encoding.ASCII.GetBytes("beam").CopyTo(bytes, 4); bytes[10] = 3;
        PutFloat(bytes, 12, 10); PutFloat(bytes, 16, 4000); PutFloat(bytes, 24, 90); PutFloat(bytes, 48, .5f);
        var frame = BeamNgOutGaugeAdapter.Decode(bytes, 1, 1); Assert(Math.Abs(Numeric(frame, "speed") - 36) < 1e-6);
        Assert(Numeric(frame, "gear") == 2); Throws<InvalidDataException>(() => BeamNgOutGaugeAdapter.Decode(new byte[92], 1, 1));
        return Task.CompletedTask;
    });
    await Test("TLS pin, two WebSocket clients, control ack, disconnect/reconnect, stale and revoke", async () =>
    {
        var listener = new TcpListener(IPAddress.Loopback, 0); listener.Start(); var port = ((IPEndPoint)listener.LocalEndpoint).Port; listener.Stop();
        var config = new BridgeConfiguration { Port = port, MobileControlEnabled = true, Hz = 60 };
        config.Bindings["acr"]["lights"] = new("L");
        var registry = new DeviceRegistry(Path.Combine(temporary, "integration-devices.json"));
        using var certificate = BridgeCertificate.LoadOrCreate(Path.Combine(temporary, "certificate"));
        var memory = new FixtureMemory { AutoIncrement = true }; var probe = new FixtureProbe(); var sink = new FixtureSink();
        await using var runtime = new BridgeRuntime(config, registry, certificate, new AcSharedMemoryAdapter("acr", memory, probe), probe, sink, ["skoda-fabia-rs-rally2"]);
        await runtime.StartAsync(); var token = registry.OpenPairingWindow();
        var a = HelloFor(token, "dashboard") with { LayoutId = "dash-personal" }; var b = HelloFor(token) with { LayoutId = "panel-personal" };
        using var clientA = Client(certificate); using var clientB = Client(certificate);
        await clientA.ConnectAsync(new Uri($"wss://127.0.0.1:{port}/ws"), default); await Send(clientA, a);
        var welcomeA = await ReceiveType(clientA, "welcome"); var secretA = welcomeA.GetProperty("secret").GetString();
        await clientB.ConnectAsync(new Uri($"wss://127.0.0.1:{port}/ws"), default); await Send(clientB, b);
        var welcomeB = await ReceiveType(clientB, "welcome"); Assert(welcomeB.GetProperty("canControl").GetBoolean() == false);
        registry.SetPermission(b.DeviceId, true);
        var frameA = (await ReceiveType(clientA, "telemetry")).GetProperty("frame");
        var frameB = (await ReceiveType(clientB, "telemetry")).GetProperty("frame");
        Assert(frameA.GetProperty("fields").GetProperty("speed").GetProperty("value").GetDouble() == 137.25);
        Assert(frameB.GetProperty("gameId").GetString() == "acr" && runtime.Clients.Count == 2);
        Assert(runtime.Clients.Any(c => c.LayoutId == "dash-personal") && runtime.Clients.Any(c => c.LayoutId == "panel-personal"));
        await Send(clientB, new { type = "command", id = "lights-1", sequence = 1, action = "lights", phase = "press" });
        Assert((await ReceiveType(clientB, "ack")).GetProperty("stage").GetString() == "received");
        Assert((await ReceiveType(clientB, "ack")).GetProperty("stage").GetString() == "executed");
        Assert(sink.Events.Contains("down:76") && sink.Events.Contains("up:76"));
        await Send(clientB, new { type = "command", id = "lights-1", sequence = 1, action = "lights", phase = "press" });
        Assert((await ReceiveType(clientB, "ack")).GetProperty("reason").GetString() == "duplicate_or_out_of_order");
        await Send(clientA, new { type = "profile", profileId = "skoda-fabia-rs-rally2" });
        Assert((await ReceiveType(clientB, "profileSuggestion")).GetProperty("profileId").GetString() == "skoda-fabia-rs-rally2");
        clientA.Abort();
        Assert((await ReceiveType(clientB, "telemetry")).GetProperty("frame").GetProperty("state").GetString() == "live");
        using var reconnect = Client(certificate); await reconnect.ConnectAsync(new Uri($"wss://127.0.0.1:{port}/ws"), default);
        await Send(reconnect, a with { PairingToken = null, Secret = secretA }); await ReceiveType(reconnect, "welcome");
        memory.AutoIncrement = false;
        await Task.Delay(650);
        while ((await ReceiveType(clientB, "telemetry")).GetProperty("frame").GetProperty("state").GetString() != "stale") { }
        Assert(runtime.Latest!.Fields["speed"].Validity == Validity.Stale);
        registry.Revoke(b.DeviceId);
        Assert(!registry.Contains(b.DeviceId)); Assert(runtime.Controls.HeldKeyCount == 0);
        memory.AutoIncrement = true;
        Assert((await ReceiveType(reconnect, "telemetry")).GetProperty("frame").GetProperty("fields").TryGetProperty("rpm", out _));
    });
    await Test("TLS pin rejection, revoked credentials, malformed messages and disconnect releases held input", async () =>
    {
        var listener = new TcpListener(IPAddress.Loopback, 0); listener.Start(); var port = ((IPEndPoint)listener.LocalEndpoint).Port; listener.Stop();
        var config = new BridgeConfiguration { Port = port, MobileControlEnabled = true };
        config.Bindings["acr"]["lights"] = new("CTRL+L", "hold");
        var registry = new DeviceRegistry(Path.Combine(temporary, "edge-devices.json"));
        using var certificate = BridgeCertificate.LoadOrCreate(Path.Combine(temporary, "edge-cert"));
        var probe = new FixtureProbe();
        await using var runtime = new BridgeRuntime(config, registry, certificate,
            new AcSharedMemoryAdapter("acr", new FixtureMemory { AutoIncrement = true }, probe), probe, new FixtureSink());
        await runtime.StartAsync();
        using (var badPin = new ClientWebSocket())
        {
            badPin.Options.RemoteCertificateValidationCallback = (_, _, _, _) => false;
            var rejected = false;
            try { await badPin.ConnectAsync(new Uri($"wss://127.0.0.1:{port}/ws"), default); }
            catch (WebSocketException) { rejected = true; }
            Assert(rejected, "An untrusted certificate must not connect");
        }
        var hello = HelloFor(registry.OpenPairingWindow());
        var saved = registry.Authenticate(hello)!;
        using (var invalidSecret = Client(certificate))
        {
            await invalidSecret.ConnectAsync(new Uri($"wss://127.0.0.1:{port}/ws"), default);
            await Send(invalidSecret, hello with { PairingToken = null, Secret = "wrong" });
            using var timeout = new CancellationTokenSource(2000);
            Assert(await BridgeRuntime.ReadMessageAsync(invalidSecret, timeout.Token) == null);
            Assert(invalidSecret.CloseStatus == WebSocketCloseStatus.PolicyViolation);
        }
        registry.SetPermission(hello.DeviceId, true);
        using (var held = Client(certificate))
        {
            await held.ConnectAsync(new Uri($"wss://127.0.0.1:{port}/ws"), default);
            await Send(held, hello with { PairingToken = null, Secret = saved.NewSecret }); await ReceiveType(held, "welcome");
            await Send(held, new { type = "command", id = "held", sequence = 1, action = "lights", phase = "down" });
            await ReceiveType(held, "ack"); Assert((await ReceiveType(held, "ack")).GetProperty("stage").GetString() == "executed");
            Assert(runtime.Controls.HeldKeyCount == 2); held.Abort();
            var deadline = Environment.TickCount64 + 2000;
            while (runtime.Controls.HeldKeyCount > 0 && Environment.TickCount64 < deadline) await Task.Delay(20);
            Assert(runtime.Controls.HeldKeyCount == 0, "Disconnect left an injected key down");
        }
        using (var malformed = Client(certificate))
        {
            await malformed.ConnectAsync(new Uri($"wss://127.0.0.1:{port}/ws"), default);
            await Send(malformed, hello with { PairingToken = null, Secret = saved.NewSecret }); await ReceiveType(malformed, "welcome");
            await malformed.SendAsync(new byte[] { 0xff, 0xfe }, WebSocketMessageType.Text, true, default);
            using var timeout = new CancellationTokenSource(2000);
            try { while (await BridgeRuntime.ReadMessageAsync(malformed, timeout.Token) != null) { } }
            catch (WebSocketException) { }
            Assert(runtime.Controls.HeldKeyCount == 0 && runtime.IsRunning);
        }
        registry.Revoke(hello.DeviceId);
        Assert(registry.Authenticate(hello with { PairingToken = null, Secret = saved.NewSecret }) == null);
    });
    await Test("Configuration validation and control is disarmed after restart", () =>
    {
        var path = Path.Combine(temporary, "bridge.json"); var config = new BridgeConfiguration { MobileControlEnabled = true };
        config.Save(path); Assert(!BridgeConfiguration.Load(path).MobileControlEnabled);
        Throws<ArgumentException>(() => new BridgeConfiguration { Hz = 120 }.Validate());
        Throws<ArgumentException>(() => new BridgeConfiguration { GameId = "not_implemented" }.Validate());
        return Task.CompletedTask;
    });
    await Test("Car-specific maps, legacy import and empty overrides persist without cross-car leakage", async () =>
    {
        var config = new BridgeConfiguration { MobileControlEnabled = true };
        config.Bindings["acr"]["lights"] = new("L");
        config.ProfileBindings["acr/car-a"] = new() { ["lights"] = new("K") };
        config.ProfileBindings["acr/car-b"] = [];
        var sink = new FixtureSink(); using var engine = new ControlEngine(config, new FixtureProbe(), sink);
        await engine.ExecuteAsync("a", true, new("a", 1, "lights", "press"), profileId: "car-a");
        Assert(sink.Events.SequenceEqual(new[] { "down:75", "up:75" }));
        Assert((await engine.ExecuteAsync("b", true, new("b", 1, "lights", "press"), profileId: "car-b")).Reason == "unsupported_or_unmapped");
        var path = Path.Combine(temporary, "profile-maps.json"); config.Save(path);
        Assert(BridgeConfiguration.Load(path).ResolveBindings("car-a")["lights"].Keys == "K");
        Assert(BindingBundle.Parse(Protocol.Serialize(config.Bindings)).Bindings["acr"]["lights"].Keys == "L");
        var bundle = BindingBundle.Parse(Protocol.Serialize(new BindingBundle { ProfileBindings = config.ProfileBindings }));
        Assert(bundle.ProfileBindings["acr/car-b"].Count == 0 && bundle.Bindings.Count == 0);
        Throws<ArgumentException>(() => BindingBundle.Parse("{\"schemaVersion\":99}"));
    });
    await Test("Queued presses cancel on release; other actions and key-up remain responsive", async () =>
    {
        var config = new BridgeConfiguration { MobileControlEnabled = true };
        config.Bindings["acr"]["lights"] = new("L", DurationMs: 1000);
        config.Bindings["acr"]["radio"] = new("R", "hold");
        var sink = new FixtureSink(); using var engine = new ControlEngine(config, new FixtureProbe(), sink);
        var first = engine.ExecuteAsync("a", true, new("a1", 1, "lights", "press"));
        var queued = engine.ExecuteAsync("a", true, new("a2", 2, "lights", "press"));
        var clock = System.Diagnostics.Stopwatch.StartNew();
        await engine.ExecuteAsync("b", true, new("b1", 1, "radio", "down"));
        await engine.ExecuteAsync("b", true, new("b2", 2, "radio", "up"));
        Assert(clock.ElapsedMilliseconds < 300, "An unrelated hold/up waited for a long press");
        engine.ReleaseOwner("a");
        Assert((await first).Reason == "cancelled" && (await queued).Reason == "cancelled");
        Assert(engine.HeldKeyCount == 0 && sink.Events.Count(e => e == "down:76") == 1);
    });
    await Test("DEMO is labeled, synthesizes fields and hard-blocks all real input", async () =>
    {
        var config = new BridgeConfiguration { GameId = "demo", MobileControlEnabled = true };
        config.Bindings["demo"] = new() { ["lights"] = new("L") };
        var sink = new FixtureSink(); using var engine = new ControlEngine(config, new FixtureProbe(), sink);
        Assert((await engine.ExecuteAsync("a", true, new("1", 1, "lights", "press"))).Stage == "rejected");
        using var demo = new DemoAdapter();
        demo.Apply("a", new("d", 1, "lights", "press"));
        demo.Apply("a", new("r", 2, "radio", "down"));
        var frame = (await demo.PollAsync(default))!;
        Assert(frame.Mode == "demo" && frame.State == "demo" && frame.Fields["lights"].Value is true);
        Assert(frame.Fields["radioActive"].Value is true && !demo.Health.GameDetected);
        Assert(frame.Fields.Values.All(f => f.Source.StartsWith("demo:", StringComparison.Ordinal)));
        demo.ReleaseOwner("a"); Assert((await demo.PollAsync(default))!.Fields["radioActive"].Value is false);
        Assert(sink.Events.Count == 0);
    });
    await Test("DEMO through real TLS: role permissions, profile change and never SendInput", async () =>
    {
        var listener = new TcpListener(IPAddress.Loopback, 0); listener.Start(); var port = ((IPEndPoint)listener.LocalEndpoint).Port; listener.Stop();
        var config = new BridgeConfiguration { GameId = "demo", Port = port };
        var registry = new DeviceRegistry(Path.Combine(temporary, "demo-devices.json"));
        using var certificate = BridgeCertificate.LoadOrCreate(Path.Combine(temporary, "demo-cert"));
        var sink = new FixtureSink();
        await using var runtime = new BridgeRuntime(config, registry, certificate, new DemoAdapter(), new FixtureProbe(), sink);
        await runtime.StartAsync(); var token = registry.OpenPairingWindow();
        using var dash = Client(certificate); using var panel = Client(certificate);
        await dash.ConnectAsync(new Uri($"wss://127.0.0.1:{port}/ws"), default); await Send(dash, HelloFor(token, "dashboard"));
        Assert((await ReceiveType(dash, "welcome")).GetProperty("mode").GetString() == "demo");
        await panel.ConnectAsync(new Uri($"wss://127.0.0.1:{port}/ws"), default); await Send(panel, HelloFor(token)); await ReceiveType(panel, "welcome");
        await Send(panel, new { type = "command", id = "demo-radio", sequence = 1, action = "radio", phase = "down" });
        await ReceiveType(panel, "ack"); Assert((await ReceiveType(panel, "ack")).GetProperty("stage").GetString() == "simulated");
        await Send(dash, new { type = "command", id = "denied", sequence = 1, action = "lights", phase = "press" });
        await ReceiveType(dash, "ack"); Assert((await ReceiveType(dash, "ack")).GetProperty("reason").GetString() == "dashboard_read_only");
        Assert(runtime.Clients.Count == 2 && runtime.Clients.All(c => c.ProfileId == "skoda-fabia-rs-rally2"));
        Assert((await ReceiveType(panel, "telemetry")).GetProperty("frame").GetProperty("mode").GetString() == "demo");
        Assert(sink.Events.Count == 0 && runtime.Controls.HeldKeyCount == 0);
    });

}
finally
{
    Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output))!);
    AtomicFile.Write(output, Protocol.Serialize(new { appVersion = Protocol.AppVersion, executedAtUtc = DateTimeOffset.UtcNow,
        environment = System.Runtime.InteropServices.RuntimeInformation.OSDescription + " .NET; synthetic binary fixtures and real local TLS/WebSocket transport; no physical game or device",
        passed = results.Count - failures, failed = failures, tests = results }));
    Directory.Delete(temporary, true);
}
Environment.ExitCode = failures == 0 ? 0 : 1;

static ClientWebSocket Client(System.Security.Cryptography.X509Certificates.X509Certificate2 certificate)
{
    var client = new ClientWebSocket(); var expected = BridgeCertificate.Fingerprint(certificate);
    client.Options.RemoteCertificateValidationCallback = (_, presented, _, _) => presented != null &&
        Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(presented.GetRawCertData())).Equals(expected, StringComparison.OrdinalIgnoreCase);
    return client;
}
static Task Send(ClientWebSocket client, object data) => client.SendAsync(Encoding.UTF8.GetBytes(Protocol.Serialize(data)), WebSocketMessageType.Text, true, default);
static async Task<JsonElement> ReceiveType(ClientWebSocket client, string type)
{
    using var timeout = new CancellationTokenSource(4000);
    while (true)
    {
        var text = await BridgeRuntime.ReadMessageAsync(client, timeout.Token) ?? throw new Exception("Socket closed waiting for " + type);
        using var doc = JsonDocument.Parse(text);
        if (doc.RootElement.GetProperty("type").GetString() == type) return doc.RootElement.Clone();
    }
}

// Test-only fixtures. They are never registered as production adapters.
sealed class FixtureMemory : IMemorySource
{
    public int Packet;
    public volatile bool AutoIncrement;
    public byte[]? Read(string name, int size, bool packetCounter)
    {
        if (!name.EndsWith("physics", StringComparison.Ordinal)) return null;
        var bytes = new byte[800];
        void I(int offset, int value) => BinaryPrimitives.WriteInt32LittleEndian(bytes.AsSpan(offset, 4), value);
        void F(int offset, float value) => I(offset, BitConverter.SingleToInt32Bits(value));
        if (AutoIncrement) Interlocked.Increment(ref Packet);
        I(0, Packet); I(16, 5); I(20, 6432); F(28, 137.25f); F(4, .75f); F(8, .125f); F(24, -12.5f);
        F(44, 1.2f); F(48, -.4f); F(52, 1f); return bytes;
    }
    public void Reset() { }
    public void Dispose() { }
}
sealed class FixtureProbe : IGameProbe
{
    public bool Running = true, Foreground = true, Conflict;
    public bool IsRunning(string gameId) => Running;
    public bool IsForeground(string gameId) => Foreground;
    public bool HasSharedMemoryConflict(string gameId) => Conflict;
}
sealed class FixtureSink : IKeySink
{
    public List<string> Events { get; } = [];
    public void KeyDown(ushort key) { lock (Events) Events.Add("down:" + key); }
    public void KeyUp(ushort key) { lock (Events) Events.Add("up:" + key); }
}
sealed class FailingSink : IKeySink
{
    public void KeyDown(ushort key) => throw new System.ComponentModel.Win32Exception(5, "Fixture input denied");
    public void KeyUp(ushort key) { }
}
