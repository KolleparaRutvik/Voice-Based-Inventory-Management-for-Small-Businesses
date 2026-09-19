-- ============================================================
-- DUKAANSETU — Complete Database Schema
-- Supabase PostgreSQL
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth_id UUID UNIQUE NOT NULL, -- Links to Supabase Auth
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    language TEXT DEFAULT 'en',
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- SHOPS
-- ============================================================
CREATE TABLE IF NOT EXISTS shops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT DEFAULT 'kirana', -- kirana, grocery, wholesale, retail, distributor
    phone TEXT,
    address TEXT,
    city TEXT,
    state TEXT DEFAULT 'Telangana',
    gst_number TEXT,
    currency TEXT DEFAULT 'INR',
    tax_rate DECIMAL(5,2) DEFAULT 0,
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- SHOP MEMBERS (multi-staff support)
-- ============================================================
CREATE TABLE IF NOT EXISTS shop_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'staff', -- owner, manager, staff
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(shop_id, user_id)
);

-- ============================================================
-- CATEGORIES
-- ============================================================
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- SUPPLIERS
-- ============================================================
CREATE TABLE IF NOT EXISTS suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    gst_number TEXT,
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- PRODUCTS
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    local_name TEXT, -- Name in local language
    category_id UUID REFERENCES categories(id),
    category TEXT, -- Simple category string fallback
    description TEXT,
    sku TEXT,
    barcode TEXT,
    base_unit TEXT NOT NULL DEFAULT 'kg', -- kg, gram, litre, ml, piece, packet, box, bag, carton, dozen, quintal
    purchase_unit TEXT DEFAULT 'kg',
    selling_unit TEXT DEFAULT 'kg',
    conversion_factor DECIMAL(10,4) DEFAULT 1, -- 1 purchase_unit = X base_units
    purchase_price DECIMAL(12,2) DEFAULT 0,
    selling_price DECIMAL(12,2) DEFAULT 0,
    minimum_stock DECIMAL(12,3) DEFAULT 0,
    recommended_stock DECIMAL(12,3) DEFAULT 0,
    reorder_quantity DECIMAL(12,3) DEFAULT 0,
    supplier_id UUID REFERENCES suppliers(id),
    image_url TEXT,
    tags TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- PRODUCT UNITS (conversion rules)
-- ============================================================
CREATE TABLE IF NOT EXISTS product_units (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    from_unit TEXT NOT NULL,
    to_unit TEXT NOT NULL,
    conversion_factor DECIMAL(10,4) NOT NULL, -- 1 from_unit = X to_unit
    is_global BOOLEAN DEFAULT false, -- If true, applies to all products
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- INVENTORY
-- ============================================================
CREATE TABLE IF NOT EXISTS inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    current_stock DECIMAL(12,3) DEFAULT 0,
    stock_unit TEXT NOT NULL DEFAULT 'kg', -- base_unit of the product
    last_stock_in TIMESTAMPTZ,
    last_stock_out TIMESTAMPTZ,
    last_counted TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(shop_id, product_id)
);

-- ============================================================
-- CUSTOMERS
-- ============================================================
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    notes TEXT,
    total_credit DECIMAL(12,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TRANSACTIONS (Audit Ledger)
-- ============================================================
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id), -- Nullable for pure monetary udhar / payment transactions
    transaction_type TEXT NOT NULL, -- STOCK_IN, STOCK_OUT, SALE, PURCHASE, BORROW_OUT, BORROW_RETURN, ADJUSTMENT, RETURN, DAMAGE, TRANSFER
    quantity DECIMAL(12,3) NOT NULL,
    unit TEXT, -- Nullable for pure monetary transactions
    quantity_in_base_unit DECIMAL(12,3), -- Converted to base unit
    price DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    supplier_id UUID REFERENCES suppliers(id),
    customer_id UUID REFERENCES customers(id),
    borrowing_id UUID,
    purchase_order_id UUID,
    source TEXT DEFAULT 'manual', -- manual, voice, import
    voice_conversation_id UUID,
    notes TEXT,
    reference_number TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- BORROWINGS
-- ============================================================
CREATE TABLE IF NOT EXISTS borrowings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id),
    customer_name TEXT NOT NULL, -- Denormalized for quick access
    status TEXT DEFAULT 'ACTIVE', -- ACTIVE, PARTIALLY_RETURNED, RETURNED, OVERDUE
    total_value DECIMAL(12,2) DEFAULT 0,
    paid_amount DECIMAL(12,2) DEFAULT 0,
    remaining_balance DECIMAL(12,2) DEFAULT 0,
    due_date TIMESTAMPTZ,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- BORROWING ITEMS
-- ============================================================
CREATE TABLE IF NOT EXISTS borrowing_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrowing_id UUID NOT NULL REFERENCES borrowings(id) ON DELETE CASCADE,
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity DECIMAL(12,3) NOT NULL,
    unit TEXT NOT NULL,
    returned_quantity DECIMAL(12,3) DEFAULT 0,
    price DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    status TEXT DEFAULT 'ACTIVE', -- ACTIVE, PARTIALLY_RETURNED, RETURNED
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CUSTOMER CREDIT
-- ============================================================
CREATE TABLE IF NOT EXISTS customer_credit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id),
    credit_type TEXT NOT NULL, -- BORROW, PAYMENT, ADJUSTMENT
    amount DECIMAL(12,2) NOT NULL,
    running_balance DECIMAL(12,2) NOT NULL,
    reference_id UUID, -- borrowing_id or payment_id
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- PURCHASE ORDERS
-- ============================================================
CREATE TABLE IF NOT EXISTS purchase_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    supplier_id UUID NOT NULL REFERENCES suppliers(id),
    order_number TEXT,
    status TEXT DEFAULT 'DRAFT', -- DRAFT, SENT, CONFIRMED, RECEIVED, CANCELLED
    subtotal DECIMAL(12,2) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    tax_rate DECIMAL(5,2) DEFAULT 0,
    notes TEXT,
    expected_date TIMESTAMPTZ,
    received_date TIMESTAMPTZ,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- PURCHASE ORDER ITEMS
-- ============================================================
CREATE TABLE IF NOT EXISTS purchase_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    purchase_order_id UUID NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity DECIMAL(12,3) NOT NULL,
    unit TEXT NOT NULL,
    unit_price DECIMAL(12,2) DEFAULT 0,
    total_price DECIMAL(12,2) DEFAULT 0,
    received_quantity DECIMAL(12,3) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- STOCK ALERTS
-- ============================================================
CREATE TABLE IF NOT EXISTS stock_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    alert_type TEXT NOT NULL, -- LOW_STOCK, OUT_OF_STOCK, OVERSTOCK
    current_stock DECIMAL(12,3),
    threshold DECIMAL(12,3),
    is_resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    type TEXT NOT NULL, -- LOW_STOCK, SMART_REORDER, BORROW_REMINDER, OVERDUE_BORROW, PURCHASE_RECEIVED, PRICE_CHANGE, DEMAND_ALERT
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- VOICE CONVERSATIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS voice_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID DEFAULT uuid_generate_v4(), -- Groups multi-turn dialogue thread
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    speaker TEXT DEFAULT 'user', -- user or assistant
    audio_url TEXT,
    transcript TEXT,
    response_text TEXT,
    voice_text TEXT,
    language TEXT,
    duration DECIMAL(8,2), -- seconds
    intent TEXT,
    extracted_entities JSONB DEFAULT '{}',
    confidence DECIMAL(5,2) DEFAULT 0.95,
    confirmation_status TEXT DEFAULT 'PENDING', -- PENDING, CONFIRMED, REJECTED, EDITED
    action_performed TEXT,
    transaction_id UUID REFERENCES transactions(id),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- DEMAND FORECASTS
-- ============================================================
CREATE TABLE IF NOT EXISTS demand_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    forecast_date DATE NOT NULL,
    predicted_demand DECIMAL(12,3),
    confidence DECIMAL(5,2),
    method TEXT, -- rule_based, trend, seasonal
    factors JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- PRODUCT PRICE HISTORY
-- ============================================================
CREATE TABLE IF NOT EXISTS product_price_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    price_type TEXT NOT NULL, -- purchase, selling
    old_price DECIMAL(12,2),
    new_price DECIMAL(12,2) NOT NULL,
    changed_by UUID REFERENCES users(id),
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- AUDIT LOGS
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID,
    old_data JSONB,
    new_data JSONB,
    ip_address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- PRODUCT ALIASES (regional name → product mapping)
-- ============================================================
CREATE TABLE IF NOT EXISTS product_aliases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    alias TEXT NOT NULL,
    language TEXT DEFAULT 'te', -- te, hi, en
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_products_shop ON products(shop_id);
CREATE INDEX idx_products_name ON products(shop_id, name);
CREATE INDEX idx_products_category ON products(shop_id, category);
CREATE INDEX idx_inventory_shop ON inventory(shop_id);
CREATE INDEX idx_inventory_product ON inventory(shop_id, product_id);
CREATE INDEX idx_transactions_shop ON transactions(shop_id);
CREATE INDEX idx_transactions_product ON transactions(shop_id, product_id);
CREATE INDEX idx_transactions_type ON transactions(shop_id, transaction_type);
CREATE INDEX idx_transactions_date ON transactions(shop_id, created_at);
CREATE INDEX idx_borrowings_shop ON borrowings(shop_id);
CREATE INDEX idx_borrowings_customer ON borrowings(shop_id, customer_id);
CREATE INDEX idx_borrowings_status ON borrowings(shop_id, status);
CREATE INDEX idx_customers_shop ON customers(shop_id);
CREATE INDEX idx_suppliers_shop ON suppliers(shop_id);
CREATE INDEX idx_notifications_shop ON notifications(shop_id, is_read);
CREATE INDEX idx_voice_shop ON voice_conversations(shop_id);
CREATE INDEX idx_stock_alerts_shop ON stock_alerts(shop_id, is_resolved);
CREATE INDEX idx_purchase_orders_shop ON purchase_orders(shop_id);
CREATE INDEX idx_price_history_product ON product_price_history(shop_id, product_id);

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE shops ENABLE ROW LEVEL SECURITY;
ALTER TABLE shop_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_units ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE borrowings ENABLE ROW LEVEL SECURITY;
ALTER TABLE borrowing_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_credit ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE demand_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_price_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Users can read/update their own profile
CREATE POLICY users_own ON users FOR ALL USING (auth_id = auth.uid());

-- Shop owner can manage their shop
CREATE POLICY shops_owner ON shops FOR ALL USING (
    owner_id IN (SELECT id FROM users WHERE auth_id = auth.uid())
);

-- Shop members can access shop data
CREATE POLICY shop_members_access ON shop_members FOR ALL USING (
    user_id IN (SELECT id FROM users WHERE auth_id = auth.uid())
);

-- Helper function: get shop IDs for current user
CREATE OR REPLACE FUNCTION get_user_shop_ids()
RETURNS SETOF UUID AS $$
    SELECT shop_id FROM shop_members
    WHERE user_id = (SELECT id FROM users WHERE auth_id = auth.uid())
    AND is_active = true
    UNION
    SELECT id FROM shops
    WHERE owner_id = (SELECT id FROM users WHERE auth_id = auth.uid())
    AND is_active = true;
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- All shop-scoped tables use same policy pattern
CREATE POLICY products_shop ON products FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY suppliers_shop ON suppliers FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY categories_shop ON categories FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY product_units_shop ON product_units FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY inventory_shop ON inventory FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY customers_shop ON customers FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY transactions_shop ON transactions FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY borrowings_shop ON borrowings FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY borrowing_items_shop ON borrowing_items FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY customer_credit_shop ON customer_credit FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY purchase_orders_shop ON purchase_orders FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY purchase_order_items_shop ON purchase_order_items FOR ALL USING (
    purchase_order_id IN (SELECT id FROM purchase_orders WHERE shop_id IN (SELECT get_user_shop_ids()))
);
CREATE POLICY stock_alerts_shop ON stock_alerts FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY notifications_shop ON notifications FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY voice_conversations_shop ON voice_conversations FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY demand_forecasts_shop ON demand_forecasts FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY price_history_shop ON product_price_history FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));
CREATE POLICY audit_logs_shop ON audit_logs FOR ALL USING (shop_id IN (SELECT get_user_shop_ids()));

-- ============================================================
-- TRIGGERS: Auto-update updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_shops_updated_at BEFORE UPDATE ON shops FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_suppliers_updated_at BEFORE UPDATE ON suppliers FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_inventory_updated_at BEFORE UPDATE ON inventory FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_customers_updated_at BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_borrowings_updated_at BEFORE UPDATE ON borrowings FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_borrowing_items_updated_at BEFORE UPDATE ON borrowing_items FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_purchase_orders_updated_at BEFORE UPDATE ON purchase_orders FOR EACH ROW EXECUTE FUNCTION update_updated_at();
