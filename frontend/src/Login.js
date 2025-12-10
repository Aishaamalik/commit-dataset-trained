import React, { useState } from 'react';
import { signInWithEmailAndPassword, signInWithPopup, GithubAuthProvider } from 'firebase/auth';
import { auth } from './firebase';
import './Login.css';

function Login({ onLoginSuccess, onSwitchToRegister, onGithubToken }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await signInWithEmailAndPassword(auth, email, password);
      // Clear registration flag if it exists
      localStorage.removeItem('registering_user');
      onLoginSuccess();
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };



  const handleGithubLogin = async () => {
    setLoading(true);
    setError('');
    const provider = new GithubAuthProvider();
    provider.addScope('repo');
    provider.addScope('user');

    try {
      const result = await signInWithPopup(auth, provider);
      const credential = GithubAuthProvider.credentialFromResult(result);
      const token = credential.accessToken;
      const user = result.user;
      
      // Check if user data exists in localStorage, if not create it
      const existingUsername = localStorage.getItem(`user_${user.uid}_username`);
      if (!existingUsername) {
        const githubUsername = result.additionalUserInfo?.username || user.displayName || 'github_user';
        localStorage.setItem(`user_${user.uid}_username`, githubUsername);
      }
      
      if (token && onGithubToken) {
        onGithubToken(token);
      }
      
      // Clear registration flag if it exists
      localStorage.removeItem('registering_user');
      onLoginSuccess();
    } catch (err) {
      if (err.code === 'auth/account-exists-with-different-credential') {
        setError('An account already exists with this email using a different sign-in method. Please use the original sign-in method.');
      } else {
        setError(err.message);
      }
    }
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <div className="auth-header">
          <button className="back-link" onClick={onSwitchToRegister}>
            ← Back to register
          </button>
          <button className="help-link">Need any help?</button>
        </div>

        <div className="auth-content">
          <h1>Login</h1>
          <p className="auth-subtitle">Sign-in to continue</p>

          <form onSubmit={handleEmailLogin}>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />

            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />

            {error && <div className="error-message">{error}</div>}

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Loading...' : 'Submit'}
            </button>
          </form>

          <div className="divider">
            <span>OR</span>
          </div>

          <button className="social-btn github-btn" onClick={handleGithubLogin} disabled={loading}>
            <svg height="20" width="20" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            With Github
          </button>

          <p className="switch-auth">
            Don't have an account? <span onClick={onSwitchToRegister}>Register here</span>
          </p>
        </div>


      </div>
    </div>
  );
}

export default Login;
