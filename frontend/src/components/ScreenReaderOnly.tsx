/**
 * Screen reader only component for accessibility.
 *
 * Hides content visually but keeps it accessible to screen readers.
 */

import React, { ReactNode } from 'react';
import { Box } from '@chakra-ui/react';

interface ScreenReaderOnlyProps {
  children: ReactNode;
  id?: string;
}

export const ScreenReaderOnly: React.FC<ScreenReaderOnlyProps> = ({ children, id }) => {
  return (
    <Box
      id={id}
      position="absolute"
      width="1px"
      height="1px"
      padding="0"
      margin="-1px"
      overflow="hidden"
      clip="rect(0, 0, 0, 0)"
      whiteSpace="nowrap"
      border="0"
    >
      {children}
    </Box>
  );
};
