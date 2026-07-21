import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import { useToast } from './ToastContext';

const RealTimeSyncContext = createContext();

export const RealTimeSyncProvider = ({ children }) => {
  const [tick30, setTick30] = useState(0);
  const [tick60, setTick60] = useState(0);
  const [tick120, setTick120] = useState(0);

  useEffect(() => {
    // Master Clocks
    const interval30 = setInterval(() => setTick30((t) => t + 1), 30000);
    const interval60 = setInterval(() => setTick60((t) => t + 1), 60000);
    const interval120 = setInterval(() => setTick120((t) => t + 1), 120000);

    return () => {
      clearInterval(interval30);
      clearInterval(interval60);
      clearInterval(interval120);
    };
  }, []);

  return (
    <RealTimeSyncContext.Provider value={{ tick30, tick60, tick120 }}>
      {children}
    </RealTimeSyncContext.Provider>
  );
};

/**
 * Custom hook for intelligent background polling and caching.
 * 
 * @param {Function} fetchFn - The async function that fetches data. Must return the raw data object/array.
 * @param {Array} dependencies - Array of dependencies that should trigger a hard reload (e.g. query params).
 * @param {String} priority - 'high' (30s), 'medium' (60s), 'low' (120s), or 'none'.
 * @returns {Object} { data, loading, isSyncing, error, refresh, lastUpdated }
 */
export const useDataSync = (fetchFn, dependencies = [], priority = 'medium') => {
  const context = useContext(RealTimeSyncContext);
  const { showToast } = useToast();
  
  if (!context) {
    throw new Error('useDataSync must be used within a RealTimeSyncProvider');
  }

  const { tick30, tick60, tick120 } = context;
  
  const [data, setData] = useState(null);
  // `loading` is true ONLY on the very first mount or when dependencies change (hard refresh).
  const [loading, setLoading] = useState(true);
  // `isSyncing` is true during background polling refreshes, allowing the UI to retain old data.
  const [isSyncing, setIsSyncing] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const dataRef = useRef(null);
  
  const fetchFnRef = useRef(fetchFn);
  useEffect(() => {
    fetchFnRef.current = fetchFn;
  }, [fetchFn]);

  const executeFetch = useCallback(async (isBackground = false) => {
    if (isBackground) {
      setIsSyncing(true);
    } else {
      setLoading(true);
    }
    
    try {
      const result = await fetchFnRef.current(isBackground);
      setData(result);
      dataRef.current = result;
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Data Sync Error:", err);
      // Only set hard error if we don't have data, otherwise just toast so we don't break the UI.
      if (!dataRef.current) {
        setError(err.message || "Failed to fetch data.");
      }
      
      // Prevent toast spam on 401/403s which auth context handles
      if (err?.response?.status !== 401 && err?.response?.status !== 403) {
         showToast("Live Sync Failed: " + (err.message || "Network Error"), "error");
      }
    } finally {
      if (isBackground) {
        setIsSyncing(false);
      } else {
        setLoading(false);
      }
    }
  }, [showToast]);

  // Hard fetch on mount or dependency change
  useEffect(() => {
    executeFetch(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  // Background polling based on priority tick
  useEffect(() => {
    if (priority === 'high' && tick30 > 0) executeFetch(true);
  }, [tick30, priority, executeFetch]);

  useEffect(() => {
    if (priority === 'medium' && tick60 > 0) executeFetch(true);
  }, [tick60, priority, executeFetch]);

  useEffect(() => {
    if (priority === 'low' && tick120 > 0) executeFetch(true);
  }, [tick120, priority, executeFetch]);

  return {
    data,
    loading,
    isSyncing,
    error,
    refresh: () => executeFetch(false),
    silentRefresh: () => executeFetch(true),
    lastUpdated,
    setData // Expose for optimistic updates
  };
};
