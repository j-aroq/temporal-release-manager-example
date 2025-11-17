/**
 * Release Detail page.
 *
 * Shows the complete hierarchy for a single release with all child entities.
 */

import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Heading,
  Text,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Button,
  HStack,
  VStack,
  Badge,
  Tooltip,
  IconButton,
} from '@chakra-ui/react';
import { ArrowBackIcon, RepeatIcon } from '@chakra-ui/icons';
import { Layout } from '../components/Layout';
import { EntityTree } from '../components/EntityTree';
import apiClient from '../services/api';

interface ReleaseHierarchy {
  id: string;
  state: string;
  workflow_id: string;
  wave_ids: string[];
  waves: any[];
  updated_at?: string;
}

const getStateColor = (state: string): string => {
  const stateLower = state.toLowerCase();
  if (stateLower.includes('complet')) return 'green';
  if (stateLower.includes('fail') || stateLower.includes('error')) return 'red';
  if (stateLower.includes('terminated')) return 'orange';  // Terminated externally
  if (stateLower.includes('cancelled') || stateLower.includes('cancel')) return 'purple';
  if (stateLower.includes('timed_out') || stateLower.includes('timeout')) return 'orange';
  if (stateLower.includes('progress') || stateLower.includes('running')) return 'blue';
  if (stateLower.includes('deploy')) return 'cyan';
  if (stateLower.includes('pend')) return 'yellow';
  return 'gray';
};

export const ReleaseDetailPage: React.FC = () => {
  const { releaseId } = useParams<{ releaseId: string }>();
  const navigate = useNavigate();
  const [hierarchy, setHierarchy] = useState<ReleaseHierarchy | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAutoRefreshEnabled, setIsAutoRefreshEnabled] = useState(true);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchHierarchy = useCallback(async () => {
    if (!releaseId) {
      setError('No release ID provided');
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const response = await apiClient.get(`/releases/${releaseId}/hierarchy`);
      setHierarchy(response.data);
    } catch (err: any) {
      console.error('Error fetching release hierarchy:', err);
      const errorMessage =
        err.response?.data?.detail || 'Failed to load release hierarchy. Please try again.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [releaseId]);

  const toggleAutoRefresh = useCallback(() => {
    setIsAutoRefreshEnabled((prev) => !prev);
  }, []);

  // Initial fetch on mount
  useEffect(() => {
    fetchHierarchy();
  }, [fetchHierarchy]);

  // Set up auto-refresh polling
  useEffect(() => {
    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Set up new interval if auto-refresh is enabled
    if (isAutoRefreshEnabled) {
      intervalRef.current = setInterval(() => {
        fetchHierarchy();
      }, 10000); // 10 seconds
    }

    // Cleanup on unmount or when dependencies change
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isAutoRefreshEnabled, fetchHierarchy]);

  const handleBack = () => {
    navigate('/');
  };

  const handleRetry = () => {
    window.location.reload();
  };

  if (isLoading) {
    return (
      <Layout>
        <VStack spacing={4} justify="center" minH="400px">
          <Spinner size="xl" color="blue.500" thickness="4px" />
          <Text color="gray.600">Loading release hierarchy...</Text>
        </VStack>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <Alert
          status="error"
          variant="subtle"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          textAlign="center"
          minH="400px"
        >
          <AlertIcon boxSize="40px" mr={0} />
          <AlertTitle mt={4} mb={1} fontSize="lg">
            Unable to Load Release
          </AlertTitle>
          <AlertDescription maxW="md">
            {error}
          </AlertDescription>
          <HStack mt={4} spacing={3}>
            <Button colorScheme="blue" onClick={handleRetry}>
              Retry
            </Button>
            <Button variant="outline" onClick={handleBack}>
              Back to List
            </Button>
          </HStack>
        </Alert>
      </Layout>
    );
  }

  if (!hierarchy) {
    return (
      <Layout>
        <Alert status="warning">
          <AlertIcon />
          Release not found
        </Alert>
        <Button mt={4} leftIcon={<ArrowBackIcon />} onClick={handleBack}>
          Back to List
        </Button>
      </Layout>
    );
  }

  return (
    <Layout>
      <VStack align="stretch" spacing={6}>
        <Box>
          <Button
            leftIcon={<ArrowBackIcon />}
            variant="ghost"
            onClick={handleBack}
            mb={4}
          >
            Back to Releases
          </Button>

          <HStack justify="space-between" align="start">
            <Box>
              <Heading size="lg" mb={2}>
                Release Details
              </Heading>
              <HStack spacing={3}>
                <Text fontSize="xl" fontWeight="medium" color="gray.700">
                  {hierarchy.id}
                </Text>
                <Badge colorScheme={getStateColor(hierarchy.state)} fontSize="md" px={3} py={1}>
                  {hierarchy.state}
                </Badge>
              </HStack>
              {hierarchy.updated_at && (
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Last updated: {new Date(hierarchy.updated_at).toLocaleString()}
                </Text>
              )}
              {isAutoRefreshEnabled && (
                <Badge colorScheme="green" fontSize="xs" px={2} py={1} mt={2}>
                  Auto-refreshing every 10 seconds
                </Badge>
              )}
            </Box>
            <HStack spacing={2}>
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
                  aria-label="Refresh hierarchy"
                  icon={<RepeatIcon />}
                  size="sm"
                  onClick={() => fetchHierarchy()}
                  isLoading={isLoading}
                  colorScheme="blue"
                />
              </Tooltip>
            </HStack>
          </HStack>
        </Box>

        <Box
          p={6}
          borderWidth={1}
          borderRadius="lg"
          boxShadow="sm"
          bg="white"
        >
          <Heading size="md" mb={4}>
            Entity Hierarchy
          </Heading>
          <Text color="gray.600" mb={4}>
            Complete deployment tree with all waves, clusters, bundles, and apps
          </Text>

          <Box
            p={4}
            bg="gray.50"
            borderRadius="md"
            maxH="600px"
            overflowY="auto"
          >
            <EntityTree hierarchy={hierarchy} />
          </Box>
        </Box>

        <Box
          p={4}
          bg="blue.50"
          borderRadius="md"
          borderLeft="4px"
          borderColor="blue.500"
        >
          <Text fontSize="sm" color="gray.700">
            <strong>Tip:</strong> Click on any entity with a chevron icon to expand or collapse its children.
            Color-coded badges indicate the current state of each entity.
          </Text>
        </Box>
      </VStack>
    </Layout>
  );
};
