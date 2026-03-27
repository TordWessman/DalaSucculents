export function createD1DataService(baseUrl) {
  const base = baseUrl || '/api';

  async function fetchJSON(url) {
    const res = await fetch(base + url, {
      cache: 'default',
      headers: {
        'Cache-Control': 'public, max-age=300, stale-while-revalidate=60',
      },
    });
    if (!res.ok) throw new Error('API error: ' + res.status);
    return res.json();
  }

  return {
    getPlants: () => fetchJSON('/plants').then(data => data.results),
    getPlant: (slug) => fetchJSON('/plants/' + encodeURIComponent(slug)).then(data => data.result),
    getFilters: () => fetchJSON('/filters').then(({ success, ...filters }) => filters),
  };
}
