using System.Text.Json;
using System.Text.Json.Serialization;

namespace SimControlStudio;

public static class Protocol
{
    public const int Version = 1;
    public const string AppVersion = "0.2.0";
    public const int MaxMessageBytes = 16 * 1024;
    public static readonly JsonSerializerOptions Json = new(JsonSerializerDefaults.Web)
    {
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        Converters = { new JsonStringEnumConverter(JsonNamingPolicy.CamelCase) }
    };
    public static string Serialize(object value) => JsonSerializer.Serialize(value, Json);
    public static T? Deserialize<T>(string text) => JsonSerializer.Deserialize<T>(text, Json);
}

public enum Validity { Valid, Stale, Unsupported, Invalid }
public sealed record Datum(object? Value, string Unit, string Source, long TimestampMs,
    Validity Validity = Validity.Valid, bool Derived = false);
public sealed record TelemetryFrame(long Sequence, long TimestampMs, string GameId, string Adapter,
    string State, IReadOnlyDictionary<string, Datum> Fields, string? VehicleId = null,
    string? GameVersion = null, string Mode = "live")
{
    public TelemetryFrame Stale(long now) => this with
    {
        State = "stale",
        Fields = Fields.ToDictionary(p => p.Key, p => p.Value with
        {
            Validity = p.Value.Validity == Validity.Valid ? Validity.Stale : p.Value.Validity
        })
    };
}
public sealed record Hello(int Protocol, string DeviceId, string Name, string Role, string? ProfileId,
    int Hz = 30, string? PairingToken = null, string? Secret = null, string? LayoutId = null);
public sealed record ControlRequest(string Id, long Sequence, string Action, string Phase);
public sealed record ControlAck(string Type, string Id, string Stage, string? Reason = null,
    string? Detail = null, long? TimestampMs = null);
public sealed record AdapterHealth(string GameId, string Adapter, bool GameDetected, bool MemoryAvailable,
    string State, string? Error, long? LastPacketMs, double ActualHz, string? GameVersion = null,
    IReadOnlyDictionary<string, bool>? MemoryBlocks = null);

public static class TelemetryCatalog
{
    public static readonly IReadOnlyDictionary<string, string> Fields = new Dictionary<string, string>
    {
        ["speed"]="km/h", ["rpm"]="rpm", ["rpmLimit"]="rpm", ["gear"]="gear",
        ["throttle"]="ratio", ["brake"]="ratio", ["clutch"]="ratio", ["steering"]="raw",
        ["handbrake"]="ratio", ["ignition"]="bool", ["engineRunning"]="bool",
        ["waterTemp"]="°C", ["oilTemp"]="°C", ["oilPressure"]="bar", ["turbo"]="bar",
        ["fuel"]="L", ["consumption"]="L/100km", ["range"]="km", ["engineMap"]="level",
        ["gearboxTemp"]="°C", ["differential"]="level", ["faults"]="flags",
        ["tyrePressure"]="psi", ["tyreTempInner"]="°C", ["tyreTempMiddle"]="°C",
        ["tyreTempOuter"]="°C", ["tyreWear"]="ratio", ["brakeTemp"]="°C",
        ["wheelSpeed"]="rad/s", ["wheelSlip"]="raw", ["wheelLock"]="bool",
        ["absActive"]="bool", ["absLevel"]="level", ["tcActive"]="bool", ["tcLevel"]="level",
        ["brakeBias"]="%", ["lapCurrent"]="ms", ["lapLast"]="ms", ["lapBest"]="ms",
        ["sectors"]="ms", ["delta"]="ms", ["position"]="position", ["lap"]="count",
        ["lapsRemaining"]="count", ["timeRemaining"]="s", ["inPit"]="bool",
        ["pitLimit"]="km/h", ["flags"]="flags", ["drs"]="bool", ["ers"]="ratio",
        ["hybridEnergy"]="kJ", ["battery"]="ratio", ["gX"]="g", ["gY"]="g", ["gZ"]="g",
        ["yaw"]="rad", ["pitch"]="rad", ["roll"]="rad", ["suspension"]="m",
        ["stageTime"]="ms", ["stageSplits"]="ms", ["stageDistance"]="m",
        ["stageState"]="state", ["vehicleId"]="text", ["stageId"]="text", ["navigation"]="text",
        ["damage"]="raw", ["sessionStatus"]="state", ["lights"]="bool", ["wiperLevel"]="level",
        ["radioActive"]="bool", ["intercomActive"]="bool", ["starterActive"]="bool"
    };
    public static Dictionary<string, Datum> Empty(string source, long timestamp) => Fields.ToDictionary(
        p => p.Key, p => new Datum(null, p.Value, source, timestamp, Validity.Unsupported));
}
