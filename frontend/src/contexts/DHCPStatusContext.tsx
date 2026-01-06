import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService } from '../services/api';

interface DHCPStatusContextType {
  pendingChanges: boolean;
  checkPendingChanges: () => Promise<void>;
}

const DHCPStatusContext = createContext<DHCPStatusContextType | undefined>(undefined);

export function DHCPStatusProvider({ children }: { children: ReactNode }) {
  const [pendingChanges, setPendingChanges] = useState(false);

  const checkPendingChanges = async () => {
    try {
      const status = await apiService.getDHCPStatus();
      console.log('[DHCPStatusContext] DHCP status:', status);
      setPendingChanges(status.pending_changes);
    } catch (error) {
      console.error('[DHCPStatusContext] Failed to check DHCP status:', error);
    }
  };

  // Poll every 10 seconds
  useEffect(() => {
    checkPendingChanges();
    const interval = setInterval(checkPendingChanges, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <DHCPStatusContext.Provider value={{ pendingChanges, checkPendingChanges }}>
      {children}
    </DHCPStatusContext.Provider>
  );
}

export function useDHCPStatus() {
  const context = useContext(DHCPStatusContext);
  if (context === undefined) {
    throw new Error('useDHCPStatus must be used within a DHCPStatusProvider');
  }
  return context;
}
