using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;

namespace SimControlStudio;

public sealed record PairedDevice(string Id, string Name, string SecretHash, string Role,
    string? ProfileId, bool CanControl, long PairedAtMs);
public sealed record Authentication(PairedDevice Device, string? NewSecret);

public sealed class DeviceRegistry
{
    private readonly object _gate = new();
    private readonly string _path;
    private Dictionary<string, PairedDevice> _devices = [];
    private string? _pairingToken;
    private long _pairingExpires;
    public event Action<string>? Revoked;
    public DeviceRegistry(string path)
    {
        _path = path;
        if (File.Exists(path))
        {
            _devices = Protocol.Deserialize<List<PairedDevice>>(File.ReadAllText(path))?.ToDictionary(d => d.Id)
                ?? throw new InvalidDataException("Sérült párosítási nyilvántartás.");
        }
    }
    public string OpenPairingWindow()
    {
        lock (_gate)
        {
            _pairingToken = Convert.ToHexString(RandomNumberGenerator.GetBytes(24)).ToLowerInvariant();
            _pairingExpires = Environment.TickCount64 + 120000;
            return _pairingToken;
        }
    }
    public void ClosePairingWindow() { lock (_gate) { _pairingToken = null; _pairingExpires = 0; } }
    public long PairingSecondsRemaining { get { lock (_gate) return Math.Max(0, (_pairingExpires - Environment.TickCount64) / 1000); } }
    public IReadOnlyList<PairedDevice> Devices { get { lock (_gate) return _devices.Values.ToArray(); } }
    public bool Contains(string id) { lock (_gate) return _devices.ContainsKey(id); }
    public PairedDevice? Get(string id) { lock (_gate) return _devices.GetValueOrDefault(id); }
    private static string Hash(string secret) => Convert.ToHexString(SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(secret)));
    private static bool Equal(string a, string b) => CryptographicOperations.FixedTimeEquals(
        System.Text.Encoding.UTF8.GetBytes(a), System.Text.Encoding.UTF8.GetBytes(b));
    public Authentication? Authenticate(Hello hello)
    {
        if (hello.Protocol != Protocol.Version || !Guid.TryParse(hello.DeviceId, out _) ||
            hello.Name == null || hello.Name.Length is < 1 or > 60 || hello.Name.Any(char.IsControl) ||
            hello.Role is not ("dashboard" or "panel" or "hybrid") || hello.Hz is not (20 or 30 or 60)) return null;
        lock (_gate)
        {
            if (_devices.TryGetValue(hello.DeviceId, out var existing))
            {
                if (hello.Secret == null || hello.Secret.Length > 128 || !Equal(existing.SecretHash, Hash(hello.Secret))) return null;
                var updated = existing with { Name = hello.Name, Role = hello.Role, ProfileId = hello.ProfileId };
                _devices[existing.Id] = updated; Save();
                return new(updated, null);
            }
            if (_devices.Count >= 16 || _pairingToken == null || Environment.TickCount64 > _pairingExpires ||
                hello.PairingToken == null || hello.PairingToken.Length > 128 || !Equal(_pairingToken, hello.PairingToken)) return null;
            var secret = Convert.ToHexString(RandomNumberGenerator.GetBytes(32)).ToLowerInvariant();
            var device = new PairedDevice(hello.DeviceId, hello.Name, Hash(secret), hello.Role, hello.ProfileId,
                false, DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());
            _devices[device.Id] = device; Save();
            return new(device, secret);
        }
    }
    public void SetPermission(string id, bool control)
    {
        lock (_gate) if (_devices.TryGetValue(id, out var device)) { _devices[id] = device with { CanControl = control }; Save(); }
        if (!control) Revoked?.Invoke(id);
    }
    public void RememberProfile(string id, string? profile)
    {
        lock (_gate) if (_devices.TryGetValue(id, out var device)) { _devices[id] = device with { ProfileId = profile }; Save(); }
    }
    public void Revoke(string id)
    {
        lock (_gate) { _devices.Remove(id); Save(); }
        Revoked?.Invoke(id);
    }
    private void Save() => AtomicFile.Write(_path, Protocol.Serialize(_devices.Values));
}

public static class BridgeCertificate
{
    public static X509Certificate2 LoadOrCreate(string directory)
    {
        Directory.CreateDirectory(directory);
        var path = Path.Combine(directory, "bridge.pfx");
        if (File.Exists(path)) return X509CertificateLoader.LoadPkcs12FromFile(path, null, X509KeyStorageFlags.Exportable);
        using var key = RSA.Create(3072);
        var request = new CertificateRequest("CN=SIM CONTROL STUDIO Local Bridge", key, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        request.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, false));
        request.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature | X509KeyUsageFlags.KeyEncipherment, false));
        var san = new SubjectAlternativeNameBuilder(); san.AddDnsName("simcontrol.local"); san.AddDnsName("localhost"); san.AddIpAddress(System.Net.IPAddress.Loopback);
        request.CertificateExtensions.Add(san.Build());
        using var certificate = request.CreateSelfSigned(DateTimeOffset.UtcNow.AddDays(-1), DateTimeOffset.UtcNow.AddYears(5));
        var bytes = certificate.Export(X509ContentType.Pfx);
        var temporary = path + ".tmp";
        File.WriteAllBytes(temporary, bytes);
        File.Move(temporary, path, true);
        return X509CertificateLoader.LoadPkcs12(bytes, null, X509KeyStorageFlags.Exportable);
    }
    public static string Fingerprint(X509Certificate2 certificate) => Convert.ToHexString(SHA256.HashData(certificate.RawData)).ToLowerInvariant();
    public static string PairingUri(string host, int port, string fingerprint, string token) =>
        $"simcontrol://pair?host={Uri.EscapeDataString(host)}&port={port}&pin={fingerprint}&token={token}&v=1";
}
