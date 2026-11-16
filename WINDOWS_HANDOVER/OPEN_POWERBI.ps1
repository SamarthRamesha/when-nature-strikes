param([switch]$Authorized, [switch]$NoOpen)
. "$PSScriptRoot/Common.ps1"
$project = Join-Path $ProjectRoot 'submission\powerbi\demo\When_Nature_Strikes.pbip'
if ($Authorized) {
    Require-ProjectPython
    $output = Join-Path $ProjectRoot ('submission\powerbi\local\authorized-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
    $project = Join-Path $output 'When_Nature_Strikes.pbip'
    Push-Location -LiteralPath $ProjectRoot
    try { Invoke-Checked $VenvPython @('scripts/build_powerbi.py','--output',$output,'--processed-data','data/processed') }
    finally { Pop-Location }
}
if (-not (Test-Path -LiteralPath $project -PathType Leaf)) { throw "Project not found: $project" }
Write-Host $project
if (-not $NoOpen) {
    try { Start-Process -FilePath $project -ErrorAction Stop }
    catch { throw "Open the printed PBIP path from File > Open in Power BI Desktop. $($_.Exception.Message)" }
}
