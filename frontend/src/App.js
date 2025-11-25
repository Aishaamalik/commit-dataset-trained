import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [gitStatus, setGitStatus] = useState(null);
  const [commitMessage, setCommitMessage] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const API_URL = 'http://localhost:5000/api';

  // Fetch git status on load
  useEffect(() => {
    fetchGitStatus();
  }, []);

  const fetchGitStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/git-status`);
      const data = await response.json();
      if (data.success) {
        setGitStatus(data);
      }
    } catch (err) {
      console.error('Error fetching git status:', err);
    }
  };

  const handleStageAll = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/stage-all`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('All changes staged!');
        fetchGitStatus();
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to stage changes');
    }
    setLoading(false);
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      const data = await response.json();
      if (data.success) {
        setCommitMessage(data.commit_message);
        setAnalysis(data.analysis);
        setSuccess('Commit message generated!');
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to generate commit message');
    }
    setLoading(false);
  };

  const handleCommit = async () => {
    if (!commitMessage) {
      setError('No commit message to commit');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/commit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: commitMessage }),
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Committed successfully!');
        fetchGitStatus();
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to commit');
    }
    setLoading(false);
  };

  const handlePush = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/push`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        setSuccess(data.message);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to push');
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 AI Commit Message Generator</h1>
        <p>RAG + Groq LLM</p>
      </header>

      <div className="container">
        {/* Git Status */}
        <div className="card">
          <h2>📁 Git Status</h2>
          {gitStatus && (
            <div>
              <p><strong>Branch:</strong> {gitStatus.branch}</p>
              <p><strong>Unstaged files:</strong> {gitStatus.unstaged_files.length}</p>
              <p><strong>Staged files:</strong> {gitStatus.staged_files.length}</p>
              {gitStatus.staged_files.length > 0 && (
                <div className="file-list">
                  {gitStatus.staged_files.map((file, i) => (
                    <div key={i} className="file-item">✓ {file}</div>
                  ))}
                </div>
              )}
            </div>
          )}
          <button onClick={handleStageAll} disabled={loading}>
            Stage All Changes
          </button>
        </div>

        {/* Generate */}
        <div className="card">
          <h2>✨ Generate Commit Message</h2>
          <button 
            onClick={handleGenerate} 
            disabled={loading || !gitStatus || gitStatus.staged_files.length === 0}
            className="primary"
          >
            {loading ? 'Generating...' : 'Generate Message'}
          </button>
        </div>

        {/* Commit Message */}
        {commitMessage && (
          <div className="card">
            <h2>📝 Generated Message</h2>
            <textarea
              value={commitMessage}
              onChange={(e) => setCommitMessage(e.target.value)}
              rows="6"
            />
            {analysis && (
              <div className="analysis">
                <p>Files: {analysis.files_changed.length} | 
                   Added: +{analysis.additions} | 
                   Deleted: -{analysis.deletions}</p>
              </div>
            )}
            <div className="button-group">
              <button onClick={handleCommit} disabled={loading} className="primary">
                Commit
              </button>
              <button onClick={handlePush} disabled={loading}>
                Push to Remote
              </button>
            </div>
          </div>
        )}

        {/* Messages */}
        {error && <div className="message error">{error}</div>}
        {success && <div className="message success">{success}</div>}
      </div>
    </div>
  );
}

export default App;
