param([string]$OutputDirectory = "")
$ErrorActionPreference = 'Stop'
$TaskRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) { $OutputDirectory = Join-Path $TaskRoot 'releases/Windows' }
Push-Location $TaskRoot
try {
    & dotnet run --project tests/Bridge.Tests/Bridge.Tests.csproj -c Release -- (Join-Path $TaskRoot 'tests/results/bridge-tests.json')
    if ($LASTEXITCODE -ne 0) { throw 'Bridge tests failed.' }
    & dotnet publish windows_bridge/Bridge.Windows/Bridge.Windows.csproj -c Release -r win-x64 --self-contained true '-p:PublishSingleFile=true' '-p:EnableCompressionInSingleFile=true' '-p:IncludeNativeLibrariesForSelfExtract=true' '-p:DebugType=None' -o $OutputDirectory
    if ($LASTEXITCODE -ne 0) { throw 'Windows publish failed.' }
    Get-FileHash (Join-Path $OutputDirectory 'SimControlStudio.Bridge.exe') -Algorithm SHA256 | Format-List
} finally { Pop-Location }
