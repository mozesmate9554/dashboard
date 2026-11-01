using System.Buffers.Binary;
using System.Diagnostics;
using System.IO.MemoryMappedFiles;
using System.Net;
using System.Net.Sockets;
using System.Text;

namespace SimControlStudio;

public interface IGameAdapter : IDisposable
{
    bool IsDemo => false;
    string GameId { get; }
    AdapterHealth Health { get; }
    ValueTask<TelemetryFrame?> PollAsync(CancellationToken cancellation);
}

public interface IGameProbe
{
    bool IsRunning(string gameId);
    bool HasSharedMemoryConflict(string gameId);
    bool IsForeground(string gameId);
}

public sealed class WindowsGameProbe(string[] rallyProcessNames) : IGameProbe
{
    private string[] Names(string game) => game switch
    {
        "acr" => rallyProcessNames, "ac" => ["acs", "acs_x86"],
        "acc" => ["acc", "AC2-Win64-Shipping"], "beamng" => ["BeamNG.drive.x64", "BeamNG.drive"], _ => []
    };
    public bool IsRunning(string gameId) => OperatingSystem.IsWindows() && Names(gameId).Any(name =>
    {
        var processes = Process.GetProcessesByName(name);
        try { return processes.Length > 0; }
        finally { foreach (var process in processes) process.Dispose(); }
    });
    public bool HasSharedMemoryConflict(string gameId) => new[] { "acr", "ac", "acc" }
        .Any(id => id != gameId && IsRunning(id));
    public bool IsForeground(string gameId)
    {
        if (!OperatingSystem.IsWindows()) return false;
        NativeInput.GetWindowThreadProcessId(NativeInput.GetForegroundWindow(), out var pid);
        if (pid == 0) return false;
        try
        {
            using var process = Process.GetProcessById((int)pid);
            return Names(gameId).Contains(process.ProcessName, StringComparer.OrdinalIgnoreCase);
        }
        catch (ArgumentException) { return false; }
        catch (System.ComponentModel.Win32Exception) { return false; }
    }
}

public interface IMemorySource : IDisposable
{
    byte[]? Read(string name, int size, bool packetCounter);
    void Reset();
}

public sealed class WindowsMemorySource : IMemorySource
{
    private readonly Dictionary<string, (MemoryMappedFile File, MemoryMappedViewAccessor View)> _maps = [];
    public byte[]? Read(string name, int size, bool packetCounter)
    {
        if (!OperatingSystem.IsWindows()) return null;
        try
        {
            if (!_maps.TryGetValue(name, out var map))
            {
                var file = MemoryMappedFile.OpenExisting(name, MemoryMappedFileRights.Read);
                try { map = (file, file.CreateViewAccessor(0, size, MemoryMappedFileAccess.Read)); }
                catch { file.Dispose(); throw; }
                _maps[name] = map;
            }
            var first = new byte[size];
            var second = new byte[size];
            // The API has no reader lock. Retry unstable copies; never invent a packet counter.
            for (var attempt = 0; attempt < 3; attempt++)
            {
                var before = packetCounter ? map.View.ReadInt32(0) : 0;
                map.View.ReadArray(0, first, 0, size);
                Thread.MemoryBarrier();
                map.View.ReadArray(0, second, 0, size);
                var after = packetCounter ? map.View.ReadInt32(0) : 0;
                if (before == after && first.AsSpan().SequenceEqual(second)) return first;
            }
            return null;
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or ArgumentException)
        {
            if (_maps.Remove(name, out var map)) { map.View.Dispose(); map.File.Dispose(); }
            return null;
        }
    }
    public void Reset() { foreach (var map in _maps.Values) { map.View.Dispose(); map.File.Dispose(); } _maps.Clear(); }
    public void Dispose() => Reset();
}

/// <summary>Independent byte decoder. Layout provenance is pinned in documentation/TELEMETRY.md.</summary>
public static class AcMemoryDecoder
{
    public const int PhysicsBytes = 800;
    public const int StaticBytes = 784;
    public const int GraphicsPrefixBytes = 176;
    public static TelemetryFrame Decode(byte[] physics, byte[]? statics, byte[]? graphics,
        string gameId, long timestampMs, long sequence)
    {
        if (physics.Length < 56) throw new InvalidDataException("Túl rövid physics blokk (legalább 56 bájt szükséges).");
        var source = $"{gameId}:shared-memory:v1";
        var fields = TelemetryCatalog.Empty(source, timestampMs);
        var invalid = false;
        int I(byte[] b, int o) => BinaryPrimitives.ReadInt32LittleEndian(b.AsSpan(o, 4));
        float F(byte[] b, int o) => BitConverter.Int32BitsToSingle(I(b, o));
        void Number(string key, double value, double low, double high, bool derived = false, string? unit = null)
        {
            var valid = double.IsFinite(value) && value >= low && value <= high;
            fields[key] = new(valid ? value : null, unit ?? TelemetryCatalog.Fields[key], source,
                timestampMs, valid ? Validity.Valid : Validity.Invalid, derived);
            if (!valid && key is "speed" or "rpm" or "gear") invalid = true;
        }
        Number("speed", F(physics, 28), 0, 1000);
        Number("rpm", I(physics, 20), 0, 30000);
        Number("gear", I(physics, 16) - 1, -1, 12, true); // wire 0=R, 1=N, 2=1
        Number("throttle", F(physics, 4), 0, 1);
        Number("brake", F(physics, 8), 0, 1);
        Number("steering", F(physics, 24), -10000, 10000); // Raw units: Rally unit not independently verified.
        Number("gX", F(physics, 44), -100, 100);
        Number("gY", F(physics, 48), -100, 100);
        Number("gZ", F(physics, 52), -100, 100);
        string? car = null;
        string? gameVersion = null;
        static string Text(byte[] b, int offset, int chars) => Encoding.Unicode.GetString(b, offset, chars * 2)
            .Split('\0')[0].Trim();
        if (statics is { Length: >= 420 })
        {
            car = Text(statics, 68, 33);
            if (car.Length == 0) car = null;
            gameVersion = Text(statics, 30, 15);
            if (gameVersion.Length == 0) gameVersion = null;
            if (car != null) fields["vehicleId"] = new(car, "text", source, timestampMs);
            var track = Text(statics, 134, 33);
            if (track.Length > 0) fields["stageId"] = new(track, "text", source, timestampMs);
            var limit = I(statics, 412);
            if (limit is > 0 and <= 30000) Number("rpmLimit", limit, 1, 30000);
        }
        // These extended offsets have an AC/ACC contract. ACR does NOT inherit their availability.
        if (gameId is "ac" or "acc" && physics.Length >= PhysicsBytes)
        {
            Number("fuel", F(physics, 12), 0, 1000);
            Number("clutch", F(physics, 364), 0, 1);
            Number("turbo", F(physics, 276), 0, 20);
            Number("yaw", F(physics, 208), -100, 100);
            Number("pitch", F(physics, 212), -100, 100);
            Number("roll", F(physics, 216), -100, 100);
            Number("brakeBias", F(physics, 564) * 100, 0, 100, true);
            Number("tcLevel", F(physics, 204), 0, 100);
            Number("absLevel", F(physics, 252), 0, 100);
            if (gameId == "acc") Number("waterTemp", F(physics, 712), -40, 300);
            foreach (var (key, offset, low, high) in new[]
            {
                ("tyrePressure", 88, 0d, 100d), ("tyreTempInner", 368, -40d, 400d),
                ("tyreTempMiddle", 384, -40d, 400d), ("tyreTempOuter", 400, -40d, 400d),
                ("brakeTemp", 348, -40d, 2000d), ("wheelSpeed", 104, -5000d, 5000d),
                ("wheelSlip", 56, -1000d, 1000d), ("suspension", 184, -1d, 2d)
            })
            {
                var values = Enumerable.Range(0, 4).Select(n => (double)F(physics, offset + 4 * n)).ToArray();
                var valid = values.All(v => double.IsFinite(v) && v >= low && v <= high);
                fields[key] = new(valid ? values : null, TelemetryCatalog.Fields[key], source, timestampMs,
                    valid ? Validity.Valid : Validity.Invalid);
            }
        }
        if (graphics is { Length: >= GraphicsPrefixBytes } && gameId is "ac" or "acc")
        {
            var status = I(graphics, 4);
            if (status is >= 0 and <= 3)
            {
                fields["sessionStatus"] = new(new[] { "off", "replay", "live", "paused" }[status], "state", source, timestampMs);
                Number("lap", I(graphics, 132), 0, 100000);
                Number("position", I(graphics, 136), 0, 10000);
                Number("lapCurrent", I(graphics, 140), 0, 86400000);
                Number("lapLast", I(graphics, 144), 0, 86400000);
                Number("lapBest", I(graphics, 148), 0, 86400000);
                Number("timeRemaining", F(graphics, 152), -1, 604800);
            }
        }
        if (invalid) throw new InvalidDataException("Érvénytelen alapteljesítmény-adatok; ismeretlen vagy sérült memóriakiosztás.");
        return new(sequence, timestampMs, gameId, source, "live", fields, car, gameVersion);
    }
}

public sealed class AcSharedMemoryAdapter(string gameId, IMemorySource memory, IGameProbe probe) : IGameAdapter
{
    private int? _lastPacket;
    private long _sequence;
    private long? _lastTicks;
    private long _windowMs = Environment.TickCount64;
    private int _windowFrames;
    private double _actualHz;
    public string GameId => gameId;
    public AdapterHealth Health { get; private set; } = new(gameId, $"{gameId}-shared-memory/0.1.0", false, false, "waiting", null, null, 0);
    public ValueTask<TelemetryFrame?> PollAsync(CancellationToken cancellation)
    {
        cancellation.ThrowIfCancellationRequested();
        var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        var running = probe.IsRunning(gameId);
        if (!running || probe.HasSharedMemoryConflict(gameId))
        {
            memory.Reset(); _lastPacket = null;
            Health = Health with { GameDetected = running, MemoryAvailable = false, State = "waiting",
                Error = running ? "Több játék használja ugyanazt a memórianevet. Zárd be a másik AC/ACC/Rally játékot." : null, ActualHz = 0,
                MemoryBlocks = new Dictionary<string, bool> { ["physics"] = false, ["static"] = false, ["graphics"] = false } };
            return ValueTask.FromResult<TelemetryFrame?>(null);
        }
        var bytes = memory.Read("Local\\acpmf_physics", AcMemoryDecoder.PhysicsBytes, true);
        if (bytes == null)
        {
            Health = Health with { GameDetected = true, MemoryAvailable = false, State = "waiting", Error = "A physics shared memory még nem érhető el.", ActualHz = 0,
                MemoryBlocks = new Dictionary<string, bool> { ["physics"] = false, ["static"] = false, ["graphics"] = false } };
            return ValueTask.FromResult<TelemetryFrame?>(null);
        }
        var packet = BinaryPrimitives.ReadInt32LittleEndian(bytes);
        if (packet == _lastPacket)
        {
            if (Environment.TickCount64 - (_lastTicks ?? 0) > 500)
            {
                Health = Health with { State = "stale", ActualHz = 0 };
                // Reopen handles after a silent/closed mapping to recover when the game recreates it.
                memory.Reset();
            }
            return ValueTask.FromResult<TelemetryFrame?>(null);
        }
        try
        {
            var statics = memory.Read("Local\\acpmf_static", AcMemoryDecoder.StaticBytes, false);
            var graphics = memory.Read("Local\\acpmf_graphics", AcMemoryDecoder.GraphicsPrefixBytes, true);
            var frame = AcMemoryDecoder.Decode(bytes, statics, graphics, gameId, now, ++_sequence);
            _lastPacket = packet; _lastTicks = Environment.TickCount64; _windowFrames++;
            var elapsed = Environment.TickCount64 - _windowMs;
            if (elapsed >= 1000) { _actualHz = _windowFrames * 1000d / elapsed; _windowFrames = 0; _windowMs = Environment.TickCount64; }
            Health = Health with { GameDetected = true, MemoryAvailable = true, State = "live", Error = null,
                LastPacketMs = now, ActualHz = _actualHz, GameVersion = frame.GameVersion,
                MemoryBlocks = new Dictionary<string, bool> { ["physics"] = true, ["static"] = statics != null, ["graphics"] = graphics != null } };
            return ValueTask.FromResult<TelemetryFrame?>(frame);
        }
        catch (InvalidDataException e)
        {
            Health = Health with { GameDetected = true, MemoryAvailable = true, State = "invalid", Error = e.Message, ActualHz = 0 };
            return ValueTask.FromResult<TelemetryFrame?>(null);
        }
    }
    public void Dispose() => memory.Dispose();
}

public sealed class BeamNgOutGaugeAdapter(int port, IGameProbe probe) : IGameAdapter
{
    private readonly UdpClient _udp = new(new IPEndPoint(IPAddress.Loopback, port));
    private long _sequence;
    public string GameId => "beamng";
    public AdapterHealth Health { get; private set; } = new("beamng", "beamng-outgauge/0.1.0", false, false, "waiting", null, null, 0);
    public ValueTask<TelemetryFrame?> PollAsync(CancellationToken cancellation)
    {
        cancellation.ThrowIfCancellationRequested();
        var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        TelemetryFrame? latest = null;
        var running = probe.IsRunning(GameId);
        var drained = 0;
        while (_udp.Available > 0 && drained++ < 64)
        {
            IPEndPoint? remote = null;
            var bytes = _udp.Receive(ref remote);
            if (!running || remote == null || !IPAddress.IsLoopback(remote.Address)) continue;
            try { latest = Decode(bytes, now, ++_sequence); }
            catch (InvalidDataException e) { Health = Health with { State = "invalid", Error = e.Message }; }
        }
        if (latest != null) Health = Health with { GameDetected = true, MemoryAvailable = true, State = "live", Error = null, LastPacketMs = now };
        else if (!running || now - (Health.LastPacketMs ?? 0) > 500)
            Health = Health with { GameDetected = running, State = "waiting", MemoryAvailable = false, ActualHz = 0 };
        return ValueTask.FromResult(latest);
    }
    public static TelemetryFrame Decode(byte[] bytes, long now, long sequence)
    {
        if (bytes.Length is not (92 or 96) || Encoding.ASCII.GetString(bytes, 4, 4).TrimEnd('\0') != "beam")
            throw new InvalidDataException("Nem BeamNG OutGauge csomag (92/96 bájt, beam azonosító szükséges).");
        float F(int o) => BitConverter.Int32BitsToSingle(BinaryPrimitives.ReadInt32LittleEndian(bytes.AsSpan(o, 4)));
        var source = "beamng:outgauge";
        var fields = TelemetryCatalog.Empty(source, now);
        foreach (var (name, value, min, max, derived) in new[]
        {
            ("speed", F(12) * 3.6, 0d, 1500d, true), ("rpm", (double)F(16), 0, 50000, false),
            ("gear", (double)bytes[10] - 1, -1, 20, true), ("throttle", (double)F(48), 0, 1, false),
            ("brake", (double)F(52), 0, 1, false), ("clutch", (double)F(56), 0, 1, false),
            ("waterTemp", (double)F(24), -273, 1000, false)
        })
        {
            if (!double.IsFinite(value) || value < min || value > max) throw new InvalidDataException("Érvénytelen OutGauge mező.");
            fields[name] = new(value, TelemetryCatalog.Fields[name], source, now, Derived: derived);
        }
        return new(sequence, now, "beamng", "beamng-outgauge/0.1.0", "live", fields);
    }
    public void Dispose() => _udp.Dispose();
}

public static class AdapterFactory
{
    public static IGameAdapter Create(BridgeConfiguration config, IGameProbe probe) => config.GameId switch
    {
        "acr" or "ac" or "acc" => new AcSharedMemoryAdapter(config.GameId, new WindowsMemorySource(), probe),
        "beamng" => new BeamNgOutGaugeAdapter(config.UdpPort, probe),
        "demo" => new DemoAdapter(),
        _ => throw new NotSupportedException("Az adapter még nincs implementálva.")
    };
}
