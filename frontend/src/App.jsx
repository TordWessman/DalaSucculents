import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ProductPage from './pages/ProductPage';
import PlantIndexPage from './pages/PlantIndexPage';
import PlantProfilePage from './pages/PlantProfilePage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/plants" element={<PlantIndexPage />} />
        <Route path="/plants/:slug" element={<PlantProfilePage />} />
        <Route path="/products/:slug" element={<ProductPage />} />
      </Route>
    </Routes>
  );
}
