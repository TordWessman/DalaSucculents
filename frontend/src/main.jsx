import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './services/AuthContext';
import { DataProvider } from './services/DataContext';
import { createApiDataService } from './services/ApiDataService';
import { createD1DataService } from './services/D1DataService';
import App from './App';
import './style.css';

const service = import.meta.env.VITE_DATA_BACKEND === 'cloudflare'
  ? createD1DataService()
  : createApiDataService();

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <DataProvider service={service}>
          <App />
        </DataProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);
