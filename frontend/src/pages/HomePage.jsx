import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <section className="hero">
      <h1>Dala Succulents</h1>
      <p className="hero-tagline">
        Specializing in rare and unusual succulents, cacti, and caudiciform plants since 2020.
      </p>
      <p className="hero-about">
        We offer a hand-curated collection of uncommon plants sourced from trusted growers
        around the world. Every plant is carefully inspected and shipped with care to collectors
        and enthusiasts nationwide.
      </p>
      <Link to="/plants" className="hero-cta">Browse Plants</Link>
    </section>
  );
}
