"""Synchronizes the full 12-product catalogs, 4 suppliers, and 3 customer accounts
for Auto Parts & Spares and Electronics & Mobiles into Supabase PostgreSQL.
"""
import os
import psycopg2
from datetime import datetime, timezone
import sys

# Add backend directory to sys.path to load STORE_SEED_DATA
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.routes.auth import STORE_SEED_DATA

def sync_verticals():
    host = "aws-0-ap-northeast-1.pooler.supabase.com"
    user = "postgres.cauvtvhqjvseuyqazpqu"
    password = "J5iD8tNjdegLJzJe"

    print("Connecting to Supabase PostgreSQL...", flush=True)
    conn = psycopg2.connect(
        host=host,
        port=6543,
        user=user,
        password=password,
        dbname="postgres",
        sslmode="require",
        connect_timeout=15
    )
    conn.autocommit = True
    cur = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()

    shops_to_sync = [
        {
            'shop_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
            'user_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
            'key': 'autoparts',
            'prefix': 'bbbbbbbb-2222-0000-0000-',
            'supp_prefix': 'bbbbbbbb-0000-0000-0000-',
            'cust_prefix': 'bbbbbbbb-1111-0000-0000-'
        },
        {
            'shop_id': 'dddddddd-dddd-dddd-dddd-dddddddddddd',
            'user_id': 'dddddddd-dddd-dddd-dddd-dddddddddddd',
            'key': 'electronics',
            'prefix': 'dddddddd-2222-0000-0000-',
            'supp_prefix': 'dddddddd-0000-0000-0000-',
            'cust_prefix': 'dddddddd-1111-0000-0000-'
        }
    ]

    for s in shops_to_sync:
        sid = s['shop_id']
        uid = s['user_id']
        data = STORE_SEED_DATA[s['key']]
        shop_name = data.get('shop_name') or ('Sri Ganesh Auto Spares & Accessories' if s['key'] == 'autoparts' else 'Sri Tech Zone Mobiles & Electronics')
        print(f"\nSyncing vertical: {shop_name} ({s['key']})...", flush=True)

        # 1. Update shop type and details
        cur.execute("""
            INSERT INTO shops (id, owner_id, name, type, phone, address, city, state, gst_number, currency, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET type = EXCLUDED.type, name = EXCLUDED.name;
        """, (sid, uid, shop_name, s['key'], '+91 98480bbbbb' if s['key'] == 'autoparts' else '+91 98480ddddd', 'Auto Nagar' if s['key'] == 'autoparts' else 'Complex Road', 'Warangal', 'Telangana', '36IIIP1111K1Z7' if s['key'] == 'autoparts' else '36KKKP3333M1Z9', 'INR', True, now, now))

        # 2. Categories
        for cat in data['categories']:
            cur.execute("""
                INSERT INTO categories (shop_id, name, is_active, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (sid, cat, True, now))
        print(f"  - {len(data['categories'])} categories verified.", flush=True)

        # 3. Suppliers
        for i, supp in enumerate(data['suppliers'], start=1):
            supp_id = f"{s['supp_prefix']}{i:012d}"
            sname = supp[0] if isinstance(supp, (list, tuple)) else supp['name']
            sphone = supp[1] if isinstance(supp, (list, tuple)) else supp['phone']
            cur.execute("""
                INSERT INTO suppliers (id, shop_id, name, phone, email, address, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, phone = EXCLUDED.phone;
            """, (supp_id, sid, sname, sphone, '', '', True, now, now))
        print(f"  - {len(data['suppliers'])} suppliers synced.", flush=True)

        # 4. Customers and Borrowings
        for i, cust in enumerate(data['customers'], start=1):
            cust_id = f"{s['cust_prefix']}{i:012d}"
            cname = cust[0] if isinstance(cust, (list, tuple)) else cust['name']
            cphone = cust[1] if isinstance(cust, (list, tuple)) else cust['phone']
            credit = float(cust[2] if isinstance(cust, (list, tuple)) else cust.get('credit', 0))
            cnote = cust[3] if isinstance(cust, (list, tuple)) and len(cust) > 3 else (cust.get('notes', '') if isinstance(cust, dict) else 'Store credit account')
            cur.execute("""
                INSERT INTO customers (id, shop_id, name, phone, total_credit, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, total_credit = EXCLUDED.total_credit;
            """, (cust_id, sid, cname, cphone, credit, True, now, now))

            if credit > 0:
                cur.execute("""
                    DELETE FROM borrowings WHERE shop_id = %s AND customer_id = %s;
                """, (sid, cust_id))
                cur.execute("""
                    INSERT INTO borrowings (shop_id, customer_id, customer_name, status, total_value, paid_amount, remaining_balance, notes, created_by, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (sid, cust_id, cname, 'ACTIVE', credit, 0.0, credit, cnote, uid, now, now))
        print(f"  - {len(data['customers'])} customers & borrowings synced.", flush=True)

        # 5. Products & Live Inventory
        for i, prod in enumerate(data['products'], start=1):
            pid = f"{s['prefix']}{i:012d}"
            cur.execute("""
                INSERT INTO products (
                    id, shop_id, name, local_name, category, base_unit, purchase_unit, selling_unit,
                    conversion_factor, purchase_price, selling_price, minimum_stock, recommended_stock,
                    reorder_quantity, is_active, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    local_name = EXCLUDED.local_name,
                    category = EXCLUDED.category,
                    base_unit = EXCLUDED.base_unit,
                    purchase_price = EXCLUDED.purchase_price,
                    selling_price = EXCLUDED.selling_price,
                    minimum_stock = EXCLUDED.minimum_stock,
                    recommended_stock = EXCLUDED.recommended_stock;
            """, (
                pid, sid, prod['name'], prod.get('local_name', ''), prod['category'],
                prod['base_unit'], prod['purchase_unit'], prod['selling_unit'],
                float(prod.get('conversion_factor', 1.0)), float(prod['purchase_price']),
                float(prod['selling_price']), float(prod['minimum_stock']),
                float(prod['recommended_stock']), float(prod.get('reorder_quantity', 10)),
                True, now, now
            ))

            cur.execute("""
                INSERT INTO inventory (shop_id, product_id, current_stock, stock_unit, last_stock_in, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (shop_id, product_id) DO UPDATE SET current_stock = EXCLUDED.current_stock;
            """, (sid, pid, float(prod.get('current_stock', 10)), prod['base_unit'], now, now, now))
        print(f"  - {len(data['products'])} products and inventory records synced successfully.", flush=True)

    cur.close()
    conn.close()
    print("\nSUCCESS: Auto Parts and Electronics verticals are completely synced in Supabase PostgreSQL!", flush=True)

if __name__ == '__main__':
    sync_verticals()
