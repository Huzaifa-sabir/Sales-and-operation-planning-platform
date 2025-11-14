# Test Forecast Entry Deadline Calculation
# This script tests the active cycle endpoint and verifies date calculations

Write-Host "=== Testing Active Cycle Endpoint ===" -ForegroundColor Cyan
Write-Host ""

# Login
Write-Host "1. Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@heavygarlic.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body $loginBody
    $token = $loginResponse.access_token
    Write-Host "   ✓ Login successful" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Login failed: $_" -ForegroundColor Red
    exit 1
}

# Get active cycle
Write-Host "2. Fetching active cycle..." -ForegroundColor Yellow
try {
    $cycle = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sop/cycles/active" -Method GET -Headers @{"Authorization"="Bearer $token"}
    Write-Host "   ✓ Active cycle fetched" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Cycle Details:" -ForegroundColor Cyan
    Write-Host "   - Name: $($cycle.cycleName)"
    Write-Host "   - Status: $($cycle.status)"
    Write-Host "   - Start Date: $($cycle.dates.startDate)"
    Write-Host "   - End Date: $($cycle.dates.endDate)"
    Write-Host "   - Submission Deadline: $($cycle.dates.submissionDeadline)"
    Write-Host ""
} catch {
    Write-Host "   ✗ Failed to fetch active cycle: $_" -ForegroundColor Red
    exit 1
}

# Calculate days remaining
Write-Host "3. Calculating days remaining..." -ForegroundColor Yellow
$endDateStr = $cycle.dates.endDate
if (!$endDateStr) {
    Write-Host "   ✗ End date not found in cycle data" -ForegroundColor Red
    exit 1
}

$endDate = [DateTime]::Parse($endDateStr)
$now = Get-Date
$daysRemaining = ($endDate.Date - $now.Date).Days

Write-Host "   Current Date: $($now.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor White
Write-Host "   End Date: $($endDate.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor White
Write-Host "   Days Remaining: $daysRemaining" -ForegroundColor $(if ($daysRemaining -lt 0) { "Red" } elseif ($daysRemaining -eq 0) { "Yellow" } else { "Green" })
Write-Host ""

# Expected message
Write-Host "4. Expected Frontend Message:" -ForegroundColor Yellow
if ($cycle.status -ne "open") {
    Write-Host "   Message: Cycle is $($cycle.status.ToUpper()). Editing disabled." -ForegroundColor Cyan
} elseif ($daysRemaining -lt 0) {
    Write-Host "   Message: Cycle deadline has passed ($($endDate.ToString('MMM dd, yyyy'))). Please contact administrator." -ForegroundColor Red
} elseif ($daysRemaining -eq 0) {
    Write-Host "   Message: Cycle closes TODAY ($($endDate.ToString('MMM dd, yyyy'))). Please submit your forecasts immediately." -ForegroundColor Yellow
} elseif ($daysRemaining -le 3) {
    Write-Host "   Message: Cycle closes in $daysRemaining day$(if ($daysRemaining -ne 1) { 's' }) ($($endDate.ToString('MMM dd, yyyy')))" -ForegroundColor Yellow
} else {
    Write-Host "   Message: Cycle closes in $daysRemaining day$(if ($daysRemaining -ne 1) { 's' }) ($($endDate.ToString('MMM dd, yyyy')))" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan

