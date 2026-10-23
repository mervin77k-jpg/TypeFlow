@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Setup-TypeFlow.ps1"
if errorlevel 1 (
  echo TypeFlow could not start. See the message above for help.
  pause
)
