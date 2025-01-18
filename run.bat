@echo off
call venv\Scripts\activate.bat
python.exe text_to_speech.py
set ERRORLEVEL_PYTHON=%ERRORLEVEL%
call venv\Scripts\deactivate.bat
exit /b %ERRORLEVEL_PYTHON%