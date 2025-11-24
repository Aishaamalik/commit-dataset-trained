# AI Commit Message Generator - Usage Guide

## ✅ System Status: FULLY OPERATIONAL

Your AI commit message generator is trained and ready to use!

## What You Have

### 1. **RAG System** (Trained ✓)
- Learned from 1000+ commits (Microsoft VSCode, Rust, PyTorch, TensorFlow)
- Model saved: `rag_model.pkl`
- Can retrieve similar commits for context

### 2. **LLM Integration** (Configured ✓)
- Using Groq's LLaMA 3.3 70B model
- API key configured in `.env`
- Generates professional, contextual commit messages

### 3. **Git Integration** (Ready ✓)
- Analyzes git diffs automatically
- Extracts file changes, additions, deletions
- Can commit directly from the tool

## Quick Start

### Generate Commit Message for Your Changes

```bash
# 1. Make your changes
# 2. Stage them
git add .

# 3. Generate commit message
python commit_generator.py

# 4. Review and commit (or the tool will do it for you)
```

### Run Demo Examples

```bash
python demo.py
```

This shows 3 examples:
- Bug fix commit
- New feature commit
- Refactoring commit

### Interactive Mode

```bash
python commit_api.py --interactive
```

Options:
1. Generate for staged changes
2. Generate for unstaged changes
3. Provide custom diff
4. Exit

### Search Commit History

```bash
python interactive_search.py
```

Search through your dataset without generating new messages.

## How It Works

```
Your Changes
    ↓
Git Diff Analysis
    ↓
RAG System (finds similar commits)
    ↓
Groq LLM (generates message)
    ↓
Professional Commit Message
```

## Example Output

```
GENERATED COMMIT MESSAGE:
feat: add user authentication API

Implement user authentication endpoints with bcrypt password hashing.
Added login and registration routes with JWT token generation.
Includes input validation and error handling.

ANALYSIS:
Files changed: 3
Lines added: 156
Lines deleted: 12

SIMILAR COMMITS (for context):
1. Add live progress tracking to chat session descriptions
2. Implement commit message generation using Groq LLM
3. Support skills and context retrieval
```

## Files Overview

| File | Purpose |
|------|---------|
| `commit_generator.py` | Main generator (RAG + Groq) |
| `commit_api.py` | API wrapper & interactive mode |
| `rag_system.py` | RAG implementation |
| `demo.py` | Demo with examples |
| `test_generator.py` | Test script |
| `interactive_search.py` | Search commit history |
| `.env` | API key (DO NOT COMMIT) |
| `rag_model.pkl` | Trained RAG model |

## Programmatic Usage

```python
from commit_generator import CommitMessageGenerator

# Initialize
generator = CommitMessageGenerator()

# Generate for current repo
result = generator.generate_commit_message()

# Access results
print(result['commit_message'])
print(f"Files: {result['analysis']['files_changed']}")
print(f"Similar: {result['similar_commits']}")

# Or provide custom diff
custom_diff = "diff --git a/file.py..."
result = generator.generate_commit_message(diff_text=custom_diff)
```

## Tips for Best Results

1. **Stage meaningful changes**: The tool works best with focused, logical changes
2. **Review the output**: Always review generated messages before committing
3. **Customize if needed**: You can edit the generated message
4. **Use conventional commits**: The tool follows feat/fix/docs/refactor/etc.

## Troubleshooting

### "No staged changes found"
```bash
git add .  # Stage your changes first
```

### "GROQ_API_KEY not found"
```bash
# Check .env file exists and contains:
GROQ_API_KEY=your-key-here
```

### "Model not trained"
```bash
python rag_system.py  # Train the RAG model
```

## Next Steps

1. ✅ System is ready - start using it!
2. Try it on your own projects
3. Customize the prompt in `commit_generator.py` if needed
4. Add more commits to the dataset for better context

## Performance

- **RAG Training**: ~2 seconds (1000 commits)
- **Message Generation**: ~2-5 seconds per commit
- **Model Size**: ~2MB (rag_model.pkl)
- **API Cost**: Free tier on Groq (generous limits)

---

**Ready to generate amazing commit messages! 🚀**
