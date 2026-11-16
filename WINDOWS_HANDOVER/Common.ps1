Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$VenvPython = Join-Path $ProjectRoot '.venv\Scripts\python.exe'

function Invoke-Checked {
    param([Parameter(Mandatory)][string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Program exited with code $LASTEXITCODE."
    }
}

function Require-ProjectPython {
    if (-not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
        throw 'Run WINDOWS_HANDOVER\INSTALL_WINDOWS.ps1 first.'
    }
}
