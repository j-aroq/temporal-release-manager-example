/**
 * Skeleton loading component for release list.
 *
 * Displays placeholder UI while release data is loading.
 */

import React from 'react';
import { Stack, Skeleton, Box, HStack } from '@chakra-ui/react';

interface ReleaseListSkeletonProps {
  count?: number;
}

export const ReleaseListSkeleton: React.FC<ReleaseListSkeletonProps> = ({ count = 5 }) => {
  return (
    <Stack spacing={4}>
      {Array.from({ length: count }).map((_, index) => (
        <Box key={index} p={4} borderWidth="1px" borderRadius="md" borderColor="gray.200">
          <HStack justify="space-between">
            <Stack spacing={2} flex={1}>
              <Skeleton height="20px" width="40%" />
              <Skeleton height="16px" width="60%" />
            </Stack>
            <Skeleton height="24px" width="100px" />
          </HStack>
        </Box>
      ))}
    </Stack>
  );
};
