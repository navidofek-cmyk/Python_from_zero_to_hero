$ErrorActionPreference = "Stop"

$Projekt = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = Join-Path $Projekt ".venv"

Set-Location $Projekt

if (-not (Test-Path $Venv)) {
    Write-Host "[*] Vytvářím virtuální prostředí..."
    python -m venv $Venv
}

& "$Venv\Scripts\Activate.ps1"

$installed = python -c "import mkdocs_material" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[*] Instaluji mkdocs-material..."
    pip install --quiet mkdocs-material
}

Write-Host "[*] Spouštím kurz na http://127.0.0.1:9999"
mkdocs serve
