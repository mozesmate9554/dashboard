using System.Net;

namespace SimControlStudio;

public sealed class BridgeConfiguration
{
    public string BindAddress { get; set; } = "127.0.0.1";
    public int Port { get; set; } = 19760;
    public int DiscoveryPort { get; set; } = 19761;
    public bool DiscoveryEnabled { get; set; }
    public string GameId { get; set; } = "acr";
    public int Hz { get; set; } = 60;
    public bool MobileControlEnabled { get; set; }
    public string[] RallyProcessNames { get; set; } = ["acr", "acr-Win64-Shipping"];
    public Dictionary<string, Dictionary<string, KeyBinding>> Bindings { get; set; } = new()
    {
        ["acr"] = [], ["ac"] = [], ["acc"] = [], ["beamng"] = []
    };
    public Dictionary<string, Dictionary<string, KeyBinding>> ProfileBindings { get; set; } = [];
    public IReadOnlyDictionary<string, KeyBinding> ResolveBindings(string? profileId) =>
        profileId != null && ProfileBindings.TryGetValue(GameId + "/" + profileId, out var profile)
            ? profile : Bindings.GetValueOrDefault(GameId) ?? new Dictionary<string, KeyBinding>();
    public int UdpPort { get; set; } = 4444;
    public void Validate()
    {
        if (!IPAddress.TryParse(BindAddress, out var address) || address.AddressFamily != System.Net.Sockets.AddressFamily.InterNetwork)
            throw new ArgumentException("Érvénytelen IPv4 kötési cím.");
        if (Port is < 1024 or > 65535 || DiscoveryPort is < 1024 or > 65535 || UdpPort is < 1024 or > 65535)
            throw new ArgumentException("A port 1024 és 65535 között legyen.");
        if (Hz is not (20 or 30 or 60)) throw new ArgumentException("A frissítés 20, 30 vagy 60 Hz lehet.");
        if (!new[] { "acr", "ac", "acc", "beamng", "demo" }.Contains(GameId)) throw new ArgumentException("Nem implementált játékadapter.");
        if (RallyProcessNames == null || RallyProcessNames.Length is < 1 or > 6 || RallyProcessNames.Any(name =>
            string.IsNullOrWhiteSpace(name) || name.Length > 100 || name.Any(c => !(char.IsAsciiLetterOrDigit(c) || c is '-' or '_' or '.'))))
            throw new ArgumentException("Érvénytelen Rally-folyamatnév.");
        if (Bindings == null || ProfileBindings == null) throw new ArgumentException("Üres kiosztásnyilvántartás.");
        foreach (var key in ProfileBindings.Keys)
        {
            var parts = key.Split('/');
            if (parts.Length != 2 || !new[] { "acr", "ac", "acc", "beamng", "demo" }.Contains(parts[0]) ||
                parts[1].Length is < 1 or > 100 || parts[1].Any(char.IsControl)) throw new ArgumentException("Hibás profilkiosztás-azonosító.");
        }
        foreach (var game in Bindings.Values.Concat(ProfileBindings.Values))
        {
            if (game == null) throw new ArgumentException("Üres játék-/profilkiosztás.");
            foreach (var (action, binding) in game)
            {
                if (!ActionCatalog.Actions.Contains(action)) throw new ArgumentException($"Ismeretlen művelet: {action}");
                if (binding == null) throw new ArgumentException("Üres billentyű-hozzárendelés.");
                binding.Validate();
            }
        }
    }
    public static BridgeConfiguration Load(string path)
    {
        if (!File.Exists(path)) return new();
        var config = Protocol.Deserialize<BridgeConfiguration>(File.ReadAllText(path)) ?? throw new InvalidDataException("Üres konfiguráció.");
        config.MobileControlEnabled = false; // Every Bridge start requires deliberate local arming.
        config.Validate();
        return config;
    }
    public void Save(string path) { Validate(); AtomicFile.Write(path, Protocol.Serialize(this)); }
}

public static class AtomicFile
{
    public static void Write(string path, string text)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
        var temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try { File.WriteAllText(temporary, text); File.Move(temporary, path, true); }
        finally { if (File.Exists(temporary)) File.Delete(temporary); }
    }
}

public sealed class BindingBundle
{
    public int SchemaVersion { get; set; } = 2;
    public Dictionary<string, Dictionary<string, KeyBinding>> Bindings { get; set; } = [];
    public Dictionary<string, Dictionary<string, KeyBinding>> ProfileBindings { get; set; } = [];
    public static BindingBundle Parse(string json)
    {
        using var doc = System.Text.Json.JsonDocument.Parse(json);
        var wrapped = doc.RootElement.TryGetProperty("schemaVersion", out var version);
        if (wrapped && version.GetInt32() != 2) throw new ArgumentException("Nem támogatott kiosztásséma.");
        var result = wrapped ? Protocol.Deserialize<BindingBundle>(json)! : new BindingBundle
        { Bindings = Protocol.Deserialize<Dictionary<string, Dictionary<string, KeyBinding>>>(json)! };
        new BridgeConfiguration { Bindings = result.Bindings, ProfileBindings = result.ProfileBindings }.Validate();
        return result;
    }
}

public sealed record KeyBinding(string Keys, string Mode = "press", int DurationMs = 80, int RepeatMs = 150)
{
    public void Validate()
    {
        _ = KeyNames.Parse(Keys);
        if (Mode is not ("press" or "hold" or "repeat")) throw new ArgumentException("Hibás gombmód.");
        if (DurationMs is < 20 or > 3000 || RepeatMs is < 50 or > 2000) throw new ArgumentException("Hibás időzítés.");
    }
}

public static class ActionCatalog
{
    public static readonly HashSet<string> Actions = new(StringComparer.Ordinal)
    {
        "ignition", "starter", "lights", "flash", "wiper", "radio", "intercom", "camera",
        "pitLimiter", "brakeBiasUp", "brakeBiasDown", "absUp", "absDown", "tcUp", "tcDown",
        "diffUp", "diffDown", "engineMapUp", "engineMapDown", "drs", "ers", "p2p", "neutral",
        "reverse", "displayNext", "displayPrevious", "acknowledge", "drink", "fan", "rainLight"
    };
}
