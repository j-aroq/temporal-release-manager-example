/**
 * EntityTree component for displaying release hierarchy.
 *
 * Shows the complete tree structure: Release → Waves → Clusters → Bundles → Apps
 * with expand/collapse functionality and state badges.
 */

import React, { useState, memo, useMemo } from 'react';
import {
  Box,
  Text,
  Badge,
  VStack,
  HStack,
  Collapse,
  IconButton,
  useColorModeValue,
} from '@chakra-ui/react';
import { ChevronDownIcon, ChevronRightIcon } from '@chakra-ui/icons';

interface Entity {
  id: string;
  state: string;
  workflow_id: string;
}

interface App extends Entity {
  bundle_id: string;
}

interface Bundle extends Entity {
  cluster_id: string;
  app_ids: string[];
  apps?: App[];
}

interface Cluster extends Entity {
  wave_id: string;
  bundle_id?: string | null;
  bundle?: Bundle | null;
}

interface Wave extends Entity {
  release_id: string;
  cluster_ids: string[];
  clusters?: Cluster[];
}

interface Release extends Entity {
  wave_ids: string[];
  waves?: Wave[];
}

interface ReleaseHierarchy extends Release {
  waves: Wave[];
}

interface EntityTreeProps {
  hierarchy: ReleaseHierarchy;
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

const EntityNode: React.FC<{
  label: string;
  id: string;
  state: string;
  level: number;
  children?: React.ReactNode;
  hasChildren?: boolean;
}> = memo(({ label, id, state, level, children, hasChildren = false }) => {
  const [isOpen, setIsOpen] = useState(true);
  const bgColor = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const indent = useMemo(() => level * 24, [level]);
  const stateColor = useMemo(() => getStateColor(state), [state]);

  return (
    <Box>
      <HStack
        spacing={2}
        p={2}
        pl={`${indent + 8}px`}
        _hover={{ bg: bgColor }}
        borderRadius="md"
        cursor={hasChildren ? 'pointer' : 'default'}
        onClick={() => hasChildren && setIsOpen(!isOpen)}
      >
        {hasChildren && (
          <IconButton
            aria-label={isOpen ? 'Collapse' : 'Expand'}
            icon={isOpen ? <ChevronDownIcon /> : <ChevronRightIcon />}
            size="xs"
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation();
              setIsOpen(!isOpen);
            }}
          />
        )}
        {!hasChildren && <Box w="24px" />}

        <Text fontWeight="medium" fontSize="sm">
          {label}:
        </Text>
        <Text fontSize="sm" color="gray.600">
          {id}
        </Text>
        <Badge colorScheme={stateColor} fontSize="xs">
          {state}
        </Badge>
      </HStack>

      {hasChildren && (
        <Collapse in={isOpen} animateOpacity>
          <Box borderLeft="1px" borderColor={borderColor} ml={`${indent + 8}px`} pl={2}>
            {children}
          </Box>
        </Collapse>
      )}
    </Box>
  );
});

EntityNode.displayName = 'EntityNode';

export const EntityTree: React.FC<EntityTreeProps> = memo(({ hierarchy }) => {
  return (
    <VStack align="stretch" spacing={1}>
      <EntityNode
        label="Release"
        id={hierarchy.id}
        state={hierarchy.state}
        level={0}
        hasChildren={(hierarchy.waves?.length ?? 0) > 0}
      >
        {hierarchy.waves?.map((wave) => (
          <EntityNode
            key={wave.id}
            label="Wave"
            id={wave.id}
            state={wave.state}
            level={1}
            hasChildren={(wave.clusters?.length ?? 0) > 0}
          >
            {wave.clusters?.map((cluster) => (
              <EntityNode
                key={cluster.id}
                label="Cluster"
                id={cluster.id}
                state={cluster.state}
                level={2}
                hasChildren={!!cluster.bundle}
              >
                {cluster.bundle && (
                  <EntityNode
                    label="Bundle"
                    id={cluster.bundle.id}
                    state={cluster.bundle.state}
                    level={3}
                    hasChildren={(cluster.bundle.apps?.length ?? 0) > 0}
                  >
                    {cluster.bundle.apps?.map((app) => (
                      <EntityNode
                        key={app.id}
                        label="App"
                        id={app.id}
                        state={app.state}
                        level={4}
                        hasChildren={false}
                      />
                    ))}
                  </EntityNode>
                )}
              </EntityNode>
            ))}
          </EntityNode>
        ))}
      </EntityNode>
    </VStack>
  );
});

EntityTree.displayName = 'EntityTree';
