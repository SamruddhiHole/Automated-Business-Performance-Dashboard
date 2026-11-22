<#
.SYNOPSIS
    Schedules the Automated Retail Business Pipeline in Windows Task Scheduler.

.DESCRIPTION
    Creates a scheduled task named "AutomatedRetailPipeline" that runs daily at 02:00 AM
    (or custom time) using python/automated_pipeline.py.
    
.EXAMPLE
    .\schedule_task.ps1 -Time "03:00"
#>

param(
    [string]$TaskName = "AutomatedRetailPipeline",
    [string]$Time = "02:00",
    [switch]$RunNow,
    [switch]$Remove
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Resolve-Path (Join-Path $scriptDir "..")
$pythonExe = (Get-Command python.exe -ErrorAction SilentlyContinue).Source

if (-not $pythonExe) {
    Write-Error "Python executable not found in system PATH. Please ensure Python is installed and added to PATH."
    exit 1
}

$pipelineScript = Join-Path $projectDir "python\automated_pipeline.py"

if ($Remove) {
    Write-Host "[INFO] Unregistering scheduled task '$TaskName'..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "[SUCCESS] Task '$TaskName' removed successfully." -ForegroundColor Green
    exit 0
}

if ($RunNow) {
    Write-Host "[INFO] Executing pipeline immediately..." -ForegroundColor Cyan
    Set-Location $projectDir
    & $pythonExe $pipelineScript
    exit $LASTEXITCODE
}

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "WINDOWS TASK SCHEDULER SETUP: $TaskName" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Project Directory: $projectDir"
Write-Host "Python Path      : $pythonExe"
Write-Host "Script           : $pipelineScript"
Write-Host "Scheduled Daily  : $Time"
Write-Host ""

$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$pipelineScript`"" -WorkingDirectory $projectDir
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "Daily Automated Business Performance Dashboard pipeline execution" -Force

Write-Host "[SUCCESS] Scheduled task '$TaskName' registered successfully!" -ForegroundColor Green
Write-Host "To run task immediately: .\schedule_task.ps1 -RunNow"
Write-Host "To delete task         : .\schedule_task.ps1 -Remove"
