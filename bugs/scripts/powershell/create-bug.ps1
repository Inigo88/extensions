#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [Parameter(Position = 0, Mandatory = $true)]
    [string]$Title,

    [string]$Feature = '',
    [Alias('FeatureTitle')]
    [string]$FeatureTitle = '',

    [string]$ShortName = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Utf8NoBom = New-Object System.Text.UTF8Encoding $false

function Read-TextUtf8NoBom([string]$LiteralPath) {
    return [System.IO.File]::ReadAllText($LiteralPath, $Utf8NoBom)
}

function Write-TextUtf8NoBom([string]$LiteralPath, [string]$Content) {
    [System.IO.File]::WriteAllText($LiteralPath, $Content, $Utf8NoBom)
}

function Resolve-BugsPython {
    foreach ($name in @('python3', 'python')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) {
            return @{ Exe = $cmd.Source; ArgsPrefix = @() }
        }
    }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return @{ Exe = $py.Source; ArgsPrefix = @('-3') }
    }
    throw 'Python 3 not found. Install Python 3 and ensure python3, python, or py -3 is on PATH.'
}

function Invoke-BugsPython {
    param([string[]]$PythonArgs)
    $py = Resolve-BugsPython
    & $py.Exe @($py.ArgsPrefix + $PythonArgs)
    if ($LASTEXITCODE -ne 0) {
        throw "Python exited with code $LASTEXITCODE"
    }
}

$ScriptDir = $PSScriptRoot
$ExtensionRoot = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path

$gitTop = ''
try {
    $gitTop = (& git rev-parse --show-toplevel 2>$null | Out-String).Trim()
}
catch { }
if ([string]::IsNullOrWhiteSpace($gitTop)) {
    $RepoRoot = (Get-Location).Path
}
else {
    $RepoRoot = $gitTop
}

$BugsPathsPy = Join-Path $ExtensionRoot 'scripts/python/bugs_paths.py'
$py = Resolve-BugsPython
$bpText = (& $py.Exe @($py.ArgsPrefix + @($BugsPathsPy, $ExtensionRoot, $RepoRoot)) | Out-String).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "bugs_paths.py failed with exit code $LASTEXITCODE"
}
$bpLines = @($bpText -split "`r?`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' })
if ($bpLines.Count -lt 6) {
    throw 'bugs_paths.py must print six lines: data dir, registry path, then status markers (open, investigating, fix_proposed, resolved)'
}
$SPECS_DIR = $bpLines[0]
$REGISTRY_FILE = $bpLines[1]
$StatusOpen = $bpLines[2]
$BUG_TEMPLATE = Join-Path $ExtensionRoot 'templates/bug-template.md'
$REGISTRY_TEMPLATE = Join-Path $ExtensionRoot 'templates/bug-report-registry-template.md'
$UPDATE_REGISTRY_PY = Join-Path $ExtensionRoot 'scripts/python/update_registry.py'
$RECONCILE_HEADER_PY = Join-Path $ExtensionRoot 'scripts/python/reconcile_registry_header.py'
$FORMAT_TITLE_PY = Join-Path $ExtensionRoot 'scripts/python/format_feature_title.py'

New-Item -ItemType Directory -Path $SPECS_DIR -Force | Out-Null

if (-not (Test-Path -LiteralPath $REGISTRY_FILE)) {
    if (-not (Test-Path -LiteralPath $REGISTRY_TEMPLATE)) {
        Write-Error "Registry template not found at $REGISTRY_TEMPLATE"
        exit 1
    }
    Copy-Item -LiteralPath $REGISTRY_TEMPLATE -Destination $REGISTRY_FILE -Force
    Write-Host 'Initialized bug registry from template.'
}

$regRaw = Read-TextUtf8NoBom $REGISTRY_FILE
$all = [regex]::Matches($regRaw, 'B(\d{3})')
$highest = 0
foreach ($m in $all) {
    $n = [int]$m.Groups[1].Value
    if ($n -gt $highest) { $highest = $n }
}
$nextNum = $highest + 1
$NEXT_ID = 'B{0:D3}' -f $nextNum

$FeatureId = $Feature
if ([string]::IsNullOrWhiteSpace($FeatureId)) {
    $FeatureId = '000-general'
}

if ($FeatureId -match '^\d{3}$') {
    $specsPath = Join-Path $RepoRoot 'specs'
    if (Test-Path -LiteralPath $specsPath) {
        $matchDir = Get-ChildItem -LiteralPath $specsPath -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -like "$FeatureId-*" } |
            Select-Object -First 1
        if ($matchDir) {
            $FeatureId = $matchDir.Name
        }
    }
}

$featurePrefix = if ($FeatureId.Length -ge 3) { $FeatureId.Substring(0, 3) } else { $FeatureId }

if ([string]::IsNullOrWhiteSpace($FeatureTitle)) {
    $py = Resolve-BugsPython
    $lines = & $py.Exe @($py.ArgsPrefix + @($FORMAT_TITLE_PY, $FeatureId)) 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "format_feature_title.py failed with exit code $LASTEXITCODE"
    }
    $FeatureTitle = ($lines | Out-String).Trim()
}

$TARGET_DIR = Join-Path $SPECS_DIR $FeatureId
New-Item -ItemType Directory -Path $TARGET_DIR -Force | Out-Null

$slug = $Title.ToLowerInvariant()
$slug = $slug -creplace '[^a-z0-9]', '-'
$slug = $slug -creplace '-+', '-'
$slug = $slug.Trim('-')
if ($slug.Length -gt 50) {
    $slug = $slug.Substring(0, 50)
}
if ([string]::IsNullOrWhiteSpace($ShortName)) {
    $ShortName = $slug
}

$BUG_FILENAME = "$NEXT_ID-$ShortName.md"
$BUG_FILEPATH = Join-Path $TARGET_DIR $BUG_FILENAME
$REL_BUG_PATH = "$FeatureId/$BUG_FILENAME"

$fillPy = @'
import sys
from datetime import date
from pathlib import Path

tpl_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])
bug_id = sys.argv[3]
title = sys.argv[4]
text = tpl_path.read_text(encoding="utf-8")
text = text.replace("BXXX", bug_id)
text = text.replace("[Title]", title)
text = text.replace("YYYY-MM-DD", date.today().strftime("%Y-%m-%d"))
out_path.write_text(text, encoding="utf-8")
'@

if (Test-Path -LiteralPath $BUG_TEMPLATE) {
    Invoke-BugsPython @('-c', $fillPy, $BUG_TEMPLATE, $BUG_FILEPATH, $NEXT_ID, $Title)
    Write-Host "Created bug report: $BUG_FILEPATH"
}
else {
    New-Item -ItemType File -Path $BUG_FILEPATH -Force | Out-Null
    Write-Host "Created empty bug report (template missing): $BUG_FILEPATH"
}

$tempRegistry = [System.IO.Path]::GetTempFileName()
try {
    Copy-Item -LiteralPath $REGISTRY_FILE -Destination $tempRegistry -Force

    $sectionPattern = "^## $([regex]::Escape($featurePrefix))([^0-9]|$)"
    $hasSection = Select-String -Path $tempRegistry -Pattern $sectionPattern -Quiet

    if ($hasSection) {
        Invoke-BugsPython @(
            $UPDATE_REGISTRY_PY,
            $tempRegistry,
            $FeatureId,
            $NEXT_ID,
            $REL_BUG_PATH,
            $Title,
            $FeatureTitle,
            $StatusOpen
        )
    }
    else {
        $append = @"

## $FeatureTitle

| ID | Title | Fix | Status |
|----|-------|-----|--------|
| [$NEXT_ID]($REL_BUG_PATH) | $Title | — | $StatusOpen |
"@
        [System.IO.File]::AppendAllText($tempRegistry, $append, $Utf8NoBom)
    }

    Invoke-BugsPython @($RECONCILE_HEADER_PY, $tempRegistry, $ExtensionRoot)

    Move-Item -LiteralPath $tempRegistry -Destination $REGISTRY_FILE -Force
}
catch {
    if (Test-Path -LiteralPath $tempRegistry) {
        Remove-Item -LiteralPath $tempRegistry -Force -ErrorAction SilentlyContinue
    }
    throw
}

Write-Host "Updated registry: $REGISTRY_FILE"

Write-Host "Success: $NEXT_ID created."
