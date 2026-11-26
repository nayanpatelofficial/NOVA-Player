[CmdletBinding()]
param([switch]$SkipExecutableBuild)
$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $PSScriptRoot
Set-Location $Project
$Python = $env:NOVA_BUILD_PYTHON
if ([string]::IsNullOrWhiteSpace($Python)) { $Python = Join-Path $Project '.venv\Scripts\python.exe' }
if (-not (Test-Path $Python)) { throw 'Set NOVA_BUILD_PYTHON or create .venv with this release requirements.' }
$SdkTools = $env:NOVA_WINDOWS_SDK_TOOLS
if ([string]::IsNullOrWhiteSpace($SdkTools)) { $SdkTools = 'C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64' }
$MakeAppx = Join-Path $SdkTools 'makeappx.exe'
$SignTool = Join-Path $SdkTools 'signtool.exe'
if (-not (Test-Path $MakeAppx) -or -not (Test-Path $SignTool)) { throw 'Set NOVA_WINDOWS_SDK_TOOLS to the folder containing MakeAppx.exe and SignTool.exe.' }
if (-not $SkipExecutableBuild) {
    & (Join-Path $Project 'scripts\build_windows.ps1')
    if ($LASTEXITCODE -ne 0) { throw 'NOVA Player executable build failed.' }
}
& (Join-Path $PSScriptRoot 'prepare_store_assets.ps1')
$VersionLine = Select-String -Path (Join-Path $Project 'nova\__init__.py') -Pattern '__version__\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"'
if (-not $VersionLine) { throw 'Cannot read NOVA version.' }
$Version = "$($VersionLine.Matches[0].Groups[1].Value).0"
$Output = Join-Path $Project 'dist\dev-test'
if (Test-Path $Output) { Remove-Item -LiteralPath $Output -Recurse -Force }
$PackageRoot = Join-Path $Output 'NOVAPlayer'
$BundleStage = Join-Path $Output 'bundle-stage'
New-Item -ItemType Directory -Path $PackageRoot -Force | Out-Null
New-Item -ItemType Directory -Path $BundleStage -Force | Out-Null
Copy-Item -Path (Join-Path $Project 'dist\NOVAPlayer\*') -Destination $PackageRoot -Recurse -Force
Copy-Item -LiteralPath (Join-Path $Project 'store\Assets') -Destination $PackageRoot -Recurse -Force
$Publisher = 'CN=NOVA Player Developer Test'
$Manifest = Get-Content -Raw (Join-Path $PSScriptRoot 'Package.appxmanifest.template.xml')
$Manifest = $Manifest.Replace('__STORE_IDENTITY_NAME__','NOVA.Player.DevTest')
$Manifest = $Manifest.Replace('__STORE_PUBLISHER__',$Publisher)
$Manifest = $Manifest.Replace('__PUBLISHER_DISPLAY_NAME__','NOVA Player Developer Test')
$Manifest = $Manifest.Replace('__VERSION__',$Version)
Set-Content -Path (Join-Path $PackageRoot 'AppxManifest.xml') -Value $Manifest -Encoding utf8

$Pfx = Join-Path $Output 'temporary-signing.pfx'
try {
    $DevPassword = [Guid]::NewGuid().ToString('N')
    $Rsa = [System.Security.Cryptography.RSA]::Create(2048)
    $Subject = [System.Security.Cryptography.X509Certificates.X500DistinguishedName]::new($Publisher)
    $Request = [System.Security.Cryptography.X509Certificates.CertificateRequest]::new($Subject,$Rsa,[System.Security.Cryptography.HashAlgorithmName]::SHA256,[System.Security.Cryptography.RSASignaturePadding]::Pkcs1)
    $Eku = [System.Security.Cryptography.OidCollection]::new()
    [void]$Eku.Add([System.Security.Cryptography.Oid]::new('1.3.6.1.5.5.7.3.3'))
    $Request.CertificateExtensions.Add([System.Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension]::new($Eku,$false))
    $Request.CertificateExtensions.Add([System.Security.Cryptography.X509Certificates.X509KeyUsageExtension]::new([System.Security.Cryptography.X509Certificates.X509KeyUsageFlags]::DigitalSignature,$false))
    $CertificateObject = $Request.CreateSelfSigned([DateTimeOffset]::UtcNow.AddMinutes(-5),[DateTimeOffset]::UtcNow.AddYears(1))
    [IO.File]::WriteAllBytes($Pfx,$CertificateObject.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Pfx,$DevPassword))
    $PublicCert = Join-Path $Output 'NOVAPlayer-DevTest.cer'
    [IO.File]::WriteAllBytes($PublicCert,$CertificateObject.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert))
    $Appx = Join-Path $BundleStage "NOVAPlayer_${Version}_x64.msix"
    & $MakeAppx pack /d $PackageRoot /p $Appx /o /nv
    if ($LASTEXITCODE -ne 0) { throw 'MakeAppx package creation failed.' }
    $Bundle = Join-Path $Output "NOVAPlayer-v$($VersionLine.Matches[0].Groups[1].Value)-DevTest.msixbundle"
    & $MakeAppx bundle /d $BundleStage /p $Bundle /o /bv $Version
    if ($LASTEXITCODE -ne 0) { throw 'MakeAppx bundle creation failed.' }
    & $SignTool sign /fd SHA256 /f $Pfx /p $DevPassword $Bundle
    if ($LASTEXITCODE -ne 0) { throw 'Signing the local test bundle failed.' }
    $Check = Join-Path $Output 'unbundle-check'
    & $MakeAppx unbundle /p $Bundle /d $Check /o
    if ($LASTEXITCODE -ne 0) { throw 'MakeAppx could not unbundle the signed package.' }
    Remove-Item -LiteralPath $Check -Recurse -Force
    Remove-Item -LiteralPath $PackageRoot,$BundleStage -Recurse -Force
    Write-Host "Development-only bundle built: $Bundle"
    Write-Host 'Self-signed development identity; trust the public CER before sideloading. This bundle is not a Store upload package.'
} finally {
    Remove-Item -LiteralPath $Pfx -Force -ErrorAction SilentlyContinue
}
