# Windows Troubleshooting Guide

## 🪟 Common Windows Issues

### Issue 1: "Access is denied" when cloning

**Error:**
```
[WinError 5] Access is denied: 'cloned_repos\repo\.git\objects\pack\...'
```

**Cause:** 
- Git creates readonly files in `.git` folder
- Windows prevents deletion of readonly files
- Previous clone attempt left locked files

**Solutions:**

#### Solution A: Use Cleanup Script (Recommended)
```bash
cleanup_repos.bat
```

This will:
- Remove readonly attributes
- Delete all cloned repos
- Handle Windows permissions properly

#### Solution B: Manual Cleanup
```bash
# Remove readonly attributes
attrib -r -h cloned_repos\*.* /s /d

# Delete folder
rmdir /s /q cloned_repos
```

#### Solution C: Use File Explorer
1. Open File Explorer
2. Navigate to project folder
3. Right-click `cloned_repos` folder
4. Select "Delete"
5. If prompted, click "Continue" or "Try Again"

#### Solution D: Restart and Clean
1. Close all terminals
2. Close VS Code or any IDE
3. Run `cleanup_repos.bat`
4. Start fresh with `start_fresh.bat`

---

### Issue 2: Port Already in Use

**Error:**
```
Address already in use: Port 5000
```

**Solution:**

#### Option A: Kill Process
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

#### Option B: Use Different Port
Edit `api_server.py`:
```python
app.run(debug=True, port=5001)  # Change to 5001
```

---

### Issue 3: Git Not Found

**Error:**
```
'git' is not recognized as an internal or external command
```

**Solution:**

1. **Install Git for Windows:**
   - Download from: https://git-scm.com/download/win
   - Run installer
   - Restart terminal

2. **Add Git to PATH:**
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add: `C:\Program Files\Git\bin`
   - Restart terminal

3. **Verify Installation:**
   ```bash
   git --version
   ```

---

### Issue 4: Python Not Found

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solution:**

1. **Install Python:**
   - Download from: https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation
   - Restart terminal

2. **Try `py` instead:**
   ```bash
   py api_server.py
   py -m pip install -r requirements.txt
   ```

---

### Issue 5: Node/NPM Not Found

**Error:**
```
'npm' is not recognized as an internal or external command
```

**Solution:**

1. **Install Node.js:**
   - Download from: https://nodejs.org/
   - Run installer
   - Restart terminal

2. **Verify Installation:**
   ```bash
   node --version
   npm --version
   ```

---

### Issue 6: Permission Denied on Save

**Error:**
```
Permission denied when saving file
```

**Solution:**

1. **Run as Administrator:**
   - Right-click terminal
   - Select "Run as administrator"
   - Start servers again

2. **Check File Permissions:**
   - Right-click file
   - Properties → Security
   - Ensure you have "Write" permission

---

### Issue 7: CRLF Line Endings Warning

**Warning:**
```
warning: CRLF will be replaced by LF
```

**This is normal on Windows!** Git automatically handles line endings.

**To disable warning:**
```bash
git config --global core.autocrlf true
```

---

### Issue 8: Antivirus Blocking

**Symptoms:**
- Slow cloning
- Files disappearing
- Access denied errors

**Solution:**

1. **Add Exclusion:**
   - Open Windows Security
   - Virus & threat protection
   - Manage settings
   - Add exclusion
   - Add your project folder

2. **Temporarily Disable:**
   - Only if you trust the repositories
   - Re-enable after testing

---

### Issue 9: Long Path Names

**Error:**
```
Filename too long
```

**Solution:**

Enable long paths in Windows:

```bash
# Run as Administrator
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

Or use Group Policy:
1. Run `gpedit.msc`
2. Navigate to: Computer Configuration → Administrative Templates → System → Filesystem
3. Enable "Enable Win32 long paths"

---

### Issue 10: Firewall Blocking

**Symptoms:**
- Cannot clone repositories
- Cannot push to remote
- Network errors

**Solution:**

1. **Allow Python through Firewall:**
   - Windows Security → Firewall
   - Allow an app
   - Add Python and Node.js

2. **Check Proxy Settings:**
   ```bash
   git config --global http.proxy
   git config --global https.proxy
   ```

---

## 🔧 Quick Fixes

### Complete Reset (Nuclear Option)

```bash
# 1. Stop all processes
# Press Ctrl+C in all terminals

# 2. Clean everything
cleanup_repos.bat

# 3. Reinstall dependencies
pip install -r requirements.txt
cd frontend
npm install
cd ..

# 4. Start fresh
start_fresh.bat
```

---

## 🎯 Best Practices for Windows

### 1. Use Short Paths
```
✅ C:\Projects\commit-gen\
❌ C:\Users\YourName\Documents\My Projects\AI Commit Generator\
```

### 2. Close Unnecessary Programs
- Close VS Code when running cleanup
- Close File Explorer in project folder
- Stop all terminals before cleanup

### 3. Run as Administrator (if needed)
- Right-click terminal
- "Run as administrator"
- Only when you get permission errors

### 4. Use Windows Terminal (Recommended)
- Better than CMD
- Supports multiple tabs
- Better Unicode support
- Download from Microsoft Store

### 5. Keep Paths Clean
- No spaces in folder names
- No special characters
- Use forward slashes in code: `cloned_repos/repo`

---

## 📋 Checklist Before Starting

- [ ] Git installed and in PATH
- [ ] Python installed and in PATH
- [ ] Node.js installed and in PATH
- [ ] No old `cloned_repos` folder
- [ ] No processes using ports 5000 or 3000
- [ ] Antivirus exclusion added (optional)
- [ ] Running from short path

---

## 🆘 Still Having Issues?

### Check System Requirements
```bash
# Check Git
git --version

# Check Python
python --version

# Check Node
node --version
npm --version

# Check ports
netstat -ano | findstr :5000
netstat -ano | findstr :3000
```

### Get Detailed Errors
1. Run commands manually to see full errors
2. Check browser console (F12)
3. Check Flask terminal output
4. Check React terminal output

### Common Command Variations
```bash
# If 'python' doesn't work, try:
py api_server.py
python3 api_server.py

# If 'pip' doesn't work, try:
py -m pip install -r requirements.txt
python -m pip install -r requirements.txt
```

---

## ✅ Success Indicators

You'll know everything is working when:

1. **Cleanup runs without errors**
   ```
   ✅ Cleanup completed successfully!
   ```

2. **Flask starts successfully**
   ```
   🚀 AI Commit Generator - Web Interface
   Starting server at http://localhost:5000
   ```

3. **React starts successfully**
   ```
   Compiled successfully!
   Local: http://localhost:3000
   ```

4. **Can clone repositories**
   ```
   Repository cloned successfully
   ```

---

**Most Windows issues are related to file permissions and readonly attributes. The cleanup script should handle 90% of problems!** 🪟
