"""DukaanSetu — Populate Supabase PostgreSQL with rich seed data."""
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
    """, (user_id, auth_id, 'srinivas@dukaansetu.com', 'Srinivas Kumar', '+91 9876543210', 'te', True, now, now))

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

    # ============================================================
    # 2. JEWELLERY SHOP — Sri Swarna Mahal Jewellers
    # ============================================================
    print("\n--- SEEDING JEWELLERY SHOP ---")
    jewel_user_id = '33333333-3333-3333-3333-333333333333'
    jewel_auth_id = '33333333-3333-3333-3333-333333333333'
    jewel_shop_id = '33333333-3333-3333-3333-333333333333'

    cur.execute("""
        INSERT INTO users (id, auth_id, email, full_name, phone, language, is_active, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name, email = EXCLUDED.email;
    """, (jewel_user_id, jewel_auth_id, 'jewellery@dukaansetu.com', 'Rajesh Varma (Gold Merchant)', '+91 9848012345', 'te', True, now, now))

    cur.execute("""
        INSERT INTO shops (id, owner_id, name, type, phone, address, city, state, gst_number, currency, is_active, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, type = EXCLUDED.type;
    """, (jewel_shop_id, jewel_user_id, 'Sri Swarna Mahal Jewellers', 'jewellery', '+91 9848012345', 'MG Road, Pot Market, Secunderabad', 'Hyderabad', 'Telangana', '36AABCS1234F1Z9', 'INR', True, now, now))

    jewel_categories = [
        'Gold Jewellery (22K 916)', 'Silver Ornaments & Articles (92.5)',
        'Diamond & Gemstone Jewellery', 'Bullion & Gold Coins (24K)',
        'Pooja Silverware', 'Custom Bridal Sets'
    ]
    for cat in jewel_categories:
        cur.execute("""
            INSERT INTO categories (shop_id, name, is_active, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (jewel_shop_id, cat, True, now))

    jewel_suppliers = [
        ('66666666-0000-0000-0000-000000000001', 'Kalyan Bullion Wholesalers', '+91 9848099001', 'kalyan@bullion.com', 'Bullion Street, Secunderabad'),
        ('66666666-0000-0000-0000-000000000002', 'Zaveri Bazar Gold Exporters', '+91 9848099002', 'orders@zaverigold.com', 'Zaveri Bazaar, Mumbai'),
        ('66666666-0000-0000-0000-000000000003', 'Madras Silver Crafts', '+91 9848099003', 'sales@madrassilver.com', 'NSC Bose Road, Chennai')
    ]
    for sid, name, phone, email, addr in jewel_suppliers:
        cur.execute("""
            INSERT INTO suppliers (id, shop_id, name, phone, email, address, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (sid, jewel_shop_id, name, phone, email, addr, True, now, now))

    jewel_customers = [
        ('77777777-0000-0000-0000-000000000001', 'Suresh Goud (Gold Loan / Udhar)', '+91 9848122331', 35000.0),
        ('77777777-0000-0000-0000-000000000002', 'Padma Priya (Bridal Set Advance)', '+91 9848122332', 60000.0),
        ('77777777-0000-0000-0000-000000000003', 'Venkateswara Rao (Ring Token)', '+91 9848122333', 15000.0)
    ]
    for cid, name, phone, cred in jewel_customers:
        cur.execute("""
            INSERT INTO customers (id, shop_id, name, phone, total_credit, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (cid, jewel_shop_id, name, phone, cred, True, now, now))

    jewel_products = [
        ('88888888-0000-0000-0000-000000000001', '22K Gold Chain (తాళి / నెక్లెస్ గొలుసు)', 'Bhangaru Golusu', 'Gold Jewellery (22K 916)', 'gram', 'gram', 'gram', 1.0, 6850.0, 7250.0, 20.0, 200.0, 50.0, 145.0),
        ('88888888-0000-0000-0000-000000000002', '22K Gold Bangles / Kadiyalu (బంగారు గాజులు)', 'Bhangaru Gajulu', 'Gold Jewellery (22K 916)', 'gram', 'gram', 'gram', 1.0, 6850.0, 7250.0, 40.0, 300.0, 80.0, 220.0),
        ('88888888-0000-0000-0000-000000000003', '22K Gold Ring (బంగారు ఉంగరం)', 'Bhangaru Ungaram', 'Gold Jewellery (22K 916)', 'gram', 'gram', 'gram', 1.0, 6850.0, 7300.0, 10.0, 100.0, 30.0, 45.0),
        ('88888888-0000-0000-0000-000000000004', '22K Temple Haramu (గుండాల హారం)', 'Temple Haram', 'Gold Jewellery (22K 916)', 'gram', 'gram', 'gram', 1.0, 6900.0, 7400.0, 30.0, 150.0, 40.0, 85.0),
        ('88888888-0000-0000-0000-000000000005', '22K Jhumkas / Buttalu (బంగారు బుట్టలు)', 'Bhangaru Buttalu', 'Gold Jewellery (22K 916)', 'gram', 'gram', 'gram', 1.0, 6850.0, 7350.0, 15.0, 100.0, 30.0, 65.0),
        ('88888888-0000-0000-0000-000000000006', '92.5 Silver Anklets / Pattilu (వెండి పట్టీలు)', 'Vendi Pattilu', 'Silver Ornaments & Articles (92.5)', 'gram', 'gram', 'gram', 1.0, 82.0, 95.0, 100.0, 1000.0, 250.0, 650.0),
        ('88888888-0000-0000-0000-000000000007', 'Silver Kamakshi Pooja Lamp (వెండి కామాక్షి దీపం)', 'Vendi Deepam', 'Pooja Silverware', 'gram', 'gram', 'gram', 1.0, 80.0, 92.0, 100.0, 800.0, 200.0, 480.0),
        ('88888888-0000-0000-0000-000000000008', 'Silver Dinner Plate (వెండి కంచం)', 'Vendi Kancham', 'Pooja Silverware', 'gram', 'gram', 'gram', 1.0, 78.0, 90.0, 150.0, 1000.0, 300.0, 750.0),
        ('88888888-0000-0000-0000-000000000009', '18K Diamond Solitaire Ring (వజ్రాల ఉంగరం)', 'Vajrapu Ungaram', 'Diamond & Gemstone Jewellery', 'piece', 'piece', 'piece', 1.0, 68000.0, 85000.0, 2.0, 20.0, 5.0, 12.0),
        ('88888888-0000-0000-0000-000000000010', '24K Pure Gold Coin 999 (బంగారు నాణెం 1 పవన్)', 'Bhangaru Coin', 'Bullion & Gold Coins (24K)', 'gram', 'pavan', 'gram', 8.0, 60000.0, 63200.0, 16.0, 160.0, 40.0, 80.0),
    ]
    for pid, name, loc, cat, base, pur, sel, conv, pur_pr, sel_pr, min_st, rec_st, reo_qty, cur_st in jewel_products:
        cur.execute("""
            INSERT INTO products (
                id, shop_id, name, local_name, category, base_unit, purchase_unit, selling_unit,
                conversion_factor, purchase_price, selling_price, minimum_stock, recommended_stock,
                reorder_quantity, is_active, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (pid, jewel_shop_id, name, loc, cat, base, pur, sel, conv, pur_pr, sel_pr, min_st, rec_st, reo_qty, True, now, now))

        cur.execute("""
            INSERT INTO inventory (shop_id, product_id, current_stock, stock_unit, last_stock_in, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (shop_id, product_id) DO UPDATE SET current_stock = EXCLUDED.current_stock;
        """, (jewel_shop_id, pid, cur_st, base, now, now, now))

    cur.execute("""
        INSERT INTO borrowings (shop_id, customer_id, customer_name, status, total_value, paid_amount, remaining_balance, notes, created_by, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (jewel_shop_id, '77777777-0000-0000-0000-000000000001', 'Suresh Goud (Gold Loan / Udhar)', 'ACTIVE', 35000.0, 0.0, 35000.0, 'Gold token balance on 22K bangles order', jewel_user_id, now, now))

    # ============================================================
    # 3. FLOWER SHOP — Sri Venkateswara Flower Mart
    # ============================================================
    print("\n--- SEEDING FLOWER SHOP ---")
    flower_user_id = '44444444-4444-4444-4444-444444444444'
    flower_auth_id = '44444444-4444-4444-4444-444444444444'
    flower_shop_id = '44444444-4444-4444-4444-444444444444'

    cur.execute("""
        INSERT INTO users (id, auth_id, email, full_name, phone, language, is_active, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name, email = EXCLUDED.email;
    """, (flower_user_id, flower_auth_id, 'flowers@dukaansetu.com', 'Anand Rao (Pushpa Merchant)', '+91 9440156789', 'te', True, now, now))

    cur.execute("""
        INSERT INTO shops (id, owner_id, name, type, phone, address, city, state, gst_number, currency, is_active, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, type = EXCLUDED.type;
    """, (flower_shop_id, flower_user_id, 'Sri Venkateswara Flower Mart', 'flowers', '+91 9440156789', 'Flower Market Lane, Subedari, Warangal', 'Warangal', 'Telangana', '36BBMFP5678K1ZQ', 'INR', True, now, now))

    flower_categories = [
        'Loose Flowers (విడి పూలు)', 'Garlands & Dandalu (పూల దండలు)',
        'Fragrant Leaves & Foliage (మరువం / ధవనం)', 'Pooja & Temple Offerings',
        'Bridal & Special Decor (కళ్యాణ పూలు)'
    ]
    for cat in flower_categories:
        cur.execute("""
            INSERT INTO categories (shop_id, name, is_active, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (flower_shop_id, cat, True, now))

    flower_suppliers = [
        ('99999999-0000-0000-0000-000000000001', 'Gudur Wholesale Flower Mandi', '+91 9440199001', 'gudur@flowermandi.com', 'Mandi Road, Nellore'),
        ('99999999-0000-0000-0000-000000000002', 'Hosur Rose Farmers Guild', '+91 9440199002', 'hosur@rosefarmers.org', 'Greenhouse Hub, Hosur'),
        ('99999999-0000-0000-0000-000000000003', 'Warangal Chamanthi Growers', '+91 9440199003', 'chamanthi@warangal.com', 'Market Yard, Warangal')
    ]
    for sid, name, phone, email, addr in flower_suppliers:
        cur.execute("""
            INSERT INTO suppliers (id, shop_id, name, phone, email, address, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (sid, flower_shop_id, name, phone, email, addr, True, now, now))

    flower_customers = [
        ('aaaaaaaa-0000-0000-0000-000000000001', 'Ravi Wedding Decorators (Event Booking)', '+91 9440211221', 8500.0),
        ('aaaaaaaa-0000-0000-0000-000000000002', 'Bhadrakali Temple Trust (Pooja Account)', '+91 9440211222', 4200.0),
        ('aaaaaaaa-0000-0000-0000-000000000003', 'Kavitha Garu (Varalakshmi Advance)', '+91 9440211223', 1800.0)
    ]
    for cid, name, phone, cred in flower_customers:
        cur.execute("""
            INSERT INTO customers (id, shop_id, name, phone, total_credit, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (cid, flower_shop_id, name, phone, cred, True, now, now))

    flower_products = [
        ('bbbbbbbb-0000-0000-0000-000000000001', 'Jasmine / Mallepoolu (మల్లెపూలు)', 'Mallepoolu', 'Loose Flowers (విడి పూలు)', 'mora', 'basket', 'mora', 25.0, 1000.0, 60.0, 10.0, 60.0, 20.0, 45.0),
        ('bbbbbbbb-0000-0000-0000-000000000002', 'Yellow Marigold / Banthi (పసుపు బంతిపూలు)', 'Banthipoolu', 'Loose Flowers (విడి పూలు)', 'kg', 'bag', 'kg', 20.0, 1000.0, 80.0, 15.0, 100.0, 30.0, 65.0),
        ('bbbbbbbb-0000-0000-0000-000000000003', 'Orange Marigold (కాషాయం బంతిపూలు)', 'Kashayam Banthi', 'Loose Flowers (విడి పూలు)', 'kg', 'bag', 'kg', 20.0, 1100.0, 90.0, 10.0, 80.0, 25.0, 40.0),
        ('bbbbbbbb-0000-0000-0000-000000000004', 'Red Dutch Roses (ఎరుపు గులాబీలు)', 'Gulabi Poolu', 'Loose Flowers (విడి పూలు)', 'bundle', 'bundle', 'stem', 20.0, 180.0, 15.0, 2.0, 15.0, 5.0, 8.0),
        ('bbbbbbbb-0000-0000-0000-000000000005', 'Chrysanthemum / Chamanthi (చామంతిపూలు)', 'Chamanthi', 'Loose Flowers (విడి పూలు)', 'kg', 'bag', 'kg', 10.0, 1200.0, 180.0, 8.0, 50.0, 15.0, 35.0),
        ('bbbbbbbb-0000-0000-0000-000000000006', 'Crossandra / Kanakambaram (కనకాంబరాలు)', 'Kanakambaram', 'Loose Flowers (విడి పూలు)', 'mora', 'basket', 'mora', 15.0, 1275.0, 120.0, 5.0, 40.0, 10.0, 25.0),
        ('bbbbbbbb-0000-0000-0000-000000000007', 'Pink Lotus / Kamalam (తామరపూలు)', 'Kamalam', 'Pooja & Temple Offerings', 'piece', 'bundle', 'piece', 25.0, 375.0, 25.0, 10.0, 100.0, 30.0, 60.0),
        ('bbbbbbbb-0000-0000-0000-000000000008', 'Wedding Rose & Jasmine Garlands (కళ్యాణ దండలు)', 'Kalyana Dandalu', 'Bridal & Special Decor (కళ్యాణ పూలు)', 'set', 'set', 'set', 1.0, 2200.0, 3500.0, 1.0, 6.0, 2.0, 4.0),
        ('bbbbbbbb-0000-0000-0000-000000000009', 'Fragrant Maru Bundles (మరువము కట్టలు)', 'Maruvamu', 'Fragrant Leaves & Foliage (మరువం / ధవనం)', 'kattu', 'basket', 'kattu', 50.0, 600.0, 20.0, 10.0, 80.0, 25.0, 50.0),
        ('bbbbbbbb-0000-0000-0000-000000000010', 'Temple Tulasi Garland (తులసి మాల)', 'Tulasi Mala', 'Pooja & Temple Offerings', 'piece', 'bundle', 'piece', 10.0, 250.0, 40.0, 5.0, 50.0, 15.0, 30.0),
    ]
    for pid, name, loc, cat, base, pur, sel, conv, pur_pr, sel_pr, min_st, rec_st, reo_qty, cur_st in flower_products:
        cur.execute("""
            INSERT INTO products (
                id, shop_id, name, local_name, category, base_unit, purchase_unit, selling_unit,
                conversion_factor, purchase_price, selling_price, minimum_stock, recommended_stock,
                reorder_quantity, is_active, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (pid, flower_shop_id, name, loc, cat, base, pur, sel, conv, pur_pr, sel_pr, min_st, rec_st, reo_qty, True, now, now))

        cur.execute("""
            INSERT INTO inventory (shop_id, product_id, current_stock, stock_unit, last_stock_in, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (shop_id, product_id) DO UPDATE SET current_stock = EXCLUDED.current_stock;
        """, (flower_shop_id, pid, cur_st, base, now, now, now))

    cur.execute("""
        INSERT INTO borrowings (shop_id, customer_id, customer_name, status, total_value, paid_amount, remaining_balance, notes, created_by, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (flower_shop_id, 'aaaaaaaa-0000-0000-0000-000000000001', 'Ravi Wedding Decorators (Event Booking)', 'ACTIVE', 8500.0, 0.0, 8500.0, 'Mandapam flower garland booking advance', flower_user_id, now, now))

    cur.close()
    conn.close()
    print("\nALL SEED DATA FOR KIRANA, JEWELLERY & FLOWER SHOPS INSERTED SUCCESSFULLY!")

if __name__ == '__main__':
    seed_database()
