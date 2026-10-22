function Write-SensorSnapshot {
    param([string]$Path, [object]$Data)
    $temporary = [IO.Path]::ChangeExtension($Path, '.tmp')
    $json = $Data | ConvertTo-Json
    $encoding = New-Object Text.UTF8Encoding($false)
    for ($attempt = 0; $attempt -lt 10; $attempt++) {
        try {
            [IO.File]::WriteAllText($temporary, $json, $encoding)
            if ([IO.File]::Exists($Path)) {
                # Replace atomically; Move-Item -Force can delete the old file
                # before failing when a Windows reader holds it open.
                [IO.File]::Replace($temporary, $Path, [System.Management.Automation.Language.NullString]::Value)
            } else {
                [IO.File]::Move($temporary, $Path)
            }
            return $true
        } catch [IO.IOException] {
            if ($attempt -eq 9) { return $false }
        } catch [UnauthorizedAccessException] {
            if ($attempt -eq 9) { return $false }
        }
        Start-Sleep -Milliseconds 25
    }
}
