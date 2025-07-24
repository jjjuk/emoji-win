# 🍎 emoji-win <release-version> - Beautiful iOS <ios-version> Apple Emojis for Windows 11

**Tired of boring Windows 11 emojis?** Transform your Windows experience with beautiful, expressive Apple emojis from iOS <ios-version>!

## 🎉 What's Included

### Ready-to-Install Font
- **`AppleColorEmojiForWindows.ttf`** - Pre-converted iOS <ios-version> Apple Color Emoji font
- **Fully Windows 11 compatible** - No more "file is not a font" errors
- **1,400+ emoji characters** - All the latest iOS <ios-version> emojis working perfectly
- **High quality** - Rich colors, detailed designs, expressive characters

### Installation Tools
- **`windows_font_manager.bat`** - Automated Windows font manager with auto-elevation
- **Complete backup system** - Safe installation with easy restoration
- **Smart font detection** - Automatically finds font in fonts folder
- **One-click process** - INSTALL backs up + installs, RESTORE brings back Windows emojis

## � Super Quick Installation

### Option 1: Automated (Recommended)
1. **Download** `emoji-win-<release-version>-ios-<ios-version>.zip` and **extract all files** 
4. Go to to **extracted directory** and **Double-click** `windows_font_manager.bat` (auto-elevates to admin)
5. **Choose option 1** (INSTALL) - font auto-detected from fonts folder
6. **Restart Windows** - Enjoy beautiful Apple emojis! 🎨

### Option 2: Manual Installation
```cmd
# Create backup directory
mkdir C:\FontBackup

# Backup original font and registry
copy "C:\Windows\Fonts\seguiemj.ttf" "C:\FontBackup\seguiemj_original.ttf"
reg export "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "C:\FontBackup\fonts_registry_backup.reg"

# Install Apple emojis
copy "AppleColorEmojiForWindows.ttf" "C:\Windows\Fonts\seguiemj.ttf"
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Segoe UI Emoji (TrueType)" /t REG_SZ /d "seguiemj.ttf" /f

# Clear font cache and restart
del /q /s "%windir%\ServiceProfiles\LocalService\AppData\Local\FontCache\*"
shutdown /r /t 0
```

## 🔄 Easy Restoration

To go back to Windows emojis:
1. **Double-click** `windows_font_manager.bat`
2. **Choose option 2** (RESTORE)
3. **Restart Windows**

## ✨ Before vs After

| Windows 11 Default | iOS <ios-version> Apple |
|-------------------|-----------------|
| 😐 Flat, boring | 😍 Rich, expressive |
| 🎨 Limited colors | 🌈 Vibrant details |
| 📱 Outdated design | ✨ Modern, beautiful |

## 🛡️ Safety Features

- ✅ **Automatic admin elevation** - No need to right-click "Run as administrator"
- ✅ **Smart font detection** - Finds font in fonts folder automatically
- ✅ **Automatic backup** of original Windows font and registry
- ✅ **Font cache clearing** for proper rendering
- ✅ **Easy restoration** - one click back to Windows emojis
- ✅ **Error handling** - Clear messages if font file missing

## 📁 Required Folder Structure

```
Your Installation Folder/
├── windows_font_manager.bat
└── fonts/
    └── AppleColorEmojiForWindows.ttf
```

## 📋 System Requirements

- **Windows 11** (latest version recommended)
- **~25MB free space** for font file and backups
- **Administrator privileges** (automatically requested)

## 🎯 Perfect For

- 🎨 **Designers** who want consistent emoji appearance
- 💬 **Content creators** who need expressive emojis
- 📱 **iPhone/Mac users** who want familiar emojis on Windows
- 👥 **Anyone** tired of Windows' bland emoji design

## ⚠️ Important Notes

- **Experimental software** - Always backup your system before installation
- **iOS <ios-version> source** - Latest Apple emoji designs as of 2024
- **Personal use** - This conversion is intended for personal use
- **99% AI-generated** - This project was created using Vibe/Claude AI

## 🔧 Technical Details

- **Font format**: TrueType (.ttf)
- **Color support**: Full CBDT/CBLC bitmap color
- **Character count**: 1,494 emoji characters
- **Windows compatibility**: Mimics Segoe UI Emoji structure
- **File size**: ~24MB
- **Auto-elevation**: PowerShell Start-Process with RunAs

## 🙏 Acknowledgments

- **[apple-emoji-linux](https://github.com/samuelngs/apple-emoji-linux)** - For making Apple emojis accessible on non-Apple platforms
- **iOS <ios-version> emoji designs** - Created by Apple Inc.

## 📞 Support

Having issues? Check the troubleshooting guide in the repository or open an issue at https://github.com/jjjuk/emoji-win/issues

---

**Disclaimer**: This tool is for personal use and educational purposes. Apple Color Emoji is proprietary to Apple Inc. Users are responsible for ensuring they have appropriate rights to use the font. This is experimental software - use at your own risk and always backup your system fonts.
