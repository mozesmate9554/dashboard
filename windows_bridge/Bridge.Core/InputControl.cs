using System.Runtime.InteropServices;

namespace SimControlStudio;

public static class KeyNames
{
    private static readonly Dictionary<string, ushort> Named = new(StringComparer.OrdinalIgnoreCase)
    {
        ["CTRL"] = 0x11, ["SHIFT"] = 0x10, ["ALT"] = 0x12, ["SPACE"] = 0x20,
        ["ENTER"] = 0x0D, ["TAB"] = 9, ["BACKSPACE"] = 8, ["ESC"] = 0x1B,
        ["UP"] = 0x26, ["DOWN"] = 0x28, ["LEFT"] = 0x25, ["RIGHT"] = 0x27,
        ["PAGEUP"] = 0x21, ["PAGEDOWN"] = 0x22, ["HOME"] = 0x24, ["END"] = 0x23,
        ["INSERT"] = 0x2D, ["DELETE"] = 0x2E, ["MINUS"] = 0xBD, ["EQUALS"] = 0xBB,
        ["COMMA"] = 0xBC, ["PERIOD"] = 0xBE
    };
    public static ushort[] Parse(string value)
    {
        if (string.IsNullOrWhiteSpace(value) || value.Length > 60) throw new ArgumentException("Üres vagy túl hosszú billentyűkombináció.");
        var names = value.ToUpperInvariant().Split('+', StringSplitOptions.TrimEntries);
        if (names.Length is < 1 or > 4 || names.Distinct().Count() != names.Length) throw new ArgumentException("Hibás kombináció.");
        var codes = names.Select(n =>
        {
            if (Named.TryGetValue(n, out var code)) return code;
            if (n.Length == 1 && char.IsAsciiLetterOrDigit(n[0])) return (ushort)n[0];
            if (n.StartsWith('F') && int.TryParse(n.AsSpan(1), out var function) && function is >= 1 and <= 12) return (ushort)(0x6F + function);
            throw new ArgumentException($"Nem támogatott billentyű: {n}");
        }).ToArray();
        if (names.Contains("ALT") && (names.Contains("F4") || names.Contains("TAB") || names.Contains("ESC")) ||
            names.Contains("CTRL") && (names.Contains("ESC") || names.Contains("ALT") && names.Contains("DELETE")))
            throw new ArgumentException("Ez rendszerbillentyű, nem játékvezérlés.");
        return codes;
    }
}

public interface IKeySink { void KeyDown(ushort key); void KeyUp(ushort key); }

public sealed class WindowsKeySink : IKeySink
{
    public void KeyDown(ushort key) => Send(key, false);
    public void KeyUp(ushort key) => Send(key, true);
    private static void Send(ushort key, bool up)
    {
        if (!OperatingSystem.IsWindows()) throw new PlatformNotSupportedException("Windows SendInput szükséges.");
        var scan = NativeInput.MapVirtualKey(key, 0);
        var extended = key is 0x21 or 0x22 or 0x23 or 0x24 or 0x25 or 0x26 or 0x27 or 0x28 or 0x2D or 0x2E;
        var input = new NativeInput.Input
        {
            Type = 1,
            Data = new() { Keyboard = new() { Scan = (ushort)scan, Flags = 8u | (up ? 2u : 0) | (extended ? 1u : 0) } }
        };
        if (scan == 0 || NativeInput.SendInput(1, [input], Marshal.SizeOf<NativeInput.Input>()) != 1)
            throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error(), "A Windows nem fogadta a billentyűt. Ellenőrizd az előtérjátékot és az azonos jogosultsági szintet.");
    }
}

internal static class NativeInput
{
    [StructLayout(LayoutKind.Sequential)] internal struct Input { public uint Type; public InputUnion Data; }
    [StructLayout(LayoutKind.Explicit)] internal struct InputUnion
    {
        [FieldOffset(0)] public KeyboardInput Keyboard;
        [FieldOffset(0)] public MouseInput Mouse;
    }
    [StructLayout(LayoutKind.Sequential)] internal struct KeyboardInput
    { public ushort VirtualKey; public ushort Scan; public uint Flags; public uint Time; public nuint ExtraInfo; }
    [StructLayout(LayoutKind.Sequential)] internal struct MouseInput
    { public int X; public int Y; public uint MouseData; public uint Flags; public uint Time; public nuint ExtraInfo; }
    [DllImport("user32.dll", SetLastError = true)] internal static extern uint SendInput(uint count, Input[] inputs, int size);
    [DllImport("user32.dll")] internal static extern uint MapVirtualKey(uint code, uint type);
    [DllImport("user32.dll")] internal static extern nint GetForegroundWindow();
    [DllImport("user32.dll")] internal static extern uint GetWindowThreadProcessId(nint window, out uint processId);
}

public sealed class ControlEngine(BridgeConfiguration config, IGameProbe probe, IKeySink sink) : IDisposable
{
    private sealed record Lease(string Owner, string Action, ushort[] Keys, long ExpiresAt);
    private readonly object _gate = new();
    private readonly Dictionary<string, Lease> _leases = [];
    private readonly Dictionary<ushort, int> _keyOwners = [];
    private readonly Dictionary<string, CancellationTokenSource> _repeats = [];
    private readonly Dictionary<string, CancellationTokenSource> _owners = [];
    private readonly System.Collections.Concurrent.ConcurrentDictionary<string, SemaphoreSlim> _pressGates = [];
    private readonly CancellationTokenSource _shutdown = new();
    public int HeldKeyCount { get { lock (_gate) return _keyOwners.Count; } }
    public event Action<string>? Error;
    private bool Allowed => config.GameId != "demo" && config.MobileControlEnabled && probe.IsRunning(config.GameId) && probe.IsForeground(config.GameId);

    public async Task<ControlAck> ExecuteAsync(string owner, bool canControl, ControlRequest request,
        CancellationToken cancellation = default, string? profileId = null)
    {
        if (request.Phase != "press" || !ActionCatalog.Actions.Contains(request.Action))
            return await ExecuteCoreAsync(owner, canControl, request, cancellation, profileId);
        CancellationToken ownerToken;
        lock (_gate)
        {
            if (!_owners.TryGetValue(owner, out var source)) _owners[owner] = source = new();
            ownerToken = source.Token;
        }
        using var linked = CancellationTokenSource.CreateLinkedTokenSource(cancellation, ownerToken, _shutdown.Token);
        var gate = _pressGates.GetOrAdd(request.Action, _ => new(1, 1));
        var entered = false;
        try
        {
            await gate.WaitAsync(linked.Token); entered = true;
            return await ExecuteCoreAsync(owner, canControl, request, linked.Token, profileId);
        }
        catch (OperationCanceledException) { return new("ack", request.Id, "rejected", "cancelled"); }
        finally { if (entered) gate.Release(); }
    }
    private async Task<ControlAck> ExecuteCoreAsync(string owner, bool canControl, ControlRequest request,
        CancellationToken cancellation, string? profileId)
    {
        ControlAck Ack(string stage, string? reason = null) => new("ack", request.Id, stage, reason, TimestampMs: DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());
        if (cancellation.IsCancellationRequested) return Ack("rejected", "cancelled");
        if (string.IsNullOrEmpty(request.Id) || request.Id.Length > 100 || !ActionCatalog.Actions.Contains(request.Action) ||
            request.Phase is not ("press" or "down" or "up")) return Ack("rejected", "invalid_command");
        var leaseId = owner + ":" + request.Action;
        // Key-up always releases this session's existing lease, even after permissions/focus changed.
        if (request.Phase == "up") { lock (_gate) { StopRepeat(leaseId); Release(leaseId); } return Ack("released"); }
        if (!canControl) return Ack("rejected", "device_read_only");
        if (!Allowed) { ReleaseOwner(owner); return Ack("rejected", "control_disabled_or_game_not_foreground"); }
        if (!config.ResolveBindings(profileId).TryGetValue(request.Action, out var binding))
            return Ack("rejected", "unsupported_or_unmapped");
        try { binding.Validate(); }
        catch (ArgumentException) { return Ack("rejected", "invalid_binding"); }
        if (request.Phase == "down" && binding.Mode == "press") return Ack("rejected", "press_mode_requires_press");
        if (binding.Mode == "repeat" && request.Phase == "down")
        {
            try
            {
                lock (_gate)
                {
                    if (_repeats.ContainsKey(leaseId)) return Ack("executed");
                    if (!Allowed) return Ack("rejected", "focus_lost");
                    // Acknowledge execution only after the first actual input succeeded.
                    Acquire(leaseId, owner, request.Action, KeyNames.Parse(binding.Keys));
                    var repeat = CancellationTokenSource.CreateLinkedTokenSource(cancellation, _shutdown.Token);
                    _repeats[leaseId] = repeat;
                    _ = RepeatAsync(leaseId, owner, request.Action, binding, repeat);
                }
                return Ack("executed");
            }
            catch (Exception e) when (e is System.ComponentModel.Win32Exception or PlatformNotSupportedException)
            { ReleaseOwner(owner); return Ack("rejected", "input_failed"); }
        }
        try
        {
            var id = request.Phase == "down" ? leaseId : leaseId + ":" + request.Id;
            lock (_gate)
            {
                if (!Allowed) return Ack("rejected", "focus_lost");
                Acquire(id, owner, request.Action, KeyNames.Parse(binding.Keys));
            }
            if (request.Phase == "down") return Ack("executed");
            try { await Task.Delay(binding.DurationMs, cancellation); }
            finally { lock (_gate) Release(id); }
            return Ack("executed");
        }
        catch (OperationCanceledException) { return Ack("rejected", "cancelled"); }
        catch (Exception e) when (e is System.ComponentModel.Win32Exception or PlatformNotSupportedException)
        { ReleaseOwner(owner); return Ack("rejected", "input_failed"); }
    }

    private async Task RepeatAsync(string id, string owner, string action, KeyBinding binding, CancellationTokenSource source)
    {
        var expiry = Environment.TickCount64 + 3000; // Repeated input is never an unbounded macro.
        var first = true;
        try
        {
            while (!source.IsCancellationRequested && Allowed && Environment.TickCount64 < expiry)
            {
                lock (_gate)
                {
                    if (!Allowed) break;
                    if (!first) Acquire(id, owner, action, KeyNames.Parse(binding.Keys));
                    first = false;
                }
                try { await Task.Delay(binding.DurationMs, source.Token); }
                finally { lock (_gate) Release(id); }
                await Task.Delay(binding.RepeatMs, source.Token);
            }
        }
        catch (OperationCanceledException) { }
        catch (Exception e) when (e is System.ComponentModel.Win32Exception or PlatformNotSupportedException) { Error?.Invoke(e.Message); }
        finally
        {
            lock (_gate)
            {
                Release(id);
                if (_repeats.TryGetValue(id, out var current) && ReferenceEquals(current, source)) _repeats.Remove(id);
            }
            source.Dispose();
        }
    }
    private void Acquire(string id, string owner, string action, ushort[] keys)
    {
        if (_leases.TryGetValue(id, out var existing)) { _leases[id] = existing with { ExpiresAt = Environment.TickCount64 + 3000 }; return; }
        var acquired = new List<ushort>();
        try
        {
            foreach (var key in keys)
            {
                var count = _keyOwners.GetValueOrDefault(key);
                if (count == 0) sink.KeyDown(key);
                _keyOwners[key] = count + 1; acquired.Add(key);
            }
            _leases[id] = new(owner, action, keys, Environment.TickCount64 + 3000);
        }
        catch
        {
            foreach (var key in acquired.AsEnumerable().Reverse()) ReleaseKey(key);
            throw;
        }
    }
    private void ReleaseKey(ushort key)
    {
        if (!_keyOwners.TryGetValue(key, out var count)) return;
        if (count > 1) { _keyOwners[key] = count - 1; return; }
        try { sink.KeyUp(key); _keyOwners.Remove(key); }
        catch (System.ComponentModel.Win32Exception e) { Error?.Invoke(e.Message); } // Retain failed releases for watchdog retry.
    }
    private void Release(string id)
    {
        if (_leases.Remove(id, out var lease)) foreach (var key in lease.Keys.Reverse()) ReleaseKey(key);
    }
    private void StopRepeat(string id) { if (_repeats.Remove(id, out var repeat)) repeat.Cancel(); }
    public void ReleaseOwner(string owner)
    {
        lock (_gate)
        {
            if (_owners.Remove(owner, out var source)) { source.Cancel(); source.Dispose(); }
            foreach (var id in _repeats.Keys.Where(k => k.StartsWith(owner + ":", StringComparison.Ordinal)).ToArray()) StopRepeat(id);
            foreach (var id in _leases.Where(k => k.Value.Owner == owner).Select(k => k.Key).ToArray()) Release(id);
        }
    }
    public void Watchdog()
    {
        lock (_gate)
        {
            if (!Allowed) { ReleaseAll(); return; }
            foreach (var id in _leases.Where(k => k.Value.ExpiresAt < Environment.TickCount64).Select(k => k.Key).ToArray()) Release(id);
            foreach (var key in _keyOwners.Keys.Where(k => !_leases.Values.Any(l => l.Keys.Contains(k))).ToArray()) ReleaseKey(key);
        }
    }
    public void ReleaseAll()
    {
        lock (_gate)
        {
            foreach (var source in _owners.Values) { source.Cancel(); source.Dispose(); }
            _owners.Clear();
            foreach (var id in _repeats.Keys.ToArray()) StopRepeat(id);
            foreach (var id in _leases.Keys.ToArray()) Release(id);
            foreach (var key in _keyOwners.Keys.ToArray()) ReleaseKey(key);
        }
    }
    public void Dispose() { _shutdown.Cancel(); ReleaseAll(); _shutdown.Dispose(); }
}

public sealed class SessionCommandGuard
{
    private long _lastSequence = -1;
    private readonly HashSet<string> _ids = [];
    private readonly Queue<string> _order = [];
    private double _tokens = 30;
    private long _last = Environment.TickCount64;
    public string? Validate(ControlRequest request)
    {
        if (request.Id == null || request.Id.Length is < 1 or > 100) return "invalid_id";
        if (request.Sequence <= _lastSequence || _ids.Contains(request.Id)) return "duplicate_or_out_of_order";
        var now = Environment.TickCount64;
        _tokens = Math.Min(30, _tokens + (now - _last) * 0.03); _last = now;
        // Release is exempt from throttling so a burst can never strand a held key.
        if (_tokens < 1 && request.Phase != "up") return "rate_limited";
        if (request.Phase != "up") _tokens--;
        _lastSequence = request.Sequence; _ids.Add(request.Id); _order.Enqueue(request.Id);
        if (_order.Count > 256) _ids.Remove(_order.Dequeue());
        return null;
    }
}
