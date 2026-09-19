import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { supabase } from '../lib/supabase';
import { authService } from '../services/api';
import type { User, Shop, AuthState, LoginCredentials, RegisterData } from '../types';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  loginAsDemo: () => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    shop: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  const refreshProfile = useCallback(async () => {
    try {
      const result = await authService.getProfile();
      if (result.success && result.data) {
        const { user, shop } = result.data as { user: User; shop: Shop };
        setState(prev => ({
          ...prev,
          user,
          shop,
          isAuthenticated: true,
          isLoading: false,
        }));
      } else {
        setState(prev => ({ ...prev, isLoading: false }));
      }
    } catch {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, []);

  useEffect(() => {
    // Check initial session
    const initAuth = async () => {
      if (localStorage.getItem('vyapari_demo_mode') === 'true') {
        setState(prev => ({
          ...prev,
          token: 'demo-token-vyapari',
          isAuthenticated: true,
        }));
        await refreshProfile();
        return;
      }

      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
          setState(prev => ({
            ...prev,
            token: session.access_token,
            isAuthenticated: true,
          }));
          await refreshProfile();
        } else {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      } catch {
        setState(prev => ({ ...prev, isLoading: false }));
      }
    };

    initAuth();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (localStorage.getItem('vyapari_demo_mode') === 'true') {
        return;
      }
      if (event === 'SIGNED_IN' && session) {
        setState(prev => ({
          ...prev,
          token: session.access_token,
          isAuthenticated: true,
        }));
        await refreshProfile();
      } else if (event === 'SIGNED_OUT') {
        setState({
          user: null,
          shop: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    });

    return () => subscription.unsubscribe();
  }, [refreshProfile]);

  const loginAsDemo = async () => {
    localStorage.setItem('vyapari_demo_mode', 'true');
    setState(prev => ({
      ...prev,
      token: 'demo-token-vyapari',
      isAuthenticated: true,
      isLoading: true,
    }));
    await refreshProfile();
  };

  const login = async (credentials: LoginCredentials) => {
    localStorage.removeItem('vyapari_demo_mode');
    const { data, error } = await supabase.auth.signInWithPassword({
      email: credentials.email,
      password: credentials.password,
    });
    if (error) throw new Error(error.message);
    if (data.session) {
      setState(prev => ({
        ...prev,
        token: data.session!.access_token,
        isAuthenticated: true,
      }));
      await refreshProfile();
    }
  };

  const register = async (registerData: RegisterData) => {
    localStorage.removeItem('vyapari_demo_mode');
    // First create Supabase Auth user
    const { data, error } = await supabase.auth.signUp({
      email: registerData.email,
      password: registerData.password,
      options: {
        data: {
          full_name: registerData.full_name,
          phone: registerData.phone,
        },
      },
    });
    if (error) throw new Error(error.message);

    if (data.session) {
      // Then register in our backend (creates user profile, shop, seed data)
      await authService.register({
        email: registerData.email,
        password: registerData.password,
        full_name: registerData.full_name,
        phone: registerData.phone,
        shop_name: registerData.shop_name,
        shop_type: registerData.shop_type,
      });

      setState(prev => ({
        ...prev,
        token: data.session!.access_token,
        isAuthenticated: true,
      }));
      await refreshProfile();
    }
  };

  const logout = async () => {
    localStorage.removeItem('vyapari_demo_mode');
    try {
      await supabase.auth.signOut();
    } catch {
      // ignore
    }
    setState({
      user: null,
      shop: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  };

  return (
    <AuthContext.Provider value={{ ...state, login, loginAsDemo, register, logout, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
