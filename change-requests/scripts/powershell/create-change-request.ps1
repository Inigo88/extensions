#!/usr/bin/env pwsh
# PowerShell entry for create-change-request; behavior matches scripts/bash/create-change-request.sh (shared Python helpers).

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

function Resolve-CrPython {
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

function Invoke-CrPython {
    param([string[]]$PythonArgs)
    $py = Resolve-CrPython
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

$CrPathsPy = Join-Path $ExtensionRoot 'scripts/python/change_requests_paths.py'
$py = Resolve-CrPython
$bpText = (& $py.Exe @($py.ArgsPrefix + @($CrPathsPy, $ExtensionRoot, $RepoRoot)) | Out-String).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "change_requests_paths.py failed with exit code $LASTEXITCODE"
}
$bpLines = @($bpText -split "`r?`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' })
if ($bpLines.Count -lt 2) {
    throw 'change_requests_paths.py must print two lines: data dir, then registry file path'
}
$SPECS_DIR = $bpLines[0]
$REGISTRY_FILE = $bpLines[1]
$CR_TEMPLATE = Join-Path $ExtensionRoot 'templates/change-request-template.md'
$REGISTRY_TEMPLATE = Join-Path $ExtensionRoot 'templates/change-request-registry-template.md'
$UPDATE_REGISTRY_PY = Join-Path $ExtensionRoot 'scripts/python/update_cr_registry.py'
$FORMAT_TITLE_PY = Join-Path $ExtensionRoot 'scripts/python/format_feature_title.py'

New-Item -ItemType Directory -Path $SPECS_DIR -Force | Out-Null

if (-not (Test-Path -LiteralPath $REGISTRY_FILE)) {
    if (-not (Test-Path -LiteralPath $REGISTRY_TEMPLATE)) {
        Write-Error "Registry template not found at $REGISTRY_TEMPLATE"
        exit 1
    }
    Copy-Item -LiteralPath $REGISTRY_TEMPLATE -Destination $REGISTRY_FILE -Force
    Write-Host 'Initialized change request registry from template.'
}

$regRaw = Read-TextUtf8NoBom $REGISTRY_FILE
$all = [regex]::Matches($regRaw, 'CR(\d{3})')
$highest = 0
foreach ($m in $all) {
    $n = [int]$m.Groups[1].Value
    if ($n -gt $highest) { $highest = $n }
}
Get-ChildItem -LiteralPath $SPECS_DIR -Recurse -File -Filter 'CR*.md' -ErrorAction SilentlyContinue |
    ForEach-Object {
        $bn = $_.Name
        $mm = [regex]::Match($bn, '^CR(\d{3})-')
        if ($mm.Success) {
            $n = [int]$mm.Groups[1].Value
            if ($n -gt $highest) { $highest = $n }
        }
    }

$nextNum = $highest + 1
$NEXT_ID = 'CR{0:D3}' -f $nextNum

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
    $py = Resolve-CrPython
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

$CR_FILENAME = "$NEXT_ID-$ShortName.md"
$CR_FILEPATH = Join-Path $TARGET_DIR $CR_FILENAME
$REL_CR_PATH = "$FeatureId/$CR_FILENAME"

$fillPy = @'
import sys
from datetime import date
from pathlib import Path

tpl_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])
cr_id = sys.argv[3]
title = sys.argv[4]
text = tpl_path.read_text(encoding="utf-8")
text = text.replace("CRXXX", cr_id)
text = text.replace("[Title]", title)
text = text.replace("YYYY-MM-DD", date.today().strftime("%Y-%m-%d"))
out_path.write_text(text, encoding="utf-8")
'@

if (Test-Path -LiteralPath $CR_TEMPLATE) {
    Invoke-CrPython @('-c', $fillPy, $CR_TEMPLATE, $CR_FILEPATH, $NEXT_ID, $Title)
    Write-Host "Created change request: $CR_FILEPATH"
}
else {
    New-Item -ItemType File -Path $CR_FILEPATH -Force | Out-Null
    Write-Host "Created empty change request (template missing): $CR_FILEPATH"
}

$TOTAL = 0
$COMPLETED = 0
$DRAFT = 0
$APPR = 0
$mTot = [regex]::Match($regRaw, '\*\*(\d+) total\*\*')
if ($mTot.Success) {
    $TOTAL = [int]$mTot.Groups[1].Value
}
$mComp = [regex]::Match($regRaw, '✅\s+(\d+)\s+completed')
if ($mComp.Success) {
    $COMPLETED = [int]$mComp.Groups[1].Value
}
$mDraft = [regex]::Match($regRaw, '🔴\s+(\d+)\s+draft / in flight')
if ($mDraft.Success) {
    $DRAFT = [int]$mDraft.Groups[1].Value
}
$mAppr = [regex]::Match($regRaw, '🟡\s+(\d+)\s+approved or in progress')
if ($mAppr.Success) {
    $APPR = [int]$mAppr.Groups[1].Value
}

$NEW_TOTAL = $TOTAL + 1
$NEW_DRAFT = $DRAFT + 1

$tempRegistry = [System.IO.Path]::GetTempFileName()
try {
    $regForTemp = Read-TextUtf8NoBom $REGISTRY_FILE
    $regForTemp = $regForTemp.Replace("**$TOTAL total**", "**$NEW_TOTAL total**")
    $regForTemp = $regForTemp.Replace("🔴 $DRAFT draft", "🔴 $NEW_DRAFT draft")
    Write-TextUtf8NoBom $tempRegistry $regForTemp

    $sectionPattern = "^## $([regex]::Escape($featurePrefix))([^0-9]|$)"
    $hasSection = Select-String -Path $tempRegistry -Pattern $sectionPattern -Quiet

    if ($hasSection) {
        Invoke-CrPython @(
            $UPDATE_REGISTRY_PY,
            $tempRegistry,
            $FeatureId,
            $NEXT_ID,
            $REL_CR_PATH,
            $Title,
            $FeatureTitle
        )
    }
    else {
        $append = @"

## $FeatureTitle

| ID | Title | Summary | Status |
|----|-------|---------|--------|
| [$NEXT_ID]($REL_CR_PATH) | $Title | — | 🔴 |
"@
        [System.IO.File]::AppendAllText($tempRegistry, $append, $Utf8NoBom)
    }

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
