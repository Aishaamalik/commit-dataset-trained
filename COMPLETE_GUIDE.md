# AI Commit Generator - Complete Guide

## 🎯 What This Does

This is a **web-based IDE** that:
1. **Clones any Git repository** you provide
2. **Shows all files** in a VS Code-like interface
3. **Lets you edit files** directly in the browser
4. **Generates AI commit messages** based on your changes
5. **Commits and pushes** to the original repository

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Groq API Key

Create a `.env` file:
```
GROQ_API_KEY=your-groq-api-key-here
```

Get your free API key from: https://console.groq.com/

### Step 3: Start the Backend

```bash
python api_server.py
```

You should see:
```
🚀 AI Commit Generator - Web Interface
Starting server at http://localhost:5000
```

### Step 4: Start the Frontend

Open a new terminal:
```bash
cd frontend
npm install
npm start
```

Browser will open at: http://localhost:3000

## 📖 How to Use

### 1. Enter Repository URL

When you open the app, you'll see:

```
┌─────────────────────────────────────┐
│   🤖 AI Commit Generator            │
│   Enter a Git repository URL        │
│                                     │
│   [https://github.com/user/repo]    │
│   [📥 Clone Repository]             │
└─────────────────────────────────────┘
```

**Examples:**
- `https://github.com/facebook/react.git`
- `https://github.com/microsoft/vscode.git`
- `https://github.com/your-username/your-project.git`

### 2. Clone Repository

Click "Clone Repository" button. The system will:
- Clone the repository to `cloned_repos/` folder
- Load all files in the file explorer
- Check git status
- Show the IDE interface

### 3. Browse & Edit Files

**Left Sidebar - File Explorer:**
- Click on any file to view it
- Files are organized in a tree structure
- Icons show file types (🐍 Python, 📜 JS, etc.)

**Center - Code Editor:**
- View file contents
- Edit directly in the browser
- Click "💾 Save" to save changes

**Right Sidebar - Git Panel:**
- See all changed files
- View git status
- Perform git operations

### 4. Make Changes

Edit any file in the code editor:
```python
# Before
def hello():
    print("Hello")

# After
def hello(name):
    print(f"Hello {name}!")
```

Click "💾 Save" to save your changes.

### 5. Generate Commit Message

**Step-by-step:**

1. **Stage Changes**
   - Click "📦 Stage All Changes"
   - All modified files are staged

2. **Generate AI Message**
   - Click "✨ Generate Commit Message"
   - AI analyzes your changes
   - Generates a professional commit message
   - Takes 2-5 seconds

3. **Review Message**
   - Message appears in a text box
   - You can edit it if needed
   - Follows conventional commit format

4. **Commit**
   - Click "✅ Commit"
   - Changes are committed locally

5. **Push to Remote**
   - Click "🚀 Push to Remote"
   - Changes are pushed to GitHub/GitLab

## 🎨 Interface Overview

```
┌──────────────────────────────────────────────────────────────┐
│ 🤖 AI Commit Generator    📦 repository-name    3 changes    │
├──────────────┬───────────────────────┬───────────────────────┤
│              │                       │                       │
│ 📂 Files     │   Code Editor         │   🔄 Git Automation   │
│              │                       │                       │
│ 📁 src       │   def main():         │   Changes (3)         │
│   🐍 app.py  │       print("Hi")     │   ┌─────────────────┐ │
│   📜 api.js  │                       │   │ M  src/app.py   │ │
│ 📁 tests     │   [💾 Save]           │   │ A  new_file.py  │ │
│ 📝 README.md │                       │   │ M  README.md    │ │
│              │                       │   └─────────────────┘ │
│              │                       │                       │
│              │                       │   [📦 Stage All]      │
│              │                       │   [✨ Generate AI]    │
│              │                       │                       │
│              │                       │   Generated Message:  │
│              │                       │   ┌─────────────────┐ │
│              │                       │   │ feat: add new   │ │
│              │                       │   │ feature...      │ │
│              │                       │   └─────────────────┘ │
│              │                       │                       │
│              │                       │   [✅ Commit]         │
│              │                       │   [🚀 Push]           │
│              │                       │                       │
└──────────────┴───────────────────────┴───────────────────────┘
```

## 🔧 How It Works

### Architecture

```
Frontend (React)          Backend (Flask)           AI System
Port 3000                 Port 5000                 Groq API
     │                         │                         │
     │  1. Clone Repo          │                         │
     ├────────────────────────>│                         │
     │                         │  git clone              │
     │                         │                         │
     │  2. Get Files           │                         │
     ├────────────────────────>│                         │
     │  <────────────────────  │                         │
     │                         │                         │
     │  3. Edit & Save         │                         │
     ├────────────────────────>│                         │
     │                         │  Write to file          │
     │                         │                         │
     │  4. Generate Commit     │                         │
     ├────────────────────────>│                         │
     │                         │  Get git diff           │
     │                         │  Find similar commits   │
     │                         ├────────────────────────>│
     │                         │  <──────────────────────│
     │                         │  LLaMA generates msg    │
     │  <────────────────────  │                         │
     │                         │                         │
     │  5. Commit & Push       │                         │
     ├────────────────────────>│                         │
     │                         │  git commit             │
     │                         │  git push               │
```

### Data Flow

1. **User Input**: Repository URL
2. **Clone**: System clones to `cloned_repos/repo-name/`
3. **Load**: Files loaded from cloned repository
4. **Edit**: Changes saved to cloned repository
5. **Analyze**: Git diff extracted from cloned repo
6. **RAG**: Similar commits retrieved from dataset
7. **LLM**: Groq generates commit message
8. **Commit**: Changes committed in cloned repo
9. **Push**: Pushed to original remote repository

## 📁 Project Structure

```
.
├── api_server.py              # Flask backend
├── commit_generator.py        # AI commit generator
├── rag_system.py             # RAG implementation
├── github_commits_api.csv    # Training data
├── rag_model.pkl             # Trained model
├── requirements.txt          # Python dependencies
├── .env                      # API keys (not committed)
├── .gitignore               # Git ignore rules
│
├── frontend/                 # React frontend
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js           # Main component
│       ├── App.css          # Styles
│       ├── index.js
│       └── index.css
│
├── cloned_repos/            # Cloned repositories (not committed)
│   └── repo-name/           # Your cloned repo
│
└── docs/
    ├── README.md
    ├── QUICK_START.md
    ├── FEATURES.md
    └── COMPLETE_GUIDE.md
```

## 🔐 Security & Privacy

### What Gets Stored
- Cloned repositories: `cloned_repos/` (local only)
- RAG model: `rag_model.pkl` (local only)
- API key: `.env` (local only, not committed)

### What Gets Sent
- **To Groq API**: Git diff + similar commits (for message generation)
- **To Git Remote**: Your commits (standard git push)

### Credentials
- Uses your system's Git credentials
- For private repos, configure Git authentication:
  ```bash
  git config --global credential.helper store
  ```

## 🐛 Troubleshooting

### "Failed to clone repository"
**Cause**: Invalid URL or no access
**Solution**: 
- Check URL is correct
- For private repos, use SSH or configure credentials
- Try a public repo first

### "No changes found"
**Cause**: No files modified or not saved
**Solution**:
- Make sure you clicked "Save" after editing
- Check if files show in "Changes" panel

### "Error generating commit message"
**Cause**: No staged changes or API error
**Solution**:
- Click "Stage All Changes" first
- Check Groq API key in `.env`
- Check internet connection

### "Error pushing to remote"
**Cause**: No push access or authentication issue
**Solution**:
- Ensure you have push access to the repository
- Configure Git credentials
- For private repos, use SSH keys

### Port already in use
**Cause**: Another app using port 5000 or 3000
**Solution**:
```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## 🧪 Testing

### Test the Backend
```bash
python test_clone.py
```

This will:
- Clone a test repository
- Load files
- Check git status
- Read a file

### Test the Full System
1. Start backend: `python api_server.py`
2. Start frontend: `cd frontend && npm start`
3. Open http://localhost:3000
4. Clone: `https://github.com/octocat/Hello-World.git`
5. Edit README file
6. Generate commit message
7. Commit and push

## 💡 Tips & Best Practices

### For Best Results
- ✅ Make focused, logical changes
- ✅ Stage related changes together
- ✅ Review generated messages
- ✅ Edit messages if needed
- ✅ Test with public repos first

### Commit Message Quality
- The AI learns from 1000+ real commits
- Follows conventional commit format
- Generates contextual messages
- Better with clear, focused changes

### Performance
- Small repos clone faster
- Large repos may take 30+ seconds
- AI generation takes 2-5 seconds
- Commit/push depends on network

## 🎓 Examples

### Example 1: Bug Fix
```
1. Clone: https://github.com/your-username/my-app.git
2. Edit: src/auth.py (fix password validation)
3. Save changes
4. Generate: "fix: correct password validation logic"
5. Commit & Push
```

### Example 2: New Feature
```
1. Clone: https://github.com/your-username/api-server.git
2. Create: src/routes/users.py
3. Add user management endpoints
4. Generate: "feat: add user management API endpoints"
5. Commit & Push
```

### Example 3: Documentation
```
1. Clone: https://github.com/your-username/docs.git
2. Edit: README.md (add installation guide)
3. Generate: "docs: add installation instructions"
4. Commit & Push
```

## 🚀 Next Steps

1. **Try it out**: Clone a test repository
2. **Make changes**: Edit some files
3. **Generate commits**: Use the AI
4. **Customize**: Modify the UI or AI prompts
5. **Share**: Use it for your projects!

---

**Questions? Issues? Check the other docs or create an issue!**

**Happy committing! 🎉**
