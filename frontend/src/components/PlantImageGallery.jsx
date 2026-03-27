import { useState, useRef } from 'react';
import { useDataService } from '../services/DataContext';

export default function PlantImageGallery({ images: initialImages, slug, canUpload }) {
  const dataService = useDataService();
  const [images, setImages] = useState(initialImages || []);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [caption, setCaption] = useState('');
  const fileRef = useRef(null);

  async function handleUpload(e) {
    e.preventDefault();
    const file = fileRef.current?.files[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    try {
      const newImage = await dataService.uploadPlantImage(slug, file, caption);
      setImages(prev => [...prev, newImage]);
      setCaption('');
      fileRef.current.value = '';
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(imageId) {
    setError(null);
    try {
      await dataService.deletePlantImage(slug, imageId);
      setImages(prev => prev.filter(img => img.id !== imageId));
    } catch (err) {
      setError(err.message);
    }
  }

  if (!canUpload && images.length === 0) return null;

  return (
    <section className="plant-section plant-image-gallery">
      <h2>Images</h2>

      {error && <p className="plant-image-error">{error}</p>}

      {images.length > 0 && (
        <div className="plant-image-grid">
          {images.map(img => (
            <div key={img.id} className="plant-image-item">
              <a href={img.image_url} target="_blank" rel="noopener noreferrer">
                <img src={img.image_url} alt={img.caption || 'Plant image'} />
              </a>
              {img.caption && <p className="plant-image-caption">{img.caption}</p>}
              {canUpload && (
                <button
                  className="plant-image-delete"
                  onClick={() => handleDelete(img.id)}
                  title="Delete image"
                >
                  X
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {canUpload && (
        <form className="plant-image-upload" onSubmit={handleUpload}>
          <input
            type="file"
            ref={fileRef}
            accept="image/jpeg,image/png,image/webp"
            required
          />
          <input
            type="text"
            value={caption}
            onChange={e => setCaption(e.target.value)}
            placeholder="Caption (optional)"
            className="plant-image-caption-input"
          />
          <button type="submit" disabled={uploading} className="btn-shop">
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </form>
      )}
    </section>
  );
}
