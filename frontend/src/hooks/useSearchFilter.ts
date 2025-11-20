/**
 * Custom hook for search and filter functionality.
 *
 * Handles search term and state filtering for releases.
 */

import { useState, useMemo } from 'react';
import { Release } from '../types/entities';

interface UseSearchFilterResult {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  stateFilter: string;
  setStateFilter: (state: string) => void;
  filteredReleases: Release[];
}

export const useSearchFilter = (releases: Release[]): UseSearchFilterResult => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [stateFilter, setStateFilter] = useState<string>('all');

  const filteredReleases = useMemo(() => {
    let filtered = releases;

    // Apply search filter
    if (searchTerm.trim()) {
      const lowerSearch = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (release) =>
          release.id.toLowerCase().includes(lowerSearch) ||
          release.workflow_id.toLowerCase().includes(lowerSearch) ||
          release.state.toLowerCase().includes(lowerSearch)
      );
    }

    // Apply state filter
    if (stateFilter !== 'all') {
      filtered = filtered.filter((release) => release.state === stateFilter);
    }

    return filtered;
  }, [releases, searchTerm, stateFilter]);

  return {
    searchTerm,
    setSearchTerm,
    stateFilter,
    setStateFilter,
    filteredReleases,
  };
};
