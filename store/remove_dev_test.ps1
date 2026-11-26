$ErrorActionPreference = 'Stop'
$Folder = Split-Path -Parent $PSCommandPath
$CertificatePath = Join-Path $Folder 'NOVAPlayer-DevTest.cer'
Get-AppxPackage -Name 'NOVA.Player.DevTest' -ErrorAction SilentlyContinue | Remove-AppxPackage
if (Test-Path -LiteralPath $CertificatePath) {
    $Thumbprint = (Get-PfxCertificate -FilePath $CertificatePath).Thumbprint
    foreach ($Store in @('Cert:\LocalMachine\TrustedPeople','Cert:\CurrentUser\TrustedPeople')) {
        Get-ChildItem -LiteralPath $Store |
            Where-Object Thumbprint -EQ $Thumbprint | Remove-Item
    }
}
Write-Host 'Removed NOVA Player developer test package and matching test certificates from the machine and current-user Trusted People stores.'
