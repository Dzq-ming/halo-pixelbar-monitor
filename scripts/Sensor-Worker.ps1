$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
. "$PSScriptRoot\Write-SensorSnapshot.ps1"
$runtime = Join-Path $root 'runtime'
New-Item -ItemType Directory -Path $runtime -Force | Out-Null
$mutex = New-Object Threading.Mutex($false, 'Local\HaloPixelBarPerformanceMonitor')
if (-not $mutex.WaitOne(0)) { $mutex.Dispose(); exit }
$computer = $null
$display = $null
try {
    Remove-Item -LiteralPath "$runtime\stop.flag" -ErrorAction SilentlyContinue
    $admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if ($admin -and -not (Get-Service PawnIO -ErrorAction SilentlyContinue)) {
        $manifest = Get-Content -LiteralPath "$root\scripts\dependencies.json" -Raw | ConvertFrom-Json
        $setup = "$root\lib\PawnIO_setup.exe"
        $signature = Get-AuthenticodeSignature -LiteralPath $setup
        if ((Get-FileHash -LiteralPath $setup -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.pawnio.sha256 -or
            $signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notlike "*$($manifest.pawnio.signer_subject)*") {
            throw 'PawnIO verification failed'
        }
        $installer = Start-Process -FilePath $setup -ArgumentList '-install','-silent' -WindowStyle Hidden -Wait -PassThru
        if ($installer.ExitCode -ne 0) { throw 'PawnIO installation failed' }
    }
    $gpuIndex = 0
    if (Test-Path -LiteralPath "$root\config.json") {
        $settings = Get-Content -LiteralPath "$root\config.json" -Raw | ConvertFrom-Json
        if ($settings.gpu_index -is [int] -and $settings.gpu_index -ge 0) { $gpuIndex = $settings.gpu_index }
    }
    Set-Location "$root\lib\LibreHardwareMonitor"
    Add-Type -Path '.\LibreHardwareMonitorLib.dll'
    $computer = New-Object LibreHardwareMonitor.Hardware.Computer
    $computer.IsCpuEnabled = $true
    $computer.IsGpuEnabled = $true
    $computer.IsMemoryEnabled = $true
    $computer.Open()
    $display = Start-Process -FilePath "$root\.venv\Scripts\pythonw.exe" -WorkingDirectory $root -ArgumentList '-m','halo_pixelbar_monitor' -WindowStyle Hidden -PassThru
    @{sensor_pid=$PID; display_pid=$display.Id; elevated=$admin} | ConvertTo-Json | Set-Content -LiteralPath "$runtime\running.json" -Encoding UTF8
    function Read-Sensor($hardware, $kind, $names) {
        foreach ($name in $names) {
            $sensor = $hardware.Sensors | Where-Object { $_.SensorType.ToString() -eq $kind -and $_.Name -eq $name -and $null -ne $_.Value } | Select-Object -First 1
            if ($null -ne $sensor) { return [double]$sensor.Value }
        }
        return $null
    }
    $snapshotBlocked = $false
    while (-not (Test-Path -LiteralPath "$runtime\stop.flag")) {
        $data = @{timestamp=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000.0; cpu_temp=$null; cpu_load=$null; gpu_temp=$null; gpu_load=$null; memory_load=$null}
        foreach ($hardware in $computer.Hardware) { $hardware.Update() }
        $cpu = $computer.Hardware | Where-Object { $_.HardwareType.ToString() -eq 'Cpu' } | Select-Object -First 1
        if ($cpu) {
            $data.cpu_temp = Read-Sensor $cpu 'Temperature' @('CPU Package','Core (Tctl/Tdie)','Core (Tdie)','Core Average','Core Max')
            $data.cpu_load = Read-Sensor $cpu 'Load' @('CPU Total')
        }
        $gpus = @($computer.Hardware | Where-Object { $_.HardwareType.ToString().StartsWith('Gpu') })
        if ($gpuIndex -lt $gpus.Count) {
            $data.gpu_temp = Read-Sensor $gpus[$gpuIndex] 'Temperature' @('GPU Core')
            $data.gpu_load = Read-Sensor $gpus[$gpuIndex] 'Load' @('GPU Core','D3D 3D')
        }
        $memory = $computer.Hardware | Where-Object { $_.HardwareType.ToString() -eq 'Memory' } | Select-Object -First 1
        if ($memory) { $data.memory_load = Read-Sensor $memory 'Load' @('Memory') }
        # Only numeric readings are saved. Hardware names, USB paths, serials,
        # network adapters and account information are intentionally excluded.
        $written = Write-SensorSnapshot -Path "$runtime\sensors.json" -Data $data
        if (-not $written -and -not $snapshotBlocked) {
            ('{0:o} Sensor snapshot temporarily unavailable; retrying next sample.' -f (Get-Date)) | Add-Content -LiteralPath "$runtime\sensor-error.log" -Encoding UTF8 -ErrorAction SilentlyContinue
        }
        $snapshotBlocked = -not $written
        if ($display.HasExited) { throw 'Display worker exited' }
        Start-Sleep -Seconds 1
    }
} catch {
    # Do not serialize exception messages or full stack traces containing paths.
    ('{0:o} Sensor worker stopped ({1}). Check setup, driver and permissions.' -f (Get-Date), $_.Exception.GetType().Name) | Add-Content -LiteralPath "$runtime\sensor-error.log" -Encoding UTF8
} finally {
    New-Item -ItemType File -Path "$runtime\stop.flag" -Force | Out-Null
    if ($display -and -not $display.HasExited) { $display.WaitForExit(5000) | Out-Null }
    if ($computer) { $computer.Close() }
    $mutex.ReleaseMutex()
    $mutex.Dispose()
    Remove-Item -LiteralPath "$runtime\running.json" -ErrorAction SilentlyContinue
}
