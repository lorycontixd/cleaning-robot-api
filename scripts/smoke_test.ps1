#Requires -Version 7.0
<#
.SYNOPSIS
    End-to-end smoke test for the Cleaning Robot API.

.DESCRIPTION
    Drives a running instance of the API through a full, ordered walkthrough
    that mirrors the documented contract:

        1. PUT an invalid map              -> 422 (invalid map content)
        2. PUT a valid map                 -> 200
        3. POST an invalid /clean          -> 422 (start outside the map)
        4. POST a valid /clean  (basic)    -> 200
        5. POST a valid /clean  (premium)  -> 200  (same start + actions)
        6. GET /history                    -> 200  (CSV export)

    Steps 1 and 3 are expected to fail; the script asserts the exact HTTP
    status and treats that failure as success. Any other outcome aborts.

    The service must already be running and reachable at -BaseUrl
    (see the README for how to start it).

.PARAMETER BaseUrl
    Base URL of the running API. Defaults to http://localhost:8000.

.EXAMPLE
    ./scripts/smoke_test.ps1

.EXAMPLE
    ./scripts/smoke_test.ps1 -BaseUrl http://localhost:8080
#>
[CmdletBinding()]
param(
    [string]$BaseUrl = "http://localhost:8000"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# --- small output helpers ---------------------------------------------------
function Write-Section { param([string]$Text) Write-Host "`n=== $Text ===" -ForegroundColor Cyan }
function Write-Ok      { param([string]$Text) Write-Host "  [ok]   $Text" -ForegroundColor Green }
function Write-Detail  { param([string]$Text) Write-Host "  [info] $Text" -ForegroundColor DarkGray }

# Runs $Action and asserts it fails with a specific HTTP status code.
# Succeeding, or failing with a different status, aborts the script.
function Assert-HttpStatus {
    param(
        [Parameter(Mandatory)] [scriptblock]$Action,
        [Parameter(Mandatory)] [int]$ExpectedStatus,
        [Parameter(Mandatory)] [string]$What
    )
    try {
        $null = & $Action
    }
    catch {
        $response = $_.Exception.Response
        if ($null -ne $response -and [int]$response.StatusCode -eq $ExpectedStatus) {
            Write-Ok "$What rejected with HTTP $ExpectedStatus, as expected."
            return
        }
        throw
    }
    throw "$What unexpectedly succeeded (expected HTTP $ExpectedStatus)."
}

# Resolve the valid map shipped in data/ relative to this script.
$validMap = Join-Path $PSScriptRoot ".." "data" "sample_map.json"
if (-not (Test-Path -LiteralPath $validMap)) {
    throw "Missing map file: $validMap"
}
$validMap = (Resolve-Path -LiteralPath $validMap).Path

# --- 0. service must be up --------------------------------------------------
Write-Section "0. Health check"
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get -TimeoutSec 5
}
catch {
    throw "Cannot reach the API at $BaseUrl. Start the service first (see README) and retry."
}
Write-Ok "Service is up: $($health | ConvertTo-Json -Compress)"

# --- 1. PUT an invalid map (expected failure) -------------------------------
Write-Section "1. PUT /map with an invalid map (expect HTTP 422)"
# Valid .json extension, but the contents do not describe a valid map:
# the tile list is empty while rows * cols = 4.
$invalidMap = Join-Path ([System.IO.Path]::GetTempPath()) "invalid_map_$(New-Guid).json"
'{ "rows": 2, "cols": 2, "tiles": [] }' | Set-Content -LiteralPath $invalidMap -Encoding utf8
try {
    Assert-HttpStatus -What "Invalid map upload" -ExpectedStatus 422 -Action {
        Invoke-WebRequest -Uri "$BaseUrl/map" -Method Put -Form @{ file = Get-Item -LiteralPath $invalidMap }
    }
}
finally {
    Remove-Item -LiteralPath $invalidMap -ErrorAction SilentlyContinue
}

# --- 2. PUT a valid map -----------------------------------------------------
Write-Section "2. PUT /map with a valid map (expect HTTP 200)"
$summary = Invoke-RestMethod -Uri "$BaseUrl/map" -Method Put -Form @{ file = Get-Item -LiteralPath $validMap }
Write-Ok "Loaded sample_map.json -> rows=$($summary.rows) cols=$($summary.cols) walkable_tiles=$($summary.walkable_tiles)"

# --- 3. POST an invalid /clean (expected failure) ---------------------------
Write-Section "3. POST /clean with a start outside the map (expect HTTP 422)"
# (0,1) would also be rejected as a non-walkable start; (99,99) is out of bounds.
$invalidClean = @{
    start       = @{ x = 99; y = 99 }
    robot_model = "basic"
    actions     = @()
} | ConvertTo-Json -Depth 5
Assert-HttpStatus -What "Invalid clean request" -ExpectedStatus 422 -Action {
    Invoke-RestMethod -Uri "$BaseUrl/clean" -Method Post -ContentType "application/json" -Body $invalidClean
}

# Shared start + actions reused by both valid runs below ("same path").
# On sample_map this path stays on walkable tiles: (0,0) -> (1,0) -> (1,1).
$sharedPath = @{
    start   = @{ x = 0; y = 0 }
    actions = @(
        @{ direction = "east";  steps = 1 },
        @{ direction = "south"; steps = 1 }
    )
}

# --- 4. Valid clean with the basic robot ------------------------------------
Write-Section "4. POST /clean with the basic robot (expect HTTP 200)"
$basicBody = $sharedPath + @{ robot_model = "basic" }
$basic = Invoke-RestMethod -Uri "$BaseUrl/clean" -Method Post -ContentType "application/json" -Body ($basicBody | ConvertTo-Json -Depth 5)
Write-Ok "basic   -> state=$($basic.state) successful_steps=$($basic.successful_steps) cleaned_tiles=$($basic.cleaned_tiles.Count)"

# --- 5. Valid clean with the premium robot (same path) ----------------------
Write-Section "5. POST /clean with the premium robot, same path (expect HTTP 200)"
# Reload the map first so tile cleanliness is reset; otherwise the basic run
# above would have left the whole path clean and premium would skip everything.
$null = Invoke-RestMethod -Uri "$BaseUrl/map" -Method Put -Form @{ file = Get-Item -LiteralPath $validMap }
Write-Detail "Reloaded sample_map.json to reset cleanliness before the premium run."
$premiumBody = $sharedPath + @{ robot_model = "premium" }
$premium = Invoke-RestMethod -Uri "$BaseUrl/clean" -Method Post -ContentType "application/json" -Body ($premiumBody | ConvertTo-Json -Depth 5)
Write-Ok "premium -> state=$($premium.state) successful_steps=$($premium.successful_steps) cleaned_tiles=$($premium.cleaned_tiles.Count)"
Write-Detail "premium cleaned $($premium.cleaned_tiles.Count) tile(s): it cleans only dirty tiles and skips the one already clean on load."

# --- 6. Download history ----------------------------------------------------
Write-Section "6. GET /history (expect HTTP 200, text/csv)"
$history = Invoke-RestMethod -Uri "$BaseUrl/history" -Method Get
Write-Ok "History CSV:"
Write-Host $history

Write-Host "`nAll steps completed successfully." -ForegroundColor Green
