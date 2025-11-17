/**
 * Layout component.
 *
 * Provides common layout with header, navigation, and main content area.
 */

import React from 'react';
import {
  Box,
  Flex,
  Heading,
  Button,
  Container,
  HStack,
  Text,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box minH="100vh" bg="gray.50">
      {/* Header */}
      <Box bg="white" borderBottom="1px" borderColor="gray.200" py={4}>
        <Container maxW="container.xl">
          <Flex justify="space-between" align="center">
            <HStack spacing={3}>
              <Heading size="md" color="blue.600">
                Temporal Release Manager
              </Heading>
            </HStack>

            <HStack spacing={4}>
              {user && (
                <>
                  <Text fontSize="sm" color="gray.600">
                    {user.email}
                  </Text>
                  <Menu>
                    <MenuButton
                      as={Button}
                      variant="ghost"
                      size="sm"
                      rounded="full"
                      p={0}
                    >
                      <Avatar size="sm" name={user.full_name || user.email} />
                    </MenuButton>
                    <MenuList>
                      <MenuItem isDisabled>
                        <Box>
                          <Text fontWeight="semibold">{user.full_name || 'User'}</Text>
                          <Text fontSize="xs" color="gray.600">
                            {user.email}
                          </Text>
                          {user.is_admin && (
                            <Text fontSize="xs" color="blue.600" mt={1}>
                              Administrator
                            </Text>
                          )}
                        </Box>
                      </MenuItem>
                      <MenuDivider />
                      <MenuItem onClick={handleLogout} color="red.600">
                        Logout
                      </MenuItem>
                    </MenuList>
                  </Menu>
                </>
              )}
            </HStack>
          </Flex>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxW="container.xl" py={8}>
        {children}
      </Container>
    </Box>
  );
};
