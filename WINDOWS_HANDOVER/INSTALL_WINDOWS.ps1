param([switch]$CoreOnly, [switch]$Browser)
. "$PSScriptRoot/Common.ps1"

if ($CoreOnly -and $Browser) { throw '-Browser requires the full installation.' }

Push-Location -LiteralPath $ProjectRoot
try {
    if (-not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
        $probe = 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 11) else 1)'
        $python = Get-Command python -ErrorAction SilentlyContinue
        $launcher = Get-Command py -ErrorAction SilentlyContinue
        $selected = $null
        $target = @()
        if ($python) {
            & $python.Source -c $probe
            if ($LASTEXITCODE -eq 0) { $selected = $python.Source }
        }
        if (-not $selected -and $launcher) {
            & $launcher.Source -3.11 -c $probe
            if ($LASTEXITCODE -eq 0) { $selected = $launcher.Source; $target = @('-3.11') }
        }
        if (-not $selected) { throw 'Install 64-bit Python 3.11 from python.org, then rerun this script.' }
        Invoke-Checked $selected ($target + @('-m', 'venv', '.venv'))
    }
    Invoke-Checked $VenvPython @('-c', 'import sys; assert sys.version_info[:2] == (3, 11), sys.version')
    Invoke-Checked $VenvPython @('--version')
    $manifest = if ($CoreOnly) { 'requirements-ci.txt' } else { 'requirements.txt' }
    Invoke-Checked $VenvPython @('-m', 'pip', 'install', '-r', $manifest)
    if ($Browser) { Invoke-Checked $VenvPython @('-m', 'playwright', 'install', 'chromium', '--only-shell') }
    Write-Host "Environment ready at $VenvPython"
}
finally { Pop-Location }
