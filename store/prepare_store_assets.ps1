$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $PSScriptRoot
$Output = Join-Path $Project 'store\Assets'
$Source = Join-Path $Project 'assets\nova_logo_light_dark.png'
New-Item -ItemType Directory -Path $Output -Force | Out-Null
Add-Type -AssemblyName System.Drawing
$Original = [System.Drawing.Bitmap]::new($Source)
try {
    # Crop the supplied dark NOVA blossom card from the right-hand design variant.
    $Crop = $Original.Clone([System.Drawing.Rectangle]::new(707, 407, 467, 467), [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    try {
        function Save-Square($Name, $Size) {
            $Image = [System.Drawing.Bitmap]::new($Size, $Size, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
            $Graphics = [System.Drawing.Graphics]::FromImage($Image)
            try {
                $Graphics.Clear([System.Drawing.Color]::Transparent)
                $Graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
                $Graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
                $Graphics.DrawImage($Crop, 0, 0, $Size, $Size)
                $Image.Save((Join-Path $Output $Name), [System.Drawing.Imaging.ImageFormat]::Png)
            } finally { $Graphics.Dispose(); $Image.Dispose() }
        }
        Save-Square 'Square44x44Logo.png' 44
        Save-Square 'Square71x71Logo.png' 71
        Save-Square 'Square150x150Logo.png' 150
        Save-Square 'Square310x310Logo.png' 310
        Save-Square 'StoreLogo.png' 50
        $Wide = [System.Drawing.Bitmap]::new(620, 300, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $Graphics = [System.Drawing.Graphics]::FromImage($Wide)
        try {
            $Graphics.Clear([System.Drawing.Color]::Transparent)
            $Graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $Graphics.DrawImage($Crop, 160, 0, 300, 300)
            $Wide.Save((Join-Path $Output 'Wide310x150Logo.png'), [System.Drawing.Imaging.ImageFormat]::Png)
            $Wide.Save((Join-Path $Output 'SplashScreen.png'), [System.Drawing.Imaging.ImageFormat]::Png)
        } finally { $Graphics.Dispose(); $Wide.Dispose() }
    } finally { $Crop.Dispose() }
} finally { $Original.Dispose() }
Get-ChildItem $Output -File | Select-Object Name,Length
