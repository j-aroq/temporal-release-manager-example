/**
 * Login form component.
 *
 * Provides email/password login form with validation and error handling.
 */

import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputRightElement,
  IconButton,
  VStack,
  Heading,
  Text,
  Alert,
  AlertIcon,
  AlertDescription,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { LoginCredentials } from '../types/auth';

interface LoginProps {
  onLogin: (credentials: LoginCredentials) => Promise<void>;
  isLoading: boolean;
}

export const Login: React.FC<LoginProps> = ({ onLogin, isLoading }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }

    try {
      await onLogin({
        username: email, // OAuth2 uses 'username' field for email
        password,
      });
    } catch (err: any) {
      console.error('Login error:', err);
      const errorMessage =
        err.response?.data?.detail || 'Login failed. Please check your credentials.';
      setError(errorMessage);
    }
  };

  return (
    <Box
      as="form"
      onSubmit={handleSubmit}
      maxW="md"
      mx="auto"
      mt={8}
      p={6}
      borderWidth={1}
      borderRadius="lg"
      boxShadow="lg"
    >
      <VStack spacing={4} align="stretch">
        <Heading size="lg" textAlign="center">
          Login
        </Heading>

        <Text fontSize="sm" color="gray.600" textAlign="center">
          Sign in to access release management dashboard
        </Text>

        {error && (
          <Alert status="error">
            <AlertIcon />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <FormControl isRequired>
          <FormLabel>Email</FormLabel>
          <Input
            type="email"
            placeholder="admin@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            disabled={isLoading}
          />
        </FormControl>

        <FormControl isRequired>
          <FormLabel>Password</FormLabel>
          <InputGroup>
            <Input
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              disabled={isLoading}
            />
            <InputRightElement>
              <IconButton
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                onClick={() => setShowPassword(!showPassword)}
                variant="ghost"
                size="sm"
                disabled={isLoading}
              />
            </InputRightElement>
          </InputGroup>
        </FormControl>

        <Button
          type="submit"
          colorScheme="blue"
          width="full"
          isLoading={isLoading}
          loadingText="Signing in..."
        >
          Sign In
        </Button>

        <Text fontSize="xs" color="gray.500" textAlign="center" mt={4}>
          Development credentials:
          <br />
          Admin: admin@example.com / admin123
          <br />
          User: user@example.com / user123
        </Text>
      </VStack>
    </Box>
  );
};
