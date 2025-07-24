# 🔧 emoji-win Troubleshooting Guide

## 🎯 Application-Specific Issues

### Telegram Desktop Not Showing Emojis

**Problem**: Telegram Desktop doesn't show Apple emojis in message input or chat.

**Solutions**:

1. **Force Font Cache Refresh**:

   ```cmd
   # Run as Administrator
   net stop "Windows Font Cache Service"
   del /q /s "%windir%\ServiceProfiles\LocalService\AppData\Local\FontCache\*"
   del /q /s "%windir%\System32\FNTCACHE.DAT"
   net start "Windows Font Cache Service"
   ```

2. **Telegram-Specific Fix**:

   - Close Telegram completely
   - Delete Telegram cache: `%appdata%\Telegram Desktop\tdata\emoji`
   - Restart Telegram
   - Go to Settings → Chat Settings → Use system emoji

3. **Registry Font Fallback** (Enhanced in latest version):
   ```cmd
   # These are now automatically added by windows_font_manager.bat
   reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\FontLink\SystemLink" /v "Segoe UI" /t REG_MULTI_SZ /d "seguiemj.ttf,Segoe UI Emoji"
   ```

### Chrome/Edge Browser Issues

**Problem**: Web browsers not showing Apple emojis.

**Solutions**:

1. **Clear browser font cache**:
   - Chrome: `chrome://settings/fonts` → Reset to defaults
   - Edge: `edge://settings/fonts` → Reset to defaults
2. **Force refresh**: `Ctrl + F5` on pages with emojis
3. **Check browser flags**:
   - Chrome: `chrome://flags/#enable-experimental-web-platform-features`
   - Enable "Experimental Web Platform features"

### Microsoft Office Applications

**Problem**: Word, Excel, PowerPoint not showing Apple emojis.

**Solutions**:

1. **Office font settings**:
   - File → Options → Advanced → Show font preview in font list
   - Insert → Symbols → Font: "Segoe UI Emoji"
2. **Clear Office font cache**:
   ```cmd
   del "%localappdata%\Microsoft\Office\16.0\OfficeFileCache\*"
   ```

## 🛠️ General Troubleshooting

### Font Not Recognized at All

**Symptoms**: No applications show Apple emojis, "file is not a font" error.

**Solutions**:

1. **Verify font installation**:

   ```cmd
   dir "C:\Windows\Fonts\seguiemj.ttf"
   reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)"
   ```

2. **Reinstall with enhanced compatibility**:
   - Use latest `windows_font_manager.bat` with enhanced registry entries
   - Ensure font is in `fonts\AppleColorEmojiForWindows.ttf`

### Some Emojis Missing

**Symptoms**: Some emojis show as squares or default Windows emojis.

**Solutions**:

1. **Check font completeness**:
   - Ensure you're using the complete `AppleColorEmojiForWindows.ttf`
   - Verify file size is ~24MB
2. **Unicode range issues**:
   - Some newer emojis might not be in older font versions
   - Try with latest iOS 18.4 font from apple-emoji-linux

### Performance Issues

**Symptoms**: Slow emoji rendering, system lag.

**Solutions**:

1. **Font cache optimization**:
   ```cmd
   # Clear and rebuild font cache
   sfc /scannow
   dism /online /cleanup-image /restorehealth
   ```
2. **Reduce font cache size**:
   - Restart Windows after font installation
   - Avoid installing multiple emoji fonts simultaneously

## 🔄 Complete Reset Procedure

If nothing works, try this complete reset:

1. **Remove all emoji fonts**:

   ```cmd
   # Run windows_font_manager.bat → Option 2 (RESTORE)
   ```

2. **Clean system font cache**:

   ```cmd
   net stop "Windows Font Cache Service"
   del /q /s "%windir%\ServiceProfiles\LocalService\AppData\Local\FontCache\*"
   del /q /s "%windir%\System32\FNTCACHE.DAT"
   net start "Windows Font Cache Service"
   ```

3. **Restart Windows**

4. **Reinstall with latest version**:
   ```cmd
   # Run windows_font_manager.bat → Option 1 (INSTALL)
   ```

## 📱 Application-Specific Settings

### Enable System Emojis in Apps

Many applications have settings to use system emojis:

- **Telegram**: Settings → Chat Settings → Use system emoji
- **Discord**: Settings → Text & Images → Show emoji reactions
- **Slack**: Preferences → Messages & media → Emoji style → System
- **WhatsApp Desktop**: Settings → Chats → Emoji style → System default

## 🆘 Still Having Issues?

1. **Check Windows version**: Ensure you're on Windows 11 (latest version recommended)
2. **Verify admin rights**: All font operations require administrator privileges
3. **Antivirus interference**: Temporarily disable antivirus during installation
4. **System file integrity**: Run `sfc /scannow` to check for system file corruption
5. **Create GitHub issue**: Report specific application and symptoms at https://github.com/jjjuk/emoji-win/issues

## 📋 Diagnostic Information

When reporting issues, please include:

- Windows version (`winver`)
- Application name and version
- Font file size and location
- Registry entries present
- Error messages or screenshots
