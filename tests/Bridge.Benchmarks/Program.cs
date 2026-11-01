using System.Diagnostics;
using System.Net;
using System.Net.Sockets;
using System.Net.WebSockets;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using SimControlStudio;

// Benchmark real local TLS transport, with explicitly synthetic source and no OS input.
var output = args.FirstOrDefault() ?? "tests/results/transport-benchmark.json";
var temp = Path.Combine(Path.GetTempPath(), "simcontrol-bench-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(temp);
try
{
    var results = new List<object>();
    foreach (var hz in new[] { 30, 60 })
    {
        var listener = new TcpListener(IPAddress.Loopback, 0); listener.Start(); var port = ((IPEndPoint)listener.LocalEndpoint).Port; listener.Stop();
        var config = new BridgeConfiguration { GameId = "demo", Hz = hz, Port = port };
        using var certificate = BridgeCertificate.LoadOrCreate(temp);
        var registry = new DeviceRegistry(Path.Combine(temp, $"devices-{hz}.json"));
        await using var bridge = new BridgeRuntime(config, registry, certificate, new DemoAdapter(), new NoGame(), new ForbiddenInput());
        await bridge.StartAsync(); var token = registry.OpenPairingWindow();
        ClientWebSocket Client()
        {
            var client = new ClientWebSocket();
            client.Options.RemoteCertificateValidationCallback = (_, presented, _, _) => presented != null &&
                Convert.ToHexString(SHA256.HashData(presented.GetRawCertData())).Equals(bridge.Fingerprint, StringComparison.OrdinalIgnoreCase);
            return client;
        }
        using var dashboard = Client(); using var panel = Client();
        async Task Send(ClientWebSocket socket, object message) => await socket.SendAsync(Encoding.UTF8.GetBytes(Protocol.Serialize(message)), WebSocketMessageType.Text, true, default);
        async Task Connect(ClientWebSocket socket, string role)
        {
            await socket.ConnectAsync(new Uri($"wss://127.0.0.1:{port}/ws"), default);
            await Send(socket, new Hello(1, Guid.NewGuid().ToString(), "Benchmark " + role, role, "skoda-fabia-rs-rally2", hz, token));
            using var cts = new CancellationTokenSource(5000);
            using var welcome = JsonDocument.Parse((await BridgeRuntime.ReadMessageAsync(socket, cts.Token))!);
            if (welcome.RootElement.GetProperty("type").GetString() != "welcome") throw new Exception("Missing welcome");
        }
        await Connect(dashboard, "dashboard"); await Connect(panel, "panel");
        var frames = new int[2]; var bytes = new long[2]; var rtts = new List<double>(); var simulated = 0;
        var clock = Stopwatch.StartNew(); var process = Process.GetCurrentProcess(); var cpu = process.TotalProcessorTime;
        var alloc = GC.GetTotalAllocatedBytes();
        using var duration = new CancellationTokenSource(20000);
        async Task Read(ClientWebSocket socket, int index)
        {
            try
            {
                while (!duration.IsCancellationRequested)
                {
                    var text = await BridgeRuntime.ReadMessageAsync(socket, duration.Token); if (text == null) break;
                    if (clock.ElapsedMilliseconds < 1000) continue;
                    bytes[index] += Encoding.UTF8.GetByteCount(text);
                    using var doc = JsonDocument.Parse(text); var root = doc.RootElement;
                    switch (root.GetProperty("type").GetString())
                    {
                        case "telemetry":
                            if (root.GetProperty("frame").GetProperty("mode").GetString() != "demo") throw new Exception("Unlabeled synthetic sample");
                            frames[index]++; break;
                        case "pong": if (index == 1) rtts.Add(clock.Elapsed.TotalMilliseconds - root.GetProperty("sentMs").GetDouble()); break;
                        case "ack": if (root.GetProperty("stage").GetString() == "simulated") simulated++; break;
                    }
                }
            }
            catch (OperationCanceledException) when (duration.IsCancellationRequested) { }
            catch (WebSocketException) when (duration.IsCancellationRequested) { }
        }
        var readers = Task.WhenAll(Read(dashboard, 0), Read(panel, 1));
        await Task.Delay(1000); cpu = process.TotalProcessorTime; alloc = GC.GetTotalAllocatedBytes();
        var measurementStart = clock.Elapsed;
        for (var i = 1; i <= 50; i++)
        {
            await Send(dashboard, new { type = "ping", sentMs = clock.ElapsedMilliseconds });
            await Send(panel, new { type = "ping", sentMs = clock.ElapsedMilliseconds });
            await Send(panel, new { type = "command", id = "b" + i, sequence = i, action = "lights", phase = "press" });
            await Task.Delay(100);
        }
        await Task.Delay(200); clock.Stop(); duration.Cancel(); await readers; rtts.Sort();
        double Percentile(double p) => rtts.Count == 0 ? double.NaN : rtts[(int)Math.Ceiling((rtts.Count - 1) * p)];
        var measured = (clock.Elapsed - measurementStart).TotalSeconds;
        results.Add(new { requestedHz = hz, warmupSeconds = 1, seconds = measured, clientCount = 2, frames,
            receivedHz = frames.Select(f => f / measured).ToArray(), payloadBytes = bytes,
            roundTrips = rtts.Count, rttMedianMs = Percentile(.5), rttP95Ms = Percentile(.95), rttMaxMs = rtts.LastOrDefault(),
            simulatedCommandAcks = simulated, cpuMilliseconds = (process.TotalProcessorTime - cpu).TotalMilliseconds,
            cpuPercentOfOneCore = (process.TotalProcessorTime - cpu).TotalSeconds / measured * 100,
            managedAllocatedBytes = GC.GetTotalAllocatedBytes() - alloc, workingSetBytes = process.WorkingSet64 });
        if (frames.Any(f => f < hz * 3) || simulated != 50 || rtts.Count != 50) throw new Exception("Transport benchmark lost too many frames or acknowledgments");
        dashboard.Abort(); panel.Abort();
    }
    AtomicFile.Write(output, Protocol.Serialize(new { appVersion = Protocol.AppVersion, measuredAtUtc = DateTimeOffset.UtcNow,
        environment = System.Runtime.InteropServices.RuntimeInformation.OSDescription, runtime = System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription,
        scope = "Real loopback TLS/WebSocket, two software clients, synthetic DEMO; not Wi-Fi, physical phones, FPS or game-input latency", results }));
    Console.WriteLine(File.ReadAllText(output));
}
finally { Directory.Delete(temp, true); }

sealed class NoGame : IGameProbe
{
    public bool IsRunning(string gameId) => false;
    public bool IsForeground(string gameId) => false;
    public bool HasSharedMemoryConflict(string gameId) => false;
}
sealed class ForbiddenInput : IKeySink
{
    public void KeyDown(ushort key) => throw new InvalidOperationException("DEMO attempted real input");
    public void KeyUp(ushort key) => throw new InvalidOperationException("DEMO attempted real input");
}
