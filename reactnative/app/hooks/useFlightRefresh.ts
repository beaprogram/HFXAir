import { useState, useEffect, useCallback } from "react";
import { Alert } from "react-native";

interface RefreshState {
  lastRefreshed: Date;
  refreshing: boolean;
  isManualRefreshing: boolean;
}

type RefreshStateUpdate = (prev: RefreshState) => RefreshState;

export const useFlightRefresh = () => {
  const [state, setState] = useState<RefreshState>({
    lastRefreshed: new Date(),
    refreshing: false,
    isManualRefreshing: false,
  });

  const handleRefresh = useCallback(async (isAutomatic = false) => {
    let timeoutId: ReturnType<typeof setTimeout>;
    let cleanupCalled = false;

    const cleanup = () => {
      if (timeoutId && !cleanupCalled) {
        clearTimeout(timeoutId);
        cleanupCalled = true;
      }
    };

    try {
      if (!isAutomatic) {
        setState((prev: RefreshState) => ({
          ...prev,
          isManualRefreshing: true,
        }));
      } else {
        setState((prev: RefreshState) => ({ ...prev, refreshing: true }));
      }

      // Simulating refresh operation
      await new Promise<void>((resolve, reject) => {
        timeoutId = setTimeout(() => {
          try {
            setState((prev: RefreshState) => ({
              ...prev,
              lastRefreshed: new Date(),
              refreshing: false,
              isManualRefreshing: false,
            }));

            if (!isAutomatic) {
              Alert.alert(
                "✓ Refreshed",
                "Flight information updated successfully"
              );
            }
            resolve();
          } catch (err) {
            reject(err);
          }
        }, 1000);
      });
    } catch (error) {
      setState((prev: RefreshState) => ({
        ...prev,
        refreshing: false,
        isManualRefreshing: false,
      }));
      Alert.alert("Error", "Failed to refresh flight information");
    } finally {
      cleanup();
    }

    return cleanup;
  }, []);

  const formatLastRefreshed = useCallback(() => {
    const now = new Date();
    const diff = Math.floor(
      (now.getTime() - state.lastRefreshed.getTime()) / 1000
    );
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return state.lastRefreshed.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  }, [state.lastRefreshed]);

  useEffect(() => {
    const interval = setInterval(() => {
      handleRefresh(true);
    }, 30000);

    return () => clearInterval(interval);
  }, [handleRefresh]);

  return {
    lastRefreshed: state.lastRefreshed,
    refreshing: state.refreshing,
    isManualRefreshing: state.isManualRefreshing,
    handleRefresh,
    formatLastRefreshed,
  };
};
