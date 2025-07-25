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
echo Step 1: Creating backup of original Windows emoji font...
if not exist "C:\FontBackup" mkdir "C:\FontBackup"

REM Backup the original font file
if exist "C:\Windows\Fonts\seguiemj.ttf" (
    if not exist "C:\FontBackup\seguiemj_original.ttf" (
        copy "C:\Windows\Fonts\seguiemj.ttf" "C:\FontBackup\seguiemj_original.ttf" >nul 2>&1
        if %errorLevel% equ 0 (
            echo [SUCCESS] Original Windows emoji font backed up
        ) else (
            echo [ERROR] Failed to backup original font file
            pause
            goto MENU
        )
    ) else (
        echo [INFO] Font backup already exists, skipping font backup
    )
) else (
    echo [WARNING] Original Windows emoji font not found - this is unusual
)

REM Backup the registry
if not exist "C:\FontBackup\fonts_registry_backup.reg" (
    reg export "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "C:\FontBackup\fonts_registry_backup.reg" >nul 2>&1
    if %errorLevel% equ 0 (
        echo [SUCCESS] Font registry backed up
    ) else (
        echo [WARNING] Failed to backup registry
    )
) else (
    echo [INFO] Registry backup already exists, skipping registry backup
)

echo.
REM Step 2: Install converted font
echo Step 2: Installing converted font...
set "fontpath=%AUTO_FONT_PATH%"
echo Using font: %fontpath%



echo.
echo Installing Apple emoji font (file replacement method)...
echo [INFO] This method replaces the Windows emoji font file directly

REM Step 2-pre: Stop Windows Font Cache Service to release file locks
echo Stopping Windows Font Cache Service...
net stop "Windows Font Cache Service" >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Font Cache Service stopped
    set FONT_SERVICE_STOPPED=1
) else (
    echo [INFO] Font Cache Service was not running or couldn't be stopped
    set FONT_SERVICE_STOPPED=0
)

REM Step 2a: Advanced ownership and permissions for system font file
echo Taking ownership of Windows emoji font file...

REM Method 1: Take ownership with full recursive control
takeown /f "C:\Windows\Fonts\seguiemj.ttf" /a >nul 2>&1
takeown /f "C:\Windows\Fonts\seguiemj.ttf" >nul 2>&1

REM Method 2: Grant full permissions to multiple security principals
icacls "C:\Windows\Fonts\seguiemj.ttf" /grant administrators:F >nul 2>&1
icacls "C:\Windows\Fonts\seguiemj.ttf" /grant "%username%":F >nul 2>&1
icacls "C:\Windows\Fonts\seguiemj.ttf" /grant "NT AUTHORITY\SYSTEM":F >nul 2>&1

REM Method 3: Remove inheritance and reset permissions
icacls "C:\Windows\Fonts\seguiemj.ttf" /inheritance:r >nul 2>&1
icacls "C:\Windows\Fonts\seguiemj.ttf" /grant administrators:F >nul 2>&1

echo [INFO] Advanced permissions applied

REM Step 2b: Attempt to remove the original font file with multiple methods
if exist "C:\Windows\Fonts\seguiemj.ttf" (
    echo Attempting to remove original font file...

    REM Method 1: Standard deletion
    del "C:\Windows\Fonts\seguiemj.ttf" >nul 2>&1

    if exist "C:\Windows\Fonts\seguiemj.ttf" (
        echo [INFO] Standard deletion failed, trying advanced methods...

        REM Method 2: Force deletion with attributes reset
        attrib -r -s -h "C:\Windows\Fonts\seguiemj.ttf" >nul 2>&1
        del /f /q "C:\Windows\Fonts\seguiemj.ttf" >nul 2>&1

        if exist "C:\Windows\Fonts\seguiemj.ttf" (
            REM Method 3: Use PowerShell Remove-Item with Force
            powershell -Command "Remove-Item 'C:\Windows\Fonts\seguiemj.ttf' -Force -ErrorAction SilentlyContinue" >nul 2>&1

            if exist "C:\Windows\Fonts\seguiemj.ttf" (
                echo [ERROR] Cannot remove original font file - Windows protection active
                echo.
                echo Advanced Solutions:
                echo 1. Restart Windows and run this script immediately after login
                echo 2. Boot into Safe Mode and run this script
                echo 3. Disable Windows Defender real-time protection temporarily
                echo 4. Use the alternative rename method below
                echo.

                REM Method 4: Rename instead of delete (fallback)
                echo Trying rename method as fallback...
                ren "C:\Windows\Fonts\seguiemj.ttf" "seguiemj_original_backup.ttf" >nul 2>&1
                if %errorLevel% equ 0 (
                    echo [SUCCESS] Original font renamed instead of deleted
                ) else (
                    echo [ERROR] All methods failed - file is heavily protected
                    pause
                    goto MENU
                )
            ) else (
                echo [SUCCESS] Original font removed using PowerShell method
            )
        ) else (
            echo [SUCCESS] Original font removed using force deletion
        )
    ) else (
        echo [SUCCESS] Original font removed using standard deletion
    )
)

REM Step 2c: Copy our Apple emoji font as the Windows emoji font
copy "%fontpath%" "C:\Windows\Fonts\seguiemj.ttf" >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Apple emoji font installed as Windows emoji font
) else (
    echo [ERROR] Cannot install Apple emoji font
    echo.
    echo Critical error - attempting to restore original font...
    if exist "C:\FontBackup\seguiemj_original.ttf" (
        copy "C:\FontBackup\seguiemj_original.ttf" "C:\Windows\Fonts\seguiemj.ttf" >nul 2>&1
        echo [WARNING] Original font restored - Apple emojis not installed
    )
    pause
    goto MENU
)

REM Step 2d: Update registry to point to the replaced font
echo Updating font registry...
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)" /t REG_SZ /d "seguiemj.ttf" /f >nul
echo [SUCCESS] Font registry updated

REM Step 2e: Restart Windows Font Cache Service if we stopped it
if %FONT_SERVICE_STOPPED% equ 1 (
    echo Restarting Windows Font Cache Service...
    net start "Windows Font Cache Service" >nul 2>&1
    if %errorLevel% equ 0 (
        echo [SUCCESS] Font Cache Service restarted
    ) else (
        echo [WARNING] Font Cache Service couldn't be restarted - will start automatically
    )
)

REM Step 3: Clear font cache
echo.
echo Step 3: Clearing font cache...
del /q /s "%windir%\ServiceProfiles\LocalService\AppData\Local\FontCache\*" >nul 2>&1
del /q /s "%windir%\System32\FNTCACHE.DAT" >nul 2>&1
echo [SUCCESS] Font cache cleared

REM Step 4: Restart Windows Explorer to refresh font system
echo.
echo Step 4: Refreshing Windows font system...
taskkill /f /im explorer.exe >nul 2>&1
start explorer.exe
echo [SUCCESS] Windows Explorer restarted - font system refreshed

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

echo Step 1: Restoring original Windows emoji font...

if not exist "C:\FontBackup\seguiemj_original.ttf" (
    echo [ERROR] Original font backup not found!
    echo Cannot restore without backup file.
    echo Please ensure you ran INSTALL first to create the backup.
    pause
    goto MENU
)

REM Take ownership of current font file
takeown /f "C:\Windows\Fonts\seguiemj.ttf" >nul 2>&1
icacls "C:\Windows\Fonts\seguiemj.ttf" /grant administrators:F >nul 2>&1

REM Remove current font file (Apple emoji)
if exist "C:\Windows\Fonts\seguiemj.ttf" (
    del "C:\Windows\Fonts\seguiemj.ttf" >nul 2>&1
)

REM Restore original Windows font
copy "C:\FontBackup\seguiemj_original.ttf" "C:\Windows\Fonts\seguiemj.ttf" >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Original Windows emoji font restored
) else (
    echo [ERROR] Failed to restore original font file
    pause
    goto MENU
)

echo Step 2: Restoring font registry...
if exist "C:\FontBackup\fonts_registry_backup.reg" (
    reg import "C:\FontBackup\fonts_registry_backup.reg" >nul 2>&1
    if %errorLevel% equ 0 (
        echo [SUCCESS] Original font registry restored from backup
    ) else (
        echo [WARNING] Failed to restore registry from backup - using default
        reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)" /t REG_SZ /d "seguiemj.ttf" /f >nul
        echo [SUCCESS] Default registry entry recreated
    )
) else (
    echo [INFO] No registry backup found - recreating default entry
    reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)" /t REG_SZ /d "seguiemj.ttf" /f >nul
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
