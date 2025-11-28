# Git Automation Workflow

## 📋 Complete Workflow

### Step 1: Clone Repository
```
User Action: Enter repository URL and click "Clone"
System Action: 
  - Clones repo to cloned_repos/
  - Loads files
  - Checks git status
Result: Files shown, 0 changes
```

### Step 2: Select & View File
```
User Action: Click on a file in the file explorer
System Action:
  - Loads file content from cloned repo
  - Displays in code editor
Result: File content shown in center panel
```

### Step 3: Edit File
```
User Action: Type changes in the code editor
System Action: 
  - Updates fileContent state
  - No save yet
Result: Content changed but not saved
```

### Step 4: Save File ⭐ (Auto Git Detection)
```
User Action: Click "💾 Save" button
System Action:
  1. Saves file to cloned repo
  2. Shows "File saved!" notification
  3. Automatically refreshes git status (after 500ms)
  4. Git detects the change
Result: 
  - File saved to disk
  - Git status updates automatically
  - Shows "M filename" in Changes panel
  - Change count increases
```

### Step 5: Stage Changes
```
User Action: Click "📦 Stage All Changes"
System Action:
  - Runs: git add . (in cloned repo)
  - Refreshes git status
Result: Changes staged for commit
```

### Step 6: Generate Commit Message
```
User Action: Click "✨ Generate Commit Message"
System Action:
  1. Gets git diff from cloned repo
  2. Finds similar commits (RAG)
  3. Sends to Groq LLM
  4. Generates commit message
Result: AI-generated message appears in text box
```

### Step 7: Commit
```
User Action: Click "✅ Commit"
System Action:
  - Runs: git commit -m "message" (in cloned repo)
  - Refreshes git status
Result: 
  - Changes committed
  - Git status shows 0 changes
```

### Step 8: Push
```
User Action: Click "🚀 Push to Remote"
System Action:
  - Gets current branch
  - Runs: git push origin branch (in cloned repo)
Result: Changes pushed to GitHub/GitLab
```

---

## 🔄 Auto-Refresh Features

### 1. After Save (Immediate)
```
Save File → Wait 500ms → Refresh Git Status
```

### 2. Periodic Refresh (Every 3 seconds)
```
While repo is loaded → Check git status every 3s
```

### 3. Manual Refresh
```
Click 🔄 button in Git panel header → Refresh immediately
```

### 4. After Git Operations
```
Stage → Refresh
Commit → Refresh
```

---

## 📊 Git Status Display

### Status Codes
- **M** = Modified (file changed)
- **A** = Added (new file)
- **D** = Deleted (file removed)
- **??** = Untracked (not in git)

### Example Display
```
Changes (3)
┌─────────────────┐
│ M  src/app.py   │  ← Modified existing file
│ A  new_file.py  │  ← New file added
│ M  README.md    │  ← Modified existing file
└─────────────────┘
```

---

## 🎯 Expected Behavior Timeline

```
Time    Action                  Git Status
────────────────────────────────────────────
0:00    Clone repo              Changes (0)
0:05    Select file             Changes (0)
0:10    Edit file               Changes (0)  ← Not saved yet
0:15    Click Save              Changes (0)  ← Saving...
0:16    Auto-refresh            Changes (1)  ← ✅ Detected!
0:20    Edit another file       Changes (1)
0:25    Click Save              Changes (1)  ← Saving...
0:26    Auto-refresh            Changes (2)  ← ✅ Detected!
0:30    Click Stage All         Changes (2)  ← Staged
0:35    Click Generate          Changes (2)  ← Generating...
0:40    Message generated       Changes (2)  ← Ready to commit
0:45    Click Commit            Changes (2)  ← Committing...
0:46    Auto-refresh            Changes (0)  ← ✅ Committed!
0:50    Click Push              Changes (0)  ← Pushing...
0:55    Push complete           Changes (0)  ← ✅ Done!
```

---

## 🐛 Troubleshooting

### Problem: Changes not showing after save

**Check:**
1. Is the file saved? (Look for notification)
2. Wait 1-2 seconds for auto-refresh
3. Click 🔄 button to manually refresh
4. Check if you're in the cloned repo

**Solution:**
```javascript
// Auto-refresh is set to 500ms after save
// If not working, try manual refresh
```

### Problem: Wrong files showing in git status

**Check:**
1. Are you seeing files from your project? (WRONG)
2. Should only see files from cloned repo (CORRECT)

**Solution:**
```bash
# Restart with fresh state
start_fresh.bat
```

### Problem: Git status not updating

**Check:**
1. Is auto-refresh enabled? (Should refresh every 3s)
2. Is the backend running?
3. Check browser console for errors

**Solution:**
```javascript
// Check if useEffect is running
// Should see periodic API calls to /api/git/status
```

---

## ✅ Success Indicators

You'll know it's working when:

1. **After Save:**
   - ✅ "File saved!" notification appears
   - ✅ Git status updates within 1 second
   - ✅ File appears in Changes list with "M" badge

2. **Auto-Refresh:**
   - ✅ Changes count updates automatically
   - ✅ No need to manually refresh
   - ✅ Can see changes appear in real-time

3. **After Commit:**
   - ✅ Changes count goes to 0
   - ✅ "No changes" message appears
   - ✅ Ready for next edit

---

## 🎬 Demo Scenario

### Complete Example: Fix a Bug

```
1. Clone: https://github.com/your-username/test-repo.git
   → Files loaded, Changes (0)

2. Click: src/app.py
   → File content shown

3. Edit: Fix a bug in the code
   → Content changed

4. Click: 💾 Save
   → "File saved!" notification
   → Wait 1 second
   → Changes (1) appears
   → Shows "M src/app.py"

5. Click: 📦 Stage All Changes
   → "Changes staged!" notification

6. Click: ✨ Generate Commit Message
   → AI generates: "fix: correct validation logic in app.py"

7. Review message, then Click: ✅ Commit
   → "Committed successfully!" notification
   → Changes (0)

8. Click: 🚀 Push to Remote
   → "Pushed to origin/main!" notification
   → Done! ✅
```

---

**The entire workflow is now automated - just edit, save, and let the system handle the rest!** 🚀
