/**
 * Custom hook for managing resource scans
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { scanAPI } from '@/lib/api/v2';
import { ScanStatus, ScanHistory } from '@/lib/api/types';

interface UseScanResult {
  status: ScanStatus | null;
  history: ScanHistory[];
  loading: boolean;
  error: string | null;
  triggerScan: () => Promise<void>;
  refreshStatus: () => Promise<void>;
}

/**
 * Hook to manage scan operations
 * 
 * Features:
 * - Trigger new scans
 * - Monitor scan progress
 * - Auto-refresh during active scans
 * - View scan history
 */
export function useScan(autoRefresh: boolean = true): UseScanResult {
  const [status, setStatus] = useState<ScanStatus | null>(null);
  const [history, setHistory] = useState<ScanHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch scan status
  const fetchStatus = useCallback(async () => {
    try {
      const data = await scanAPI.getStatus();
      setStatus(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch scan status');
      console.error('Error fetching scan status:', err);
    }
  }, []);

  // Fetch scan history
  const fetchHistory = useCallback(async () => {
    try {
      const data = await scanAPI.getHistory(10);
      setHistory(data);
    } catch (err) {
      console.error('Error fetching scan history:', err);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    const initialize = async () => {
      setLoading(true);
      await Promise.all([fetchStatus(), fetchHistory()]);
      setLoading(false);
    };
    initialize();
  }, [fetchStatus, fetchHistory]);

  // Auto-refresh during active scans
  useEffect(() => {
    if (!autoRefresh || !status?.is_scanning) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Refresh every 2 seconds during scan
    intervalRef.current = setInterval(() => {
      fetchStatus();
    }, 2000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, status?.is_scanning, fetchStatus]);

  // Trigger new scan
  const triggerScan = useCallback(async () => {
    try {
      setError(null);
      await scanAPI.trigger();
      // Immediately fetch new status
      await fetchStatus();
      await fetchHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger scan');
      console.error('Error triggering scan:', err);
      throw err;
    }
  }, [fetchStatus, fetchHistory]);

  // Manual refresh
  const refreshStatus = useCallback(async () => {
    await Promise.all([fetchStatus(), fetchHistory()]);
  }, [fetchStatus, fetchHistory]);

  return {
    status,
    history,
    loading,
    error,
    triggerScan,
    refreshStatus,
  };
}