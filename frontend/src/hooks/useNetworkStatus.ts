/**
 * Network Status Hook
 * Requirements: 21.4
 * 
 * Detects network status changes and triggers sync when online
 */

import { useState, useEffect } from 'react';

interface NetworkStatus {
  isOnline: boolean;
  wasOffline: boolean;
  effectiveType?: string;
}

export const useNetworkStatus = () => {
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>({
    isOnline: navigator.onLine,
    wasOffline: false,
    effectiveType: (navigator as any).connection?.effectiveType
  });

  useEffect(() => {
    const handleOnline = () => {
      console.log('Network: Online');
      setNetworkStatus(prev => ({
        isOnline: true,
        wasOffline: prev.wasOffline || !prev.isOnline,
        effectiveType: (navigator as any).connection?.effectiveType
      }));
    };

    const handleOffline = () => {
      console.log('Network: Offline');
      setNetworkStatus(prev => ({
        ...prev,
        isOnline: false
      }));
    };

    const handleConnectionChange = () => {
      setNetworkStatus(prev => ({
        ...prev,
        effectiveType: (navigator as any).connection?.effectiveType
      }));
    };

    // Add event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // Monitor connection type changes (if supported)
    if ((navigator as any).connection) {
      (navigator as any).connection.addEventListener('change', handleConnectionChange);
    }

    // Cleanup
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      if ((navigator as any).connection) {
        (navigator as any).connection.removeEventListener('change', handleConnectionChange);
      }
    };
  }, []);

  return networkStatus;
};
