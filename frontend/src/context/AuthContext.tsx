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
        const customSaved = localStorage.getItem('dukaansetu_custom_user');
        let finalUser = user;
        let finalShop = shop;
        if (customSaved) {
          try {
            const custom = JSON.parse(customSaved);
            if (custom.full_name) finalUser = { ...finalUser, full_name: custom.full_name, email: custom.email || finalUser.email };
            if (custom.shop_name) finalShop = { ...finalShop, name: custom.shop_name, type: custom.shop_type || finalShop.type };
          } catch {}
        }
        setState(prev => ({
          ...prev,
          user: finalUser,
          shop: finalShop,
          isAuthenticated: true,
          isLoading: false,
        }));
        return;
      }
    } catch {
      // Backend getProfile offline or unauthenticated
    }

    const customSaved = localStorage.getItem('dukaansetu_custom_user');
    const hasToken = !!localStorage.getItem('dukaansetu_demo_token') || localStorage.getItem('dukaansetu_demo_mode') === 'true';
    const storeType = (localStorage.getItem('dukaansetu_store_type') as StoreTypeSlug) || 'kirana';
    if (customSaved && hasToken) {
      try {
        const custom = JSON.parse(customSaved);
        setState(prev => ({
          ...prev,
          user: {
            id: 'custom-user-' + storeType,
            auth_id: 'custom-auth-' + storeType,
            email: custom.email || 'merchant@dukaansetu.com',
            full_name: custom.full_name || 'Merchant',
            phone: custom.phone || '',
            language: 'te',
            is_active: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          shop: {
            id: 'custom-shop-' + storeType,
            owner_id: 'custom-user-' + storeType,
            name: custom.shop_name || 'My Store',
            type: custom.shop_type || storeType,
            phone: custom.phone || '',
            address: 'Commercial Street',
            city: 'Warangal',
            state: 'Telangana',
            currency: 'INR',
            tax_rate: 0,
            settings: {},
            is_active: true,
            created_at: new Date().toISOString(),
          },
          isAuthenticated: true,
          isLoading: false,
        }));
        return;
      } catch {}
    }

    setState(prev => ({ ...prev, isAuthenticated: false, isLoading: false }));
  }, []);

  useEffect(() => {
    // Check initial session
    const initAuth = async () => {
      try {
        if (
          localStorage.getItem('dukaansetu_demo_mode') === 'true' ||
          localStorage.getItem('vyapari_demo_mode') === 'true' ||
          localStorage.getItem('dukaansetu_demo_token')
        ) {
          const demoToken = localStorage.getItem('dukaansetu_demo_token') || 'demo-token-kirana';
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
      if (
        localStorage.getItem('dukaansetu_demo_mode') === 'true' ||
        localStorage.getItem('vyapari_demo_mode') === 'true' ||
        localStorage.getItem('dukaansetu_demo_token')
      ) {
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

    // Check if user was registered locally
    const savedCustom = localStorage.getItem('dukaansetu_custom_user');
    if (savedCustom) {
      try {
        const customObj = JSON.parse(savedCustom);
        if (customObj.email && customObj.email.toLowerCase() === email) {
          const storeType = (customObj.shop_type || 'kirana') as StoreTypeSlug;
          localStorage.setItem('dukaansetu_store_type', storeType);
          const token = localStorage.getItem('dukaansetu_demo_token') || DEMO_STORE_TOKENS[storeType] || 'demo-token-kirana';
          setState(prev => ({
            ...prev,
            token,
            isAuthenticated: true,
            isLoading: true,
          }));
          await refreshProfile();
          return;
        }
      } catch {}
    }

    localStorage.removeItem('dukaansetu_demo_mode');
    localStorage.removeItem('vyapari_demo_mode');
    localStorage.removeItem('dukaansetu_demo_token');
    localStorage.removeItem('dukaansetu_store_type');

    // 1. Try Supabase Auth
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: credentials.email,
        password: credentials.password,
      });
      if (!error && data?.session) {
        setState(prev => ({
          ...prev,
          token: data.session!.access_token,
          isAuthenticated: true,
        }));
        await refreshProfile();
        return;
      }
    } catch {}

    // 2. Try Backend direct login
    try {
      const backendRes = await authService.login({
        email: credentials.email,
        password: credentials.password,
      });
      if (backendRes.success && backendRes.data) {
        const bToken = (backendRes.data as any).token || (backendRes.data as any).session?.access_token || 'demo-token-kirana';
        localStorage.setItem('dukaansetu_demo_token', bToken);
        setState(prev => ({
          ...prev,
          token: bToken,
          isAuthenticated: true,
          isLoading: true,
        }));
        await refreshProfile();
        return;
      }
    } catch {}

    throw new Error("Invalid credentials or user not found. Please try again or use quick demo store login.");
  };

  const register = async (registerData: RegisterData) => {
    localStorage.removeItem('dukaansetu_demo_mode');
    localStorage.removeItem('vyapari_demo_mode');
    const storeType = registerData.shop_type || 'kirana';
    localStorage.setItem('dukaansetu_store_type', storeType);

    let sessionToken: string | null = null;
    let registeredUser: any = null;
    let registeredShop: any = null;

    // 1. Try Supabase Auth first, catching email rate limits cleanly
    try {
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
      if (!error && data?.session?.access_token) {
        sessionToken = data.session.access_token;
      }
    } catch (e: any) {
      console.warn('Supabase signUp bypassed due to email rate limits or policy:', e?.message);
    }

    // 2. Call backend register (creates user, shop, and seeds inventory in Postgres)
    try {
      const res = await authService.register({
        email: registerData.email,
        password: registerData.password,
        full_name: registerData.full_name,
        phone: registerData.phone,
        shop_name: registerData.shop_name,
        shop_type: registerData.shop_type,
      });
      if (res.success && res.data) {
        registeredUser = (res.data as any).user;
        registeredShop = (res.data as any).shop;
        if ((res.data as any).token) {
          sessionToken = (res.data as any).token;
        }
      }
    } catch (apiErr: any) {
      console.warn('Backend register notification:', apiErr?.message);
    }

    // 3. Resilient session creation
    if (!sessionToken) {
      sessionToken = DEMO_STORE_TOKENS[storeType as StoreTypeSlug] || `user-token-${Date.now()}`;
    }

    localStorage.setItem('dukaansetu_demo_token', sessionToken as string);
    localStorage.setItem('dukaansetu_custom_user', JSON.stringify({
      email: registerData.email,
      full_name: registerData.full_name,
      phone: registerData.phone || '',
      shop_name: registerData.shop_name,
      shop_type: storeType,
    }));

    setState(prev => ({
      ...prev,
      token: sessionToken,
      user: registeredUser || {
        id: 'user-' + storeType,
        auth_id: 'auth-' + storeType,
        email: registerData.email,
        full_name: registerData.full_name,
        phone: registerData.phone || '',
        language: 'te',
        is_active: true,
        created_at: new Date().toISOString(),
      },
      shop: registeredShop || {
        id: 'shop-' + storeType,
        owner_id: 'user-' + storeType,
        name: registerData.shop_name,
        type: storeType,
        phone: registerData.phone || '',
        address: 'Commercial Street',
        city: 'Warangal',
        state: 'Telangana',
        currency: 'INR',
        tax_rate: 0,
        settings: {},
        is_active: true,
        created_at: new Date().toISOString(),
      },
      isAuthenticated: true,
      isLoading: false,
    }));

    await refreshProfile();
  };

  const logout = async () => {
    localStorage.removeItem('dukaansetu_demo_mode');
    localStorage.removeItem('vyapari_demo_mode');
    localStorage.removeItem('dukaansetu_demo_token');
    localStorage.removeItem('dukaansetu_custom_user');
    localStorage.removeItem('dukaansetu_store_type');
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
