# AI Commit Message Generator - Frontend

## Quick Start

### Option 1: Use the Startup Script (Windows)
```bash
start_app.bat
```

This will automatically start both the API server and React frontend.

### Option 2: Manual Start

**Terminal 1 - Start API Server:**
```bash
pip install -r requirements.txt
python api_server.py
```

**Terminal 2 - Start React Frontend:**
```bash
cd frontend
npm start
```

## Access the Application

- **Frontend:** http://localhost:3000
- **API:** http://localhost:5000

## Features

### 1. Git Status View
- Shows current branch
- Lists unstaged and staged files
- One-click staging of all changes

### 2. Generate Commit Message
- Analyzes staged changes
- Uses RAG + Groq LLM to generate message
- Shows file statistics (additions/deletions)

### 3. Commit & Push
- Edit generated message if needed
- Commit with one click
- Push to remote repository

## How to Use

1. **Stage Changes**: Click "Stage All Changes" button
2. **Generate**: Click "Generate Message" to create commit message
3. **Review**: Edit the message if needed
4. **Commit**: Click "Commit" to commit changes
5. **Push**: Click "Push to Remote" to sync with GitHub

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/git-status` - Get git status
- `POST /api/stage-all` - Stage all changes
- `POST /api/generate` - Generate commit message
- `POST /api/commit` - Commit changes
- `POST /api/push` - Push to remote

## Tech Stack

**Backend:**
- Flask (Python web framework)
- Flask-CORS (Cross-origin requests)
- Groq API (LLM)
- RAG System (TF-IDF)

**Frontend:**
- React 18
- Fetch API
- CSS3 (Gradient design)

## Troubleshooting

### API not connecting
- Make sure Flask server is running on port 5000
- Check GROQ_API_KEY is set in .env file

### Frontend not loading
- Run `npm install` in frontend directory
- Check if port 3000 is available

### Git commands failing
- Make sure you're in a git repository
- Check git is installed and in PATH
