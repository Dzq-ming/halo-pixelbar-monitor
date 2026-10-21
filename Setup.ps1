param([string]$PythonExecutable = '')
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

if ($PythonExecutable) {
    $pythonCommand = $PythonExecutable
    $pythonArguments = @()
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCommand = 'py'
    $pythonArguments = @('-3')
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCommand = 'python'
    $pythonArguments = @()
} else { throw 'Install Python 3.11 or newer from python.org, then run Setup.ps1 again.' }

& $pythonCommand @pythonArguments -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 or newer is required.' }
& $pythonCommand @pythonArguments -m venv "$root\.venv"
if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python virtual environment.' }
& "$root\.venv\Scripts\python.exe" -m pip install -r "$root\requirements.txt"
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }

$manifest = Get-Content -LiteralPath "$root\scripts\dependencies.json" -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Path "$root\lib\downloads" -Force | Out-Null
function Get-VerifiedDownload($entry, $destination) {
    if (-not (Test-Path -LiteralPath $destination) -or
        (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) {
        Invoke-WebRequest -UseBasicParsing -Uri $entry.url -OutFile $destination
    }
    if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) {
        throw 'Downloaded file failed SHA-256 verification. It will not be executed.'
    }
}
$archive = "$root\lib\downloads\LibreHardwareMonitor.zip"
Get-VerifiedDownload $manifest.libre_hardware_monitor $archive
Expand-Archive -LiteralPath $archive -DestinationPath "$root\lib\LibreHardwareMonitor" -Force
Get-VerifiedDownload $manifest.pawnio "$root\lib\PawnIO_setup.exe"
$signature = Get-AuthenticodeSignature -LiteralPath "$root\lib\PawnIO_setup.exe"
if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notlike "*$($manifest.pawnio.signer_subject)*") {
    throw 'PawnIO digital signature verification failed.'
}
if (-not (Test-Path -LiteralPath "$root\config.json")) {
    Copy-Item -LiteralPath "$root\config.example.json" -Destination "$root\config.json"
}
Write-Host 'Setup complete. Run Start-Monitor.cmd. First start may install the signed PawnIO driver.'
