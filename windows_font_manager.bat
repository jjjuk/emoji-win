@echo off
REM emoji-win - Windows Font Manager
REM Get beautiful Apple emojis on Windows 11
REM Auto-elevates to Administrator!

setlocal enabledelayedexpansion

REM Check if running as administrator, if not, auto-elevate
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b 0
)

echo =======================================
echo emoji-win - Windows Font Manager
echo =======================================
echo.
echo WARNING: This is experimental software!
echo Always backup your system before proceeding.
echo.

REM Check for AppleColorEmojiForWindows.ttf in fonts folder
set "FONT_FILE=%~dp0fonts\AppleColorEmojiForWindows.ttf"
if exist "%FONT_FILE%" (
    echo [SUCCESS] Found AppleColorEmojiForWindows.ttf in fonts folder
    set "AUTO_FONT_PATH=%FONT_FILE%"
) else (
    echo [ERROR] AppleColorEmojiForWindows.ttf not found in fonts folder!
    echo.
    echo Please ensure AppleColorEmojiForWindows.ttf is placed in the fonts\ directory
    echo relative to this batch file.
    echo.
    echo Expected location: %~dp0fonts\AppleColorEmojiForWindows.ttf
    echo.
    pause
    exit /b 1
)

:MENU
echo.
echo Select an option:
echo 1. INSTALL - Backup original font and install Apple emoji font [fonts\AppleColorEmojiForWindows.ttf]
echo 2. RESTORE - Restore original Windows emoji font
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto RESTORE
if "%choice%"=="3" goto EXIT
echo Invalid choice. Please try again.
goto MENU

:INSTALL
echo.
echo === BACKUP ORIGINAL FONT AND INSTALL CONVERTED FONT ===
echo.

REM Step 1: Create backup
echo Step 1: Creating registry backup (non-destructive approach)...
if not exist "C:\FontBackup" mkdir "C:\FontBackup"

if not exist "C:\FontBackup\fonts_registry_backup.reg" (
    reg export "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "C:\FontBackup\fonts_registry_backup.reg" >nul 2>&1
    if %errorLevel% equ 0 (
        echo [SUCCESS] Registry backed up to C:\FontBackup\fonts_registry_backup.reg
    ) else (
        echo [WARNING] Failed to backup registry
    )
) else (
    echo [INFO] Registry backup already exists, skipping registry backup
)

echo [INFO] Using non-destructive method - original Windows font files remain untouched

echo.
REM Step 2: Install converted font
echo Step 2: Installing converted font...
set "fontpath=%AUTO_FONT_PATH%"
echo Using font: %fontpath%



echo.
echo Installing Apple emoji font (non-destructive method)...

REM Copy our font to Windows Fonts directory with its original name
copy "%fontpath%" "C:\Windows\Fonts\AppleColorEmojiForWindows.ttf" >nul 2>&1
set COPY_RESULT=%errorLevel%

if %COPY_RESULT% equ 0 (
    echo [SUCCESS] Apple emoji font copied to Windows Fonts directory
) else (
    echo [ERROR] Cannot copy font file to Windows Fonts directory
    echo.
    echo Possible solutions:
    echo 1. Temporarily disable antivirus software
    echo 2. Run as Administrator ^(right-click batch file^)
    echo 3. Check if font file exists: %fontpath%
    echo 4. Check available disk space
    echo.
    pause
    goto MENU
)

REM Registry redirection - point to our Apple emoji font
echo Redirecting Windows emoji font to Apple emojis...

REM Main font registration - redirect Segoe UI Emoji to our Apple font
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)" /t REG_SZ /d "AppleColorEmojiForWindows.ttf" /f >nul

REM Additional font name variations for broader app compatibility
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji Regular (TrueType)" /t REG_SZ /d "AppleColorEmojiForWindows.ttf" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "SegoeUIEmoji (TrueType)" /t REG_SZ /d "AppleColorEmojiForWindows.ttf" /f >nul

if %errorLevel% equ 0 (
    echo [SUCCESS] Registry successfully redirected to Apple emoji font
    echo [INFO] Original Windows font files remain untouched
) else (
    echo [WARNING] Registry update may have failed - some entries might not work
)

REM Step 3: Clear font cache
echo.
echo Step 3: Clearing font cache...
del /q /s "%windir%\ServiceProfiles\LocalService\AppData\Local\FontCache\*" >nul 2>&1
del /q /s "%windir%\System32\FNTCACHE.DAT" >nul 2>&1
echo [SUCCESS] Font cache cleared

echo.
echo [COMPLETED] BACKUP AND INSTALLATION COMPLETED!
echo Files backed up to C:\FontBackup\
echo Apple emoji font installed successfully!
echo.
echo [IMPORTANT] Please restart Windows for changes to take effect.
goto MENU



:RESTORE
echo.
echo === RESTORE ORIGINAL WINDOWS EMOJIS ===
echo.

echo Step 1: Removing Apple emoji font...
if exist "C:\Windows\Fonts\AppleColorEmojiForWindows.ttf" (
    del "C:\Windows\Fonts\AppleColorEmojiForWindows.ttf" >nul 2>&1
    echo [SUCCESS] Apple emoji font removed from Windows Fonts directory
) else (
    echo [WARNING] Apple emoji font not found (may already be removed)
)

if exist "C:\FontBackup\fonts_registry_backup.reg" (
    echo Restoring original registry from backup...
    reg import "C:\FontBackup\fonts_registry_backup.reg" >nul 2>&1
    if %errorLevel% equ 0 (
        echo [SUCCESS] Original registry restored from backup
    ) else (
        echo [WARNING] Failed to restore registry from backup - using default
        reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)" /t REG_SZ /d "seguiemj.ttf" /f >nul
        echo [SUCCESS] Default registry entry recreated
    )
) else (
    echo No registry backup found - recreating default entry...
    reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)" /t REG_SZ /d "seguiemj.ttf" /f >nul

    REM Clean up any additional entries we may have created
    reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji Regular (TrueType)" /f >nul 2>&1
    reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "SegoeUIEmoji (TrueType)" /f >nul 2>&1

    echo [SUCCESS] Default Windows emoji registry restored
)

echo.
echo Step 3: Clearing font cache...
del /q /s "%windir%\ServiceProfiles\LocalService\AppData\Local\FontCache\*" >nul 2>&1
del /q /s "%windir%\System32\FNTCACHE.DAT" >nul 2>&1
echo [SUCCESS] Font cache cleared

echo.
echo [COMPLETED] RESTORATION COMPLETED!
echo Original Windows emoji font restored successfully!
echo.
echo [IMPORTANT] Please restart Windows for changes to take effect.
goto MENU



:EXIT
echo.
echo Thank you for using emoji-win!
echo Remember: This is experimental software - always keep backups!
pause
exit /b 0
