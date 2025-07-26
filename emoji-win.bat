@echo off
REM Root-level batch script for emoji-win CLI on Windows
REM
REM This script allows running emoji-win commands from the project root directory
REM using uv without needing to cd into the converter\ subdirectory.
REM
REM Usage from project root:
REM   emoji-win.bat convert input.ttf output.ttf
REM   emoji-win.bat diagnose font.ttf
REM   emoji-win.bat analyze font.ttf
REM
REM Author: jjjuk
REM License: MIT

setlocal

REM Get the directory where this script is located (project root)
set "SCRIPT_DIR=%~dp0"
set "CONVERTER_DIR=%SCRIPT_DIR%converter"

REM Check if converter directory exists
if not exist "%CONVERTER_DIR%" (
    echo ❌ Error: converter\ directory not found.
    echo Make sure you're running this from the project root.
    exit /b 1
)

REM Change to converter directory
cd /d "%CONVERTER_DIR%"

REM Check if uv is available
where uv >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: uv is not installed or not in PATH.
    echo Please install uv or use: python ..\emoji-win.py instead
    exit /b 1
)

REM Run the emoji-win CLI with all passed arguments
uv run python -m emoji_win %*
