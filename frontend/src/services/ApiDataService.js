export function createApiDataService(baseUrl) {
  const base = baseUrl || import.meta.env.VITE_API_BASE_URL || '/api';

  async function fetchJSON(url) {
    const res = await fetch(base + url);
    if (!res.ok) throw new Error('API error: ' + res.status);
    return res.json();
  }

  return {
    getProducts: () => fetchJSON('/products').then(data => data.results),
    getProduct: (slug) => fetchJSON('/products/' + encodeURIComponent(slug)).then(data => data.result),
    getCarouselSlides: () => fetchJSON('/carousel').then(data => data.results),
  };
}
