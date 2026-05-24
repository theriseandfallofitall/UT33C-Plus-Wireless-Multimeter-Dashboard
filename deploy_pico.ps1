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
$drive = Get-Volume | Where-Object { $_.FileSystemLabel -eq "RPI-RP2" } | Select-Object -ExpandProperty DriveLetter -ErrorAction SilentlyContinue

if (-not $drive) {
    Write-Host "Error: Pico not found in BOOTSEL mode!" -ForegroundColor Yellow
    Write-Host "Please hold the BOOT button while plugging in the USB cable."
    exit 1
}

$destination = "$($drive):\"
Write-Host "Found Pico at $destination" -ForegroundColor Green

Write-Host "`n--- [3/3] Deploying UF2 ---" -ForegroundColor Cyan
Copy-Item $UF2_FILE -Destination $destination

Write-Host "Deployment Successful! The Pico should now reboot." -ForegroundColor Green
Write-Host "Check your serial monitor for the fuzzer output.`n"
