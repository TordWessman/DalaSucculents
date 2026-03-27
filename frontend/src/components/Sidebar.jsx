import { useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';

export default function Sidebar({ open, onClose }) {
  const location = useLocation();

  // Auto-close on navigation (mobile only — desktop stays pinned via CSS)
  useEffect(() => {
    onClose();
  }, [location.pathname]);

  return (
    <>
      {/* Overlay for mobile */}
      <div
        className={`sidebar-overlay${open ? ' visible' : ''}`}
        onClick={onClose}
      />
      <aside className={`sidebar${open ? ' open' : ''}`}>
        <div className="sidebar-header">
          <button className="sidebar-close" onClick={onClose} aria-label="Close menu">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
        <nav className="sidebar-nav">
          <ul>
            <li>
              <NavLink to="/" end>Home</NavLink>
            </li>
            <li>
              <NavLink to="/plants">Plants</NavLink>
            </li>
            <li>
              <NavLink to="/shipping-terms">Shipping &amp; Terms</NavLink>
            </li>
            <li>
              <NavLink to="/faq">FAQ</NavLink>
            </li>
            <li>
              <NavLink to="/about">About</NavLink>
            </li>
            <li>
              <NavLink to="/contact">Contact</NavLink>
            </li>
          </ul>
        </nav>
      </aside>
    </>
  );
}
