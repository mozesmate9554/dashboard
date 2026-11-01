param([string]$Destination = (Join-Path $env:LOCALAPPDATA 'Programs/SimControlStudio'))
$ErrorActionPreference = 'Stop'
$TaskExecutable = Join-Path $PSScriptRoot 'SimControlStudio.Bridge.exe'
if (-not (Test-Path $TaskExecutable)) { throw 'Keep this installer next to SimControlStudio.Bridge.exe.' }
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
Copy-Item $TaskExecutable (Join-Path $Destination 'SimControlStudio.Bridge.exe') -Force
Copy-Item (Join-Path $PSScriptRoot 'profiles.json') (Join-Path $Destination 'profiles.json') -Force
$TaskShell = New-Object -ComObject WScript.Shell
$TaskMenu = [Environment]::GetFolderPath('Programs')
$TaskShortcut = $TaskShell.CreateShortcut((Join-Path $TaskMenu 'SIM CONTROL STUDIO Bridge.lnk'))
$TaskShortcut.TargetPath = Join-Path $Destination 'SimControlStudio.Bridge.exe'
$TaskShortcut.WorkingDirectory = $Destination
$TaskShortcut.Save()
Write-Output 'Installed for the current user. Start SIM CONTROL STUDIO Bridge from the Start menu.'
