$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\..\scripts\Write-SensorSnapshot.ps1"
$directory = Join-Path ([IO.Path]::GetTempPath()) ([Guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($directory) | Out-Null
$path = Join-Path $directory 'sensors.json'
$locked = $null
try {
    if (-not (Write-SensorSnapshot $path @{sample=1})) { throw 'Initial write failed' }
    $locked = [IO.File]::Open($path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    if (Write-SensorSnapshot $path @{sample=2}) { throw 'Locked destination unexpectedly replaced' }
    if (-not [IO.File]::Exists($path)) { throw 'Contention removed the last good snapshot' }
    if ((Get-Content -LiteralPath $path -Raw | ConvertFrom-Json).sample -ne 1) { throw 'Contention changed the last good sample' }
    $locked.Dispose()
    $locked = $null
    if (-not (Write-SensorSnapshot $path @{sample=3})) { throw 'Write did not recover after unlocking' }
    if ((Get-Content -LiteralPath $path -Raw | ConvertFrom-Json).sample -ne 3) { throw 'Recovered sample incorrect' }
    Write-Output 'Sensor snapshot lock, preservation and recovery checks passed.'
} finally {
    if ($locked) { $locked.Dispose() }
    # Delete only the two known files created by this test.
    [IO.File]::Delete($path)
    [IO.File]::Delete([IO.Path]::ChangeExtension($path, '.tmp'))
    [IO.Directory]::Delete($directory)
}
