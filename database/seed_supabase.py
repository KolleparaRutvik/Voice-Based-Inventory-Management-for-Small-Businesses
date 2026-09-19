"""Vyapari Voice — Populate Supabase PostgreSQL with rich seed data."""
import psycopg2
from datetime import datetime, timezone

def seed_database():
    host = "aws-0-ap-northeast-1.pooler.supabase.com"
    user = "postgres.cauvtvhqjvseuyqazpqu"
    password = "J5iD8tNjdegLJzJe"

    print("Connecting to Supabase PostgreSQL...")
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
    user_id = '11111111-1111-1111-1111-111111111111'
    auth_id = '11111111-1111-1111-1111-111111111111'
    shop_id = '22222222-2222-2222-2222-222222222222'

    print("1. Inserting User...")
    cur.execute("""
        INSERT INTO users (id, auth_id, email, full_name, phone, language, is_active, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name;
    """, (user_id, auth_id, 'srinivas@vyapari.com', 'Srinivas Kumar', '+91 9876543210', 'te', True, now, now))

    print("2. Inserting Shop...")
    cur.execute("""
        INSERT INTO shops (id, owner_id, name, type, phone, address, city, state, gst_number, currency, is_active, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
    """, (shop_id, user_id, 'Sri Lakshmi Kirana Store', 'kirana', '+91 9876543210', 'Main Road, Hanamkonda', 'Warangal', 'Telangana', '36AAAAA0000A1Z5', 'INR', True, now, now))

    print("3. Inserting Categories...")
    categories = [
        'Grains & Rice', 'Pulses & Dal', 'Spices & Masala',
        'Sugar & Jaggery', 'Oils & Ghee', 'Dairy',
        'Beverages', 'Snacks & Biscuits', 'Cleaning & Household',
        'Personal Care', 'Other'
    ]
    for cat in categories:
        cur.execute("""
            INSERT INTO categories (shop_id, name, is_active, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (shop_id, cat, True, now))

    print("4. Inserting Suppliers...")
    supp_data = [
        ('33333333-0000-0000-0000-000000000001', 'ABC Traders', '+91 9876543001', 'abc@traders.com', 'Wholesale Market, Warangal'),
        ('33333333-0000-0000-0000-000000000002', 'Srinivas Wholesale', '+91 9876543002', 'srinivas@wholesale.com', 'Grain Market, Warangal'),
        ('33333333-0000-0000-0000-000000000003', 'Lakshmi Distributors', '+91 9876543003', 'lakshmi@dist.com', 'Industrial Area, Hyderabad')
    ]
    for sid, name, phone, email, addr in supp_data:
        cur.execute("""
            INSERT INTO suppliers (id, shop_id, name, phone, email, address, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (sid, shop_id, name, phone, email, addr, True, now, now))

    print("5. Inserting Customers...")
    cust_data = [
        ('44444444-0000-0000-0000-000000000001', 'Ramesh (Kirana Regular)', '+91 9848022334', 1250.0),
        ('44444444-0000-0000-0000-000000000002', 'Suresh (Teacher)', '+91 9848033445', 450.0),
        ('44444444-0000-0000-0000-000000000003', 'Anil (Auto Driver)', '+91 9848044556', 0.0)
    ]
    for cid, name, phone, cred in cust_data:
        cur.execute("""
            INSERT INTO customers (id, shop_id, name, phone, total_credit, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (cid, shop_id, name, phone, cred, True, now, now))

    print("6. Inserting Products & Inventory...")
    products = [
        ('55555555-0000-0000-0000-000000000001', 'Rice (Biyyam)', 'Biyyam', 'Grains & Rice', 'kg', 'bag', 'kg', 25.0, 1450.0, 65.0, 125.0, 500.0, 250.0, 450.0),
        ('55555555-0000-0000-0000-000000000002', 'Sugar (Chakkera)', 'Chakkera', 'Sugar & Jaggery', 'kg', 'bag', 'kg', 50.0, 2100.0, 48.0, 50.0, 200.0, 100.0, 180.0),
        ('55555555-0000-0000-0000-000000000003', 'Sunflower Oil (Nune)', 'Nune', 'Oils & Ghee', 'litre', 'litre', 'litre', 1.0, 150.0, 165.0, 10.0, 50.0, 30.0, 35.0),
        ('55555555-0000-0000-0000-000000000004', 'Toor Dal (Kandi Pappu)', 'Kandi Pappu', 'Pulses & Dal', 'kg', 'bag', 'kg', 25.0, 2750.0, 125.0, 25.0, 100.0, 50.0, 65.0),
        ('55555555-0000-0000-0000-000000000005', 'Parle-G Biscuits', 'Parle-G', 'Snacks & Biscuits', 'packet', 'carton', 'packet', 24.0, 240.0, 10.0, 50.0, 200.0, 96.0, 120.0),
        ('55555555-0000-0000-0000-000000000006', 'Red Label Tea', 'Tea Podi', 'Beverages', 'packet', 'box', 'packet', 12.0, 1200.0, 110.0, 20.0, 60.0, 36.0, 42.0),
        ('55555555-0000-0000-0000-000000000007', 'Jaggery (Bellam)', 'Bellam', 'Sugar & Jaggery', 'kg', 'kg', 'kg', 1.0, 55.0, 70.0, 20.0, 50.0, 25.0, 8.0),
        ('55555555-0000-0000-0000-000000000008', 'Nescafe Coffee', 'Coffee Podi', 'Beverages', 'packet', 'box', 'packet', 12.0, 2400.0, 220.0, 10.0, 36.0, 24.0, 30.0),
    ]

    for pid, name, loc, cat, base, pur, sel, conv, pur_pr, sel_pr, min_st, rec_st, reo_qty, cur_st in products:
        # Product
        cur.execute("""
            INSERT INTO products (
                id, shop_id, name, local_name, category, base_unit, purchase_unit, selling_unit,
                conversion_factor, purchase_price, selling_price, minimum_stock, recommended_stock,
                reorder_quantity, is_active, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (pid, shop_id, name, loc, cat, base, pur, sel, conv, pur_pr, sel_pr, min_st, rec_st, reo_qty, True, now, now))

        # Inventory
        cur.execute("""
            INSERT INTO inventory (shop_id, product_id, current_stock, stock_unit, last_stock_in, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (shop_id, product_id) DO UPDATE SET current_stock = EXCLUDED.current_stock;
        """, (shop_id, pid, cur_st, base, now, now, now))

        # Transaction
        unit_cost = pur_pr / conv if conv > 0 else pur_pr
        cur.execute("""
            INSERT INTO transactions (
                shop_id, product_id, transaction_type, quantity, unit, quantity_in_base_unit,
                price, total_amount, source, notes, created_by, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (shop_id, pid, 'STOCK_IN', cur_st, base, cur_st, round(unit_cost, 2), round(cur_st * unit_cost, 2), 'manual', 'Initial opening stock', user_id, now))

    print("7. Inserting Low Stock Alert & Borrowings...")
    cur.execute("""
        INSERT INTO stock_alerts (shop_id, product_id, alert_type, current_stock, threshold, is_resolved, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (shop_id, '55555555-0000-0000-0000-000000000007', 'LOW_STOCK', 8.0, 20.0, False, now))

    cur.execute("""
        INSERT INTO borrowings (shop_id, customer_id, customer_name, status, total_value, paid_amount, remaining_balance, notes, created_by, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (shop_id, '44444444-0000-0000-0000-000000000001', 'Ramesh (Kirana Regular)', 'ACTIVE', 1250.0, 0.0, 1250.0, 'Monthly ration credit', user_id, now, now))

    cur.close()
    conn.close()
    print("ALL SEED DATA INSERTED INTO SUPABASE SUCCESSFULLY!")

if __name__ == '__main__':
    seed_database()
