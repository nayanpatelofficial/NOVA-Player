$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $PSScriptRoot
Set-Location $Project
$Python = $env:NOVA_BUILD_PYTHON
if ([string]::IsNullOrWhiteSpace($Python)) { $Python = Join-Path $Project '.venv\Scripts\python.exe' }
if (-not (Test-Path $Python)) { throw 'Create .venv and install requirements.txt plus requirements-build.txt first, or set NOVA_BUILD_PYTHON.' }
$IconBuilder = Join-Path $PSScriptRoot 'create_windows_icon.ps1'
& $IconBuilder
$IconPath = Join-Path $Project 'assets\nova-player.ico'
if (-not (Test-Path $IconPath)) { throw 'The NOVA Windows icon was not created.' }
$BuildArgs = @('--noconfirm', '--clean', '--windowed', '--name', 'NOVAPlayer', '--icon', $IconPath, '--add-data', 'assets;assets', '--add-data', 'THIRD_PARTY_NOTICES.md;.')
& $Python -m PyInstaller @BuildArgs main.py
if ($LASTEXITCODE -ne 0) { throw 'NOVA Player executable build failed.' }
$AppFolder = Join-Path $Project 'dist\NOVAPlayer'
$ShortcutIcon = Join-Path $AppFolder 'NOVAPlayer-icon.ico'
Copy-Item -LiteralPath $IconPath -Destination $ShortcutIcon -Force
$LicenseFolder = Join-Path $AppFolder 'Licenses'
if (Test-Path $LicenseFolder) { Remove-Item -LiteralPath $LicenseFolder -Recurse -Force }
New-Item -ItemType Directory -Path $LicenseFolder -Force | Out-Null
$SitePackages = (& $Python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])").Trim()
$LicensePackages = Get-ChildItem -LiteralPath $SitePackages -Directory | Where-Object {
    $_.Name -match '(?i)^(pyside6_(essentials|addons)|shiboken6|tinytag|pyinstaller|pyinstaller_hooks_contrib)-.*\.dist-info$'
}
foreach ($Info in $LicensePackages) {
    $LicenseDir = Join-Path $Info.FullName 'licenses'
    if (Test-Path $LicenseDir) {
        $Target = Join-Path $LicenseFolder ($Info.Name -replace '\.dist-info$','')
        New-Item -ItemType Directory -Path $Target -Force | Out-Null
        Get-ChildItem -LiteralPath $LicenseDir -Recurse -File | ForEach-Object {
            $Relative = [IO.Path]::GetRelativePath($LicenseDir, $_.FullName)
            $Destination = Join-Path $Target $Relative
            New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
            Copy-Item -LiteralPath $_.FullName -Destination $Destination -Force
        }
    }
}
$PythonBase = & $Python -c "import sys; print(sys.base_prefix)"
$PythonLicense = Join-Path $PythonBase 'LICENSE.txt'
if (Test-Path $PythonLicense) { Copy-Item -LiteralPath $PythonLicense -Destination (Join-Path $LicenseFolder 'Python-LICENSE.txt') -Force }
Get-ChildItem -LiteralPath (Join-Path $Project 'licenses') -File | Copy-Item -Destination $LicenseFolder -Force
Copy-Item -LiteralPath (Join-Path $Project 'THIRD_PARTY_NOTICES.md') -Destination $AppFolder -Force
$IsccPath = (Get-Command ISCC.exe -ErrorAction SilentlyContinue).Source
if ([string]::IsNullOrWhiteSpace($IsccPath)) {
    $Candidates = @(
        (Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'),
        (Join-Path $env:ProgramFiles 'Inno Setup 6\ISCC.exe')
    )
    $IsccPath = $Candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not [string]::IsNullOrWhiteSpace($IsccPath)) {
    & $IsccPath '.\installer\nova.iss'
    if ($LASTEXITCODE -ne 0) { throw 'NOVA Player installer build failed.' }
} else {
    Write-Host 'Inno Setup not found; portable dist\NOVAPlayer build is ready.'
}
