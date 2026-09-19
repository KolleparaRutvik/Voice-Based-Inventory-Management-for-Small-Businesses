// ============================================================
// DUKAANSETU — TypeScript Type Definitions
// ============================================================

// ---- Base Types ----
export type UUID = string;

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// ---- Auth ----
export interface User {
  id: UUID;
  auth_id: UUID;
  email: string;
  full_name: string;
  phone?: string;
  language: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
}

export interface Shop {
  id: UUID;
  owner_id: UUID;
  name: string;
  type: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  gst_number?: string;
  currency: string;
  tax_rate: number;
  settings: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  shop: Shop | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
  shop_name: string;
  shop_type?: string;
}

// ---- Products ----
export interface Product {
  id: UUID;
  shop_id: UUID;
  name: string;
  local_name?: string;
  category_id?: UUID;
  category?: string;
  description?: string;
  sku?: string;
  barcode?: string;
  base_unit: string;
  purchase_unit: string;
  selling_unit: string;
  conversion_factor: number;
  purchase_price: number;
  selling_price: number;
  minimum_stock: number;
  recommended_stock: number;
  reorder_quantity: number;
  supplier_id?: UUID;
  image_url?: string;
  tags?: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
  // Joined fields
  current_stock?: number;
  stock_value?: number;
  supplier_name?: string;
}

export interface ProductFormData {
  name: string;
  local_name?: string;
  category?: string;
  base_unit: string;
  purchase_unit: string;
  selling_unit: string;
  conversion_factor: number;
  purchase_price: number;
  selling_price: number;
  minimum_stock: number;
  recommended_stock?: number;
  reorder_quantity?: number;
  supplier_id?: UUID;
}

// ---- Inventory ----
export interface InventoryItem {
  id: UUID;
  shop_id: UUID;
  product_id: UUID;
  current_stock: number;
  stock_unit: string;
  last_stock_in?: string;
  last_stock_out?: string;
  // Joined
  product_name: string;
  product_category?: string;
  purchase_price: number;
  selling_price: number;
  minimum_stock: number;
  stock_value: number;
  is_low_stock: boolean;
}

export interface StockInData {
  product_id: UUID;
  quantity: number;
  unit: string;
  price?: number;
  supplier_id?: UUID;
  notes?: string;
  source?: 'manual' | 'voice';
}

export interface StockOutData {
  product_id: UUID;
  quantity: number;
  unit: string;
  transaction_type: 'SALE' | 'STOCK_OUT' | 'DAMAGE' | 'RETURN';
  price?: number;
  customer_id?: UUID;
  notes?: string;
  source?: 'manual' | 'voice';
}

// ---- Transactions ----
export type TransactionType = 
  | 'STOCK_IN'
  | 'STOCK_OUT'
  | 'SALE'
  | 'PURCHASE'
  | 'BORROW_OUT'
  | 'BORROW_RETURN'
  | 'ADJUSTMENT'
  | 'RETURN'
  | 'DAMAGE'
  | 'TRANSFER';

export interface Transaction {
  id: UUID;
  shop_id: UUID;
  product_id: UUID;
  transaction_type: TransactionType;
  quantity: number;
  unit: string;
  quantity_in_base_unit?: number;
  price: number;
  total_amount: number;
  supplier_id?: UUID;
  customer_id?: UUID;
  borrowing_id?: UUID;
  source: string;
  notes?: string;
  reference_number?: string;
  created_by?: UUID;
  created_at: string;
  // Joined
  product_name?: string;
  product_category?: string;
  supplier_name?: string;
  customer_name?: string;
}

// ---- Suppliers ----
export interface Supplier {
  id: UUID;
  shop_id: UUID;
  name: string;
  phone?: string;
  email?: string;
  address?: string;
  city?: string;
  gst_number?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  product_count?: number;
}

// ---- Customers ----
export interface Customer {
  id: UUID;
  shop_id: UUID;
  name: string;
  phone?: string;
  address?: string;
  notes?: string;
  total_credit: number;
  is_active: boolean;
  created_at: string;
}

// ---- Borrowings ----
export type BorrowingStatus = 'ACTIVE' | 'PARTIALLY_RETURNED' | 'RETURNED' | 'OVERDUE';

export interface Borrowing {
  id: UUID;
  shop_id: UUID;
  customer_id: UUID;
  customer_name: string;
  status: BorrowingStatus;
  total_value: number;
  paid_amount: number;
  remaining_balance: number;
  due_date?: string;
  notes?: string;
  created_at: string;
  items?: BorrowingItem[];
}

export interface BorrowingItem {
  id: UUID;
  borrowing_id: UUID;
  product_id: UUID;
  quantity: number;
  unit: string;
  returned_quantity: number;
  price: number;
  total_amount: number;
  status: string;
  product_name?: string;
}

// ---- Purchase Orders ----
export interface PurchaseOrder {
  id: UUID;
  shop_id: UUID;
  supplier_id: UUID;
  order_number?: string;
  status: 'DRAFT' | 'SENT' | 'CONFIRMED' | 'RECEIVED' | 'CANCELLED';
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  tax_rate: number;
  notes?: string;
  expected_date?: string;
  received_date?: string;
  created_at: string;
  supplier_name?: string;
  items?: PurchaseOrderItem[];
}

export interface PurchaseOrderItem {
  id: UUID;
  purchase_order_id: UUID;
  product_id: UUID;
  quantity: number;
  unit: string;
  unit_price: number;
  total_price: number;
  received_quantity: number;
  product_name?: string;
}

// ---- Notifications ----
export type NotificationType = 
  | 'LOW_STOCK'
  | 'SMART_REORDER'
  | 'BORROW_REMINDER'
  | 'OVERDUE_BORROW'
  | 'PURCHASE_RECEIVED'
  | 'PRICE_CHANGE'
  | 'DEMAND_ALERT';

export interface Notification {
  id: UUID;
  shop_id: UUID;
  type: NotificationType;
  title: string;
  message: string;
  data: Record<string, unknown>;
  is_read: boolean;
  read_at?: string;
  created_at: string;
}

// ---- Voice ----
export type VoiceState = 
  | 'ready'
  | 'listening'
  | 'processing'
  | 'understanding'
  | 'confirming'
  | 'executing'
  | 'completed'
  | 'error';

export interface VoiceIntent {
  intent: TransactionType | 'STOCK_CHECK' | 'CREDIT_CHECK' | 'BUSINESS_INSIGHT' | 'PURCHASE' | 'REORDER' | 'BORROW_CLEAR' | 'STOCK_ADJUST' | 'CUSTOMER_ADD' | 'PRODUCT_ADD' | 'GENERAL' | 'CLARIFICATION' | 'UNKNOWN';
  product?: string;
  product_name?: string;
  product_id?: UUID;
  quantity?: number;
  unit?: string;
  price?: number;
  amount?: number;
  supplier?: string;
  supplier_name?: string;
  supplier_id?: UUID;
  customer?: string;
  customer_name?: string;
  customer_id?: UUID;
  is_new_customer?: boolean;
  phone?: string;
  action?: string;
  notes?: string;
  confidence?: number;
  clarification_needed?: boolean;
  ambiguous_candidates?: string[];
  confirmation_required?: boolean;
  confirmation_prompt?: string;
  answer?: string;
  voice_text?: string;
  language?: string;
  transcript?: string;
}

export interface VoiceConversation {
  id: UUID;
  conversation_id?: UUID;
  shop_id: UUID;
  user_id: UUID;
  speaker?: 'user' | 'assistant';
  audio_url?: string;
  transcript?: string;
  response_text?: string;
  voice_text?: string;
  language?: string;
  duration?: number;
  intent?: string;
  extracted_entities?: Record<string, unknown>;
  confidence?: number;
  confirmation_status: 'PENDING' | 'CONFIRMED' | 'REJECTED' | 'EDITED';
  action_performed?: string;
  transaction_id?: UUID;
  error_message?: string;
  created_at: string;
}

// ---- Dashboard ----
export interface DashboardData {
  today_sales: number;
  today_purchases: number;
  inventory_value: number;
  estimated_margin: number;
  total_products: number;
  low_stock_count: number;
  active_borrowings: number;
  borrowed_value: number;
  recent_transactions: Transaction[];
  low_stock_products: InventoryItem[];
  fast_moving: Product[];
  slow_moving: Product[];
}

// ---- Analytics ----
export interface SalesData {
  date: string;
  amount: number;
  count: number;
}

export interface CategoryBreakdown {
  category: string;
  value: number;
  percentage: number;
}

// ---- Units ----
export const UNITS = [
  { value: 'kg', label: 'Kilogram (kg)' },
  { value: 'gram', label: 'Gram (g)' },
  { value: 'litre', label: 'Litre (L)' },
  { value: 'ml', label: 'Millilitre (ml)' },
  { value: 'piece', label: 'Piece' },
  { value: 'packet', label: 'Packet' },
  { value: 'box', label: 'Box' },
  { value: 'bag', label: 'Bag' },
  { value: 'carton', label: 'Carton' },
  { value: 'dozen', label: 'Dozen' },
  { value: 'quintal', label: 'Quintal' },
] as const;

export const CATEGORIES = [
  'Grains & Rice',
  'Pulses & Dal',
  'Spices & Masala',
  'Sugar & Jaggery',
  'Oils & Ghee',
  'Dairy',
  'Beverages',
  'Snacks & Biscuits',
  'Cleaning & Household',
  'Personal Care',
  'Other',
] as const;

export const TRANSACTION_TYPES: Record<TransactionType, { label: string; color: string; icon: string }> = {
  STOCK_IN: { label: 'Stock In', color: 'success', icon: 'plus' },
  STOCK_OUT: { label: 'Stock Out', color: 'danger', icon: 'minus' },
  SALE: { label: 'Sale', color: 'primary', icon: 'shopping-cart' },
  PURCHASE: { label: 'Purchase', color: 'accent', icon: 'package' },
  BORROW_OUT: { label: 'Borrowed', color: 'warning', icon: 'arrow-up-right' },
  BORROW_RETURN: { label: 'Return', color: 'success', icon: 'arrow-down-left' },
  ADJUSTMENT: { label: 'Adjustment', color: 'surface', icon: 'edit' },
  RETURN: { label: 'Return', color: 'warning', icon: 'rotate-ccw' },
  DAMAGE: { label: 'Damage', color: 'danger', icon: 'alert-triangle' },
  TRANSFER: { label: 'Transfer', color: 'primary', icon: 'arrow-right' },
};
