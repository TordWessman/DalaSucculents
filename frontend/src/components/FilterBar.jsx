export default function FilterBar({ filters, activeFilters, onFilterChange }) {
  if (!filters) return null;

  function handleChange(key, value) {
    onFilterChange({ ...activeFilters, [key]: value });
  }

  return (
    <div className="filter-bar">
      <select
        value={activeFilters.family || ''}
        onChange={e => handleChange('family', e.target.value)}
        aria-label="Filter by family"
      >
        <option value="">All families</option>
        {(filters.family || []).map(f => (
          <option key={f} value={f}>{f}</option>
        ))}
      </select>

      <select
        value={activeFilters.genus || ''}
        onChange={e => handleChange('genus', e.target.value)}
        aria-label="Filter by genus"
      >
        <option value="">All genera</option>
        {(filters.genus || []).map(g => (
          <option key={g} value={g}>{g}</option>
        ))}
      </select>

      <select
        value={activeFilters.vegetation_period || ''}
        onChange={e => handleChange('vegetation_period', e.target.value)}
        aria-label="Filter by vegetation period"
      >
        <option value="">All seasons</option>
        {(filters.vegetation_period || []).map(v => (
          <option key={v} value={v}>{v}</option>
        ))}
      </select>

      {Object.values(activeFilters).some(Boolean) && (
        <button
          className="filter-clear"
          onClick={() => onFilterChange({ family: '', genus: '', vegetation_period: '' })}
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
