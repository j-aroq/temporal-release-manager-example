/**
 * Dashboard page component.
 *
 * Main page displaying the list of releases with auto-refresh support.
 */

import React from 'react';
import { Box, Heading, Text, HStack, Button, Badge, Tooltip, IconButton, VStack } from '@chakra-ui/react';
import { RepeatIcon } from '@chakra-ui/icons';
import { Layout } from '../components/Layout';
import { ReleaseList } from '../components/ReleaseList';
import { ReleaseListSkeleton } from '../components/ReleaseListSkeleton';
import { SearchFilter } from '../components/SearchFilter';
import { ExportButtons } from '../components/ExportButtons';
import { useReleases } from '../hooks/useReleases';
import { useSearchFilter } from '../hooks/useSearchFilter';

export const Dashboard: React.FC = () => {
  const {
    releases,
    page,
    pageSize,
    isLoading,
    error,
    refetch,
    setPage,
    isAutoRefreshEnabled,
    toggleAutoRefresh,
  } = useReleases();

  // Search and filter functionality
  const {
    searchTerm,
    setSearchTerm,
    stateFilter,
    setStateFilter,
    filteredReleases,
  } = useSearchFilter(releases);

  return (
    <Layout>
      <VStack align="stretch" spacing={6}>
        <Box>
          <HStack justify="space-between" align="start" mb={4}>
            <Box>
              <Heading size="lg" mb={2}>
                Releases
              </Heading>
              <Text color="gray.600">
                View and monitor all deployment releases tracked by Temporal workflows.
              </Text>
            </Box>
            <HStack spacing={2}>
              <ExportButtons releases={filteredReleases} filename="temporal-releases" />
              <Tooltip label={isAutoRefreshEnabled ? 'Auto-refresh enabled (10s)' : 'Auto-refresh disabled'}>
                <Button
                  size="sm"
                  variant={isAutoRefreshEnabled ? 'solid' : 'outline'}
                  colorScheme={isAutoRefreshEnabled ? 'green' : 'gray'}
                  onClick={toggleAutoRefresh}
                >
                  {isAutoRefreshEnabled ? 'Auto-refresh: ON' : 'Auto-refresh: OFF'}
                </Button>
              </Tooltip>
              <Tooltip label="Refresh now">
                <IconButton
                  aria-label="Refresh releases"
                  icon={<RepeatIcon />}
                  size="sm"
                  onClick={() => refetch()}
                  isLoading={isLoading}
                  colorScheme="blue"
                />
              </Tooltip>
            </HStack>
          </HStack>

          {isAutoRefreshEnabled && (
            <Badge colorScheme="green" fontSize="xs" px={2} py={1}>
              Auto-refreshing every 10 seconds
            </Badge>
          )}
        </Box>

        {/* Search and Filter */}
        <SearchFilter
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          stateFilter={stateFilter}
          onStateFilterChange={setStateFilter}
        />

        {/* Show skeleton while loading */}
        {isLoading && <ReleaseListSkeleton count={5} />}

        {/* Show release list when not loading */}
        {!isLoading && (
          <ReleaseList
            releases={filteredReleases}
            total={filteredReleases.length}
            page={page}
            pageSize={pageSize}
            isLoading={isLoading}
            error={error}
            onRetry={refetch}
            onPageChange={setPage}
          />
        )}
      </VStack>
    </Layout>
  );
};
