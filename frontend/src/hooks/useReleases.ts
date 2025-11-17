/**
 * Custom React hook for fetching release list.
 *
 * Provides release list data with loading and error states.
 * Supports auto-refresh polling with configurable interval.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import releaseService from '../services/releaseService';
import { Release } from '../types/entities';

interface UseReleasesOptions {
  autoRefresh?: boolean;
  refreshInterval?: number; // milliseconds
}

interface UseReleasesResult {
  releases: Release[];
  total: number;
  page: number;
  pageSize: number;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  setPage: (page: number) => void;
  isAutoRefreshEnabled: boolean;
  toggleAutoRefresh: () => void;
}

export const useReleases = (
  initialPage: number = 1,
  initialPageSize: number = 20,
  options: UseReleasesOptions = {}
): UseReleasesResult => {
  const { autoRefresh = true, refreshInterval = 10000 } = options;
  const [releases, setReleases] = useState<Release[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(initialPage);
  const [pageSize] = useState<number>(initialPageSize);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isAutoRefreshEnabled, setIsAutoRefreshEnabled] = useState<boolean>(autoRefresh);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchReleases = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await releaseService.listReleases(page, pageSize);

      setReleases(data.items);
      setTotal(data.total);
    } catch (err: any) {
      console.error('Error fetching releases:', err);
      const errorMessage =
        err.response?.data?.detail || 'Failed to load releases. Please try again.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize]);

  const toggleAutoRefresh = useCallback(() => {
    setIsAutoRefreshEnabled((prev) => !prev);
  }, []);

  // Fetch releases on mount and when page changes
  useEffect(() => {
    fetchReleases();
  }, [fetchReleases]);

  // Set up auto-refresh polling
  useEffect(() => {
    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Set up new interval if auto-refresh is enabled
    if (isAutoRefreshEnabled && refreshInterval > 0) {
      intervalRef.current = setInterval(() => {
        fetchReleases();
      }, refreshInterval);
    }

    // Cleanup on unmount or when dependencies change
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isAutoRefreshEnabled, refreshInterval, fetchReleases]);

  return {
    releases,
    total,
    page,
    pageSize,
    isLoading,
    error,
    refetch: fetchReleases,
    setPage,
    isAutoRefreshEnabled,
    toggleAutoRefresh,
  };
};
