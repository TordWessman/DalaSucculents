import { useState, useEffect } from 'react';
import { useDataService } from '../services/DataContext';
import Carousel from '../components/Carousel';
import ProductGrid from '../components/ProductGrid';

export default function HomePage() {
  const service = useDataService();
  const [products, setProducts] = useState([]);
  const [slides, setSlides] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([service.getProducts(), service.getCarouselSlides()])
      .then(([prods, slds]) => {
        setProducts(prods);
        setSlides(slds);
      })
      .finally(() => setLoading(false));
  }, [service]);

  if (loading) return <div style={{ padding: '60px 20px', textAlign: 'center' }}>Loading...</div>;

  return (
    <>
      <Carousel slides={slides} />
      <section className="section" id="shop">
        <div className="section-header">
          <h2>Best Sellers</h2>
          <p>Our most popular plants, hand-selected for collectors and beginners alike.</p>
        </div>
        <ProductGrid products={products} />
      </section>
    </>
  );
}
