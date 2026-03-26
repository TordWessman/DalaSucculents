import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDataService } from '../services/DataContext';
import Breadcrumb from '../components/Breadcrumb';
import ProductGrid from '../components/ProductGrid';

function formatPrice(value) {
  return '$' + Number(value).toFixed(2);
}

export default function ProductPage() {
  const { slug } = useParams();
  const service = useDataService();
  const [product, setProduct] = useState(null);
  const [related, setRelated] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([service.getProduct(slug), service.getProducts()])
      .then(([prod, allProducts]) => {
        setProduct(prod);
        document.title = prod.name + ' — Dala Succulents';
        const rel = allProducts.filter(p => p.slug !== slug).slice(0, 3);
        setRelated(rel);
      })
      .finally(() => setLoading(false));
  }, [slug, service]);

  if (loading) return <div style={{ padding: '60px 20px', textAlign: 'center' }}>Loading...</div>;
  if (!product) return <div style={{ padding: '60px 20px', textAlign: 'center' }}>Product not found.</div>;

  return (
    <>
      <Breadcrumb productName={product.name} />
      <div className="product-detail">
        <div className="product-detail-image">
          <img src={product.image_url_large} alt={product.name} />
        </div>
        <div className="product-detail-info">
          <h1>{product.name}</h1>
          <div className="product-scientific">{product.scientific_name}</div>
          <span className="product-price">{formatPrice(product.price)}</span>
          <div className="description">{product.description}</div>
          {product.sold_out
            ? <span className="btn-sold-out">Sold Out</span>
            : <span className="btn-shop">Add to Cart</span>
          }
        </div>
      </div>

      {related.length > 0 && (
        <div className="related-products">
          <h2>You May Also Like</h2>
          <div className="related-grid">
            {related.map(p => (
              <Link key={p.id} to={`/products/${p.slug}`} className="product-card">
                <img src={p.image_url} alt={p.name} loading="lazy" />
                <div className="product-info">
                  <div className="product-name">{p.name}</div>
                  <div className="product-scientific">{p.scientific_name}</div>
                  <div className="product-bottom">
                    <span className="product-price">{formatPrice(p.price)}</span>
                    {p.sold_out
                      ? <span className="btn-sold-out">Sold Out</span>
                      : <span className="btn-shop">Shop</span>
                    }
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
