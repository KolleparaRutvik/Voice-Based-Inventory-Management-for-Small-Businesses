"""Database Performance & Indexing Migration for Vyapari Voice.
Creates production B-Tree indexes and product_aliases table in Supabase PostgreSQL.
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load backend .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in backend/.env")
    sys.exit(1)

INDEXES_SQL = """
-- B-Tree performance indexes for high-frequency queries
CREATE INDEX IF NOT EXISTS idx_products_shop_active ON products (shop_id, is_active);
CREATE INDEX IF NOT EXISTS idx_products_shop_name ON products (shop_id, name);
CREATE INDEX IF NOT EXISTS idx_inventory_shop_product ON inventory (shop_id, product_id);
CREATE INDEX IF NOT EXISTS idx_transactions_shop_created ON transactions (shop_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_shop_prod ON transactions (shop_id, product_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_shop_type ON transactions (shop_id, transaction_type);
CREATE INDEX IF NOT EXISTS idx_borrowings_shop_status ON borrowings (shop_id, status);
CREATE INDEX IF NOT EXISTS idx_customers_shop ON customers (shop_id);
CREATE INDEX IF NOT EXISTS idx_suppliers_shop ON suppliers (shop_id);
CREATE INDEX IF NOT EXISTS idx_stock_alerts_shop ON stock_alerts (shop_id, is_resolved);
CREATE INDEX IF NOT EXISTS idx_voice_conv_shop ON voice_conversations (shop_id, created_at DESC);

-- Product Aliases Table for multilingual Kirana speech matching
CREATE TABLE IF NOT EXISTS product_aliases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    alias VARCHAR(100) NOT NULL,
    language VARCHAR(10) DEFAULT 'auto',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(shop_id, alias)
);
CREATE INDEX IF NOT EXISTS idx_aliases_shop_alias ON product_aliases (shop_id, alias);
"""

ALIASES_SEED = [
    # Rice
    ("Rice (Biyyam)", ["biyyam", "rice", "chawal", "sona masuri", "arisi", "biyyamu", "annam biyyam"]),
    # Sugar
    ("Sugar (Chakkera)", ["chakkera", "sugar", "chini", "shakkar", "panchadara"]),
    # Sunflower Oil
    ("Sunflower Oil (Nune)", ["nune", "oil", "tel", "sunflower oil", "meetha tel"]),
    # Toor Dal
    ("Toor Dal (Kandi Pappu)", ["kandi pappu", "toor dal", "tuvar dal", "pappu", "arhar dal"]),
    # Parle-G
    ("Parle-G Biscuits", ["parle", "biscuit", "biscuits", "parle-g", "parle g"]),
    # Red Label Tea
    ("Red Label Tea", ["tea", "chai", "tea powder", "red label", "chaha"]),
    # Jaggery
    ("Jaggery (Bellam)", ["bellam", "jaggery", "gud", "vellam"]),
    # Nescafe Coffee
    ("Nescafe Coffee", ["coffee", "nescafe", "coffee powder", "kaapi"]),
]

def run_migration():
    print(f"Connecting to Supabase PostgreSQL: {DATABASE_URL.split('@')[-1]}...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        print("1. Creating performance indexes and product_aliases table...")
        cur.execute(INDEXES_SQL)
        print("   [OK] Indexes created successfully!")

        print("2. Seeding product aliases for shop...")
        cur.execute("SELECT id FROM shops LIMIT 1;")
        shop = cur.fetchone()
        if not shop:
            print("   [WARN] No shop found, skipping alias seeding.")
            return
        shop_id = shop[0]

        alias_count = 0
        for prod_name_pattern, aliases in ALIASES_SEED:
            cur.execute(
                "SELECT id FROM products WHERE shop_id = %s AND (name ILIKE %s OR local_name ILIKE %s) LIMIT 1;",
                (shop_id, f"%{prod_name_pattern.split('(')[0].strip()}%", f"%{prod_name_pattern.split('(')[0].strip()}%")
            )
            p = cur.fetchone()
            if p:
                product_id = p[0]
                for alias in aliases:
                    cur.execute("""
                        INSERT INTO product_aliases (shop_id, product_id, alias)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (shop_id, alias) DO NOTHING;
                    """, (shop_id, product_id, alias.lower()))
                    alias_count += 1

        print(f"   [OK] Seeded/verified {alias_count} product aliases across Telugu, Hindi, and English!")

        # Verify index count
        cur.execute("""
            SELECT count(*) FROM pg_indexes 
            WHERE schemaname = 'public' AND indexname LIKE 'idx_%';
        """)
        idx_count = cur.fetchone()[0]
        print(f"   [OK] Active custom B-Tree indexes in live database: {idx_count}")

    except Exception as e:
        print(f"[ERROR] Migration error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    run_migration()
