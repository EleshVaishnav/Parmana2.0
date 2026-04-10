@echo off
echo Starting Parmana 2.0 Installation...

REM Create virtual environment
python -m venv .venv

REM Activate and install
call .venv\Scripts\activate.bat
pip install -r requirements.txt

REM Copy .env file if it doesn't exist
if not exist .env (
    copy .env.example .env
    echo .env created from template. Make sure to edit it and add your API keys!
)

echo.
echo Installation complete!
echo To start the agent:
echo 1. .venv\Scripts\activate
echo 2. python main.py
