@echo off
call venv\Scripts\activate.bat
python.exe text_to_speech.py
call venv\Scripts\deactivate.bat