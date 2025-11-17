/**
 * Custom React hook for authentication state and operations.
 *
 * Provides login, logout, and authentication state management.
 */

import { useState, useEffect, useCallback } from 'react';
import authService from '../services/authService';
import { LoginCredentials, AuthState } from '../types/auth';

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = () => {
      const token = authService.getToken();
      const user = authService.getUser();

      setAuthState({
        user,
        token,
        isAuthenticated: token !== null,
        isLoading: false,
      });
    };

    initializeAuth();
  }, []);

  // Login function
  const login = useCallback(async (credentials: LoginCredentials): Promise<void> => {
    try {
      setAuthState((prev) => ({ ...prev, isLoading: true }));

      const tokenResponse = await authService.login(credentials);
      const user = authService.getUser();

      setAuthState({
        user,
        token: tokenResponse.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      setAuthState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
      throw error;
    }
  }, []);

  // Logout function
  const logout = useCallback(() => {
    authService.logout();
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  }, []);

  // Refresh user info
  const refreshUser = useCallback(async (): Promise<void> => {
    try {
      const user = await authService.getCurrentUser();
      authService.setUser(user);
      setAuthState((prev) => ({ ...prev, user }));
    } catch (error) {
      console.error('Error refreshing user:', error);
      // If refresh fails, logout
      logout();
    }
  }, [logout]);

  return {
    user: authState.user,
    token: authState.token,
    isAuthenticated: authState.isAuthenticated,
    isLoading: authState.isLoading,
    login,
    logout,
    refreshUser,
  };
};
