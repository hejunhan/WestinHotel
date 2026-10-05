@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Tools\Verify-And-Launch.ps1" -Launch
if errorlevel 1 pause
