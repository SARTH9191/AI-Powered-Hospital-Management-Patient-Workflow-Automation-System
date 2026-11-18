# Quick State Persistence Test
Write-Host "=== STATE PERSISTENCE QUICK TEST ===" -ForegroundColor Cyan

# 1. Get token
Write-Host "`n[1/5] Getting auth token..." -ForegroundColor Yellow
try {
    $token = (Invoke-RestMethod -Uri "http://127.0.0.1:8000/token" -Method Post -Body @{username="admin"; password="admin123"} -ContentType "application/x-www-form-urlencoded").access_token
    Write-Host "✅ Token obtained: $($token.Substring(0,20))..." -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to get token: $_" -ForegroundColor Red
    exit 1
}

# 2. Start workflow
Write-Host "`n[2/5] Starting test workflow..." -ForegroundColor Yellow
$headers = @{Authorization="Bearer $token"}
$patientData = @{
    name = "Quick Test Patient"
    age = 35
    gender = "Male"
    phone = "+1234567890"
    email = "quicktest@hospital.com"
    current_symptoms = "Quick state persistence test"
    has_insurance = $true
    insurance_provider = "Test Insurance"
} | ConvertTo-Json

try {
    $workflow = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/workflow/start" -Method Post -Headers $headers -Body $patientData -ContentType "application/json"
    Write-Host "✅ Workflow started" -ForegroundColor Green
    Write-Host "   Patient ID: $($workflow.patient_id)" -ForegroundColor Cyan
    Write-Host "   Current Stage: $($workflow.current_stage)" -ForegroundColor Cyan
    Write-Host "   Status: $($workflow.status)" -ForegroundColor Cyan
    $patientId = $workflow.patient_id
} catch {
    Write-Host "❌ Failed to start workflow: $_" -ForegroundColor Red
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 3. Check state file
Write-Host "`n[3/5] Checking state file..." -ForegroundColor Yellow
if (Test-Path "data/workflow_states.json") {
    Write-Host "✅ State file exists" -ForegroundColor Green
    try {
        $jsonContent = Get-Content "data/workflow_states.json" -Raw
        $states = $jsonContent | ConvertFrom-Json
        if ($states.PSObject.Properties.Name -contains $patientId) {
            Write-Host "✅ Patient state saved in file" -ForegroundColor Green
            $savedState = $states.$patientId
            Write-Host "   Last Saved: $($savedState.last_saved)" -ForegroundColor Cyan
            Write-Host "   Current Stage: $($savedState.current_stage)" -ForegroundColor Cyan
            Write-Host "   Completed: $($savedState.workflow_completed)" -ForegroundColor Cyan
        } else {
            Write-Host "⚠️ Patient state not found in file" -ForegroundColor Yellow
            Write-Host "   Available patients: $($states.PSObject.Properties.Name -join ', ')" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Error parsing JSON file: $_" -ForegroundColor Red
        Write-Host "   The file may contain malformed JSON" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ State file not found at data/workflow_states.json" -ForegroundColor Red
}

# 4. Get status
Write-Host "`n[4/5] Getting workflow status via API..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/workflow/status/$patientId" -Headers $headers
    Write-Host "✅ Status retrieved successfully" -ForegroundColor Green
    Write-Host "   Patient ID: $($status.patient_id)" -ForegroundColor Cyan
    Write-Host "   Current Stage: $($status.current_stage)" -ForegroundColor Cyan
    Write-Host "   Last Saved: $($status.last_saved)" -ForegroundColor Cyan
    Write-Host "   Workflow Completed: $($status.workflow_completed)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to get status: $_" -ForegroundColor Red
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. List workflows
Write-Host "`n[5/5] Listing all workflows..." -ForegroundColor Yellow
try {
    $all = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/workflow/list" -Headers $headers
    if ($all.workflows) {
        Write-Host "✅ Found $($all.workflows.Count) workflow(s)" -ForegroundColor Green
        foreach ($wf in $all.workflows) {
            Write-Host "   - $($wf.patient_id): $($wf.current_stage)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "⚠️ No workflows found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to list workflows: $_" -ForegroundColor Red
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== TEST RESULTS SUMMARY ===" -ForegroundColor Cyan
Write-Host "Test Patient ID: $patientId" -ForegroundColor White
Write-Host "`nYou can use this ID for further testing:" -ForegroundColor Yellow
Write-Host "  Resume: Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/workflow/resume/$patientId' -Method Post -Headers @{Authorization='Bearer $token'}" -ForegroundColor Gray
Write-Host "  Delete: Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/workflow/$patientId' -Method Delete -Headers @{Authorization='Bearer $token'}" -ForegroundColor Gray
Write-Host "`n=== TEST COMPLETE ===" -ForegroundColor Cyan
