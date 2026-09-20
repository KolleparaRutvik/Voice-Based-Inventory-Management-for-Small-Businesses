import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { supabase } from '../lib/supabase';
import { authService } from '../services/api';
import type { User, Shop, AuthState, LoginCredentials, RegisterData } from '../types';

export type StoreTypeSlug =
  | 'kirana'
  | 'jewellery'
  | 'flowers'
  | 'clothing'
  | 'pharmacy'
  | 'bakery'
  | 'restaurant'
  | 'teacoffee'
  | 'hardware'
  | 'autoparts'
  | 'vegetables'
  | 'electronics';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  loginAsDemo: (storeType?: StoreTypeSlug) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const DEMO_STORE_TOKENS: Record<StoreTypeSlug, string> = {
  kirana: 'demo-token-kirana',
  jewellery: 'demo-token-jewellery',
  flowers: 'demo-token-flowers',
  clothing: 'demo-token-clothing',
  pharmacy: 'demo-token-pharmacy',
  bakery: 'demo-token-bakery',
  restaurant: 'demo-token-restaurant',
  teacoffee: 'demo-token-teacoffee',
  hardware: 'demo-token-hardware',
  autoparts: 'demo-token-autoparts',
  vegetables: 'demo-token-vegetables',
  electronics: 'demo-token-electronics',
};

const EMAIL_TO_STORE_TYPE: Record<string, StoreTypeSlug> = {
  'srinivas@dukaansetu.com': 'kirana',
  'jewellery@dukaansetu.com': 'jewellery',
  'flowers@dukaansetu.com': 'flowers',
  'clothing@dukaansetu.com': 'clothing',
  'pharmacy@dukaansetu.com': 'pharmacy',
  'bakery@dukaansetu.com': 'bakery',
  'restaurant@dukaansetu.com': 'restaurant',
  'teacoffee@dukaansetu.com': 'teacoffee',
  'hardware@dukaansetu.com': 'hardware',
  'autoparts@dukaansetu.com': 'autoparts',
  'vegetables@dukaansetu.com': 'vegetables',
  'electronics@dukaansetu.com': 'electronics',
};

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
      try {
        if (localStorage.getItem('dukaansetu_demo_mode') === 'true' || localStorage.getItem('vyapari_demo_mode') === 'true') {
          const demoToken = localStorage.getItem('dukaansetu_demo_token') || 'demo-token-dukaansetu';
          setState(prev => ({
            ...prev,
            token: demoToken,
            isAuthenticated: true,
          }));
          await refreshProfile();
          return;
        }

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
      if (localStorage.getItem('dukaansetu_demo_mode') === 'true' || localStorage.getItem('vyapari_demo_mode') === 'true') {
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

  const loginAsDemo = async (storeType: StoreTypeSlug = 'kirana') => {
    localStorage.setItem('dukaansetu_demo_mode', 'true');
    localStorage.setItem('dukaansetu_store_type', storeType);
    const token = DEMO_STORE_TOKENS[storeType] || 'demo-token-kirana';
    localStorage.setItem('dukaansetu_demo_token', token);
    setState(prev => ({
      ...prev,
      token,
      isAuthenticated: true,
      isLoading: true,
    }));
    await refreshProfile();
  };

  const login = async (credentials: LoginCredentials) => {
    const email = credentials.email.trim().toLowerCase();
    // Support quick login for any of the 12 specialized demo stores
    if (EMAIL_TO_STORE_TYPE[email]) {
      await loginAsDemo(EMAIL_TO_STORE_TYPE[email]);
      return;
    }
    for (const [demoEmail, storeType] of Object.entries(EMAIL_TO_STORE_TYPE)) {
      const keyword = demoEmail.split('@')[0];
      if (email.includes(keyword)) {
        await loginAsDemo(storeType);
        return;
      }
    }

    localStorage.removeItem('dukaansetu_demo_mode');
    localStorage.removeItem('vyapari_demo_mode');
    localStorage.removeItem('dukaansetu_demo_token');
    localStorage.removeItem('dukaansetu_store_type');
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
    localStorage.removeItem('dukaansetu_demo_mode');
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
    localStorage.removeItem('dukaansetu_demo_mode');
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
