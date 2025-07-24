# emoji-win <emoji-wi-version> - iOS <ios-version> Apple Emojis for Windows 11

## ⚠️ LEGAL DISCLAIMER

**Apple Color Emoji is proprietary to Apple Inc.** The converted font referenced below is provided for educational purposes only. Users must:

- Own a legal license to Apple Color Emoji (e.g., own an iOS/macOS device)
- Use for personal, non-commercial purposes only
- Understand this is experimental software

## 📥 Installation Instructions

### Quick Install (Windows 11)

1. **Download** `AppleColorEmojiForWindows.ttf`
2. **Download** `windows_font_manager.bat`
3. **Run** `windows_font_manager.bat` as Administrator
4. **Choose** option 1 (BACKUP) and provide the path to downloaded font
5. **Restart** Windows

### Manual Installation

```cmd
# 1. Backup original (IMPORTANT!)
copy "C:\Windows\Fonts\seguiemj.ttf" "C:\FontBackup\seguiemj_original.ttf"

# 2. Install converted font
copy "AppleEmojiForWindows.ttf" "C:\Windows\Fonts\seguiemj.ttf"

# 3. Update registry
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)" /t REG_SZ /d "seguiemj.ttf" /f

# 4. Restart Windows
```

## 🔄 Restoration

To restore original Windows emojis:

1. Run `windows_font_manager.bat` as Administrator
2. Choose option 2 (RESTORE)
3. Restart Windows

## 🛡️ Safety Notes

- **Always backup** your original font before installation
- **Create system restore point** before making changes
- **This is experimental** - use at your own risk
- **Test in safe mode** if you encounter issues

## 📱 What You Get

- 🎨 **Beautiful iOS <ios-version> emojis** instead of bland Windows ones
- 🌈 **Rich colors and details** that match Apple devices
- 😍 **1,400+ emoji characters** fully working on Windows
- 🔄 **Easy restoration** back to Windows emojis

---

**Legal Notice:** This release references a converted font file. Users are responsible for ensuring they have legal rights to use Apple Color Emoji. This tool is for personal use only.
