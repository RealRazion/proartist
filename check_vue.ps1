$raw = Get-Content 'frontend/src/views/HhuTool.vue' -Raw
$scriptMatch = [regex]::Match($raw, '(?s)<script setup>(.*?)</script>')
if ($scriptMatch.Success) {
    $sc = $scriptMatch.Groups[1].Value
    $clean = [regex]::Replace($sc, '//.*', '')
    
    $inSingle = $false
    $inDouble = $false
    $inBacktick = $false
    $cDepth = 0
    
    $lines = $clean -split "`r?`n"
    for ($l = 0; $l -lt $lines.Length; $l++) {
        $line = $lines[$l]
        $startDepth = $cDepth
        for ($i = 0; $i -lt $line.Length; $i++) {
            $ch = $line[$i]
            $prev = if ($i -gt 0) { $line[$i-1] } else { '' }
            
            if ($ch -eq "'" -and -not $inDouble -and -not $inBacktick -and $prev -ne "\") {
                $inSingle = -not $inSingle
                continue
            }
            if ($ch -eq '"' -and -not $inSingle -and -not $inBacktick -and $prev -ne "\") {
                $inDouble = -not $inDouble
                continue
            }
            if ($ch -eq '`' -and -not $inSingle -and -not $inDouble -and $prev -ne "\") {
                $inBacktick = -not $inBacktick
                continue
            }
            
            if (-not $inSingle -and -not $inDouble -and -not $inBacktick) {
                if ($ch -eq '{') { $cDepth++ }
                elseif ($ch -eq '}') { $cDepth-- }
            }
        }
        if ($cDepth -ne $startDepth -and $l -gt ($lines.Length - 50)) {
            Write-Host "Line $($l+1) (depth $cDepth): $line"
        }
    }
}
