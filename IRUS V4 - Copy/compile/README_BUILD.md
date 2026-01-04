# IRUS V4 - Protected Build System

This build system creates a protected, standalone executable from your IRUS V4 Python script.

## 🛡️ Protection Features Applied

- **Anti-debugging protection** - Detects and prevents common debugging tools
- **Virtual machine detection** - Exits if running in VM environments
- **String obfuscation** - Encodes sensitive strings to prevent easy reading
- **Code obfuscation** - Makes the code structure harder to understand
- **Runtime integrity checks** - Verifies the application hasn't been tampered with
- **Single executable packaging** - No need for Python installation on target machines
- **Optional UPX compression** - Reduces file size and adds another protection layer

## 🚀 Quick Start

### Method 1: Use the Batch File (Easiest)
1. Double-click `build.bat`
2. Wait for the build to complete
3. Find your executable in the `dist_final` folder

### Method 2: Manual Build
1. Install Python 3.7 or newer
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the build script:
   ```bash
   python build_protected.py
   ```

## 📁 Output

After successful build, you'll find:
- `dist_final/IRUS_V4.exe` - Your protected executable
- `build_protected/` - Temporary build files (can be deleted)

## 🔒 Security Levels

The build script applies multiple protection layers:

1. **Level 1: Basic Obfuscation**
   - Variable name mangling
   - String encoding
   - Dummy code injection

2. **Level 2: Runtime Protection**
   - Anti-debugging checks
   - Process monitoring
   - VM detection

3. **Level 3: Packaging Protection**
   - Compiled bytecode
   - Single executable
   - Optional compression

## 📋 System Requirements

### Build Requirements:
- Windows 10/11
- Python 3.7+
- 2GB free disk space
- Internet connection (for downloading packages)

### Runtime Requirements (for end users):
- Windows 10/11
- No Python installation needed
- ~100MB disk space

## ⚠️ Important Notes

### What This Protects Against:
- ✅ Casual source code viewing
- ✅ Simple decompilation attempts
- ✅ Basic reverse engineering
- ✅ Running in debugging environments
- ✅ Execution in virtual machines

### What It Doesn't Protect Against:
- ❌ Advanced reverse engineering by experts
- ❌ Memory dumps during execution
- ❌ Dedicated crackers with specialized tools

### Legal Protection:
Remember that technical protection should be combined with:
- Copyright notices
- Software licensing agreements
- Terms of service
- Legal enforcement when necessary

## 🔧 Customization

You can modify the protection by editing `build_protected.py`:

- **Increase obfuscation**: Modify the `obfuscate_code()` function
- **Add more anti-debug**: Enhance `add_anti_debug_protection()`
- **Custom packaging**: Modify the PyInstaller spec file generation

## 🐛 Troubleshooting

### Common Issues:

1. **"Python not found"**
   - Install Python from python.org
   - Make sure it's added to PATH

2. **"Module not found" errors**
   - Run: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Build fails**
   - Check antivirus isn't blocking PyInstaller
   - Try running as administrator
   - Disable real-time protection temporarily

4. **Large executable size**
   - Install UPX for compression
   - Consider excluding unused modules

### Getting UPX Compression:
1. Download UPX from https://upx.github.io/
2. Extract upx.exe to your PATH or the project folder
3. Re-run the build script

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Ensure all requirements are installed
3. Try building without protection first to isolate issues
4. Check Windows Defender/antivirus settings

---

**Built with security in mind - Protecting your intellectual property**