import { createContext, useContext } from 'react';

const DataContext = createContext(null);

export function DataProvider({ service, children }) {
  return <DataContext.Provider value={service}>{children}</DataContext.Provider>;
}

export function useDataService() {
  const service = useContext(DataContext);
  if (!service) throw new Error('useDataService must be used within a DataProvider');
  return service;
}
