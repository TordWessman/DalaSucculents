import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const { user, loading, login, logout } = useAuth();
  const googleBtnRef = useRef(null);
  const dropdownRef = useRef(null);

  function toggleMenu() {
    setMenuOpen(prev => !prev);
  }

  // Render Google Sign-In button when not logged in
  useEffect(() => {
    if (loading || user || !googleBtnRef.current) return;
    if (!window.google?.accounts?.id) {
      // GIS not loaded yet — wait for it
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
    // Revoke Google session so the button reappears fresh
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
        <Link to="/" className="brand">Dala Succulents</Link>
        <nav>
          <ul className="nav-links">
            <li><Link to="/#shop">Shop</Link></li>
            <li><Link to="/#about">About</Link></li>
            <li><Link to="/#contact">Contact</Link></li>
          </ul>
        </nav>
        <div className="header-icons">
          {renderAuthBadge()}
          <button aria-label="Search">
            <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </button>
          <button aria-label="Cart">
            <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
          </button>
          <button className={`hamburger${menuOpen ? ' active' : ''}`} aria-label="Menu" onClick={toggleMenu}>
            <span></span><span></span><span></span>
          </button>
        </div>
      </div>
      <div className={`mobile-menu${menuOpen ? ' open' : ''}`} id="mobileMenu">
        <ul>
          <li><Link to="/#shop" onClick={toggleMenu}>Shop</Link></li>
          <li><Link to="/#about" onClick={toggleMenu}>About</Link></li>
          <li><Link to="/#contact" onClick={toggleMenu}>Contact</Link></li>
        </ul>
      </div>
    </header>
  );
}
