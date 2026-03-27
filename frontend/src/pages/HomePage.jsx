import { useState, useEffect } from 'react';
import { useDataService } from '../services/DataContext';
import PlantGrid from '../components/PlantGrid';

export default function HomePage() {
  const service = useDataService();
  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    service.getPlants()
      .then(setPlants)
      .finally(() => setLoading(false));
  }, [service]);

  if (loading) return <div style={{ padding: '60px 20px', textAlign: 'center' }}>Loading...</div>;

  return (
    <section className="section" id="shop">
      <div className="section-header">
        <h2>Best Sellers</h2>
        <p>Our most popular plants, hand-selected for collectors and beginners alike.</p>
      </div>
      <PlantGrid plants={plants} />
    </section>
  );
}
