using System.Collections.Concurrent;
using System.Net;
using System.Net.Sockets;
using System.Net.WebSockets;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Text.Json;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;

namespace SimControlStudio;

public sealed class BridgeRuntime : IAsyncDisposable
{
    private readonly BridgeConfiguration _config;
    private readonly IGameAdapter _adapter;
    private readonly X509Certificate2 _certificate;
    private readonly CancellationTokenSource _stop = new();
    private readonly ConcurrentDictionary<string, ClientSession> _clients = [];
    private readonly ConcurrentQueue<object> _events = [];
    private readonly ConcurrentDictionary<string, (long Window, int Count)> _authAttempts = [];
    private readonly HashSet<string> _profiles;
    private WebApplication? _web;
    private Task? _pump;
    private Task? _discovery;
    private TelemetryFrame? _latest;
    private string? _suggestedProfile;
    public DeviceRegistry Registry { get; }
    public ControlEngine Controls { get; }
    public AdapterHealth Health => _adapter.Health;
    public TelemetryFrame? Latest => Volatile.Read(ref _latest);
    public string Fingerprint => BridgeCertificate.Fingerprint(_certificate);
    public IReadOnlyList<object> Events => _events.ToArray();
    public IReadOnlyList<object> Clients => _clients.Values.Select(c => (object)new { c.DeviceId, c.Name, c.Role, c.Hz, c.LatencyMs }).ToArray();
    public bool IsRunning => _web != null;
    public BridgeRuntime(BridgeConfiguration config, DeviceRegistry registry, X509Certificate2 certificate,
        IGameAdapter adapter, IGameProbe probe, IKeySink sink, IEnumerable<string>? profiles = null)
    {
        config.Validate(); _config = config; Registry = registry; _certificate = certificate;
        _adapter = adapter; Controls = new(config, probe, sink);
        _profiles = new(profiles ?? [], StringComparer.Ordinal);
        Registry.Revoked += OnRevoke;
        Controls.Error += detail => Log("input_error", detail);
    }
    public void Log(string kind, string detail)
    {
        _events.Enqueue(new { timestampMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(), kind, detail });
        while (_events.Count > 200) _events.TryDequeue(out _);
    }
    public async Task StartAsync(CancellationToken cancellation = default)
    {
        if (_web != null) throw new InvalidOperationException("A Bridge már fut.");
        var builder = WebApplication.CreateSlimBuilder();
        builder.Logging.ClearProviders(); // No URL, credential or device secret logging.
        builder.WebHost.ConfigureKestrel(k =>
        {
            k.Limits.MaxRequestBodySize = Protocol.MaxMessageBytes;
            k.Limits.MaxConcurrentConnections = 32;
            k.Limits.RequestHeadersTimeout = TimeSpan.FromSeconds(5);
            k.Listen(IPAddress.Parse(_config.BindAddress), _config.Port, listen => listen.UseHttps(_certificate));
        });
        var web = builder.Build();
        web.UseWebSockets(new WebSocketOptions { KeepAliveInterval = TimeSpan.FromSeconds(2), KeepAliveTimeout = TimeSpan.FromSeconds(5) });
        web.MapGet("/health", () => Results.Json(new { name = "SIM CONTROL STUDIO", version = Protocol.AppVersion, protocol = Protocol.Version }));
        web.Map("/ws", HandleSocketAsync);
        await web.StartAsync(cancellation);
        _web = web; _pump = PumpAsync(_stop.Token);
        if (_config.DiscoveryEnabled && _config.BindAddress != "127.0.0.1") _discovery = DiscoveryAsync(_stop.Token);
        Log("started", $"TLS / {_config.GameId} / {_config.Hz} Hz");
    }
    private async Task PumpAsync(CancellationToken cancellation)
    {
        using var timer = new PeriodicTimer(TimeSpan.FromSeconds(1d / _config.Hz));
        try
        {
            while (await timer.WaitForNextTickAsync(cancellation))
            {
                try
                {
                    var frame = await _adapter.PollAsync(cancellation);
                    if (frame != null) Volatile.Write(ref _latest, frame);
                    var latest = Latest;
                    var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
                    if (latest != null && (now - latest.TimestampMs > 500 || Health.State != "live") && latest.State != "stale")
                        Volatile.Write(ref _latest, latest.Stale(now));
                    Controls.Watchdog();
                    foreach (var client in _clients.Values)
                        if (Environment.TickCount64 - client.LastSeenTicks > 5000) { Controls.ReleaseOwner(client.Owner); client.Close(); }
                }
                catch (OperationCanceledException) when (cancellation.IsCancellationRequested) { break; }
                catch (Exception e) when (e is IOException or SocketException or InvalidDataException)
                {
                    Log("adapter_error", e.Message);
                    if (Latest is { } last) Volatile.Write(ref _latest, last.Stale(DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()));
                }
            }
        }
        catch (OperationCanceledException) { }
    }
    private bool AllowAuth(IPAddress? remote)
    {
        var key = remote?.ToString() ?? "unknown";
        var now = Environment.TickCount64;
        if (_authAttempts.Count > 128)
            foreach (var old in _authAttempts.Where(p => now - p.Value.Window > 60000).ToArray()) _authAttempts.TryRemove(old.Key, out _);
        var attempt = _authAttempts.AddOrUpdate(key, (now, 1), (_, previous) => now - previous.Window > 60000 ? (now, 1) : (previous.Window, previous.Count + 1));
        return attempt.Count <= 20;
    }
    private async Task HandleSocketAsync(HttpContext context)
    {
        // Browser origins are not part of this native-only protocol.
        if (!context.WebSockets.IsWebSocketRequest || context.Request.Headers.ContainsKey("Origin") || !AllowAuth(context.Connection.RemoteIpAddress))
        { context.Response.StatusCode = 403; return; }
        using var socket = await context.WebSockets.AcceptWebSocketAsync();
        ClientSession? session = null;
        using var lifetime = CancellationTokenSource.CreateLinkedTokenSource(_stop.Token, context.RequestAborted);
        try
        {
            using var authTimeout = CancellationTokenSource.CreateLinkedTokenSource(lifetime.Token);
            authTimeout.CancelAfter(5000);
            var raw = await ReadMessageAsync(socket, authTimeout.Token);
            var hello = raw == null ? null : Protocol.Deserialize<Hello>(raw);
            if (hello == null || hello.ProfileId?.Length > 100) { await socket.CloseAsync(WebSocketCloseStatus.PolicyViolation, "invalid_hello", lifetime.Token); return; }
            var authentication = Registry.Authenticate(hello);
            if (authentication == null) { await socket.CloseAsync(WebSocketCloseStatus.PolicyViolation, "authentication_failed", lifetime.Token); return; }
            session = new(socket, hello, lifetime);
            if (_clients.TryRemove(hello.DeviceId, out var previous)) { Controls.ReleaseOwner(previous.Owner); previous.Close(); }
            _clients[hello.DeviceId] = session;
            await session.SendAsync(new { type = "welcome", protocol = Protocol.Version, bridgeVersion = Protocol.AppVersion,
                deviceId = hello.DeviceId, secret = authentication.NewSecret, canControl = authentication.Device.CanControl,
                mobileControlEnabled = _config.MobileControlEnabled, gameId = _config.GameId,
                supportedActions = MappedActions(), suggestedProfile = _suggestedProfile }, lifetime.Token);
            Log("connected", hello.Name);
            using var senderStop = CancellationTokenSource.CreateLinkedTokenSource(lifetime.Token);
            var sender = SendFramesAsync(session, senderStop.Token);
            try
            {
                var guard = new SessionCommandGuard();
                while (!lifetime.IsCancellationRequested && socket.State == WebSocketState.Open)
                {
                    var message = await ReadMessageAsync(socket, lifetime.Token);
                    if (message == null) break;
                    session.LastSeenTicks = Environment.TickCount64;
                    using var document = JsonDocument.Parse(message, new JsonDocumentOptions { MaxDepth = 16 });
                    var root = document.RootElement;
                    if (!root.TryGetProperty("type", out var type)) continue;
                    switch (type.GetString())
                    {
                        case "ping":
                            await session.SendAsync(new { type = "pong", sentMs = root.GetProperty("sentMs").GetInt64(), bridgeMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() }, lifetime.Token);
                            break;
                        case "latency":
                            session.LatencyMs = Math.Clamp(root.GetProperty("ms").GetInt32(), 0, 60000);
                            break;
                        case "releaseAll": Controls.ReleaseOwner(session.Owner); break;
                        case "profile":
                            var profile = root.GetProperty("profileId").GetString();
                            if (profile != null && _profiles.Contains(profile))
                            {
                                _suggestedProfile = profile; Registry.RememberProfile(session.DeviceId, profile);
                                foreach (var client in _clients.Values)
                                    await client.SendAsync(new { type = "profileSuggestion", profileId = profile, sourceDevice = session.DeviceId }, lifetime.Token);
                            }
                            break;
                        case "command":
                            var request = root.Deserialize<ControlRequest>(Protocol.Json);
                            if (request == null) break;
                            var rejected = guard.Validate(request);
                            if (rejected != null) { await session.SendAsync(new ControlAck("ack", request.Id, "rejected", rejected), lifetime.Token); break; }
                            await session.SendAsync(new ControlAck("ack", request.Id, "received", TimestampMs: DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()), lifetime.Token);
                            var device = Registry.Get(session.DeviceId);
                            var ack = await Controls.ExecuteAsync(session.Owner, device?.CanControl == true && session.Role is "panel" or "hybrid", request, lifetime.Token);
                            await session.SendAsync(ack, lifetime.Token);
                            Log("command", $"{session.Name} / {request.Action} / {ack.Stage} / {ack.Reason}");
                            break;
                    }
                }
            }
            finally
            {
                senderStop.Cancel();
                try { await sender; } catch (OperationCanceledException) { } catch (WebSocketException) { }
            }
        }
        catch (Exception e) when (e is WebSocketException or OperationCanceledException or JsonException or InvalidOperationException or KeyNotFoundException or InvalidDataException or FormatException or DecoderFallbackException)
        { if (e is not OperationCanceledException) Log("connection_closed", e.GetType().Name); }
        finally
        {
            if (session != null)
            {
                Controls.ReleaseOwner(session.Owner);
                if (_clients.TryGetValue(session.DeviceId, out var current) && ReferenceEquals(current, session)) _clients.TryRemove(session.DeviceId, out _);
                Log("disconnected", session.Name);
            }
        }
    }
    private string[] MappedActions() => _config.Bindings.GetValueOrDefault(_config.GameId)?.Keys.ToArray() ?? [];
    private async Task SendFramesAsync(ClientSession client, CancellationToken cancellation)
    {
        using var timer = new PeriodicTimer(TimeSpan.FromSeconds(1d / client.Hz));
        long lastSequence = -1, lastHealth = 0;
        string? lastState = null;
        try
        {
            while (await timer.WaitForNextTickAsync(cancellation))
            {
                var frame = Latest;
                if (frame != null && (frame.Sequence != lastSequence || frame.State != lastState))
                {
                    await client.SendAsync(new { type = "telemetry", frame }, cancellation);
                    lastSequence = frame.Sequence; lastState = frame.State;
                }
                var now = Environment.TickCount64;
                if (now - lastHealth > 1000)
                {
                    await client.SendAsync(new { type = "health", health = Health, canControl = Registry.Get(client.DeviceId)?.CanControl == true,
                        mobileControlEnabled = _config.MobileControlEnabled, supportedActions = MappedActions() }, cancellation);
                    lastHealth = now;
                }
            }
        }
        catch (OperationCanceledException) when (cancellation.IsCancellationRequested) { }
        catch (WebSocketException) { client.Close(); }
    }
    public static async Task<string?> ReadMessageAsync(WebSocket socket, CancellationToken cancellation)
    {
        var buffer = new byte[Protocol.MaxMessageBytes];
        var offset = 0;
        while (true)
        {
            if (offset == buffer.Length) throw new InvalidDataException("Túl nagy hálózati üzenet.");
            var result = await socket.ReceiveAsync(buffer.AsMemory(offset), cancellation);
            if (result.MessageType == WebSocketMessageType.Close) return null;
            if (result.MessageType != WebSocketMessageType.Text) throw new InvalidDataException("Csak UTF-8 JSON szöveges üzenet engedélyezett.");
            offset += result.Count;
            if (result.EndOfMessage) return new UTF8Encoding(false, true).GetString(buffer, 0, offset);
        }
    }
    private async Task DiscoveryAsync(CancellationToken cancellation)
    {
        try
        {
            using var udp = new UdpClient(new IPEndPoint(IPAddress.Parse(_config.BindAddress), _config.DiscoveryPort));
            var last = new Dictionary<IPAddress, long>();
            while (!cancellation.IsCancellationRequested)
            {
                var packet = await udp.ReceiveAsync(cancellation);
                var query = Encoding.ASCII.GetString(packet.Buffer);
                if (!query.StartsWith("SIMCONTROL_DISCOVER_V1 ", StringComparison.Ordinal) || query.Length > 80) continue;
                var now = Environment.TickCount64;
                if (last.TryGetValue(packet.RemoteEndPoint.Address, out var sent) && now - sent < 1000) continue;
                if (last.Count > 256) last.Clear();
                last[packet.RemoteEndPoint.Address] = now;
                var response = Protocol.Serialize(new { service = "simcontrol", protocol = 1, port = _config.Port,
                    pin = Fingerprint, name = "SIM CONTROL STUDIO", nonce = query[23..].Trim() });
                await udp.SendAsync(Encoding.UTF8.GetBytes(response), packet.RemoteEndPoint, cancellation);
            }
        }
        catch (OperationCanceledException) { }
        catch (SocketException e) { Log("discovery_error", e.Message); }
    }
    private void OnRevoke(string id)
    {
        if (_clients.TryGetValue(id, out var client)) { Controls.ReleaseOwner(client.Owner); client.Close(); }
    }
    public object DiagnosticReport() => new { application = "SIM CONTROL STUDIO", version = Protocol.AppVersion,
        exportedAt = DateTimeOffset.UtcNow, health = Health, clients = Clients, latest = Latest, events = Events,
        knownLimitations = new[] { "No physical ACR or phone test performed in the build environment.",
            "ACR timing/TC/ABS/brake bias/extended fields remain unsupported until verified." } };
    public async ValueTask DisposeAsync()
    {
        Registry.Revoked -= OnRevoke; Registry.ClosePairingWindow();
        _stop.Cancel(); Controls.ReleaseAll();
        foreach (var client in _clients.Values) client.Close();
        foreach (var task in new[] { _pump, _discovery }.OfType<Task>())
            try { await task; } catch (OperationCanceledException) { }
        if (_web != null) { await _web.StopAsync(); await _web.DisposeAsync(); _web = null; }
        Controls.Dispose(); _adapter.Dispose(); _stop.Dispose();
    }

    private sealed class ClientSession(WebSocket socket, Hello hello, CancellationTokenSource lifetime)
    {
        private readonly SemaphoreSlim _sendGate = new(1, 1);
        public string DeviceId => hello.DeviceId;
        public string Name => hello.Name;
        public string Role => hello.Role;
        public int Hz => hello.Hz;
        public string Owner { get; } = hello.DeviceId + "/" + Guid.NewGuid().ToString("N");
        public long LastSeenTicks { get; set; } = Environment.TickCount64;
        public int LatencyMs { get; set; }
        public async Task SendAsync(object value, CancellationToken cancellation)
        {
            using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellation);
            timeout.CancelAfter(2000);
            await _sendGate.WaitAsync(timeout.Token);
            try { await socket.SendAsync(Encoding.UTF8.GetBytes(Protocol.Serialize(value)), WebSocketMessageType.Text, true, timeout.Token); }
            catch (OperationCanceledException) when (!cancellation.IsCancellationRequested) { Close(); }
            finally { _sendGate.Release(); }
        }
        public void Close() { lifetime.Cancel(); socket.Abort(); }
    }
}
