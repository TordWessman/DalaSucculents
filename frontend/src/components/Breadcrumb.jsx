import { Link } from 'react-router-dom';

export default function Breadcrumb({ productName }) {
  return (
    <div className="breadcrumb">
      <Link to="/">Home</Link>
      <span>&rsaquo;</span>
      <Link to="/#shop">Shop</Link>
      <span>&rsaquo;</span>
      {productName}
    </div>
  );
}
