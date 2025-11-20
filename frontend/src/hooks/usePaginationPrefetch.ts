/**
 * Custom hook for pagination with prefetching.
 *
 * Preloads next page on hover for instant navigation.
 */

import { useCallback, useRef } from 'react';

interface UsePaginationPrefetchOptions {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  prefetchFn: (page: number) => Promise<void>;
}

interface UsePaginationPrefetchResult {
  handleNextPage: () => void;
  handlePrevPage: () => void;
  handlePrefetchNext: () => void;
  handlePrefetchPrev: () => void;
}

export const usePaginationPrefetch = ({
  currentPage,
  totalPages,
  onPageChange,
  prefetchFn,
}: UsePaginationPrefetchOptions): UsePaginationPrefetchResult => {
  const prefetchedPages = useRef<Set<number>>(new Set());

  const handlePrefetch = useCallback(
    async (page: number) => {
      // Don't prefetch if already prefetched or out of bounds
      if (
        prefetchedPages.current.has(page) ||
        page < 1 ||
        page > totalPages
      ) {
        return;
      }

      // Mark as prefetched
      prefetchedPages.current.add(page);

      // Prefetch the page
      try {
        await prefetchFn(page);
      } catch (error) {
        // Remove from prefetched if failed
        prefetchedPages.current.delete(page);
      }
    },
    [totalPages, prefetchFn]
  );

  const handleNextPage = useCallback(() => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  }, [currentPage, totalPages, onPageChange]);

  const handlePrevPage = useCallback(() => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  }, [currentPage, onPageChange]);

  const handlePrefetchNext = useCallback(() => {
    handlePrefetch(currentPage + 1);
  }, [currentPage, handlePrefetch]);

  const handlePrefetchPrev = useCallback(() => {
    handlePrefetch(currentPage - 1);
  }, [currentPage, handlePrefetch]);

  return {
    handleNextPage,
    handlePrevPage,
    handlePrefetchNext,
    handlePrefetchPrev,
  };
};
