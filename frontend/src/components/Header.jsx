import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';

export default function Header({ onMenuToggle }) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const { user, loading, login, logout } = useAuth();
  const googleBtnRef = useRef(null);
  const dropdownRef = useRef(null);

  // Render Google Sign-In button when not logged in
  useEffect(() => {
    if (loading || user || !googleBtnRef.current) return;
    if (!window.google?.accounts?.id) {
      const interval = setInterval(() => {
        if (window.google?.accounts?.id) {
          clearInterval(interval);
          initGoogleButton();
        }
      }, 100);
      return () => clearInterval(interval);
    }
    initGoogleButton();

    function initGoogleButton() {
      const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
      if (!clientId) return;
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleCredentialResponse,
      });
      window.google.accounts.id.renderButton(googleBtnRef.current, {
        type: 'icon',
        shape: 'circle',
        size: 'medium',
      });
    }
  }, [loading, user]);

  // Close dropdown on outside click
  useEffect(() => {
    if (!dropdownOpen) return;
    function handleClick(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [dropdownOpen]);

  async function handleCredentialResponse(response) {
    await login(response.credential);
  }

  async function handleSignOut() {
    setDropdownOpen(false);
    await logout();
    window.google?.accounts?.id?.disableAutoSelect();
  }

  function renderAuthBadge() {
    if (loading) return null;

    if (!user) {
      return <div ref={googleBtnRef} className="auth-badge" />;
    }

    return (
      <div className="auth-badge" ref={dropdownRef}>
        <button
          className="auth-avatar-btn"
          onClick={() => setDropdownOpen(prev => !prev)}
          aria-label="Account menu"
        >
          <img
            src={user.picture_url}
            alt={user.name}
            className="auth-avatar"
            referrerPolicy="no-referrer"
          />
          {user.role === 'admin' && <span className="auth-admin-dot" />}
        </button>
        <span className="auth-role-label">{user.role}</span>
        {dropdownOpen && (
          <div className="auth-dropdown">
            <div className="auth-dropdown-name">{user.name}</div>
            <div className="auth-dropdown-role">
              {user.role === 'admin' ? 'Admin' : 'User'}
            </div>
            <button className="auth-dropdown-signout" onClick={handleSignOut}>
              Sign Out
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <header className="header">
      <div className="header-inner">
        <button
          className="menu-toggle"
          onClick={onMenuToggle}
          aria-label="Toggle menu"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
        <Link to="/" className="brand">Dala Succulents</Link>
        <div className="header-icons">
          {renderAuthBadge()}
        </div>
      </div>
    </header>
  );
}
