using SimControlStudio;

// CI-only fixture. Never included in either production app or Windows installer.
// The bootstrap endpoint is loopback-only and returns short-lived TEST pairing data.
var directory = Path.Combine(Path.GetTempPath(), "simcontrol-native-fixture-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(directory);
try
{
    var config = new BridgeConfiguration { GameId = "demo", Port = 19760, Hz = 30 };
    using var certificate = BridgeCertificate.LoadOrCreate(directory);
    var registry = new DeviceRegistry(Path.Combine(directory, "devices.json"));
    var profiles = System.Text.Json.JsonDocument.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "mobile_flutter", "assets", "catalog.json")))
        .RootElement.GetProperty("vehicles").EnumerateArray().Select(v => v.GetProperty("id").GetString()!).ToArray();
    await using var bridge = new BridgeRuntime(config, registry, certificate, new DemoAdapter(), new NoGame(), new ForbiddenInput(), profiles);
    await bridge.StartAsync();
    var builder = WebApplication.CreateSlimBuilder();
    builder.Logging.ClearProviders(); builder.WebHost.UseUrls("http://127.0.0.1:19759");
    var bootstrap = builder.Build();
    bootstrap.MapGet("/session", () => Results.Json(new { uri = BridgeCertificate.PairingUri("127.0.0.1", config.Port, bridge.Fingerprint, registry.OpenPairingWindow()) }));
    Console.WriteLine("Native integration TEST fixture: loopback, explicit DEMO, forbidden OS input.");
    await bootstrap.RunAsync();
}
finally { Directory.Delete(directory, true); }

sealed class NoGame : IGameProbe
{
    public bool IsRunning(string gameId) => false;
    public bool IsForeground(string gameId) => false;
    public bool HasSharedMemoryConflict(string gameId) => false;
}
sealed class ForbiddenInput : IKeySink
{
    public void KeyDown(ushort key) => throw new InvalidOperationException("A native DEMO test attempted OS input");
    public void KeyUp(ushort key) => throw new InvalidOperationException("A native DEMO test attempted OS input");
}
