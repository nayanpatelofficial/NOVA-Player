$ErrorActionPreference = 'Stop'
$Folder = Split-Path -Parent $PSCommandPath
$Bundle = Get-ChildItem -LiteralPath $Folder -Filter 'NOVAPlayer-v*-DevTest.msixbundle' -File |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$CertificatePath = Join-Path $Folder 'NOVAPlayer-DevTest.cer'
if (-not $Bundle) { throw 'Build the developer test bundle first. No NOVAPlayer-v*-DevTest.msixbundle was found.' }
if (-not (Test-Path -LiteralPath $CertificatePath)) { throw 'The NOVA Player developer test certificate was not found beside the bundle.' }
$Principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $Principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Run PowerShell as Administrator so Windows can trust this test certificate in Local Computer\Trusted People.'
}
Import-Certificate -FilePath $CertificatePath -CertStoreLocation 'Cert:\LocalMachine\TrustedPeople' | Out-Null
Add-AppxPackage -Path $Bundle.FullName
Write-Host "Installed local test build: $($Bundle.Name)"
