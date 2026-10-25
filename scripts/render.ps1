param(
    [Parameter(Mandatory = $true)][string]$Pptx,
    [Parameter(Mandatory = $true)][string]$OutDir,
    [int]$Dpi = 150
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $Pptx)) {
    throw "PPTX not found: $Pptx"
}
$Pptx = (Resolve-Path -LiteralPath $Pptx).Path

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$OutDir = (Resolve-Path -LiteralPath $OutDir).Path

$pdftoppm = Get-Command pdftoppm -ErrorAction SilentlyContinue
if (-not $pdftoppm) {
    throw "pdftoppm not found. Install poppler and add its bin directory to PATH."
}

$pdf = Join-Path $OutDir "render.pdf"
if (Test-Path -LiteralPath $pdf) { Remove-Item -LiteralPath $pdf -Force }

Write-Host "Opening PowerPoint..."
$ppt = New-Object -ComObject PowerPoint.Application
try {
    $pres = $ppt.Presentations.Open($Pptx, $true, $false, $false)
    try {
        $pres.SaveAs($pdf, 32)  # 32 = ppSaveAsPDF
        $count = $pres.Slides.Count
    }
    finally {
        $pres.Close()
    }
}
finally {
    $ppt.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
}

if (-not (Test-Path -LiteralPath $pdf)) {
    throw "PDF export failed: $pdf"
}

Write-Host "Rendering $count slides at $Dpi dpi..."
$prefix = Join-Path $OutDir "slide"
Get-ChildItem -LiteralPath $OutDir -Filter "slide-*.jpg" -ErrorAction SilentlyContinue |
    Remove-Item -Force

& pdftoppm -jpeg -r $Dpi $pdf $prefix
if ($LASTEXITCODE -ne 0) {
    throw "pdftoppm failed with exit code $LASTEXITCODE"
}

$rendered = @(Get-ChildItem -LiteralPath $OutDir -Filter "slide-*.jpg")
Write-Host "Done: $($rendered.Count) images in $OutDir"
if ($rendered.Count -ne $count) {
    Write-Warning "Slide count mismatch: PPTX=$count, images=$($rendered.Count)"
}
