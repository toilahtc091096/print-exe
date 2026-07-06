param(
    [string]$Name = "HoSoInWorker",
    [string]$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

if (Test-Path $PythonExe) {
    $PythonCommand = @($PythonExe)
} else {
    $PythonCommand = @("python")
}

function Invoke-ProjectPython {
    param([string[]]$Arguments)

    & $PythonCommand[0] @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE"
    }
}

Invoke-ProjectPython @("-m", "pip", "install", "-r", "requirements.txt")
$BuildArgs = @(
    "-m",
    "PyInstaller",
    "--name",
    $Name,
    "--onefile",
    "--noconsole",
    "--clean",
    "--paths",
    "$ProjectRoot\src",
    "$ProjectRoot\src\main.py"
)
Invoke-ProjectPython $BuildArgs

Write-Host "Built: $ProjectRoot\dist\$Name.exe"
