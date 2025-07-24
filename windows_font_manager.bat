@echo off
REM emoji-win - Windows Font Manager
REM Get beautiful Apple emojis on Windows 11
REM Run as Administrator!

setlocal enabledelayedexpansion

echo =======================================
echo emoji-win - Windows Font Manager
echo =======================================
echo.
echo WARNING: This is experimental software!
echo Always backup your system before proceeding.
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

:MENU
echo.
echo Select an option:
echo 1. BACKUP - Backup original font and install converted Apple emoji font
echo 2. RESTORE - Restore original Windows emoji font
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto BACKUP
if "%choice%"=="2" goto RESTORE
if "%choice%"=="3" goto EXIT
echo Invalid choice. Please try again.
goto MENU

:BACKUP
echo.
echo === BACKUP ORIGINAL FONT AND INSTALL CONVERTED FONT ===
echo.

REM Step 1: Create backup
echo Step 1: Creating backup...
if not exist "C:\FontBackup" mkdir "C:\FontBackup"

if exist "C:\Windows\Fonts\seguiemj.ttf" (
    copy "C:\Windows\Fonts\seguiemj.ttf" "C:\FontBackup\seguiemj_original.ttf" >nul
    echo ✓ Font file backed up to C:\FontBackup\seguiemj_original.ttf
) else (
    echo ⚠ Original font file not found!
)

reg export "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "C:\FontBackup\fonts_registry_backup.reg" >nul 2>&1
if %errorLevel% equ 0 (
    echo ✓ Registry backed up to C:\FontBackup\fonts_registry_backup.reg
) else (
    echo ⚠ Failed to backup registry
)

echo.
REM Step 2: Install converted font
echo Step 2: Installing converted font...
set /p fontpath="Enter path to your converted SegoeUIEmoji.ttf: "

if not exist "%fontpath%" (
    echo ERROR: Font file not found: %fontpath%
    goto MENU
)

echo.
echo Removing original font...
if exist "C:\Windows\Fonts\seguiemj.ttf" (
    takeown /f "C:\Windows\Fonts\seguiemj.ttf" >nul 2>&1
    icacls "C:\Windows\Fonts\seguiemj.ttf" /grant administrators:F >nul 2>&1
    del "C:\Windows\Fonts\seguiemj.ttf" >nul 2>&1
    if %errorLevel% equ 0 (
        echo ✓ Original font removed
    ) else (
        echo ⚠ Failed to remove original font
    )
)

reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)" /f >nul 2>&1

echo.
echo Installing converted font...
copy "%fontpath%" "C:\Windows\Fonts\seguiemj.ttf" >nul
if %errorLevel% equ 0 (
    echo ✓ Font file installed
) else (
    echo ⚠ Failed to install font file
    goto MENU
)

reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)" /t REG_SZ /d "seguiemj.ttf" /f >nul
if %errorLevel% equ 0 (
    echo ✓ Registry updated
) else (
    echo ⚠ Failed to update registry
)

REM Step 3: Clear font cache
echo.
echo Step 3: Clearing font cache...
del /q /s "%windir%\ServiceProfiles\LocalService\AppData\Local\FontCache\*" >nul 2>&1
del /q /s "%windir%\System32\FNTCACHE.DAT" >nul 2>&1
echo ✓ Font cache cleared

echo.
echo ✅ BACKUP AND INSTALLATION COMPLETED!
echo Files backed up to C:\FontBackup\
echo Apple emoji font installed successfully!
echo.
echo ⚠ IMPORTANT: Please restart Windows for changes to take effect.
goto MENU



:RESTORE
echo.
echo === RESTORE ORIGINAL FONT AND CLEAR CACHE ===
echo.

if not exist "C:\FontBackup\seguiemj_original.ttf" (
    echo ERROR: Backup file not found!
    echo Please ensure you have run BACKUP first to create the backup.
    goto MENU
)

echo Step 1: Removing converted font...
if exist "C:\Windows\Fonts\seguiemj.ttf" (
    del "C:\Windows\Fonts\seguiemj.ttf" >nul 2>&1
    echo ✓ Converted font removed
)

reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)" /f >nul 2>&1

echo.
echo Step 2: Restoring original font...
copy "C:\FontBackup\seguiemj_original.ttf" "C:\Windows\Fonts\seguiemj.ttf" >nul
if %errorLevel% equ 0 (
    echo ✓ Original font restored
) else (
    echo ⚠ Failed to restore font file
    goto MENU
)

if exist "C:\FontBackup\fonts_registry_backup.reg" (
    reg import "C:\FontBackup\fonts_registry_backup.reg" >nul 2>&1
    if %errorLevel% equ 0 (
        echo ✓ Registry restored
    ) else (
        echo ⚠ Failed to restore registry
    )
) else (
    reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)" /t REG_SZ /d "seguiemj.ttf" /f >nul
    echo ✓ Registry entry recreated
)

echo.
echo Step 3: Clearing font cache...
del /q /s "%windir%\ServiceProfiles\LocalService\AppData\Local\FontCache\*" >nul 2>&1
del /q /s "%windir%\System32\FNTCACHE.DAT" >nul 2>&1
echo ✓ Font cache cleared

echo.
echo ✅ RESTORATION COMPLETED!
echo Original Windows emoji font restored successfully!
echo.
echo ⚠ IMPORTANT: Please restart Windows for changes to take effect.
goto MENU



:EXIT
echo.
echo Thank you for using emoji-win!
echo Remember: This is experimental software - always keep backups!
pause
exit /b 0
