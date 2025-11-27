import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [gitStatus, setGitStatus] = useState([]);
  const [commitMessage, setCommitMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState('');
  const [expandedFolders, setExpandedFolders] = useState(new Set());

  useEffect(() => {
    loadFiles();
    loadGitStatus();
  }, []);

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

  const toggleFolder = (folderPath) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderPath)) {
      newExpanded.delete(folderPath);
    } else {
      newExpanded.add(folderPath);
    }
    setExpandedFolders(newExpanded);
  };

  const getFileIcon = (file) => {
    if (file.type === 'directory') {
      return expandedFolders.has(file.path) ? '📂' : '📁';
    }
    const ext = file.extension;
    if (ext === '.py') return '🐍';
    if (ext === '.js') return '📜';
    if (ext === '.json') return '📋';
    if (ext === '.md') return '📝';
    if (ext === '.css') return '🎨';
    if (ext === '.html') return '🌐';
    if (ext === '.csv') return '📊';
    if (ext === '.txt') return '📄';
    if (ext === '.bat') return '⚙️';
    return '📄';
  };

  const renderFileTree = (items, level = 0) => {
    return items.map((file, index) => (
      <div key={file.path}>
        <div
          className={`file-item ${selectedFile === file.path ? 'active' : ''}`}
          style={{ paddingLeft: `${16 + level * 16}px` }}
          onClick={() => {
            if (file.type === 'directory') {
              toggleFolder(file.path);
            } else {
              loadFileContent(file.path);
            }
          }}
        >
          <span className="file-icon">{getFileIcon(file)}</span>
          <span className="file-name">{file.name}</span>
          {file.type === 'directory' && file.children && file.children.length > 0 && (
            <span className="folder-arrow">
              {expandedFolders.has(file.path) ? '▼' : '▶'}
            </span>
          )}
        </div>
        {file.type === 'directory' && 
         expandedFolders.has(file.path) && 
         file.children && 
         file.children.length > 0 && (
          <div className="folder-children">
            {renderFileTree(file.children, level + 1)}
          </div>
        )}
      </div>
    ));
  };

  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <h1>🤖 Auto Hub AI: An Intelligent ML Framework For GitHub Automation </h1>
        <div className="header-info">
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
