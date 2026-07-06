param(
    [string]$ShortcutName = "HoSoInWorker.lnk"
)

$ErrorActionPreference = "Stop"
$StartupDir = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupDir $ShortcutName

if (Test-Path $ShortcutPath) {
    Remove-Item -LiteralPath $ShortcutPath
    Write-Host "Removed startup shortcut: $ShortcutPath"
} else {
    Write-Host "Startup shortcut not found: $ShortcutPath"
}
