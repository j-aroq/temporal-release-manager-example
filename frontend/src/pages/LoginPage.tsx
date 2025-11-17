/**
 * Login page component.
 *
 * Provides login form with authentication integration.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Box } from '@chakra-ui/react';
import { Login } from '../components/Login';
import { useAuth } from '../hooks/useAuth';

export const LoginPage: React.FC = () => {
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (credentials: { username: string; password: string }) => {
    await login(credentials);
    // Redirect to dashboard after successful login
    navigate('/');
  };

  return (
    <Container maxW="container.md" py={8}>
      <Box>
        <Login onLogin={handleLogin} isLoading={isLoading} />
      </Box>
    </Container>
  );
};
