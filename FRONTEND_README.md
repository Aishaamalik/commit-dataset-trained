# AI Commit Generator - Web Interface

A beautiful VS Code-like web interface for the AI Commit Message Generator.

## Features

### 🎨 Three-Panel Layout

**Left Sidebar - File Explorer**
- Browse project files
- Click to view/edit files
- File type icons

**Center - Code Editor**
- View and edit file contents
- Syntax highlighting
- Save changes

**Right Sidebar - Git Automation**
- View changed files
- Stage all changes
- Generate AI commit messages
- Commit with one click
- Push to remote

## Quick Start

### Option 1: Automated (Windows)
```bash
start_app.bat
```

### Option 2: Manual

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

## Usage

1. **Open** http://localhost:3000 in your browser
2. **Browse** files in the left sidebar
3. **Edit** files in the center editor
4. **View** changes in the right Git panel
5. **Click** "Generate Commit Message" to use AI
6. **Commit** and **Push** with one click!

## Architecture

```
Frontend (React)          Backend (Flask)           AI System
    ↓                          ↓                        ↓
Port 3000              →   Port 5000            →   RAG + Groq
                           REST API                  LLaMA 3.3
```

## API Endpoints

- `GET /api/files` - Get file tree
- `GET /api/file/content?path=` - Get file content
- `POST /api/file/save` - Save file
- `GET /api/git/status` - Git status
- `POST /api/git/add` - Stage changes
- `POST /api/commit/generate` - Generate commit message
- `POST /api/git/commit` - Commit changes
- `POST /api/git/push` - Push to remote

## Tech Stack

**Frontend:**
- React 18
- Axios for API calls
- CSS3 (VS Code theme)

**Backend:**
- Flask (Python web framework)
- Flask-CORS (Cross-origin support)
- Subprocess for Git commands

**AI:**
- RAG system (TF-IDF + Cosine Similarity)
- Groq API (LLaMA 3.3 70B)

## Screenshots

```
┌─────────────────────────────────────────────────────────────┐
│  🤖 AI Commit Generator                    3 changes        │
├──────────┬──────────────────────────┬──────────────────────┤
│ 📂 Files │  Code Editor             │  🔄 Git Automation   │
│          │                          │                      │
│ 📁 src   │  def main():             │  Changes (3)         │
│ 🐍 app.py│      print("Hello")      │  ┌─────────────────┐│
│ 📜 api.js│                          │  │ M  app.py       ││
│ 📝 README│  [Save Button]           │  │ A  new_file.py  ││
│          │                          │  └─────────────────┘│
│          │                          │                      │
│          │                          │  [Stage All]         │
│          │                          │  [Generate Message]  │
│          │                          │  [Commit]            │
│          │                          │  [Push]              │
└──────────┴──────────────────────────┴──────────────────────┘
```

## Requirements

- Python 3.7+
- Node.js 14+
- Git
- Groq API key (in `.env`)

## Troubleshooting

**Port already in use:**
```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**CORS errors:**
- Make sure Flask server is running
- Check proxy in `frontend/package.json`

**API key not found:**
- Ensure `.env` file exists with `GROQ_API_KEY`

## Development

**Hot reload enabled:**
- Frontend: Changes auto-refresh
- Backend: Restart Flask server for changes

**Build for production:**
```bash
cd frontend
npm run build
```

Then Flask will serve the built React app.

---

**Enjoy your AI-powered commit workflow! 🚀**
