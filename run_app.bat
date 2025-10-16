@echo off
echo Starting Exercise Form Analyzer with Authentication...
echo.

REM Set environment variables for D drive
set PIP_CACHE_DIR=D:\pip_cache
set TMPDIR=D:\temp
set TEMP=D:\temp

REM Activate virtual environment
call "D:\exercise_2_project_updated 2\venv_drive\Scripts\activate.bat"

REM Run the application
python app.py

pause
