import React, { useState } from 'react';
import { createUserWithEmailAndPassword, signInWithPopup, signOut, GithubAuthProvider } from 'firebase/auth';
import { auth } from './firebase';
import './Login.css';

function Register({ onRegisterSuccess, onSwitchToLogin, onGithubToken, onStartRegistration }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');



  const handleEmailRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (!username.trim()) {
      setError('Username is required');
      setLoading(false);
      return;
    }

    try {
      // Set a flag to prevent any authentication processing in App.js
      localStorage.setItem('registering_user', 'true');
      localStorage.setItem('registration_complete', 'false');
      
      // Signal that registration is starting
      if (onStartRegistration) {
        onStartRegistration();
      }

      // Create user account (this will automatically sign them in)
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      // Store username in localStorage temporarily (can be moved to Firestore later when rules are configured)
      localStorage.setItem(`user_${user.uid}_username`, username.trim());
      
      // Mark registration as complete but keep user signed in temporarily
      localStorage.setItem('registration_complete', 'true');
      localStorage.setItem('show_registration_success', 'true');
      
      // Clear form fields
      setUsername('');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      
      // Show success message
      setSuccess('User is registered');
      
      // Sign out user and redirect after showing message
      setTimeout(async () => {
        try {
          await signOut(auth);
        } catch (signOutError) {
          console.error('Error signing out:', signOutError);
        }
        
        localStorage.removeItem('registering_user');
        localStorage.removeItem('registration_complete');
        localStorage.removeItem('show_registration_success');
        setSuccess('');
        onSwitchToLogin();
      }, 3000);
      
    } catch (err) {
      // Provide user-friendly error messages
      if (err.code === 'auth/email-already-in-use') {
        setError('This email is already registered. Please use a different email or try logging in.');
      } else if (err.code === 'auth/weak-password') {
        setError('Password is too weak. Please use at least 6 characters.');
      } else if (err.code === 'auth/invalid-email') {
        setError('Please enter a valid email address.');
      } else {
        setError(err.message);
      }
      
      localStorage.removeItem('registering_user');
      localStorage.removeItem('registration_complete');
      localStorage.removeItem('show_registration_success');
    }
    setLoading(false);
  };



  const handleGithubRegister = async () => {
    setLoading(true);
    setError('');
    const provider = new GithubAuthProvider();
    provider.addScope('repo');
    provider.addScope('user');

    try {
      // Set flags to prevent authentication processing in App.js
      localStorage.setItem('registering_user', 'true');
      localStorage.setItem('registration_complete', 'false');
      
      // Signal that registration is starting
      if (onStartRegistration) {
        onStartRegistration();
      }

      const result = await signInWithPopup(auth, provider);
      const credential = GithubAuthProvider.credentialFromResult(result);
      const token = credential.accessToken;
      const user = result.user;
      
      // Store GitHub username in localStorage temporarily (can be moved to Firestore later when rules are configured)
      const githubUsername = result.additionalUserInfo?.username || user.displayName || 'github_user';
      localStorage.setItem(`user_${user.uid}_username`, githubUsername);
      
      // Mark registration as complete
      localStorage.setItem('registration_complete', 'true');
      localStorage.setItem('show_registration_success', 'true');
      
      // Show success message
      setSuccess('User is registered');
      
      // Handle GitHub token and redirect after showing message
      setTimeout(async () => {
        if (token && onGithubToken) {
          onGithubToken(token);
        }
        
        try {
          await signOut(auth);
        } catch (signOutError) {
          console.error('Error signing out:', signOutError);
        }
        
        localStorage.removeItem('registering_user');
        localStorage.removeItem('registration_complete');
        localStorage.removeItem('show_registration_success');
        setSuccess('');
        onSwitchToLogin();
      }, 3000);
      
    } catch (err) {
      if (err.code === 'auth/account-exists-with-different-credential') {
        setError('An account already exists with this email using a different sign-in method. Please use the original sign-in method.');
      } else if (err.code === 'auth/popup-closed-by-user') {
        setError('GitHub sign-in was cancelled. Please try again.');
      } else {
        setError(err.message);
      }
      
      localStorage.removeItem('registering_user');
      localStorage.removeItem('registration_complete');
      localStorage.removeItem('show_registration_success');
    }
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <div className="auth-header">
          <button className="back-link" onClick={onSwitchToLogin}>
            ← Back to login
          </button>
          <button className="help-link">Need any help?</button>
        </div>

        <div className="auth-content">
          <h1>Register</h1>
          <p className="auth-subtitle">Create your account</p>

          <form onSubmit={handleEmailRegister}>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />

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

            <input
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              disabled={loading}
            />

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}

            <button type="submit" className="register-btn" disabled={loading || success}>
              {loading ? 'Loading...' : success ? 'Redirecting...' : 'Register'}
            </button>
          </form>

          <div className="divider">
            <span>OR</span>
          </div>

          <button className="social-btn github-btn" onClick={handleGithubRegister} disabled={loading || success}>
            <svg height="20" width="20" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            {loading ? 'Loading...' : success ? 'Redirecting...' : 'With Github'}
          </button>

          <p className="switch-auth">
            Already have an account? <span onClick={onSwitchToLogin}>Login here</span>
          </p>
        </div>


      </div>
    </div>
  );
}

export default Register;
