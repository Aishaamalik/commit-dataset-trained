import { useState } from 'react';
import { signInWithPopup, GithubAuthProvider, linkWithPopup } from 'firebase/auth';
import { auth } from './firebase';
import './GitHubConnect.css';

function GitHubConnect({ user, onConnect, onSkip }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleConnectGitHub = async () => {
    setLoading(true);
    setError('');

    const provider = new GithubAuthProvider();
    provider.addScope('repo');
    provider.addScope('user');

    try {
      // Try to link GitHub to existing account
      const result = await linkWithPopup(user, provider);
      const credential = GithubAuthProvider.credentialFromResult(result);
      const token = credential.accessToken;

      if (token) {
        onConnect(token);
      }
    } catch (err) {
      if (err.code === 'auth/credential-already-in-use') {
        setError('This GitHub account is already linked to another user.');
      } else if (err.code === 'auth/provider-already-linked') {
        setError('GitHub is already connected to this account.');
      } else {
        setError(err.message);
      }
    }
    setLoading(false);
  };

  return (
    <div className="github-connect-overlay">
      <div className="github-connect-modal">
        <div className="modal-header">
          <h2>🐙 Connect GitHub</h2>
          <p>Unlock powerful GitHub automation features</p>
        </div>

        <div className="modal-content">
          <div className="features-list">
            <div className="feature-item">
              <span className="feature-icon">📚</span>
              <div>
                <h4>Browse Your Repositories</h4>
                <p>View and clone all your GitHub repositories</p>
              </div>
            </div>

            <div className="feature-item">
              <span className="feature-icon">📤</span>
              <div>
                <h4>Upload Projects</h4>
                <p>Create new repositories and upload local projects</p>
              </div>
            </div>

            <div className="feature-item">
              <span className="feature-icon">🤖</span>
              <div>
                <h4>Full Automation</h4>
                <p>AI-powered commit messages and seamless workflow</p>
              </div>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="modal-actions">
            <button
              onClick={handleConnectGitHub}
              disabled={loading}
              className="btn-connect"
            >
              {loading ? '⏳ Connecting...' : '🔗 Connect GitHub'}
            </button>

            <button
              onClick={onSkip}
              disabled={loading}
              className="btn-skip"
            >
              Skip for now
            </button>
          </div>

          <p className="modal-note">
            You can still use the app without GitHub by cloning repositories via URL
          </p>
        </div>
      </div>
    </div>
  );
}

export default GitHubConnect;
