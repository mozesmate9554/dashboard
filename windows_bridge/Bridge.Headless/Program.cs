using SimControlStudio;

var data = args.Length > 0 ? Path.GetFullPath(args[0]) : Path.Combine(AppContext.BaseDirectory, "data");
Directory.CreateDirectory(data);
var config = BridgeConfiguration.Load(Path.Combine(data, "bridge.json"));
using var certificate = BridgeCertificate.LoadOrCreate(data);
var registry = new DeviceRegistry(Path.Combine(data, "devices.json"));
var probe = new WindowsGameProbe(config.RallyProcessNames);
await using var bridge = new BridgeRuntime(config, registry, certificate, AdapterFactory.Create(config, probe), probe, new WindowsKeySink());
await bridge.StartAsync();
Console.WriteLine($"SIM CONTROL STUDIO {Protocol.AppVersion} / {config.GameId} / TLS {config.BindAddress}:{config.Port}");
Console.WriteLine("No simulated telemetry. Linux runs transport/diagnostics only; game memory and SendInput require Windows.");
Console.WriteLine("Press P to open a 120-second pairing window; D for diagnostics; Q to exit.");
var finished = new TaskCompletionSource();
Console.CancelKeyPress += (_, e) => { e.Cancel = true; finished.TrySetResult(); };
if (!Console.IsInputRedirected)
{
    _ = Task.Run(() =>
    {
        while (!finished.Task.IsCompleted)
        {
            var key = Console.ReadKey(true).Key;
            if (key == ConsoleKey.Q) { finished.TrySetResult(); break; }
            if (key == ConsoleKey.P) Console.WriteLine(BridgeCertificate.PairingUri(config.BindAddress, config.Port, bridge.Fingerprint, registry.OpenPairingWindow()));
            if (key == ConsoleKey.D) Console.WriteLine(Protocol.Serialize(bridge.DiagnosticReport()));
        }
    });
}
await finished.Task;
