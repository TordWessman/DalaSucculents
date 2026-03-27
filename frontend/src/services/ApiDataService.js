export function createApiDataService(baseUrl) {
  const base = baseUrl || import.meta.env.VITE_API_BASE_URL || '/api';

  async function fetchJSON(url) {
    const res = await fetch(base + url);
    if (!res.ok) throw new Error('API error: ' + res.status);
    return res.json();
  }

  return {
    getPlants: () => fetchJSON('/plants').then(data => data.results),
    getPlant: (slug) => fetchJSON('/plants/' + encodeURIComponent(slug)).then(data => data.result),
    getFilters: () => fetchJSON('/filters').then(({ success, ...filters }) => filters),
  };
}
