param([string]$Workbook, [switch]$PrepareOnly)
. "$PSScriptRoot/Common.ps1"
Require-ProjectPython
$Arguments = @('scripts/reproduce_windows.py')
if ($Workbook) { $Arguments += @('--workbook', (Resolve-Path -LiteralPath $Workbook).Path) }
if ($PrepareOnly) { $Arguments += '--prepare-only' }
Push-Location -LiteralPath $ProjectRoot
try { Invoke-Checked $VenvPython $Arguments }
finally { Pop-Location }
