# Quick Start Guide

## 🚀 AI Commit Generator with Repository Cloning

This system now supports cloning any Git repository and generating AI-powered commit messages for it!

## How It Works

1. **Enter Repository URL** - Paste any GitHub/GitLab repository URL
2. **Clone Automatically** - System clones the repo locally
3. **Browse & Edit** - View and edit files in the web IDE
4. **AI Commit Messages** - Generate professional commit messages
5. **Push Changes** - Commit and push directly from the UI

## Start the Application

### Windows (Easy):
```bash
start_app.bat
```

### Manual Start:

**Terminal 1 - Backend:**
```bash
pip install -r requirements.txt
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm start
```

## Usage Flow

### Step 1: Open the App
Navigate to **http://localhost:3000**

### Step 2: Enter Repository URL
```
https://github.com/username/repository.git
```

Examples:
- `https://github.com/facebook/react.git`
- `https://github.com/microsoft/vscode.git`
- `https://github.com/your-username/your-repo.git`

### Step 3: Click "Clone Repository"
The system will:
- Clone the repository to `cloned_repos/`
- Load all files in the file explorer
- Check git status

### Step 4: Make Changes
- Click files in the left sidebar to view/edit
- Edit code in the center editor
- Click "Save" to save changes

### Step 5: Generate Commit Message
1. Click "📦 Stage All Changes"
2. Click "✨ Generate Commit Message"
3. AI analyzes your changes and generates a message
4. Review and edit if needed

### Step 6: Commit & Push
1. Click "✅ Commit" to commit locally
2. Click "🚀 Push to Remote" to push to GitHub/GitLab

## Features

### 🎨 Three-Panel Interface
- **Left**: File explorer with tree view
- **Center**: Code editor
- **Right**: Git automation panel

### 🤖 AI-Powered
- Learns from 1000+ real commits
- Generates contextual messages
- Follows conventional commit standards

### 🔄 Full Git Integration
- Clone repositories
- View changes
- Stage files
- Commit with AI messages
- Push to remote

## Architecture

```
User Input (Repo URL)
        ↓
Clone Repository
        ↓
Load Files → Edit Files → Save Changes
        ↓
Git Status → Stage Changes
        ↓
RAG System (Find Similar Commits)
        ↓
Groq LLM (Generate Message)
        ↓
Commit → Push to Remote
```

## API Endpoints

### Repository Management
- `POST /api/repo/clone` - Clone a repository
- `GET /api/repo/info` - Get current repo info

### File Operations
- `GET /api/files` - Get file tree
- `GET /api/file/content?path=` - Get file content
- `POST /api/file/save` - Save file changes

### Git Operations
- `GET /api/git/status` - Get git status
- `POST /api/git/add` - Stage all changes
- `POST /api/commit/generate` - Generate AI commit message
- `POST /api/git/commit` - Commit changes
- `POST /api/git/push` - Push to remote

## Requirements

- Python 3.7+
- Node.js 14+
- Git installed
- Groq API key in `.env` file

## Troubleshooting

### "Failed to clone repository"
- Check if the URL is correct
- Ensure you have access to the repository
- For private repos, you may need SSH keys or tokens

### "No changes found"
- Make sure you've edited and saved files
- Check if files are in the cloned repository

### "Error pushing to remote"
- Ensure you have push access to the repository
- For private repos, configure Git credentials

## Example Workflow

```bash
# 1. Start the app
start_app.bat

# 2. Open browser
http://localhost:3000

# 3. Enter repo URL
https://github.com/your-username/test-repo.git

# 4. Clone → Edit → Save → Generate → Commit → Push
```

## Tips

- Use public repositories for testing
- The cloned repos are stored in `cloned_repos/` folder
- Each clone creates a fresh copy
- You can clone multiple repos (one at a time)

---

**Ready to generate amazing commit messages for any repository! 🎉**
