import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [repoLoaded, setRepoLoaded] = useState(false);
  const [repoName, setRepoName] = useState('');
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [gitStatus, setGitStatus] = useState([]);
  const [commitMessage, setCommitMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState('');

  useEffect(() => {
    checkRepoStatus();
  }, []);

  const checkRepoStatus = async () => {
    try {
      const response = await axios.get('/api/repo/info');
      if (response.data.active) {
        setRepoLoaded(true);
        loadFiles();
        loadGitStatus();
      }
    } catch (error) {
      console.error('Error checking repo status:', error);
    }
  };

  const cloneRepository = async () => {
    if (!repoUrl.trim()) {
      showNotification('Please enter a repository URL', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/repo/clone', { url: repoUrl });
      setRepoName(response.data.name);
      setRepoLoaded(true);
      showNotification('Repository cloned successfully!', 'success');
      loadFiles();
      loadGitStatus();
    } catch (error) {
      showNotification(error.response?.data?.error || 'Error cloning repository', 'error');
    }
    setLoading(false);
  };

  const loadFiles = async () => {
    try {
      const response = await axios.get('/api/files');
      setFiles(response.data.files);
    } catch (error) {
      showNotification('Error loading files', 'error');
    }
  };

  const loadGitStatus = async () => {
    try {
      const response = await axios.get('/api/git/status');
      setGitStatus(response.data.files);
    } catch (error) {
      console.error('Error loading git status:', error);
    }
  };

  const loadFileContent = async (filePath) => {
    try {
      const response = await axios.get('/api/file/content', {
        params: { path: filePath }
      });
      setFileContent(response.data.content);
      setSelectedFile(filePath);
    } catch (error) {
      showNotification('Error loading file', 'error');
    }
  };

  const saveFile = async () => {
    try {
      await axios.post('/api/file/save', {
        path: selectedFile,
        content: fileContent
      });
      showNotification('File saved!', 'success');
      loadGitStatus();
    } catch (error) {
      showNotification('Error saving file', 'error');
    }
  };

  const stageChanges = async () => {
    setLoading(true);
    try {
      await axios.post('/api/git/add');
      showNotification('Changes staged!', 'success');
      loadGitStatus();
    } catch (error) {
      showNotification('Error staging changes', 'error');
    }
    setLoading(false);
  };

  const generateCommit = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/commit/generate');
      setCommitMessage(response.data.message);
      showNotification('Commit message generated!', 'success');
    } catch (error) {
      showNotification('Error generating commit message', 'error');
    }
    setLoading(false);
  };

  const commitChanges = async () => {
    if (!commitMessage) {
      showNotification('Please generate a commit message first', 'error');
      return;
    }
    setLoading(true);
    try {
      await axios.post('/api/git/commit', { message: commitMessage });
      showNotification('Committed successfully!', 'success');
      setCommitMessage('');
      loadGitStatus();
    } catch (error) {
      showNotification('Error committing', 'error');
    }
    setLoading(false);
  };

  const pushChanges = async () => {
    setLoading(true);
    try {
      await axios.post('/api/git/push');
      showNotification('Pushed to remote!', 'success');
    } catch (error) {
      showNotification('Error pushing to remote', 'error');
    }
    setLoading(false);
  };

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(''), 3000);
  };

  const getFileIcon = (file) => {
    if (file.type === 'directory') return '📁';
    const ext = file.extension;
    if (ext === '.py') return '🐍';
    if (ext === '.js') return '📜';
    if (ext === '.json') return '📋';
    if (ext === '.md') return '📝';
    if (ext === '.css') return '🎨';
    if (ext === '.html') return '🌐';
    return '📄';
  };

  const renderFileTree = (fileList) => {
    return fileList.map((file, index) => (
      <div key={index}>
        <div
          className={`file-item ${selectedFile === file.path ? 'active' : ''}`}
          onClick={() => file.type === 'file' && loadFileContent(file.path)}
        >
          <span className="file-icon">{getFileIcon(file)}</span>
          <span className="file-name">{file.name}</span>
        </div>
        {file.children && file.children.length > 0 && (
          <div className="file-children">
            {renderFileTree(file.children)}
          </div>
        )}
      </div>
    ));
  };

  // Show repository input screen if no repo is loaded
  if (!repoLoaded) {
    return (
      <div className="app">
        <div className="repo-input-screen">
          <div className="repo-input-container">
            <h1>🤖 AI Commit Generator</h1>
            <p>Enter a Git repository URL to get started</p>
            
            <div className="repo-input-form">
              <input
                type="text"
                placeholder="https://github.com/username/repository.git"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && cloneRepository()}
                disabled={loading}
              />
              <button
                onClick={cloneRepository}
                disabled={loading}
                className="btn-primary"
              >
                {loading ? '⏳ Cloning...' : '📥 Clone Repository'}
              </button>
            </div>

            <div className="repo-examples">
              <p>Examples:</p>
              <code>https://github.com/facebook/react.git</code>
              <code>https://github.com/microsoft/vscode.git</code>
            </div>
          </div>
        </div>

        {notification && (
          <div className={`notification ${notification.type}`}>
            {notification.message}
          </div>
        )}
      </div>
    );
  }

  // Main IDE interface
  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <h1>🤖 AI Commit Generator</h1>
        <div className="header-info">
          <span className="repo-badge">📦 {repoName || 'Repository'}</span>
          <span>{gitStatus.length} changes</span>
        </div>
      </div>

      <div className="main-container">
        {/* File Explorer - Left Sidebar */}
        <div className="sidebar left">
          <div className="sidebar-header">
            <h3>📂 Files</h3>
          </div>
          <div className="file-list">
            {renderFileTree(files)}
          </div>
        </div>

        {/* Code Editor - Center */}
        <div className="editor-container">
          <div className="editor-header">
            <span>{selectedFile || 'No file selected'}</span>
            {selectedFile && (
              <button onClick={saveFile} className="btn-save">
                💾 Save
              </button>
            )}
          </div>
          <textarea
            className="code-editor"
            value={fileContent}
            onChange={(e) => setFileContent(e.target.value)}
            placeholder="Select a file to view its content..."
            spellCheck="false"
          />
        </div>

        {/* Git Panel - Right Sidebar */}
        <div className="sidebar right">
          <div className="sidebar-header">
            <h3>🔄 Git Automation</h3>
          </div>

          <div className="git-panel">
            {/* Git Status */}
            <div className="git-section">
              <h4>Changes ({gitStatus.length})</h4>
              <div className="git-status-list">
                {gitStatus.length === 0 ? (
                  <p className="no-changes">No changes</p>
                ) : (
                  gitStatus.map((item, index) => (
                    <div key={index} className="git-status-item">
                      <span className="status-badge">{item.status}</span>
                      <span className="file-name">{item.file}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="git-actions">
              <button
                onClick={stageChanges}
                disabled={loading || gitStatus.length === 0}
                className="btn-primary"
              >
                📦 Stage All Changes
              </button>

              <button
                onClick={generateCommit}
                disabled={loading || gitStatus.length === 0}
                className="btn-primary"
              >
                {loading ? '⏳ Generating...' : '✨ Generate Commit Message'}
              </button>

              {commitMessage && (
                <div className="commit-message-box">
                  <h4>Generated Message:</h4>
                  <textarea
                    value={commitMessage}
                    onChange={(e) => setCommitMessage(e.target.value)}
                    rows="6"
                  />
                </div>
              )}

              <button
                onClick={commitChanges}
                disabled={loading || !commitMessage}
                className="btn-success"
              >
                ✅ Commit
              </button>

              <button
                onClick={pushChanges}
                disabled={loading}
                className="btn-warning"
              >
                🚀 Push to Remote
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Notification */}
      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.message}
        </div>
      )}
    </div>
  );
}

export default App;
