// Zustand store for authentication state management
import { create } from 'zustand';
import { authAPI, User } from '@/lib/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  logout: () => void;
  initAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  
  // Set user and mark as authenticated
  setUser: (user) => set({ user, isAuthenticated: true, isLoading: false }),
  
  // Set token in state and localStorage
  setToken: (token) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
      
      // Decode JWT to extract user info
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const userInfo = payload.user_info || {};
        
        const user: User = {
          username: userInfo.email || payload.sub || 'user',
          email: userInfo.email || payload.sub,
          role: (userInfo.role || 'patient') as 'admin' | 'doctor' | 'staff' | 'patient',
          name: userInfo.name || null,  // ✅ Extract name from Google OAuth
        };
        
        // 🔑 CHECK FOR USER CHANGE - Clear session if different user logs in
        const previousEmail = localStorage.getItem('current_user_email');
        const currentEmail = user.email || user.username;
        
        if (previousEmail && previousEmail !== currentEmail) {
          // Different user logging in - clear old session data
          console.log('🔄 User changed from', previousEmail, 'to', currentEmail, '- clearing old session');
          localStorage.removeItem('hospital_session_id');  // Force new session
          localStorage.removeItem('hospital_patient_id');   // Clear old patient ID
        }
        
        // Store current user email for future comparison
        localStorage.setItem('current_user_email', currentEmail);
        localStorage.setItem('user', JSON.stringify(user));
        set({ token, user, isAuthenticated: true, isLoading: false });
      } catch (error) {
        console.error('Failed to decode token:', error);
        set({ token, isAuthenticated: true, isLoading: false });
      }
    } else {
      set({ token, isAuthenticated: true });
    }
  },
  
  // Logout: clear state and localStorage
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      localStorage.removeItem('current_user_email');  // Clear user email tracker
      localStorage.removeItem('hospital_session_id'); // Clear session on logout
      localStorage.removeItem('hospital_patient_id'); // Clear patient ID on logout
    }
    set({ user: null, token: null, isAuthenticated: false });
    authAPI.logout();
  },
  
  // Initialize auth from localStorage on app start
  initAuth: () => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      const userStr = localStorage.getItem('user');
      
      if (token && userStr) {
        try {
          const user = JSON.parse(userStr);
          set({ user, token, isAuthenticated: true, isLoading: false });
        } catch (error) {
          set({ isLoading: false });
        }
      } else {
        set({ isLoading: false });
      }
    }
  },
}));
