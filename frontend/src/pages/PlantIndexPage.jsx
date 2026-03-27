import { useState, useEffect, useMemo } from 'react';
import { useDataService } from '../services/DataContext';
import FilterBar from '../components/FilterBar';
import PlantGrid from '../components/PlantGrid';

export default function PlantIndexPage() {
  const dataService = useDataService();
  const [plants, setPlants] = useState([]);
  const [filters, setFilters] = useState(null);
  const [activeFilters, setActiveFilters] = useState({
    family: '',
    genus: '',
    vegetation_period: '',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([dataService.getPlants(), dataService.getFilters()])
      .then(([plantData, filterData]) => {
        if (cancelled) return;
        setPlants(plantData);
        setFilters(filterData);
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
  }, [dataService]);

  const filtered = useMemo(() => {
    return plants.filter(p => {
      if (activeFilters.family && p.family !== activeFilters.family) return false;
      if (activeFilters.genus && p.genus !== activeFilters.genus) return false;
      if (activeFilters.vegetation_period && p.vegetation_period !== activeFilters.vegetation_period) return false;
      return true;
    });
  }, [plants, activeFilters]);

  if (loading) return <div className="section"><p>Loading plants...</p></div>;
  if (error) return <div className="section"><p>Error: {error}</p></div>;

  return (
    <div className="plant-index">
      <div className="section">
        <div className="section-header">
          <h2>Plants</h2>
          <p>{filtered.length} of {plants.length} plants</p>
        </div>
        <FilterBar
          filters={filters}
          activeFilters={activeFilters}
          onFilterChange={setActiveFilters}
        />
        <PlantGrid plants={filtered} />
      </div>
    </div>
  );
}
