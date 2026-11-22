@echo off
REM ==============================================================================
REM Automated Business Performance Dashboard - Scheduled Task Runner
REM Designed for Windows Task Scheduler execution
REM ==============================================================================

setlocal enabledelayedexpansion

REM Set project directory (parent of scripts folder)
set "PROJECT_DIR=%~dp0.."
cd /d "%PROJECT_DIR%"

echo [INFO] Running Automated Retail Data Pipeline at %DATE% %TIME%
echo [INFO] Working Directory: %PROJECT_DIR%

REM Run Python Pipeline
python python/automated_pipeline.py

set EXIT_CODE=%ERRORLEVEL%
if %EXIT_CODE% EQU 0 (
    echo [SUCCESS] Pipeline completed successfully.
) else (
    echo [ERROR] Pipeline failed with exit code %EXIT_CODE%. Check logs\pipeline.log for details.
)

exit /b %EXIT_CODE%
