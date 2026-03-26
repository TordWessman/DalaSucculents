import { Link } from 'react-router-dom';

function formatPrice(value) {
  return '$' + Number(value).toFixed(2);
}

export default function ProductCard({ product }) {
  return (
    <Link to={`/products/${product.slug}`} className="product-card">
      <img src={product.image_url} alt={product.name} loading="lazy" />
      <div className="product-info">
        <div className="product-name">{product.name}</div>
        <div className="product-scientific">{product.scientific_name}</div>
        <div className="product-bottom">
          <span className="product-price">{formatPrice(product.price)}</span>
          {product.sold_out
            ? <span className="btn-sold-out">Sold Out</span>
            : <span className="btn-shop">Shop</span>
          }
        </div>
      </div>
    </Link>
  );
}
