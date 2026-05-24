# UT33C+ Pico deployment script.
# Builds the active PlatformIO firmware and copies the UF2 to a Pico in BOOTSEL mode.

$ProjectDir = Join-Path $PSScriptRoot "pico\cpp"
$Uf2File = Join-Path $ProjectDir ".pio\build\pico\firmware.uf2"
$DefaultPio = Join-Path $env:USERPROFILE ".platformio\penv\Scripts\pio.exe"
$PioPath = if (Test-Path $DefaultPio) { $DefaultPio } else { (Get-Command pio -ErrorAction Stop).Source }

Write-Host "`n--- [1/3] Building Firmware ---" -ForegroundColor Cyan
Set-Location -Path $PSScriptRoot
& $PioPath run -d $ProjectDir

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Build failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n--- [2/3] Searching for RPI-RP2 Drive ---" -ForegroundColor Cyan
$PioPackages = Join-Path $env:USERPROFILE ".platformio\packages"
$Picotool = Get-ChildItem -Path $PioPackages -Recurse -Filter picotool.exe -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName
$Drive = Get-Volume | Where-Object { $_.FileSystemLabel -eq "RPI-RP2" } | Select-Object -ExpandProperty DriveLetter -ErrorAction SilentlyContinue

if (-not $Drive -and $Picotool) {
    Write-Host "Pico drive not found. Attempting to force BOOTSEL via picotool..." -ForegroundColor Yellow
    & $Picotool reboot -f
    Start-Sleep -Seconds 2
    $Drive = Get-Volume | Where-Object { $_.FileSystemLabel -eq "RPI-RP2" } | Select-Object -ExpandProperty DriveLetter -ErrorAction SilentlyContinue
}

if (-not $Drive) {
    Write-Host "Error: Pico not found in BOOTSEL mode." -ForegroundColor Red
    exit 1
}

$Destination = "$($Drive):\"
Write-Host "Found Pico at $destination" -ForegroundColor Green

Write-Host "`n--- [3/3] Deploying UF2 ---" -ForegroundColor Cyan
Copy-Item $Uf2File -Destination $Destination

Write-Host "Deployment Successful! The Pico should now reboot." -ForegroundColor Green
Write-Host "Check your serial monitor for firmware output.`n"
