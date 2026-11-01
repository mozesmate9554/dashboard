param([string]$OutputDirectory = "")
$ErrorActionPreference = 'Stop'
$TaskRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) { $OutputDirectory = Join-Path $TaskRoot 'releases/Android' }
$TaskPreviousKey = $env:SIMCONTROL_KEYSTORE
$TaskPreviousPassword = $env:SIMCONTROL_KEYSTORE_PASSWORD
Push-Location (Join-Path $TaskRoot 'mobile_flutter')
try {
    if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) { throw 'Flutter SDK required: flutter 3.35+ with Dart 3.9+.' }
    if ([string]::IsNullOrWhiteSpace($env:SIMCONTROL_KEYSTORE)) { $env:SIMCONTROL_KEYSTORE = Join-Path $TaskRoot 'releases/keys/simcontrol-release.jks' }
    if ([string]::IsNullOrWhiteSpace($env:SIMCONTROL_KEYSTORE_PASSWORD)) {
        $TaskSecurePassword = Read-Host 'Sajat kiadasi keystore jelszava (orizd meg!)' -AsSecureString
        $TaskPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($TaskSecurePassword)
        try { $env:SIMCONTROL_KEYSTORE_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($TaskPointer) }
        finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($TaskPointer) }
    }
    if ($env:SIMCONTROL_KEYSTORE_PASSWORD.Length -lt 8) { throw 'Use at least an 8-character keystore password.' }
    if (-not (Test-Path $env:SIMCONTROL_KEYSTORE)) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $env:SIMCONTROL_KEYSTORE) | Out-Null
        & keytool -genkeypair -v -keystore $env:SIMCONTROL_KEYSTORE -storepass:env SIMCONTROL_KEYSTORE_PASSWORD -keypass:env SIMCONTROL_KEYSTORE_PASSWORD -alias simcontrol -keyalg RSA -keysize 3072 -validity 10000 -dname 'CN=SIM CONTROL STUDIO Personal Release'
        if ($LASTEXITCODE -ne 0) { throw 'Keystore creation failed.' }
    }
    foreach ($TaskArguments in @(@('pub','get'),@('analyze','--no-fatal-infos'),@('test'),@('build','apk','--release'))) {
        & flutter @TaskArguments
        if ($LASTEXITCODE -ne 0) { throw ('Flutter command failed: ' + ($TaskArguments -join ' ')) }
    }
    $TaskApk = Join-Path $TaskRoot 'mobile_flutter/build/app/outputs/flutter-apk/app-release.apk'
    if (-not (Test-Path $TaskApk)) { throw 'No release APK produced.' }
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $TaskDestination = Join-Path $OutputDirectory 'SIM_CONTROL_STUDIO_0.1.0.apk'
    Copy-Item $TaskApk $TaskDestination -Force
    Get-FileHash $TaskDestination -Algorithm SHA256 | Format-List
} finally {
    $env:SIMCONTROL_KEYSTORE = $TaskPreviousKey
    $env:SIMCONTROL_KEYSTORE_PASSWORD = $TaskPreviousPassword
    Pop-Location
}
