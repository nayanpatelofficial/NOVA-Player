$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $Project 'store\Assets\Square310x310Logo.png'
$Destination = Join-Path $Project 'assets\nova-player.ico'
if (-not (Test-Path -LiteralPath $Source)) {
    throw "NOVA logo source is missing: $Source. Run store\prepare_store_assets.ps1 first."
}

Add-Type -AssemblyName System.Drawing
$Sizes = @(16, 24, 32, 48, 64, 128, 256)
$SourceImage = [System.Drawing.Bitmap]::new($Source)
$Frames = [System.Collections.Generic.List[object]]::new()
try {
    foreach ($Size in $Sizes) {
        $Image = [System.Drawing.Bitmap]::new($Size, $Size, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $Graphics = [System.Drawing.Graphics]::FromImage($Image)
        $Png = [System.IO.MemoryStream]::new()
        try {
            $Graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $Graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
            $Graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            $Graphics.DrawImage($SourceImage, 0, 0, $Size, $Size)
            $Image.Save($Png, [System.Drawing.Imaging.ImageFormat]::Png)
            $Frames.Add([pscustomobject]@{ Size = $Size; Data = $Png.ToArray() })
        } finally {
            $Png.Dispose()
            $Graphics.Dispose()
            $Image.Dispose()
        }
    }

    $Output = [System.IO.File]::Create($Destination)
    $Writer = [System.IO.BinaryWriter]::new($Output)
    try {
        $Writer.Write([UInt16]0) # Reserved
        $Writer.Write([UInt16]1) # Icon resource
        $Writer.Write([UInt16]$Frames.Count)

        $Offset = 6 + (16 * $Frames.Count)
        foreach ($Frame in $Frames) {
            $Dimension = if ($Frame.Size -eq 256) { [byte]0 } else { [byte]$Frame.Size }
            $Writer.Write($Dimension)
            $Writer.Write($Dimension)
            $Writer.Write([byte]0) # Palette colors
            $Writer.Write([byte]0) # Reserved
            $Writer.Write([UInt16]1) # Color planes
            $Writer.Write([UInt16]32) # Bits per pixel
            $Writer.Write([UInt32]$Frame.Data.Length)
            $Writer.Write([UInt32]$Offset)
            $Offset += $Frame.Data.Length
        }
        foreach ($Frame in $Frames) { $Writer.Write($Frame.Data) }
    } finally {
        $Writer.Dispose()
        $Output.Dispose()
    }
} finally {
    $SourceImage.Dispose()
}
Write-Host "Created NOVA multi-size icon: $Destination"
