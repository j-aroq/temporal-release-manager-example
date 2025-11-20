/**
 * Search and filter component for releases.
 *
 * Provides search input and state filtering functionality.
 */

import React from 'react';
import {
  Input,
  InputGroup,
  InputLeftElement,
  Select,
  HStack,
  Icon,
} from '@chakra-ui/react';
import { SearchIcon } from '@chakra-ui/icons';

interface SearchFilterProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  stateFilter: string;
  onStateFilterChange: (value: string) => void;
}

export const SearchFilter: React.FC<SearchFilterProps> = ({
  searchTerm,
  onSearchChange,
  stateFilter,
  onStateFilterChange,
}) => {
  return (
    <HStack spacing={4} mb={6}>
      <InputGroup maxW="400px">
        <InputLeftElement pointerEvents="none">
          <Icon as={SearchIcon} color="gray.400" />
        </InputLeftElement>
        <Input
          placeholder="Search releases..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          aria-label="Search releases"
        />
      </InputGroup>

      <Select
        maxW="200px"
        value={stateFilter}
        onChange={(e) => onStateFilterChange(e.target.value)}
        aria-label="Filter by state"
      >
        <option value="all">All States</option>
        <option value="pending">Pending</option>
        <option value="in_progress">In Progress</option>
        <option value="deploying">Deploying</option>
        <option value="completed">Completed</option>
        <option value="failed">Failed</option>
        <option value="terminated">Terminated</option>
        <option value="cancelled">Cancelled</option>
      </Select>
    </HStack>
  );
};
