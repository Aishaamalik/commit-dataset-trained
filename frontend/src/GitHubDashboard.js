import { useState, useEffect } from 'react';
import axios from 'axios';
import './GitHubDashboard.css';

function GitHubDashboard({ githubToken, onBack, onSelectRepo }) {
  const [view, setView] = useState('main'); // main, repos, upload
  const [repositories, setRepositories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState('');
  const [githubUser, setGithubUser] = useState(null);

  // Upload form state
  const [uploadForm, setUploadForm] = useState({
    localPath: '',
    repoName: '',
    description: '',
    private: false
  });

  useEffect(() => {
    if (githubToken) {
      loadGithubUser();
    }
  }, [githubToken]);

  const loadGithubUser = async () => {
    try {
      const response = await axios.get('/api/github/user', {
        headers: { 'X-GitHub-Token': githubToken }
      });
      setGithubUser(response.data);
    } catch (error) {
      showNotification('Error loading GitHub user', 'error');
    }
  };

  const loadRepositories = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/github/repos', {
        headers: { 'X-GitHub-Token': githubToken }
      });
      setRepositories(response.data.repositories);
      setView('repos');
    } catch (error) {
      showNotification('Error loading repositories', 'error');
    }
    setLoading(false);
  };

  const handleUploadProject = async (e) => {
    e.preventDefault();
    
    if (!uploadForm.localPath || !uploadForm.repoName) {
      showNotification('Please fill in all required fields', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/github/upload', {
        local_path: uploadForm.localPath,
        repo_name: uploadForm.repoName,
        description: uploadForm.description,
        private: uploadForm.private,
        commit_message: 'Initial commit'
      }, {
        headers: { 'X-GitHub-Token': githubToken }
      });

      showNotification('Project uploaded successfully!', 'success');
      
      // Show success with link
      setTimeout(() => {
        if (response.data.repository?.html_url) {
          window.open(response.data.repository.html_url, '_blank');
        }
        setView('main');
        setUploadForm({ localPath: '', repoName: '', description: '', private: false });
      }, 2000);
    } catch (error) {
      showNotification(error.response?.data?.error || 'Error uploading project', 'error');
    }
    setLoading(false);
  };

  const handleCloneRepo = (repo) => {
    onSelectRepo(repo.clone_url, repo.name);
  };

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(''), 3000);
  };

  // Main Dashboard View
  if (view === 'main') {
    return (
      <div className="github-dashboard">
        <div className="dashboard-container">
          <div className="dashboard-header">
            <div>
              <h1>🐙 GitHub Automation</h1>
              {githubUser && (
                <p className="github-user-info">
                  Connected as <strong>{githubUser.login}</strong>
                </p>
              )}
            </div>
            <button onClick={onBack} className="btn-back">← Back</button>
          </div>

          <div className="dashboard-options">
            <div className="option-card" onClick={loadRepositories}>
              <div className="option-icon">📚</div>
              <h3>My Repositories</h3>
              <p>Browse and clone your existing GitHub repositories</p>
            </div>

            <div className="option-card" onClick={() => setView('upload')}>
              <div className="option-icon">📤</div>
              <h3>Upload Project</h3>
              <p>Create a new repository and upload a local project</p>
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

  // Repository List View
  if (view === 'repos') {
    return (
      <div className="github-dashboard">
        <div className="dashboard-container">
          <div className="dashboard-header">
            <h1>📚 My Repositories</h1>
            <button onClick={() => setView('main')} className="btn-back">← Back</button>
          </div>

          {loading ? (
            <div className="loading-state">
              <p>Loading repositories...</p>
            </div>
          ) : (
            <div className="repo-list">
              {repositories.length === 0 ? (
                <div className="empty-state">
                  <p>No repositories found</p>
                </div>
              ) : (
                repositories.map((repo) => (
                  <div key={repo.id} className="repo-card">
                    <div className="repo-info">
                      <h3>{repo.name}</h3>
                      <p className="repo-description">
                        {repo.description || 'No description'}
                      </p>
                      <div className="repo-meta">
                        {repo.language && (
                          <span className="repo-language">
                            <span className="language-dot"></span>
                            {repo.language}
                          </span>
                        )}
                        <span>⭐ {repo.stargazers_count}</span>
                        <span>🔱 {repo.forks_count}</span>
                        {repo.private && <span className="private-badge">🔒 Private</span>}
                      </div>
                    </div>
                    <div className="repo-actions">
                      <button
                        onClick={() => handleCloneRepo(repo)}
                        className="btn-primary"
                      >
                        📥 Clone & Work
                      </button>
                      <a
                        href={repo.html_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-secondary"
                      >
                        🔗 View on GitHub
                      </a>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {notification && (
          <div className={`notification ${notification.type}`}>
            {notification.message}
          </div>
        )}
      </div>
    );
  }

  // Upload Project View
  if (view === 'upload') {
    return (
      <div className="github-dashboard">
        <div className="dashboard-container">
          <div className="dashboard-header">
            <h1>📤 Upload Project</h1>
            <button onClick={() => setView('main')} className="btn-back">← Back</button>
          </div>

          <form onSubmit={handleUploadProject} className="upload-form">
            <div className="form-group">
              <label>Local Project Path *</label>
              <input
                type="text"
                placeholder="C:\Users\username\my-project"
                value={uploadForm.localPath}
                onChange={(e) => setUploadForm({ ...uploadForm, localPath: e.target.value })}
                required
                disabled={loading}
              />
              <small>Full path to your local project directory</small>
            </div>

            <div className="form-group">
              <label>Repository Name *</label>
              <input
                type="text"
                placeholder="my-awesome-project"
                value={uploadForm.repoName}
                onChange={(e) => setUploadForm({ ...uploadForm, repoName: e.target.value })}
                required
                disabled={loading}
              />
              <small>Name for the new GitHub repository</small>
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                placeholder="A brief description of your project"
                value={uploadForm.description}
                onChange={(e) => setUploadForm({ ...uploadForm, description: e.target.value })}
                rows="3"
                disabled={loading}
              />
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={uploadForm.private}
                  onChange={(e) => setUploadForm({ ...uploadForm, private: e.target.checked })}
                  disabled={loading}
                />
                <span>Make repository private</span>
              </label>
            </div>

            <div className="form-actions">
              <button
                type="submit"
                className="btn-primary btn-large"
                disabled={loading}
              >
                {loading ? '⏳ Uploading...' : '🚀 Create & Upload'}
              </button>
            </div>

            <div className="upload-info">
              <p>ℹ️ This will:</p>
              <ul>
                <li>Create a new repository on GitHub</li>
                <li>Initialize git in your local directory (if needed)</li>
                <li>Add all files and commit them</li>
                <li>Push everything to GitHub</li>
              </ul>
            </div>
          </form>
        </div>

        {notification && (
          <div className={`notification ${notification.type}`}>
            {notification.message}
          </div>
        )}
      </div>
    );
  }

  return null;
}

export default GitHubDashboard;
