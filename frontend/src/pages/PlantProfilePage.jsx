import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDataService } from '../services/DataContext';
import { useAuth } from '../services/AuthContext';
import { formatBotanicalName } from '../utils/botanicalName';
import CultivationTable from '../components/CultivationTable';
import SpecimenList from '../components/SpecimenList';
import PlantImageGallery from '../components/PlantImageGallery';

export default function PlantProfilePage() {
  const { slug } = useParams();
  const dataService = useDataService();
  const { user } = useAuth();
  const [plant, setPlant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    dataService.getPlant(slug)
      .then(data => {
        if (cancelled) return;
        setPlant(data);
        setError(null);
      })
      .catch(err => {
        if (cancelled) return;
        setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [dataService, slug]);

  if (loading) return <div className="section"><p>Loading...</p></div>;
  if (error) return <div className="section"><p>Error: {error}</p></div>;
  if (!plant) return <div className="section"><p>Plant not found.</p></div>;

  const nameParts = formatBotanicalName(plant);
  const canUpload = user?.role === 'admin';

  return (
    <div className="plant-profile">
      <div className="breadcrumb">
        <Link to="/plants">Plants</Link>
        <span>/</span>
        {plant.display_name}
      </div>

      <div className="plant-profile-header">
        <h1 className="botanical-name">
          {nameParts.map((part, i) => (
            part.italic
              ? <i key={i}>{part.text}</i>
              : <span key={i}>{part.text}</span>
          ))}
        </h1>
        <p className="plant-taxonomy">{plant.family} — {plant.genus}</p>
      </div>

      <PlantImageGallery images={plant.images} slug={slug} canUpload={canUpload} />

      <div className="plant-profile-body">
        <section className="plant-section">
          <h2>Cultivation</h2>
          <CultivationTable cultivation={plant.cultivation} />
        </section>

        {plant.countries && plant.countries.length > 0 && (
          <section className="plant-section">
            <h2>Distribution</h2>
            <p className="plant-countries">{plant.countries.join(', ')}</p>
          </section>
        )}

        {(plant.conservation?.red_list_status || plant.conservation?.cites_listing) && (
          <section className="plant-section">
            <h2>Conservation</h2>
            <dl className="conservation-list">
              {plant.conservation.red_list_status && (
                <>
                  <dt>IUCN Red List</dt>
                  <dd>
                    {plant.conservation.red_list_status}
                    {plant.conservation.red_list_url && (
                      <> — <a href={plant.conservation.red_list_url} target="_blank" rel="noopener noreferrer">View</a></>
                    )}
                  </dd>
                </>
              )}
              {plant.conservation.cites_listing && (
                <>
                  <dt>CITES</dt>
                  <dd>{plant.conservation.cites_listing}</dd>
                </>
              )}
            </dl>
          </section>
        )}

        {plant.conservation?.llifle_url && (
          <section className="plant-section">
            <h2>External Links</h2>
            <ul className="plant-links">
              <li><a href={plant.conservation.llifle_url} target="_blank" rel="noopener noreferrer">LLIFLE Encyclopedia</a></li>
            </ul>
          </section>
        )}

        {plant.notes && (
          <section className="plant-section">
            <h2>Notes</h2>
            <p className="plant-notes">{plant.notes}</p>
          </section>
        )}

        <SpecimenList specimens={plant.specimens} />
      </div>
    </div>
  );
}
