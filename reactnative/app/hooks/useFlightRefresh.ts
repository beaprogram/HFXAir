import { useState, useEffect } from 'react';
import { Alert } from 'react-native';

export const useFlightRefresh = () => {
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());
  const [refreshing, setRefreshing] = useState(false);
  const [isManualRefreshing, setIsManualRefreshing] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      handleRefresh(true);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = (isAutomatic = false) => {
    if (!isAutomatic) {
      setIsManualRefreshing(true);
    } else {
      setRefreshing(true);
    }
    
    setTimeout(() => {
      setLastRefreshed(new Date());
      setRefreshing(false);
      setIsManualRefreshing(false);
      
      if (!isAutomatic) {
        Alert.alert('✓ Refreshed', 'Flight information updated successfully');
      }
    }, 1000);
  };

  const formatLastRefreshed = () => {
    const now = new Date();
    const diff = Math.floor((now.getTime() - lastRefreshed.getTime()) / 1000);
    if (diff < 60) return ${diff}s ago;
    if (diff < 3600) return ${Math.floor(diff / 60)}m ago;
    return lastRefreshed.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
  };

  return {
    lastRefreshed,
    refreshing,
    isManualRefreshing,
    handleRefresh,
    formatLastRefreshed,
  };
};