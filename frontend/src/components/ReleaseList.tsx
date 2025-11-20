/**
 * Release list component.
 *
 * Displays list of releases in a table with pagination.
 */

import React from 'react';
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Button,
  HStack,
  Text,
  Box,
  Link,
  Badge,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { Release } from '../types/entities';

interface ReleaseListProps {
  releases: Release[];
  total: number;
  page: number;
  pageSize: number;
  isLoading: boolean;
  error: string | null;
  onRetry: () => void;
  onPageChange: (page: number) => void;
}

export const ReleaseList: React.FC<ReleaseListProps> = ({
  releases,
  total,
  page,
  pageSize,
  isLoading,
  error,
  onRetry,
  onPageChange,
}) => {
  const totalPages = Math.ceil(total / pageSize);

  // Format date for display
  const formatDate = (dateStr?: string): string => {
    if (!dateStr) return 'N/A';
    try {
      const date = new Date(dateStr);
      return date.toLocaleString();
    } catch {
      return dateStr;
    }
  };

  // Get color scheme for state badge
  const getStateColor = (state: string): string => {
    const lowerState = state.toLowerCase();
    if (lowerState.includes('complete') || lowerState.includes('success')) return 'green';
    if (lowerState.includes('fail') || lowerState.includes('error')) return 'red';
    if (lowerState.includes('terminated')) return 'orange';  // Terminated by external action
    if (lowerState.includes('cancelled') || lowerState.includes('cancel')) return 'purple';
    if (lowerState.includes('timed_out') || lowerState.includes('timeout')) return 'orange';
    if (lowerState.includes('progress') || lowerState.includes('running')) return 'blue';
    if (lowerState.includes('deploying')) return 'cyan';
    if (lowerState.includes('pending') || lowerState.includes('waiting')) return 'yellow';
    return 'gray';
  };

  if (isLoading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4} color="gray.600">
          Loading releases...
        </Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error" variant="subtle" flexDirection="column" py={8}>
        <AlertIcon boxSize="40px" mr={0} />
        <AlertTitle mt={4} mb={1} fontSize="lg">
          Error Loading Releases
        </AlertTitle>
        <AlertDescription maxWidth="sm" textAlign="center">
          {error}
        </AlertDescription>
        <Button mt={4} onClick={onRetry} colorScheme="red" variant="outline">
          Retry
        </Button>
      </Alert>
    );
  }

  if (releases.length === 0) {
    return (
      <Alert status="info" variant="subtle">
        <AlertIcon />
        <AlertTitle mr={2}>No Releases Found</AlertTitle>
        <AlertDescription>
          There are currently no releases being tracked.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Box>
      <TableContainer>
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Release ID</Th>
              <Th>State</Th>
              <Th>Workflow ID</Th>
              <Th>Waves</Th>
              <Th>Updated</Th>
            </Tr>
          </Thead>
          <Tbody>
            {releases.map((release) => (
              <Tr key={release.id} _hover={{ bg: 'gray.50' }} role="row">
                <Td role="cell">
                  <Link
                    as={RouterLink}
                    to={`/releases/${release.id}`}
                    color="blue.600"
                    fontWeight="medium"
                    _hover={{ textDecoration: 'underline' }}
                    aria-label={`View details for ${release.id}`}
                  >
                    {release.id}
                  </Link>
                </Td>
                <Td>
                  <Badge colorScheme={getStateColor(release.state)}>
                    {release.state}
                  </Badge>
                </Td>
                <Td fontSize="sm" color="gray.600">
                  {release.workflow_id}
                </Td>
                <Td>{release.wave_ids.length}</Td>
                <Td fontSize="sm" color="gray.600">
                  {formatDate(release.updated_at)}
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {totalPages > 1 && (
        <HStack justify="space-between" mt={6} px={4}>
          <Text fontSize="sm" color="gray.600">
            Page {page} of {totalPages} ({total} total releases)
          </Text>
          <HStack spacing={2}>
            <Button
              size="sm"
              onClick={() => onPageChange(page - 1)}
              isDisabled={page === 1}
            >
              Previous
            </Button>
            <Button
              size="sm"
              onClick={() => onPageChange(page + 1)}
              isDisabled={page === totalPages}
            >
              Next
            </Button>
          </HStack>
        </HStack>
      )}
    </Box>
  );
};
