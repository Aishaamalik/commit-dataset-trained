# Expected Behavior - AI Commit Generator

## ✅ Correct Behavior

### Before Cloning a Repository

**What you should see:**

```
┌─────────────────────────────────────┐
│   🤖 AI Commit Generator            │
│   Enter a Git repository URL        │
│                                     │
│   [Input Box]                       │
│   [📥 Clone Repository Button]      │
│                                     │
│   Examples:                         │
│   • github.com/facebook/react       │
└─────────────────────────────────────┘
```

**Git Panel:** Should show 0 changes
**File Explorer:** Should be empty or show nothing

---

### After Cloning a Repository

**Example: Clone `https://github.com/octocat/Hello-World.git`**

**What you should see:**

```
┌──────────────────────────────────────────────────────────┐
│ 🤖 AI Commit Generator    📦 Hello-World    0 changes    │
├──────────────┬───────────────────────┬──────────────────┤
│ 📂 Files     │   Code Editor         │   🔄 Git Panel   │
│              │                       │                  │
│ 📝 README    │   [Select a file]     │   Changes (0)    │
│              │                       │   No changes     │
└──────────────┴───────────────────────┴──────────────────┘
```

**File Explorer (Left):**
- Shows files from `cloned_repos/Hello-World/`
- NOT from your current project
- Should see: README, etc.

**Git Panel (Right):**
- Shows: "Changes (0)"
- Shows: "No changes"

---

### After Editing a File

**Example: Edit README file and save**

**What you should see:**

```
┌──────────────────────────────────────────────────────────┐
│ 🤖 AI Commit Generator    📦 Hello-World    1 changes    │
├──────────────┬───────────────────────┬──────────────────┤
│ 📂 Files     │   Code Editor         │   🔄 Git Panel   │
│              │                       │                  │
│ 📝 README ✓  │   [Edited content]    │   Changes (1)    │
│              │   [💾 Save]           │   ┌────────────┐ │
│              │                       │   │ M  README  │ │
│              │                       │   └────────────┘ │
│              │                       │                  │
│              │                       │   [Stage All]    │
└──────────────┴───────────────────────┴──────────────────┘
```

**Git Panel (Right):**
- Shows: "Changes (1)"
- Shows: "M README" (M = Modified)
- File is from cloned repo, NOT your project

---

## ❌ Wrong Behavior (What You're Seeing Now)

### Problem: Showing Current Project Files

```
┌──────────────────────────────────────────────────────────┐
│ 🤖 AI Commit Generator                      4 changes    │
├──────────────┬───────────────────────┬──────────────────┤
│ 📂 Files     │   Code Editor         │   🔄 Git Panel   │
│              │                       │                  │
│ 📝 README    │                       │   Changes (4)    │
│ 🐍 api.py    │                       │   ┌────────────┐ │
│ 📜 app.js    │                       │   │ M  api.py  │ │ ❌ WRONG
│              │                       │   │ M  req.txt │ │ ❌ WRONG
│              │                       │   │ ?? test.py │ │ ❌ WRONG
│              │                       │   └────────────┘ │
└──────────────┴───────────────────────┴──────────────────┘
```

**Problem:** Showing files from your current project directory, not the cloned repo!

---

## 🔧 How to Test Correct Behavior

### Step 1: Start Fresh
```bash
start_fresh.bat
```

This will:
- Delete old cloned repos
- Start the servers
- Open browser

### Step 2: Clone a Test Repository
```
URL: https://github.com/octocat/Hello-World.git
```

Click "Clone Repository"

### Step 3: Verify File Explorer
**Should show:**
- ✅ README (from Hello-World repo)

**Should NOT show:**
- ❌ api_server.py (from your project)
- ❌ requirements.txt (from your project)
- ❌ test_clone.py (from your project)

### Step 4: Verify Git Status
**Should show:**
- ✅ "Changes (0)" or "No changes"

**Should NOT show:**
- ❌ Modified files from your current project

### Step 5: Edit a File
1. Click on "README" in file explorer
2. Edit the content
3. Click "Save"

### Step 6: Verify Git Status Again
**Should show:**
- ✅ "Changes (1)"
- ✅ "M README" (from cloned repo)

**Should NOT show:**
- ❌ Changes from your current project

---

## 🎯 Key Points

### Files Should Come From:
```
✅ cloned_repos/Hello-World/README
✅ cloned_repos/Hello-World/other-files

❌ NOT from: ./api_server.py
❌ NOT from: ./requirements.txt
❌ NOT from: ./your-project-files
```

### Git Status Should Show:
```
✅ Changes in: cloned_repos/Hello-World/
❌ NOT changes in: ./ (current directory)
```

### When You Commit:
```
✅ Commits to: cloned_repos/Hello-World/.git
✅ Pushes to: https://github.com/octocat/Hello-World.git

❌ NOT to: Your current project
```

---

## 🐛 If Still Showing Wrong Files

### Check 1: Is Repository Cloned?
Look in your file system:
```
cloned_repos/
  └── Hello-World/
      ├── README
      └── other files
```

### Check 2: Backend Logs
In the Flask terminal, you should see:
```
Repository cloned successfully
Path: cloned_repos/Hello-World
```

### Check 3: API Response
Open browser console (F12), check network tab:
- `/api/files` should return files from cloned repo
- `/api/git/status` should return status from cloned repo

### Check 4: Restart Everything
```bash
# Kill all processes
Ctrl+C in both terminals

# Start fresh
start_fresh.bat
```

---

## ✅ Success Criteria

You'll know it's working correctly when:

1. **Before cloning:** No files shown, 0 changes
2. **After cloning:** Only cloned repo files shown
3. **After editing:** Only cloned repo changes shown
4. **After committing:** Commit goes to cloned repo
5. **After pushing:** Push goes to original remote

---

**If you see files from your current project, the system is NOT working correctly!**
