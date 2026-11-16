param([switch]$Synthetic, [ValidateRange(1024,65535)][int]$Port = 8765)
. "$PSScriptRoot/Common.ps1"
Require-ProjectPython
Push-Location -LiteralPath $ProjectRoot
$oldMode = [System.Environment]::GetEnvironmentVariable('WNS_DATA_MODE')
try {
    if ($Synthetic) { $env:WNS_DATA_MODE = 'synthetic' }
    else { Remove-Item Env:WNS_DATA_MODE -ErrorAction SilentlyContinue }
    Write-Host "Open http://127.0.0.1:$Port in a browser. Press Ctrl+C here to stop."
    Invoke-Checked $VenvPython @('-m','streamlit','run','dashboard/app.py','--server.port',"$Port")
}
finally {
    [System.Environment]::SetEnvironmentVariable('WNS_DATA_MODE', $oldMode)
    Pop-Location
}
