import { Link } from 'react-router-dom';

export default function PlantCard({ plant }) {
  return (
    <Link to={`/plants/${plant.slug}`} className="plant-card">
      {plant.image_url ? (
        <img src={plant.image_url} alt={plant.display_name} />
      ) : (
        <div className="plant-card-placeholder" />
      )}
      <div className="plant-card-info">
        <span className="plant-card-name">{plant.display_name}</span>
        <span className="plant-card-taxonomy">{plant.family}</span>
        {plant.vegetation_period && (
          <span className="plant-card-veg">{plant.vegetation_period}</span>
        )}
      </div>
    </Link>
  );
}
