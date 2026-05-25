# Idempotent: creates .project subfolders and .gitkeep placeholders only when missing.
param(
    [string]$Root = "."
)

Set-Location $Root
$subdirs = @("assets", "backlog", "context", "documents", "crs", "bugs")

New-Item -ItemType Directory -Force -Path ".project" | Out-Null

foreach ($d in $subdirs) {
    $dir = Join-Path ".project" $d
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $gitkeep = Join-Path $dir ".gitkeep"
    if (-not (Test-Path -LiteralPath $gitkeep)) {
        New-Item -ItemType File -Force -Path $gitkeep | Out-Null
    }
}

Write-Output "OK: .project layout ensured under $(Get-Location)"
