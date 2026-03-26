import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { DataProvider } from './services/DataContext';
import { createApiDataService } from './services/ApiDataService';
import App from './App';
import './style.css';

const service = createApiDataService();

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <DataProvider service={service}>
        <App />
      </DataProvider>
    </BrowserRouter>
  </StrictMode>,
);
