import axios from 'axios';
import { supabase } from '../lib/supabase';
import type { ApiResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — attach auth token
api.interceptors.request.use(async (config) => {
  if (localStorage.getItem('vyapari_demo_mode') === 'true') {
    config.headers.Authorization = 'Bearer demo-token-vyapari';
    return config;
  }
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
  } catch {
    // ignore
  }
  return config;
}, (error) => Promise.reject(error));

// Response interceptor — normalize errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired, sign out
      supabase.auth.signOut();
      window.location.href = '/login';
    }
    const message = error.response?.data?.error?.message || error.message || 'Something went wrong';
    return Promise.reject(new Error(message));
  }
);

export default api;

// ---- Auth Service ----
export const authService = {
  async register(data: { email: string; password: string; full_name: string; phone?: string; shop_name: string; shop_type?: string }) {
    const res = await api.post<ApiResponse>('/api/auth/register', data);
    return res.data;
  },
  async login(data: { email: string; password: string }) {
    const res = await api.post<ApiResponse>('/api/auth/login', data);
    return res.data;
  },
  async getProfile() {
    const res = await api.get<ApiResponse>('/api/auth/profile');
    return res.data;
  },
};

// ---- Products Service ----
export const productsService = {
  async getAll(params?: { search?: string; category?: string; page?: number; per_page?: number }) {
    const res = await api.get<ApiResponse>('/api/products', { params });
    return res.data;
  },
  async getById(id: string) {
    const res = await api.get<ApiResponse>(`/api/products/${id}`);
    return res.data;
  },
  async create(data: Record<string, unknown>) {
    const res = await api.post<ApiResponse>('/api/products', data);
    return res.data;
  },
  async update(id: string, data: Record<string, unknown>) {
    const res = await api.put<ApiResponse>(`/api/products/${id}`, data);
    return res.data;
  },
  async delete(id: string) {
    const res = await api.delete<ApiResponse>(`/api/products/${id}`);
    return res.data;
  },
};

// ---- Inventory Service ----
export const inventoryService = {
  async getAll(params?: { search?: string; low_stock?: boolean }) {
    const res = await api.get<ApiResponse>('/api/inventory', { params });
    return res.data;
  },
  async stockIn(data: Record<string, unknown>) {
    const res = await api.post<ApiResponse>('/api/inventory/stock-in', data);
    return res.data;
  },
  async stockOut(data: Record<string, unknown>) {
    const res = await api.post<ApiResponse>('/api/inventory/stock-out', data);
    return res.data;
  },
};

// ---- Transactions Service ----
export const transactionsService = {
  async getAll(params?: { type?: string; product_id?: string; page?: number; per_page?: number; start_date?: string; end_date?: string }) {
    const res = await api.get<ApiResponse>('/api/transactions', { params });
    return res.data;
  },
  async getById(id: string) {
    const res = await api.get<ApiResponse>(`/api/transactions/${id}`);
    return res.data;
  },
};

// ---- Suppliers Service ----
export const suppliersService = {
  async getAll() {
    const res = await api.get<ApiResponse>('/api/suppliers');
    return res.data;
  },
  async getById(id: string) {
    const res = await api.get<ApiResponse>(`/api/suppliers/${id}`);
    return res.data;
  },
  async create(data: Record<string, unknown>) {
    const res = await api.post<ApiResponse>('/api/suppliers', data);
    return res.data;
  },
  async update(id: string, data: Record<string, unknown>) {
    const res = await api.put<ApiResponse>(`/api/suppliers/${id}`, data);
    return res.data;
  },
  async delete(id: string) {
    const res = await api.delete<ApiResponse>(`/api/suppliers/${id}`);
    return res.data;
  },
};

// ---- Borrowings Service ----
export const borrowingsService = {
  async getAll(params?: { status?: string }) {
    const res = await api.get<ApiResponse>('/api/borrowings', { params });
    return res.data;
  },
  async create(data: Record<string, unknown>) {
    const res = await api.post<ApiResponse>('/api/borrowings', data);
    return res.data;
  },
  async returnItems(id: string, data: Record<string, unknown>) {
    const res = await api.post<ApiResponse>(`/api/borrowings/${id}/return`, data);
    return res.data;
  },
  async recordPayment(id: string, data: { amount: number; notes?: string }) {
    const res = await api.post<ApiResponse>(`/api/borrowings/${id}/payment`, data);
    return res.data;
  },
};

// ---- Voice Service ----
export const voiceService = {
  async upload(formData: FormData) {
    const res = await api.post<ApiResponse>('/api/voice/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000,
    });
    return res.data;
  },
  async transcribeAudio(formData: FormData) {
    const res = await api.post<ApiResponse>('/api/voice/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000,
    });
    return res.data;
  },
  async transcribe(data: { audio_url: string }) {
    const res = await api.post<ApiResponse>('/api/voice/transcribe', data);
    return res.data;
  },
  async interpret(data: { transcript: string; conversation_history?: unknown[]; language?: string; conversation_id?: string }) {
    const res = await api.post<ApiResponse>('/api/voice/interpret', data);
    return res.data;
  },
  async execute(data: Record<string, unknown>) {
    const res = await api.post<ApiResponse>('/api/voice/execute', data);
    return res.data;
  },
  async getConversations(params?: { limit?: number }) {
    const res = await api.get<ApiResponse>('/api/voice/conversations', { params });
    return res.data;
  },
  async getHistory(params?: { page?: number; per_page?: number }) {
    const res = await api.get<ApiResponse>('/api/voice/conversations', { params });
    return res.data;
  },
  async delete(id: string) {
    const res = await api.delete<ApiResponse>(`/api/voice/${id}`);
    return res.data;
  },
  async saveConversation(data: Record<string, unknown>) {
    const res = await api.post<ApiResponse>('/api/voice/conversations', data);
    return res.data;
  },
};

// ---- Customers Service ----
export const customersService = {
  async getAll(params?: { search?: string }) {
    const res = await api.get<ApiResponse>('/api/customers', { params });
    return res.data;
  },
  async getById(id: string) {
    const res = await api.get<ApiResponse>(`/api/customers/${id}`);
    return res.data;
  },
  async create(data: Record<string, unknown>) {
    const res = await api.post<ApiResponse>('/api/customers', data);
    return res.data;
  },
  async update(id: string, data: Record<string, unknown>) {
    const res = await api.put<ApiResponse>(`/api/customers/${id}`, data);
    return res.data;
  },
};

// ---- Assistant Service ----
export const assistantService = {
  async query(data: { question: string; conversation_history?: Array<{ role: string; content: string }>; language?: string }) {
    const res = await api.post<ApiResponse>('/api/assistant/query', data);
    return res.data;
  },
};

// ---- Analytics Service ----
export const analyticsService = {
  async getDashboard() {
    const res = await api.get<ApiResponse>('/api/analytics/dashboard');
    return res.data;
  },
};

// ---- Notifications Service ----
export const notificationsService = {
  async getAll() {
    const res = await api.get<ApiResponse>('/api/notifications');
    return res.data;
  },
  async markRead(id: string) {
    const res = await api.post<ApiResponse>(`/api/notifications/${id}/read`);
    return res.data;
  },
};

// ---- Purchase Orders Service ----
export const purchaseOrdersService = {
  async getAll() {
    const res = await api.get<ApiResponse>('/api/purchase-orders');
    return res.data;
  },
  async create(data: Record<string, unknown>) {
    const res = await api.post<ApiResponse>('/api/purchase-orders', data);
    return res.data;
  },
  async getPdf(id: string) {
    const res = await api.get(`/api/purchase-orders/${id}/pdf`, { responseType: 'blob' });
    return res.data;
  },
};

// ---- Reorder Service ----
export const reorderService = {
  async getRecommendations() {
    const res = await api.get<ApiResponse>('/api/reorder/recommendations');
    return res.data;
  },
};

// ---- Festival Service ----
export const festivalService = {
  async getUpcoming(params?: { window_days?: number; reference_date?: string }) {
    const res = await api.get<ApiResponse>('/api/festivals/upcoming', { params });
    return res.data;
  },
  async getRecommendations(params?: { festival?: string; window_days?: number; reference_date?: string }) {
    const res = await api.get<ApiResponse>('/api/festivals/recommendations', { params });
    return res.data;
  },
  async syncNotifications(data?: { reference_date?: string }) {
    const res = await api.post<ApiResponse>('/api/festivals/sync-notifications', data || {});
    return res.data;
  },
  async createFestivalPo(data: { festival_name: string; items: Array<{ product_id: string; quantity: number; unit_price: number }>; supplier_id?: string }) {
    const res = await api.post<ApiResponse>('/api/festivals/create-po', data);
    return res.data;
  },
};
