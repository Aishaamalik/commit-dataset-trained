# AI Commit Generator - Complete Feature List

## 🎯 Core Features

### 1. Repository Cloning
- **Input any Git repository URL**
- Automatically clones to local workspace
- Supports GitHub, GitLab, Bitbucket, etc.
- Fresh clone each time

### 2. Web-Based IDE
- **VS Code-like interface**
- Three-panel layout
- Dark theme
- Responsive design

### 3. File Management
- **Tree view file explorer**
- Browse all repository files
- File type icons (Python, JS, JSON, MD, etc.)
- Nested folder support

### 4. Code Editor
- **View and edit files**
- Syntax-aware display
- Save changes instantly
- Real-time updates

### 5. Git Integration
- **Full git workflow**
- View changed files
- Stage all changes
- Commit with messages
- Push to remote

### 6. AI Commit Messages
- **RAG-powered generation**
- Learns from 1000+ commits
- Contextual and professional
- Follows conventional commits
- Editable before committing

## 🎨 User Interface

### Repository Input Screen
```
┌─────────────────────────────────────┐
│   🤖 AI Commit Generator            │
│   Enter a Git repository URL        │
│                                     │
│   [Repository URL Input]            │
│   [📥 Clone Repository Button]      │
│                                     │
│   Examples:                         │
│   • github.com/facebook/react       │
│   • github.com/microsoft/vscode     │
└─────────────────────────────────────┘
```

### Main IDE Interface
```
┌──────────────────────────────────────────────────────┐
│ 🤖 AI Commit Generator    📦 repo-name   3 changes  │
├────────────┬─────────────────────┬──────────────────┤
│ 📂 Files   │  Code Editor        │  🔄 Git Panel    │
│            │                     │                  │
│ 📁 src     │  [File Content]     │  Changes (3)     │
│ 🐍 app.py  │                     │  ┌─────────────┐ │
│ 📜 api.js  │  [Save Button]      │  │ M  app.py   │ │
│ 📝 README  │                     │  │ A  new.py   │ │
│            │                     │  └─────────────┘ │
│            │                     │                  │
│            │                     │  [Stage All]     │
│            │                     │  [Generate AI]   │
│            │                     │  [Commit]        │
│            │                     │  [Push]          │
└────────────┴─────────────────────┴──────────────────┘
```

## 🔧 Technical Stack

### Frontend
- **React 18** - UI framework
- **Axios** - HTTP client
- **CSS3** - Styling (VS Code theme)

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin support
- **Subprocess** - Git command execution

### AI System
- **TF-IDF** - Text vectorization
- **Cosine Similarity** - Retrieval
- **Groq API** - LLaMA 3.3 70B model

## 📊 Workflow

```
1. User enters repository URL
        ↓
2. System clones repository
        ↓
3. Files loaded in explorer
        ↓
4. User edits files
        ↓
5. Changes detected by Git
        ↓
6. User clicks "Generate"
        ↓
7. RAG finds similar commits
        ↓
8. LLM generates message
        ↓
9. User reviews & commits
        ↓
10. Push to remote
```

## 🎯 Use Cases

### For Developers
- Quick commit message generation
- Learn from project history
- Consistent commit style
- Save time writing messages

### For Teams
- Standardize commit messages
- Onboard new developers
- Maintain commit quality
- Review commit patterns

### For Open Source
- Contribute to any repository
- Generate professional messages
- Follow project conventions
- Quick PR commits

## 🚀 Performance

- **Clone Time**: 5-30 seconds (depends on repo size)
- **File Loading**: < 1 second
- **AI Generation**: 2-5 seconds
- **Commit/Push**: 1-3 seconds

## 🔒 Security

- Repositories cloned locally
- No data sent to external services (except Groq API)
- API key stored in `.env` (not committed)
- Git credentials use system configuration

## 📦 Storage

- Cloned repos: `cloned_repos/` folder
- RAG model: `rag_model.pkl` (~2MB)
- Training data: `github_commits_api.csv` (~500KB)

## 🎨 Customization

### Change AI Model
Edit `commit_generator.py`:
```python
model="llama-3.3-70b-versatile"  # Change this
```

### Modify UI Theme
Edit `frontend/src/App.css`:
```css
background: #1e1e1e;  /* Change colors */
```

### Add More Training Data
Add commits to `github_commits_api.csv` and retrain:
```bash
python rag_system.py
```

## 🔮 Future Enhancements

- [ ] Multiple repository support
- [ ] Branch management
- [ ] Merge conflict resolution
- [ ] Code review suggestions
- [ ] Commit history visualization
- [ ] Custom commit templates
- [ ] Team collaboration features
- [ ] Plugin system

## 📝 Supported File Types

- Python (`.py`)
- JavaScript (`.js`)
- JSON (`.json`)
- Markdown (`.md`)
- CSS (`.css`)
- HTML (`.html`)
- And more...

## 🌐 Supported Git Platforms

- ✅ GitHub
- ✅ GitLab
- ✅ Bitbucket
- ✅ Self-hosted Git servers
- ✅ Any Git repository with HTTPS/SSH

---

**A complete AI-powered Git workflow in your browser! 🎉**
