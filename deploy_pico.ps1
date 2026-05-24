# UT33C+ YD-RP2040 Deployment Script
# This script builds the firmware and deploys it to a Pico in BOOTSEL mode.

$PIO_PATH = "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe"
$PROJECT_DIR = "pico/cpp"
$UF2_FILE = "$PROJECT_DIR/.pio/build/pico/firmware.uf2"

Write-Host "`n--- [1/3] Building Firmware ---" -ForegroundColor Cyan
Set-Location -Path $PSScriptRoot
& $PIO_PATH run -d $PROJECT_DIR

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Build failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n--- [2/3] Searching for RPI-RP2 Drive ---" -ForegroundColor Cyan
$picotool = "C:\Users\StaticLabs\.platformio\packages\tool-picotool-rp2040-earlephilhower\picotool.exe"
$drive = Get-Volume | Where-Object { $_.FileSystemLabel -eq "RPI-RP2" } | Select-Object -ExpandProperty DriveLetter -ErrorAction SilentlyContinue

if (-not $drive) {
    Write-Host "Pico drive not found. Attempting to force BOOTSEL via picotool..." -ForegroundColor Yellow
    & $picotool reboot -f
    Start-Sleep -Seconds 2
    $drive = Get-Volume | Where-Object { $_.FileSystemLabel -eq "RPI-RP2" } | Select-Object -ExpandProperty DriveLetter -ErrorAction SilentlyContinue
}

if (-not $drive) {
    Write-Host "Error: Pico not found in BOOTSEL mode even after force reboot!" -ForegroundColor Red
    exit 1
}

$destination = "$($drive):\"
Write-Host "Found Pico at $destination" -ForegroundColor Green

Write-Host "`n--- [3/3] Deploying UF2 ---" -ForegroundColor Cyan
Copy-Item $UF2_FILE -Destination $destination

Write-Host "Deployment Successful! The Pico should now reboot." -ForegroundColor Green
Write-Host "Check your serial monitor for the fuzzer output.`n"
