/**
 * Authentication service for login, logout, and token management.
 *
 * Handles user authentication and stores JWT tokens in localStorage.
 */

import apiClient from './api';
import { User, Token, LoginCredentials } from '../types/auth';

const TOKEN_KEY = 'access_token';
const USER_KEY = 'user';

class AuthService {
  /**
   * Login with email and password.
   *
   * @param credentials - Login credentials (email and password)
   * @returns Token response with access token
   */
  async login(credentials: LoginCredentials): Promise<Token> {
    // Use FormData for OAuth2 password flow
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await apiClient.post<Token>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const token = response.data;

    // Store token in localStorage
    this.setToken(token.access_token);

    // Fetch and store user info
    const user = await this.getCurrentUser();
    this.setUser(user);

    return token;
  }

  /**
   * Logout and clear stored credentials.
   */
  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  /**
   * Get current authenticated user from API.
   *
   * @returns Current user information
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  }

  /**
   * Get stored JWT token.
   *
   * @returns JWT token or null if not found
   */
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  /**
   * Store JWT token in localStorage.
   *
   * @param token - JWT access token
   */
  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  }

  /**
   * Get stored user from localStorage.
   *
   * @returns User object or null if not found
   */
  getUser(): User | null {
    const userStr = localStorage.getItem(USER_KEY);
    if (!userStr) return null;

    try {
      return JSON.parse(userStr) as User;
    } catch (error) {
      console.error('Error parsing stored user:', error);
      return null;
    }
  }

  /**
   * Store user in localStorage.
   *
   * @param user - User object to store
   */
  setUser(user: User): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  /**
   * Check if user is authenticated.
   *
   * @returns True if token exists, false otherwise
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }
}

// Export singleton instance
const authService = new AuthService();
export default authService;
