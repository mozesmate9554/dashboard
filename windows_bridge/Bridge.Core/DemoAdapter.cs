using System.Diagnostics;

namespace SimControlStudio;

public interface IDemoSource : IGameAdapter
{
    ControlAck Apply(string owner, ControlRequest request);
    void ReleaseOwner(string owner);
}

/// <summary>Explicit synthetic source. Never receives or invokes an IKeySink.</summary>
public sealed class DemoAdapter : IDemoSource
{
    private readonly object _gate = new();
    private readonly Stopwatch _clock = Stopwatch.StartNew();
    private readonly Dictionary<string, (string Action, long Expires)> _holds = [];
    private bool _ignition = true, _engine = true, _lights;
    private int _radioVolume = 6, _intercomVolume = 6;
    private int _tc = 3, _abs = 2, _map = 1, _diff = 2, _wiper;
    private double _bias = 58;
    private int? _requestedGear;
    private long _gearUntil, _sequence, _windowMs;
    private int _windowFrames;
    private double _hz;
    public string GameId => "demo";
    public bool IsDemo => true;
    public AdapterHealth Health { get; private set; } = new("demo", "synthetic-demo/0.2.0", false, false, "demo", null, null, 0);
    public ValueTask<TelemetryFrame?> PollAsync(CancellationToken cancellation)
    {
        cancellation.ThrowIfCancellationRequested();
        lock (_gate)
        {
            var tick = _clock.ElapsedMilliseconds;
            foreach (var key in _holds.Where(p => p.Value.Expires <= tick).Select(p => p.Key).ToArray()) _holds.Remove(key);
            var t = tick / 1000d;
            var phase = t % 20;
            var speed = !_engine ? 0 : (phase < 10 ? phase / 10 : (20 - phase) / 10) * 160;
            var gear = _requestedGear.HasValue && tick < _gearUntil ? _requestedGear.Value : speed < 1 ? 0 : Math.Min(6, (int)(speed / 34) + 1);
            var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            var fields = TelemetryCatalog.Empty("demo:synthetic:v1", now);
            void Set(string field, object value) => fields[field] = new(value, TelemetryCatalog.Fields[field], "demo:synthetic:v1", now);
            bool Held(string action) => _holds.Values.Any(h => h.Action == action);
            Set("speed", speed); Set("gear", gear); Set("rpm", _engine ? 900 + speed % 34 * 170 : 0); Set("rpmLimit", 8000);
            Set("throttle", _engine && phase < 10 ? .65 : 0); Set("brake", phase >= 10 ? .45 : 0); Set("clutch", gear == 0 ? 1d : 0d);
            Set("steering", Math.Sin(t * .6) * 35); Set("handbrake", 0d); Set("ignition", _ignition); Set("engineRunning", _engine);
            Set("lights", _lights || Held("flash")); Set("wiperLevel", _wiper); Set("radioActive", Held("radio"));
            Set("intercomActive", Held("intercom")); Set("starterActive", Held("starter"));
            Set("waterTemp", 84 + Math.Sin(t * .1) * 3); Set("oilTemp", 96 + Math.Sin(t * .13) * 4); Set("oilPressure", _engine ? 4.2 : 0);
            Set("turbo", _engine ? .6 : 0); Set("fuel", 45 - phase * .03); Set("consumption", 32.4); Set("range", 139); Set("engineMap", _map);
            Set("gearboxTemp", 89); Set("differential", _diff); Set("faults", "none");
            Set("tyrePressure", new[] { 27.2, 27.4, 27.1, 27.3 }); Set("tyreTempInner", new[] { 85, 86, 82, 84 });
            Set("tyreTempMiddle", new[] { 83, 84, 81, 82 }); Set("tyreTempOuter", new[] { 81, 83, 79, 80 });
            Set("tyreWear", new[] { .95, .94, .96, .95 }); Set("brakeTemp", new[] { 420, 430, 340, 350 });
            Set("wheelSpeed", new[] { speed / 3.6 / .33, speed / 3.6 / .33, speed / 3.6 / .33, speed / 3.6 / .33 });
            Set("wheelSlip", new[] { .01, .02, .01, .02 }); Set("wheelLock", false);
            Set("absActive", phase > 15 && _abs > 0); Set("absLevel", _abs); Set("tcActive", phase < 4 && _tc > 0); Set("tcLevel", _tc); Set("brakeBias", _bias);
            Set("lapCurrent", (int)(t % 90 * 1000)); Set("lapLast", 91432); Set("lapBest", 88820); Set("sectors", new[] { 28900, 30200, 29720 });
            Set("delta", (int)(Math.Sin(t * .2) * 500)); Set("position", 2); Set("lap", (int)(t / 90) + 1); Set("lapsRemaining", 8);
            Set("timeRemaining", 1200 - t % 1200); Set("inPit", Held("pitLimiter")); Set("pitLimit", 60); Set("flags", "green");
            Set("drs", Held("drs")); Set("ers", .7); Set("hybridEnergy", 420); Set("battery", .72);
            Set("gX", Math.Sin(t * .6) * .8); Set("gY", 1); Set("gZ", phase < 10 ? .45 : -.45);
            Set("yaw", Math.Sin(t * .6) * .1); Set("pitch", .01); Set("roll", Math.Sin(t * .6) * .03); Set("suspension", new[] { .04, .05, .04, .05 });
            Set("stageTime", (int)(t % 180 * 1000)); Set("stageSplits", new[] { 30120, 32040 }); Set("stageDistance", t % 180 * 22);
            Set("stageState", "synthetic_demo"); Set("vehicleId", "DEMO-SYNTHETIC"); Set("stageId", "DEMO-STAGE");
            Set("navigation", "Szimulált bemutató, nem játékadat"); Set("damage", new[] { 0, 0, 0, 0, 0 }); Set("sessionStatus", "demo"); Set("radioVolume", _radioVolume); Set("intercomVolume", _intercomVolume); Set("sessionClock", (TimeSpan.FromHours(12) + TimeSpan.FromSeconds(t)).ToString(@"hh\:mm\:ss")); Set("driveMode", "ROAD"); Set("launchRpmLimit", 5500);
            _windowFrames++;
            if (tick - _windowMs >= 1000) { _hz = _windowFrames * 1000d / (tick - _windowMs); _windowFrames = 0; _windowMs = tick; }
            Health = Health with { LastPacketMs = now, ActualHz = _hz };
            return ValueTask.FromResult<TelemetryFrame?>(new(++_sequence, now, "demo", "synthetic-demo/0.2.0", "demo", fields, "DEMO-SYNTHETIC", Mode: "demo"));
        }
    }
    public ControlAck Apply(string owner, ControlRequest request)
    {
        if (!ActionCatalog.Actions.Contains(request.Action) || request.Phase is not ("press" or "down" or "up"))
            return new("ack", request.Id, "rejected", "invalid_demo_command");
        lock (_gate)
        {
            var key = owner + ":" + request.Action;
            var alreadyDown = _holds.ContainsKey(key);
            if (request.Phase == "up") { _holds.Remove(key); return new("ack", request.Id, "simulated", Detail: "DEMO felengedés; nem Windows-bemenet."); }
            _holds[key] = (request.Action, _clock.ElapsedMilliseconds + (request.Phase == "press" ? 180 : 3000));
            if (!alreadyDown || request.Phase == "press") switch (request.Action)
            {
                case "radioVolumeUp": _radioVolume = Math.Min(10, _radioVolume + 1); break;
                case "radioVolumeDown": _radioVolume = Math.Max(0, _radioVolume - 1); break;
                case "intercomVolumeUp": _intercomVolume = Math.Min(10, _intercomVolume + 1); break;
                case "intercomVolumeDown": _intercomVolume = Math.Max(0, _intercomVolume - 1); break;
                case "ignition": _ignition = !_ignition; if (!_ignition) _engine = false; break;
                case "starter": if (_ignition) _engine = true; break;
                case "lights": _lights = !_lights; break;
                case "wiper": _wiper = (_wiper + 1) % 4; break;
                case "tcUp": _tc = Math.Min(12, _tc + 1); break; case "tcDown": _tc = Math.Max(0, _tc - 1); break;
                case "absUp": _abs = Math.Min(12, _abs + 1); break; case "absDown": _abs = Math.Max(0, _abs - 1); break;
                case "brakeBiasUp": _bias = Math.Min(75, _bias + .5); break; case "brakeBiasDown": _bias = Math.Max(35, _bias - .5); break;
                case "engineMapUp": _map = Math.Min(12, _map + 1); break; case "engineMapDown": _map = Math.Max(1, _map - 1); break;
                case "diffUp": _diff = Math.Min(12, _diff + 1); break; case "diffDown": _diff = Math.Max(0, _diff - 1); break;
                case "neutral": _requestedGear = 0; _gearUntil = _clock.ElapsedMilliseconds + 3000; break;
                case "reverse": _requestedGear = -1; _gearUntil = _clock.ElapsedMilliseconds + 3000; break;
            }
            return new("ack", request.Id, "simulated", Detail: "DEMO helyi állapot; nem játékparancs.", TimestampMs: DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());
        }
    }
    public void ReleaseOwner(string owner)
    {
        lock (_gate) foreach (var key in _holds.Keys.Where(k => k.StartsWith(owner + ":", StringComparison.Ordinal)).ToArray()) _holds.Remove(key);
    }
    public void Dispose() { lock (_gate) _holds.Clear(); }
}
