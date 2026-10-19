param (
    [switch]$Commit,
    [switch]$Force,
    [string]$CustomTitle = "",
    [string]$TargetVersion = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = (git rev-parse --show-toplevel).Trim()
if (-not $repoRoot) {
    Write-Error "Nicht in einem Git-Repository!"
    exit 1
}

$patchnotesJsonPath = Join-Path $repoRoot "frontend\src\config\patchnotes.json"
$versionJsPath = Join-Path $repoRoot "frontend\src\config\version.js"
$packageJsonPath = Join-Path $repoRoot "frontend\package.json"

# 1. Aktuelle Version aus version.js einlesen
$currentVersion = "2.11.0.3-beta"
if (Test-Path $versionJsPath) {
    $versionJsContent = Get-Content $versionJsPath -Raw
    if ($versionJsContent -match 'APP_VERSION\s*=\s*"([^"]+)"') {
        $currentVersion = $matches[1]
    }
}

# 2. Bestehende Patchnotes laden
$patchnotes = @()
if (Test-Path $patchnotesJsonPath) {
    $rawObj = Get-Content $patchnotesJsonPath -Raw | ConvertFrom-Json
    if ($rawObj -is [System.Array]) {
        $patchnotes = $rawObj
    } elseif ($rawObj.value) {
        $patchnotes = @($rawObj.value)
    } elseif ($rawObj) {
        $patchnotes = @($rawObj)
    }
}

# 3. Pruefen, welche Commits neu sind
$commits = @()
$rawLog = ""
try {
    $rawLog = git log origin/master..HEAD --oneline 2>&1
} catch {
    $rawLog = ""
}

if (-not $rawLog -or $rawLog -match "fatal:" -or $rawLog.Length -eq 0) {
    try {
        $rawLog = git log -n 3 --oneline
    } catch {
        $rawLog = ""
    }
}

if ($rawLog) {
    $lines = $rawLog -split "`r?`n"
    foreach ($line in $lines) {
        $trimmed = $line.Trim()
        if ($trimmed -and (-not ($trimmed -match "chore\(patch\):")) -and (-not ($trimmed -match "Merge branch"))) {
            $msg = $trimmed -replace "^[a-f0-9]+\s+", ""
            if ($msg) {
                $commits += $msg
            }
        }
    }
}

$latestRecordedVersion = ""
if ($patchnotes.Count -gt 0) {
    $latestRecordedVersion = $patchnotes[0].version
}

# Wenn keine unpushten Commits und die Version bereits verzeichnet ist und nicht Force:
if ((-not $Force) -and ($latestRecordedVersion -eq $currentVersion) -and ($commits.Count -eq 0)) {
    Write-Host "[UNYQ Patchnotes] Keine neuen Aenderungen zum Patchen gefunden."
    exit 0
}

# 4. Naechste Patch-Version ermitteln
$newVersion = $TargetVersion
if (-not $newVersion) {
    if ($currentVersion -match '^(.*?)(\d+)(-.*)?$') {
        $prefix = $matches[1]
        $patchNum = [int]$matches[2] + 1
        $suffix = $matches[3]
        $newVersion = "$prefix$patchNum$suffix"
    } else {
        $newVersion = "$currentVersion.1"
    }
}

$today = (Get-Date).ToString("yyyy-MM-dd")
$title = "Patch $newVersion"
if ($CustomTitle) {
    $title = $CustomTitle
}

# 5. Highlights und Aenderungen
$highlights = @()
$changes = @()

if ($commits.Count -gt 0) {
    foreach ($c in $commits) {
        $changes += $c
        if ($c -match '^(feat|fix|style|refactor|perf)(\([^)]+\))?:\s*(.+)$') {
            $rawCap = $matches[3]
            $cleanTitle = $rawCap.Substring(0, 1).ToUpper() + $rawCap.Substring(1)
            if ($highlights.Count -lt 3) {
                $highlights += $cleanTitle
            }
        }
    }
}

if ($highlights.Count -eq 0) {
    $highlights += "Allgemeine Performance- und Stabilitaetsverbesserungen"
    $highlights += "UI- und Workflow-Optimierungen"
}
if ($changes.Count -eq 0) {
    $changes += "Automatischer Patch Release $newVersion"
}

# 6. Neues Patch-Objekt bauen
$newPatch = [PSCustomObject]@{
    version    = $newVersion
    date       = $today
    title      = $title
    tagline    = "Automatisches Update"
    highlights = $highlights
    changes    = $changes
}

$updatedList = [System.Collections.ArrayList]::new()
[void]$updatedList.Add($newPatch)
foreach ($p in $patchnotes) {
    if ($p.version -ne $newVersion) {
        [void]$updatedList.Add($p)
    }
}

# 7. Dateien aktualisieren
$jsonOutput = $updatedList | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText($patchnotesJsonPath, $jsonOutput, [System.Text.Encoding]::UTF8)

$versionContent = "// UI version label. package.json keeps the SemVer-compatible variant.`nexport const APP_VERSION = `"$newVersion`";`n"
[System.IO.File]::WriteAllText($versionJsPath, $versionContent, [System.Text.Encoding]::UTF8)

if (Test-Path $packageJsonPath) {
    $pkgContent = [System.IO.File]::ReadAllText($packageJsonPath, [System.Text.Encoding]::UTF8)
    $updatedPkg = $pkgContent -replace '"version":\s*"[^"]+"', "`"version`": `"$newVersion`""
    [System.IO.File]::WriteAllText($packageJsonPath, $updatedPkg, [System.Text.Encoding]::UTF8)
}

Write-Host "[OK] [UNYQ Patchnotes] Neuer Patch $newVersion erfolgreich generiert!"

if ($Commit) {
    git add $patchnotesJsonPath $versionJsPath $packageJsonPath
    git commit -m "chore(patch): bump version to $newVersion & generate patch notes [auto]"
    exit 2
}

exit 0
