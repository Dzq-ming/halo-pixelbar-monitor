param([switch]$NoElevation)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
if (-not (Test-Path -LiteralPath "$root\.venv\Scripts\pythonw.exe") -or
    -not (Test-Path -LiteralPath "$root\lib\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")) {
    throw 'Run Setup.ps1 before starting the monitor.'
}
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$arguments = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + "$root\scripts\Sensor-Worker.ps1" + '"'))
$launch = @{FilePath="$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe"; ArgumentList=$arguments; WindowStyle='Hidden'}
if (-not $admin -and -not $NoElevation) { $launch.Verb = 'RunAs' }
Start-Process @launch | Out-Null
