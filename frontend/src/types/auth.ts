/**
 * TypeScript type definitions for authentication.
 *
 * Defines User and Token types matching the backend API.
 */

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginCredentials {
  username: string; // Email address (using 'username' to match OAuth2 form field)
  password: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
