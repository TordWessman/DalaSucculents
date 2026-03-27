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
    getPlantImages: (slug) => fetchJSON('/plants/' + encodeURIComponent(slug) + '/images').then(data => data.results),
    uploadPlantImage: async (slug, file, caption) => {
      const form = new FormData();
      form.append('file', file);
      if (caption) form.append('caption', caption);
      const res = await fetch(base + '/plants/' + encodeURIComponent(slug) + '/images', {
        method: 'POST',
        body: form,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || 'Upload failed: ' + res.status);
      }
      return res.json().then(data => data.result);
    },
    deletePlantImage: async (slug, imageId) => {
      const res = await fetch(base + '/plants/' + encodeURIComponent(slug) + '/images/' + imageId, {
        method: 'DELETE',
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || 'Delete failed: ' + res.status);
      }
      return res.json();
    },
  };
}
