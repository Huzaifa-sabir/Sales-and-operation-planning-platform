# Comprehensive Test Script for SOP Cycles and Forecast Entry
# Login and get token
Write-Host "=== Testing SOP Cycles and Forecast Entry ===" -ForegroundColor Cyan
Write-Host "`n1. Logging in..." -ForegroundColor Yellow
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body '{"email":"admin@heavygarlic.com","password":"admin123"}'
$token = $loginResponse.access_token
Write-Host "✓ Login successful" -ForegroundColor Green

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# SOP CYCLE TESTS
Write-Host "`n=== SOP CYCLE TESTS ===" -ForegroundColor Cyan

# 2. List cycles
Write-Host "`n2. Listing cycles..." -ForegroundColor Yellow
try {
    $cycles = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sop/cycles?page=1`&pageSize=10" -Method GET -Headers $headers
    Write-Host "✓ Found $($cycles.cycles.Count) cycles" -ForegroundColor Green
    if ($cycles.cycles.Count -gt 0) {
        $cycleId = $cycles.cycles[0]._id
        Write-Host "   Using cycle ID: $cycleId" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    $cycleId = $null
}

# 3. Create new cycle
Write-Host "`n3. Creating new cycle..." -ForegroundColor Yellow
$cycleData = @{
    cycleName = "Test Cycle $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    year = 2025
    month = 12
    startDate = "2025-12-01T00:00:00Z"
    endDate = "2025-12-31T23:59:59Z"
    planningStartMonth = "2025-12-01T00:00:00Z"
} | ConvertTo-Json
try {
    $newCycle = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sop/cycles" -Method POST -Headers $headers -Body $cycleData
    Write-Host "✓ Cycle created: $($newCycle.cycleName)" -ForegroundColor Green
    Write-Host "   ID: $($newCycle._id)" -ForegroundColor Gray
    Write-Host "   Status: $($newCycle.status)" -ForegroundColor Gray
    Write-Host "   End Date: $($newCycle.dates.endDate)" -ForegroundColor Gray
    Write-Host "   Submission Deadline: $($newCycle.dates.submissionDeadline)" -ForegroundColor Gray
    $testCycleId = $newCycle._id
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    $testCycleId = $null
}

# 4. Get cycle by ID
if ($testCycleId) {
    Write-Host "`n4. Getting cycle by ID..." -ForegroundColor Yellow
    try {
        $cycle = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sop/cycles/$testCycleId" -Method GET -Headers $headers
        Write-Host "✓ Retrieved cycle: $($cycle.cycleName)" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 5. Open cycle
if ($testCycleId) {
    Write-Host "`n5. Opening cycle..." -ForegroundColor Yellow
    try {
        $openResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sop/cycles/$testCycleId/status" -Method PUT `
            -Headers $headers -Body '{"status":"OPEN"}'
        Write-Host "✓ Cycle opened: $($openResponse.message)" -ForegroundColor Green
        Write-Host "   Status: $($openResponse.cycle.status)" -ForegroundColor Gray
    } catch {
        Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# FORECAST ENTRY TESTS
Write-Host "`n=== FORECAST ENTRY TESTS ===" -ForegroundColor Cyan

# 6. Get active cycle
Write-Host "`n6. Getting active cycle..." -ForegroundColor Yellow
try {
    $activeCycle = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sop/cycles/active" -Method GET -Headers $headers
    Write-Host "✓ Active cycle: $($activeCycle.cycleName)" -ForegroundColor Green
    Write-Host "   ID: $($activeCycle._id)" -ForegroundColor Gray
    Write-Host "   End Date: $($activeCycle.dates.endDate)" -ForegroundColor Gray
    $activeCycleId = $activeCycle._id
} catch {
    Write-Host "✗ No active cycle found: $($_.Exception.Message)" -ForegroundColor Red
    $activeCycleId = $testCycleId
}

# 7. List forecasts
if ($activeCycleId) {
    Write-Host "`n7. Listing forecasts..." -ForegroundColor Yellow
    try {
        $forecasts = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/forecasts?cycleId=$activeCycleId`&page=1`&pageSize=10" -Method GET -Headers $headers
        Write-Host "✓ Found $($forecasts.forecasts.Count) forecasts" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 8. Create forecast
if ($activeCycleId) {
    Write-Host "`n8. Creating forecast..." -ForegroundColor Yellow
    $forecastData = @{
        cycleId = $activeCycleId
        customerId = "TEST_CUSTOMER_001"
        productId = "TEST_PRODUCT_001"
        monthlyForecasts = @(
            @{ month = "2025-12"; quantity = 100 }
            @{ month = "2026-01"; quantity = 120 }
            @{ month = "2026-02"; quantity = 130 }
        )
        useCustomerPrice = $true
        notes = "Test forecast created via API"
    } | ConvertTo-Json -Depth 10
    try {
        $newForecast = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/forecasts" -Method POST -Headers $headers -Body $forecastData
        Write-Host "✓ Forecast created: $($newForecast._id)" -ForegroundColor Green
        Write-Host "   Status: $($newForecast.status)" -ForegroundColor Gray
        Write-Host "   Total Quantity: $($newForecast.totalQuantity)" -ForegroundColor Gray
        $forecastId = $newForecast._id
    } catch {
        Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   Response: $($_.Exception.Response)" -ForegroundColor Red
        $forecastId = $null
    }
}

# 9. Update forecast
if ($forecastId) {
    Write-Host "`n9. Updating forecast..." -ForegroundColor Yellow
    $updateData = @{
        monthlyForecasts = @(
            @{ month = "2025-12"; quantity = 150 }
            @{ month = "2026-01"; quantity = 170 }
            @{ month = "2026-02"; quantity = 180 }
        )
        notes = "Updated forecast via API"
    } | ConvertTo-Json -Depth 10
    try {
        $updatedForecast = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/forecasts/$forecastId" -Method PUT -Headers $headers -Body $updateData
        Write-Host "✓ Forecast updated" -ForegroundColor Green
        Write-Host "   Total Quantity: $($updatedForecast.totalQuantity)" -ForegroundColor Gray
    } catch {
        Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 10. Submit forecast
if ($forecastId) {
    Write-Host "`n10. Submitting forecast..." -ForegroundColor Yellow
    try {
        $submitResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/forecasts/$forecastId/submit" -Method POST -Headers $headers
        Write-Host "✓ Forecast submitted: $($submitResponse.message)" -ForegroundColor Green
        Write-Host "   Status: $($submitResponse.forecast.status)" -ForegroundColor Gray
    } catch {
        Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   Details: $($_.Exception.Response)" -ForegroundColor Red
    }
}

# 11. Download template
if ($activeCycleId) {
    Write-Host "`n11. Downloading template..." -ForegroundColor Yellow
    try {
        $template = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/forecasts/cycle/$activeCycleId/template" -Method GET -Headers $headers
        Write-Host "✓ Template downloaded: $($template.Headers.'Content-Length') bytes" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 12. Export forecasts
if ($activeCycleId) {
    Write-Host "`n12. Exporting forecasts..." -ForegroundColor Yellow
    try {
        $export = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/forecasts/cycle/$activeCycleId/export" -Method GET -Headers $headers
        Write-Host "✓ Export downloaded: $($export.Headers.'Content-Length') bytes" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 13. Close cycle
if ($testCycleId) {
    Write-Host "`n13. Closing cycle..." -ForegroundColor Yellow
    try {
        $closeResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sop/cycles/$testCycleId/status" -Method PUT `
            -Headers $headers -Body '{"status":"CLOSED"}'
        Write-Host "✓ Cycle closed: $($closeResponse.message)" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== TEST COMPLETE ===" -ForegroundColor Cyan

