param([switch]$Browser, [switch]$Authorized)
. "$PSScriptRoot/Common.ps1"
Require-ProjectPython
Push-Location -LiteralPath $ProjectRoot
try {
    Write-Host "PowerShell $($PSVersionTable.PSVersion) on $([System.Environment]::OSVersion.VersionString)"
    Invoke-Checked $VenvPython @('--version')
    Invoke-Checked $VenvPython @('-m','unittest','discover','-s','tests','-v')
    Invoke-Checked $VenvPython @('-m','compileall','-q','src','scripts','dashboard','tests')
    Invoke-Checked $VenvPython @('scripts/check_submission.py')
    if ($Authorized) {
        Invoke-Checked $VenvPython @('scripts/validate_project_data.py')
        Invoke-Checked $VenvPython @('scripts/verify_eda_findings.py')
    }
    if ($Browser) {
        $Arguments = @('scripts/test_browser_local.py')
        if ($Authorized) { $Arguments += '--authorized' }
        Invoke-Checked $VenvPython $Arguments
    }
}
finally { Pop-Location }
