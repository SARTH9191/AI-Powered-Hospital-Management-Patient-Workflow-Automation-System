/**
 * Auth Hook - Simplified access to auth store
 */

import { useAuthStore } from '@/store/authStore';

export function useAuth() {
  const { user, token, isAuthenticated, setUser, setToken, logout } = useAuthStore();

  return {
    user,
    token,
    isAuthenticated,
    setUser,
    setToken,
    logout,
    role: user?.role,
    username: user?.username,
  };
}
