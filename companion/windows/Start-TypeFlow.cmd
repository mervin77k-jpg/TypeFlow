@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 typeflow_companion.py
) else (
  python typeflow_companion.py
)
if errorlevel 1 (
  echo TypeFlow Companion requires Python 3.10 or newer with Tkinter.
  echo Install Python from https://www.python.org/downloads/windows/ then run this file again.
  pause
)
