export default function Footer() {
  function handleSubscribe(e) {
    e.preventDefault();
    e.target.querySelector('input').value = '';
    alert('Thanks for subscribing!');
  }

  return (
    <footer className="footer" id="contact">
      <div className="footer-inner">
        <div className="footer-brand">
          <h3>Dala Succulents</h3>
          <p>Specializing in rare and unusual succulents, cacti, and caudiciform plants since 2020.</p>
        </div>
        <div className="footer-links">
          <h4>Shop</h4>
          <ul>
            <li><a href="#">All Plants</a></li>
            <li><a href="#">Succulents</a></li>
            <li><a href="#">Cacti</a></li>
            <li><a href="#">Caudiciforms</a></li>
          </ul>
        </div>
        <div className="footer-links">
          <h4>Info</h4>
          <ul>
            <li><a href="#">Shipping Policy</a></li>
            <li><a href="#">Care Guides</a></li>
            <li><a href="#">FAQ</a></li>
            <li><a href="#">Contact Us</a></li>
          </ul>
        </div>
        <div className="newsletter">
          <h4>Stay in the Loop</h4>
          <p>Get notified about new arrivals and restocks.</p>
          <form className="newsletter-form" onSubmit={handleSubscribe}>
            <input type="email" placeholder="your@email.com" required />
            <button type="submit">Join</button>
          </form>
        </div>
      </div>
      <div className="footer-bottom">
        <span>&copy; 2026 Dala Succulents. All rights reserved.</span>
        <div className="social-links">
          <a href="#" aria-label="Instagram">
            <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="5"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/></svg>
          </a>
          <a href="#" aria-label="TikTok">
            <svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.11v-3.5a6.37 6.37 0 00-.79-.05A6.34 6.34 0 003.15 15.2a6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.34-6.34V8.98a8.18 8.18 0 004.76 1.52V7.05a4.84 4.84 0 01-1-.36z"/></svg>
          </a>
          <a href="#" aria-label="Facebook">
            <svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg>
          </a>
        </div>
      </div>
    </footer>
  );
}
