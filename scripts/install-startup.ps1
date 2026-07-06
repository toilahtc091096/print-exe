param(
    [string]$ExePath = "$PSScriptRoot\..\dist\HoSoInWorker.exe",
    [string]$ShortcutName = "HoSoInWorker.lnk"
)

$ErrorActionPreference = "Stop"
$ResolvedExePath = (Resolve-Path $ExePath).Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$StartupDir = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupDir $ShortcutName

$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ResolvedExePath
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.WindowStyle = 7
$Shortcut.Description = "Ho so in email attachment worker"
$Shortcut.Save()

Write-Host "Installed startup shortcut: $ShortcutPath"
