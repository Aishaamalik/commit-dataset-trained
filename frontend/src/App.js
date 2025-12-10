import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { onAuthStateChanged, signOut, GithubAuthProvider } from 'firebase/auth';
import { auth } from './firebase';
import { getUserData } from './userService';
import Login from './Login';
import Register from './Register';
import GitHubDashboard from './GitHubDashboard';
import GitHubConnect from './GitHubConnect';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [userData, setUserData] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [showLogin, setShowLogin] = useState(true);
  const [githubToken, setGithubToken] = useState(null);
  const [showGithubConnect, setShowGithubConnect] = useState(false);
  const [showGithubDashboard, setShowGithubDashboard] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
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

  // Check authentication state
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      // Skip all authentication processing if user is being registered
      const isRegisteringUser = localStorage.getItem('registering_user');
      const showRegistrationSuccess = localStorage.getItem('show_registration_success');
      
      if (isRegisteringUser || showRegistrationSuccess) {
        return; // Don't process authentication during registration or success display
      }
      
      setUser(currentUser);
      
      // Get user data from Firestore
      if (currentUser) {
        try {
          const userInfo = await getUserData(currentUser.uid);
          setUserData(userInfo);
        } catch (error) {
          console.error('Error loading user data:', error);
        }

        try {
          const credential = GithubAuthProvider.credentialFromResult(currentUser);
          if (credential) {
            const token = credential.accessToken;
            if (token) {
              setGithubToken(token);
              // Verify token with backend
              await axios.post('/api/github/connect', { token });
            }
          } else {
            // User logged in with email, show GitHub connect page if they don't have a token
            if (!isRegistering && !githubToken) {
              setShowGithubConnect(true);
            }
          }
        } catch (error) {
          console.log('No GitHub credential found');
          // Show GitHub connect prompt for email logins if they don't have a token
          if (!isRegistering && !githubToken) {
            setShowGithubConnect(true);
          }
        }
      } else {
        setUserData(null);
      }
      
      setAuthLoading(false);
    });

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    checkRepoStatus();
    // Clean up any stale registration flags on app start
    const isRegisteringUser = localStorage.getItem('registering_user');
    const showRegistrationSuccess = localStorage.getItem('show_registration_success');
    const registrationComplete = localStorage.getItem('registration_complete');
    
    if (isRegisteringUser || showRegistrationSuccess || registrationComplete) {
      // Clean up stale registration flags (shouldn't persist across app restarts)
      localStorage.removeItem('registering_user');
      localStorage.removeItem('show_registration_success');
      localStorage.removeItem('registration_complete');
    }
  }, []);

  // Auto-refresh git status when repo is loaded
  useEffect(() => {
    if (repoLoaded) {
      const interval = setInterval(() => {
        loadGitStatus();
      }, 3000); // Refresh every 3 seconds

      return () => clearInterval(interval);
    }
  }, [repoLoaded]);

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

    // Clear previous repository state
    setSelectedFile(null);
    setFileContent('');
    setFiles([]);
    setGitStatus([]);
    setCommitMessage('');

    setLoading(true);
    try {
      const response = await axios.post('/api/repo/clone', { url: repoUrl });
      setRepoName(response.data.name);
      setRepoLoaded(true);
      showNotification('Repository cloned successfully!', 'success');
      await loadFiles();
      await loadGitStatus();
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
      const errorMsg = error.response?.data?.error || 'Error loading file';
      
      if (error.response?.data?.binary) {
        setFileContent('⚠️ This is a binary file and cannot be displayed or edited.\n\nBinary files include images, executables, archives, and other non-text formats.');
        setSelectedFile(filePath);
        showNotification('Binary file cannot be displayed', 'info');
      } else {
        setFileContent('');
        setSelectedFile(null);
        showNotification(errorMsg, 'error');
      }
    }
  };

  const saveFile = async () => {
    try {
      await axios.post('/api/file/save', {
        path: selectedFile,
        content: fileContent
      });
      showNotification('File saved!', 'success');
      
      // Immediately refresh git status after saving
      await loadGitStatus();
      
      // Refresh again after a short delay to catch any delayed changes
      setTimeout(() => {
        loadGitStatus();
      }, 1000);
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

  const handleLogout = async () => {
    try {
      await signOut(auth);
      // Clear all state
      setRepoLoaded(false);
      setRepoUrl('');
      setRepoName('');
      setUserData(null);
      setGithubToken(null);
      setShowGithubConnect(false);
      setShowGithubDashboard(false);
      setIsRegistering(false);
      setFiles([]);
      setSelectedFile(null);
      setFileContent('');
      setGitStatus([]);
      setCommitMessage('');
      localStorage.removeItem('github_connect_prompted');
      showNotification('Logged out successfully', 'success');
    } catch (error) {
      showNotification('Error logging out', 'error');
    }
  };

  const handleGithubConnectSuccess = async (token) => {
    setGithubToken(token);
    setShowGithubConnect(false);
    localStorage.setItem('github_connect_prompted', 'true');
    try {
      await axios.post('/api/github/connect', { token });
      showNotification('GitHub connected successfully!', 'success');
    } catch (error) {
      console.error('Error connecting GitHub:', error);
    }
  };

  const handleSkipGithubConnect = () => {
    setShowGithubConnect(false);
    localStorage.setItem('github_connect_prompted', 'true');
    showNotification('You can connect GitHub later from settings', 'info');
  };

  const handleGithubDashboardSelect = async (cloneUrl, name) => {
    // Clear previous repository state
    setSelectedFile(null);
    setFileContent('');
    setFiles([]);
    setGitStatus([]);
    setCommitMessage('');
    
    setRepoUrl(cloneUrl);
    setRepoName(name);
    setShowGithubDashboard(false);
    
    // Clone the repository
    setLoading(true);
    try {
      const response = await axios.post('/api/repo/clone', { url: cloneUrl });
      setRepoName(response.data.name);
      setRepoLoaded(true);
      showNotification('Repository cloned successfully!', 'success');
      await loadFiles();
      await loadGitStatus();
    } catch (error) {
      showNotification(error.response?.data?.error || 'Error cloning repository', 'error');
    }
    setLoading(false);
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

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="app">
        <div className="loading-screen">
          <h2>Loading...</h2>
        </div>
      </div>
    );
  }

  // Show login/register if not authenticated
  if (!user) {
    const handleGithubToken = async (token) => {
      setGithubToken(token);
      try {
        await axios.post('/api/github/connect', { token });
      } catch (error) {
        console.error('Error connecting GitHub:', error);
      }
    };

    if (showLogin) {
      return (
        <Login
          onLoginSuccess={() => {}}
          onSwitchToRegister={() => {
            setIsRegistering(false);
            setShowLogin(false);
          }}
          onGithubToken={handleGithubToken}
        />
      );
    } else {
      return (
        <Register
          onRegisterSuccess={() => {}}
          onSwitchToLogin={() => {
            setIsRegistering(false);
            setShowLogin(true);
          }}
          onGithubToken={handleGithubToken}
          onStartRegistration={() => setIsRegistering(true)}
        />
      );
    }
  }

  // Show GitHub Connect modal if needed
  if (showGithubConnect && user && !githubToken) {
    return (
      <GitHubConnect
        user={user}
        onConnect={handleGithubConnectSuccess}
        onSkip={handleSkipGithubConnect}
      />
    );
  }

  // Show GitHub Dashboard if requested
  if (showGithubDashboard && githubToken) {
    return (
      <GitHubDashboard
        githubToken={githubToken}
        onBack={() => setShowGithubDashboard(false)}
        onSelectRepo={handleGithubDashboardSelect}
      />
    );
  }

  // Show repository input screen if no repo is loaded
  if (!repoLoaded) {
    return (
      <div className="app">
        <div className="repo-input-screen">
          <div className="repo-input-container">
            <div className="repo-screen-header">
              <h1>🤖 AI Commit Generator</h1>
              <button onClick={handleLogout} className="btn-logout">Logout</button>
            </div>
            <p>Choose how to get started</p>
            
            {githubToken && (
              <div className="github-option">
                <button
                  onClick={() => setShowGithubDashboard(true)}
                  className="btn-github"
                >
                  🐙 GitHub Automation
                </button>
                <p className="option-description">
                  Browse your repositories or upload a new project
                </p>
              </div>
            )}

            <div className="divider-text">
              <span>OR</span>
            </div>
            
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
          <div className="user-info">
            <span>👤 {userData?.username || user.email}</span>
            <button onClick={handleLogout} className="btn-logout">Logout</button>
          </div>
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
            <button 
              onClick={() => {
                loadGitStatus();
                showNotification('Git status refreshed', 'info');
              }} 
              className="btn-refresh"
              title="Refresh git status"
            >
              🔄 Refresh
            </button>
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
