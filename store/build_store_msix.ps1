$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $PSScriptRoot
Set-Location $Project

$IdentityName = $env:NOVA_STORE_IDENTITY_NAME
$Publisher = $env:NOVA_STORE_PUBLISHER
$PublisherDisplayName = $env:NOVA_STORE_PUBLISHER_DISPLAY_NAME
foreach ($Item in @(@('NOVA_STORE_IDENTITY_NAME',$IdentityName),@('NOVA_STORE_PUBLISHER',$Publisher),@('NOVA_STORE_PUBLISHER_DISPLAY_NAME',$PublisherDisplayName))) {
    if ([string]::IsNullOrWhiteSpace($Item[1])) { throw "Set $($Item[0]) from the reserved Partner Center Product identity." }
}
$MakeAppx = Get-Command MakeAppx.exe -ErrorAction SilentlyContinue
if (-not $MakeAppx) { throw 'Install the Windows SDK and put MakeAppx.exe on PATH.' }

$Python = $env:NOVA_BUILD_PYTHON
if ([string]::IsNullOrWhiteSpace($Python)) { $Python = Join-Path $Project '.venv\Scripts\python.exe' }
if (-not (Test-Path $Python)) { throw 'Create .venv and install requirements.txt plus requirements-build.txt first, or set NOVA_BUILD_PYTHON.' }
& (Join-Path $Project 'scripts\build_windows.ps1')
if ($LASTEXITCODE -ne 0) { throw 'NOVA Player executable build failed.' }
& (Join-Path $PSScriptRoot 'prepare_store_assets.ps1')

$VersionLine = Select-String -Path (Join-Path $Project 'nova\__init__.py') -Pattern '__version__\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"'
if (-not $VersionLine) { throw 'Cannot read NOVA version.' }
$Version = "$($VersionLine.Matches[0].Groups[1].Value).0"
$ArtifactRoot = Join-Path $Project 'dist\store'
$PackageRoot = Join-Path $ArtifactRoot 'NOVAPlayer'
$BundleRoot = Join-Path $ArtifactRoot 'bundle'
if (Test-Path $PackageRoot) { Remove-Item -LiteralPath $PackageRoot -Recurse -Force }
if (Test-Path $BundleRoot) { Remove-Item -LiteralPath $BundleRoot -Recurse -Force }
New-Item -ItemType Directory -Path $PackageRoot -Force | Out-Null
New-Item -ItemType Directory -Path $BundleRoot -Force | Out-Null
Copy-Item -Path (Join-Path $Project 'dist\NOVAPlayer\*') -Destination $PackageRoot -Recurse -Force
Copy-Item -LiteralPath (Join-Path $Project 'store\Assets') -Destination $PackageRoot -Recurse -Force

$Manifest = Get-Content -Raw (Join-Path $PSScriptRoot 'Package.appxmanifest.template.xml')
$Manifest = $Manifest.Replace('__STORE_IDENTITY_NAME__',[Security.SecurityElement]::Escape($IdentityName))
$Manifest = $Manifest.Replace('__STORE_PUBLISHER__',[Security.SecurityElement]::Escape($Publisher))
$Manifest = $Manifest.Replace('__PUBLISHER_DISPLAY_NAME__',[Security.SecurityElement]::Escape($PublisherDisplayName))
$Manifest = $Manifest.Replace('__VERSION__',$Version)
Set-Content -Path (Join-Path $PackageRoot 'AppxManifest.xml') -Value $Manifest -Encoding utf8

$PackageFile = Join-Path $BundleRoot "NOVAPlayer_${Version}_x64.msix"
& $MakeAppx.Source pack /d $PackageRoot /p $PackageFile /o
if ($LASTEXITCODE -ne 0) { throw 'MakeAppx package creation failed.' }
$BundleFile = Join-Path $ArtifactRoot "NOVAPlayer_${Version}_x64.msixbundle"
& $MakeAppx.Source bundle /d $BundleRoot /p $BundleFile /o /bv $Version
if ($LASTEXITCODE -ne 0) { throw 'MakeAppx bundle creation failed.' }
$Check = Join-Path $ArtifactRoot 'unbundle-check'
& $MakeAppx.Source unbundle /p $BundleFile /d $Check /o
if ($LASTEXITCODE -ne 0) { throw 'MakeAppx could not unbundle the Store bundle.' }
Remove-Item -LiteralPath $Check -Recurse -Force
Write-Host "Unsigned Store submission bundle built: $BundleFile"
Write-Host 'The Microsoft Store signs packages accepted for publication. Run Windows App Certification Kit before Partner Center submission.'
