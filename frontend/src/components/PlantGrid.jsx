import PlantCard from './PlantCard';

export default function PlantGrid({ plants }) {
  if (!plants.length) {
    return <p className="plant-grid-empty">No plants match your filters.</p>;
  }

  return (
    <div className="plant-grid">
      {plants.map(plant => (
        <PlantCard key={plant.id} plant={plant} />
      ))}
    </div>
  );
}
