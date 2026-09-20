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

    # ============================================================
    # 9 ADDITIONAL RETAIL VERTICALS
    # ============================================================
    extra_verticals = [
        {
            'user_id': '55555555-5555-5555-5555-555555555555',
            'auth_id': '55555555-5555-5555-5555-555555555555',
            'email': 'clothing@dukaansetu.com',
            'full_name': 'Venkata Ramana',
            'phone': '+91 9848055555',
            'shop_id': '55555555-5555-5555-5555-555555555555',
            'shop_name': 'Sri Raghavendra Cloth Emporium',
            'shop_type': 'clothing',
            'address': 'Main Cloth Bazaar, Hanamkonda',
            'gst': '36CCCP5555E1Z1',
            'categories': ["Men's Wear", "Women's Sarees & Dresses", "Kids Wear", "Handloom & Silk", "Fabrics & Tailoring"],
            'suppliers': [
                ('55555555-0000-0000-0000-000000000001', 'Surat Silk Mills Wholesalers', '+91 9848055001', 'surat@silkmills.com', 'Textile Hub, Surat'),
            ],
            'customers': [
                ('55555555-1111-0000-0000-000000000001', 'Ravi Teja (Wedding Shopping Udhar)', '+91 9848055111', 14500.0, 'Pattu sarees and suit fabrics balance'),
            ],
            'products': [
                ('55555555-2222-0000-0000-000000000001', 'Kanchi Pattu Saree (కంచి పట్టు చీర)', 'Pattu Cheera', 'Handloom & Silk', 'piece', 'piece', 'piece', 1.0, 4800.0, 6500.0, 5.0, 40.0, 15.0, 28.0),
                ('55555555-2222-0000-0000-000000000002', "Cotton Men's Formal Shirt (కాటన్ షర్టు)", 'Cotton Shirt', "Men's Wear", 'piece', 'box', 'piece', 10.0, 5200.0, 750.0, 20.0, 120.0, 40.0, 85.0),
                ('55555555-2222-0000-0000-000000000003', "Levi's Denim Jeans 32/34 (జీన్స్ ప్యాంట్)", 'Jeans Pant', "Men's Wear", 'piece', 'piece', 'piece', 1.0, 1050.0, 1450.0, 10.0, 60.0, 20.0, 45.0),
                ('55555555-2222-0000-0000-000000000004', "Women's Cotton Kurti / Dupatta Set (కుర్తీ సెట్)", 'Kurti Set', "Women's Sarees & Dresses", 'set', 'set', 'set', 1.0, 620.0, 890.0, 15.0, 80.0, 25.0, 60.0),
                ('55555555-2222-0000-0000-000000000005', 'Pure Cotton Dhoti & Kanduva (ధోవతి & కండువా)', 'Dhovati Kanduva', "Men's Wear", 'set', 'set', 'set', 1.0, 310.0, 450.0, 10.0, 70.0, 20.0, 50.0),
                ('55555555-2222-0000-0000-000000000006', 'School Uniform Fabric Set (స్కూల్ యూనిఫామ్)', 'Uniform Fabric', 'Fabrics & Tailoring', 'meter', 'roll', 'meter', 50.0, 11000.0, 320.0, 30.0, 250.0, 100.0, 150.0),
            ]
        },
        {
            'user_id': '66666666-6666-6666-6666-666666666666',
            'auth_id': '66666666-6666-6666-6666-666666666666',
            'email': 'pharmacy@dukaansetu.com',
            'full_name': 'Dr. Suresh Reddy',
            'phone': '+91 9848066666',
            'shop_id': '66666666-6666-6666-6666-666666666666',
            'shop_name': 'Sri Durga Medical & General Stores',
            'shop_type': 'pharmacy',
            'address': 'Hospital Road, Subedari',
            'gst': '36DDDP6666F1Z2',
            'categories': ['Tablets & Capsules', 'Syrups & Suspensions', 'Injections & Insulins', 'First Aid & Ointments', 'Health & Wellness Devices'],
            'suppliers': [
                ('66666666-0000-0000-0000-000000000001', 'Apollo Pharma Wholesale Dist', '+91 9848066001', 'orders@apollodist.com', 'Pharma City, Hyderabad'),
            ],
            'customers': [
                ('66666666-1111-0000-0000-000000000001', 'Krishna Murthy (Senior Citizen BP/Sugar Udhar)', '+91 9848066111', 3250.0, 'Monthly regular prescription tab'),
            ],
            'products': [
                ('66666666-2222-0000-0000-000000000001', 'Dolo 650mg Tablets (డోలో 650)', 'Dolo 650', 'Tablets & Capsules', 'strip', 'box', 'strip', 15.0, 360.0, 32.0, 30.0, 200.0, 60.0, 150.0),
                ('66666666-2222-0000-0000-000000000002', 'Crocin Advance 500mg (క్రోసిన్)', 'Crocin', 'Tablets & Capsules', 'strip', 'box', 'strip', 20.0, 380.0, 25.0, 25.0, 150.0, 50.0, 120.0),
                ('66666666-2222-0000-0000-000000000003', 'Benadryl Cough Syrup 100ml (దగ్గు మందు)', 'Daggu Mandhu', 'Syrups & Suspensions', 'bottle', 'box', 'bottle', 12.0, 1050.0, 115.0, 10.0, 60.0, 24.0, 40.0),
                ('66666666-2222-0000-0000-000000000004', 'Human Mixtard 30/70 Insulin (ఇన్సులిన్)', 'Insulin Vial', 'Injections & Insulins', 'vial', 'pack', 'vial', 5.0, 780.0, 185.0, 5.0, 30.0, 10.0, 18.0),
                ('66666666-2222-0000-0000-000000000005', 'ORS Electral Powder 21.8g (ఓఆర్ఎస్)', 'ORS Sachet', 'First Aid & Ointments', 'sachet', 'box', 'sachet', 25.0, 420.0, 22.0, 40.0, 300.0, 100.0, 200.0),
                ('66666666-2222-0000-0000-000000000006', 'Digital BP Monitor (బీపీ మిషన్)', 'BP Monitor', 'Health & Wellness Devices', 'piece', 'piece', 'piece', 1.0, 1150.0, 1450.0, 2.0, 15.0, 5.0, 8.0),
            ]
        },
        {
            'user_id': '77777777-7777-7777-7777-777777777777',
            'auth_id': '77777777-7777-7777-7777-777777777777',
            'email': 'bakery@dukaansetu.com',
            'full_name': 'Raju Mithaiwala',
            'phone': '+91 9848077777',
            'shop_id': '77777777-7777-7777-7777-777777777777',
            'shop_name': 'Sri Sai Sweet Home & Bakery',
            'shop_type': 'bakery',
            'address': 'Nakkalagutta Junction',
            'gst': '36EEEP7777G1Z3',
            'categories': ['Fresh Cakes & Pastries', 'Traditional Sweets', 'Savory Puffs & Samosas', 'Daily Breads & Buns', 'Cookies & Biscuits'],
            'suppliers': [
                ('77777777-0000-0000-0000-000000000001', 'Vijaya Dairy Milk Supply', '+91 9848077001', 'vijaya@dairy.gov.in', 'Dairy Farm, Warangal'),
            ],
            'customers': [
                ('77777777-1111-0000-0000-000000000001', 'Modern High School (Party Order Udhar)', '+91 9848077111', 5200.0, 'Annual day samosa & cake boxes'),
            ],
            'products': [
                ('77777777-2222-0000-0000-000000000001', 'Black Forest Cake 1kg (బ్లాక్ ఫారెస్ట్ కేక్)', 'Black Forest Cake', 'Fresh Cakes & Pastries', 'kg', 'kg', 'kg', 1.0, 380.0, 550.0, 3.0, 20.0, 8.0, 12.0),
                ('77777777-2222-0000-0000-000000000002', 'Fresh Milk Bread 400g (పాల బ్రెడ్)', 'Milk Bread', 'Daily Breads & Buns', 'packet', 'crate', 'packet', 20.0, 600.0, 40.0, 15.0, 100.0, 40.0, 60.0),
                ('77777777-2222-0000-0000-000000000003', 'Ghee Mysore Pak (నెయ్యి మైసూర్ పాక్)', 'Mysore Pak', 'Traditional Sweets', 'kg', 'tray', 'kg', 5.0, 1750.0, 480.0, 5.0, 40.0, 15.0, 25.0),
                ('77777777-2222-0000-0000-000000000004', 'Kaju Katli (కాజు కట్లి)', 'Kaju Katli', 'Traditional Sweets', 'kg', 'tray', 'kg', 5.0, 3200.0, 850.0, 4.0, 25.0, 10.0, 15.0),
                ('77777777-2222-0000-0000-000000000005', 'Egg & Veg Puff (పఫ్స్)', 'Puff', 'Savory Puffs & Samosas', 'piece', 'tray', 'piece', 30.0, 480.0, 25.0, 20.0, 150.0, 60.0, 90.0),
                ('77777777-2222-0000-0000-000000000006', 'Osmania Tea Biscuits (ఉస్మానియా బిస్కెట్లు)', 'Osmania Biscuits', 'Cookies & Biscuits', 'box', 'carton', 'box', 12.0, 1080.0, 120.0, 10.0, 60.0, 24.0, 45.0),
            ]
        },
        {
            'user_id': '88888888-8888-8888-8888-888888888888',
            'auth_id': '88888888-8888-8888-8888-888888888888',
            'email': 'restaurant@dukaansetu.com',
            'full_name': 'Lakshmi Devi',
            'phone': '+91 9848088888',
            'shop_id': '88888888-8888-8888-8888-888888888888',
            'shop_name': 'Sri Annapurna Tiffin & Meals',
            'shop_type': 'restaurant',
            'address': 'Bus Stand Road',
            'gst': '36FFFP8888H1Z4',
            'categories': ['Breakfast Tiffins', 'Meals & Biryani', 'Kitchen Raw Materials', 'Curries & Starters', 'Beverages'],
            'suppliers': [
                ('88888888-0000-0000-0000-000000000001', 'Rythu Bazar Vegetable Wholesalers', '+91 9848088001', 'rythu@mandi.gov.in', 'Wholesale Mandi, Warangal'),
            ],
            'customers': [
                ('88888888-1111-0000-0000-000000000001', 'Subba Rao (Monthly Mess Account)', '+91 9848088111', 3200.0, 'Monthly lunch thali subscription'),
            ],
            'products': [
                ('88888888-2222-0000-0000-000000000001', 'Special Chicken Dum Biryani (చికెన్ దమ్ బిర్యానీ)', 'Chicken Biryani', 'Meals & Biryani', 'plate', 'plate', 'plate', 1.0, 130.0, 220.0, 10.0, 80.0, 25.0, 50.0),
                ('88888888-2222-0000-0000-000000000002', 'Ghee Masala Dosa (నెయ్యి మసాలా దోశ)', 'Masala Dosa', 'Breakfast Tiffins', 'plate', 'plate', 'plate', 1.0, 30.0, 60.0, 20.0, 150.0, 50.0, 120.0),
                ('88888888-2222-0000-0000-000000000003', 'Steamed Idli Sambar (ఇడ్లీ సాంబార్)', 'Idli Sambar', 'Breakfast Tiffins', 'plate', 'plate', 'plate', 1.0, 18.0, 40.0, 25.0, 200.0, 60.0, 150.0),
                ('88888888-2222-0000-0000-000000000004', 'South Indian Thali Meals (పూర్తి భోజనం)', 'Bhojanam', 'Meals & Biryani', 'plate', 'plate', 'plate', 1.0, 65.0, 110.0, 15.0, 100.0, 30.0, 80.0),
                ('88888888-2222-0000-0000-000000000005', 'Raw Basmati Rice Bulk 25kg (బిర్యానీ బియ్యం)', 'Basmati Rice Bag', 'Kitchen Raw Materials', 'bag', 'bag', 'bag', 1.0, 2100.0, 2400.0, 3.0, 20.0, 10.0, 15.0),
                ('88888888-2222-0000-0000-000000000006', 'Cooking Sunflower Oil Tin 15L (వంట నూనె)', 'Oil Tin', 'Kitchen Raw Materials', 'can', 'can', 'can', 1.0, 1650.0, 1850.0, 2.0, 12.0, 5.0, 8.0),
            ]
        },
        {
            'user_id': '99999999-9999-9999-9999-999999999999',
            'auth_id': '99999999-9999-9999-9999-999999999999',
            'email': 'teacoffee@dukaansetu.com',
            'full_name': 'Ramu Chaiwala',
            'phone': '+91 9848099999',
            'shop_id': '99999999-9999-9999-9999-999999999999',
            'shop_name': 'Sri Balaji Irani Tea & Coffee Point',
            'shop_type': 'teacoffee',
            'address': 'Station Road',
            'gst': '36GGGP9999I1Z5',
            'categories': ['Hot Beverages', 'Tea Stall Snacks', 'Raw Ingredients', 'Bottled Drinks', 'Biscuits & Mints'],
            'suppliers': [
                ('99999999-0000-0000-0000-000000000001', 'Sangam Dairy Whole Buffalo Milk', '+91 9848099001', 'sangam@dairy.com', 'Milk Chilling Hub, Warangal'),
            ],
            'customers': [
                ('99999999-1111-0000-0000-000000000001', 'Court Auto Drivers Union (Weekly Tea Tab)', '+91 9848099111', 1850.0, 'Daily morning and evening tea tab'),
            ],
            'products': [
                ('99999999-2222-0000-0000-000000000001', 'Special Irani Dum Chai (ఇరానీ దమ్ చాయ్)', 'Irani Chai', 'Hot Beverages', 'cup', 'cup', 'cup', 1.0, 6.0, 15.0, 50.0, 500.0, 200.0, 350.0),
                ('99999999-2222-0000-0000-000000000002', 'South Indian Filter Coffee (ఫిల్టర్ కాఫీ)', 'Filter Coffee', 'Hot Beverages', 'cup', 'cup', 'cup', 1.0, 9.0, 20.0, 30.0, 250.0, 100.0, 180.0),
                ('99999999-2222-0000-0000-000000000003', 'Hot Onion Samosa (ఉల్లి సమోసా)', 'Samosa', 'Tea Stall Snacks', 'piece', 'piece', 'piece', 1.0, 4.5, 10.0, 20.0, 180.0, 60.0, 120.0),
                ('99999999-2222-0000-0000-000000000004', 'Mirchi Bajji (మిర్చి బజ్జీ)', 'Mirchi Bajji', 'Tea Stall Snacks', 'plate', 'plate', 'plate', 1.0, 14.0, 30.0, 15.0, 100.0, 35.0, 80.0),
                ('99999999-2222-0000-0000-000000000005', 'Buffalo Milk 1 Litre (గేదె పాలు)', 'Paalu', 'Raw Ingredients', 'litre', 'can', 'litre', 20.0, 1200.0, 70.0, 10.0, 60.0, 30.0, 40.0),
                ('99999999-2222-0000-0000-000000000006', 'Sugar Commercial 50kg (చక్కెర బస్తా)', 'Chakkera Bag', 'Raw Ingredients', 'bag', 'bag', 'bag', 1.0, 1950.0, 2050.0, 2.0, 8.0, 4.0, 5.0),
            ]
        },
        {
            'user_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            'auth_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            'email': 'hardware@dukaansetu.com',
            'full_name': 'Mahesh Kumar',
            'phone': '+91 98480aaaaa',
            'shop_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            'shop_name': 'Sri Hanuman Hardware & Electricals',
            'shop_type': 'hardware',
            'address': 'Industrial Estate',
            'gst': '36HHHP0000J1Z6',
            'categories': ['Plumbing & Pipes', 'Electrical Wires & Switches', 'Cement & Construction', 'Paints & Chemicals', 'Hand Tools & Fasteners'],
            'suppliers': [
                ('aaaaaaaa-0000-0000-0000-000000000001', 'Supreme Pipes & Sanitary Wholesalers', '+91 98480aa001', 'supreme@pipesdist.com', 'Industrial Area, Hyderabad'),
            ],
            'customers': [
                ('aaaaaaaa-1111-0000-0000-000000000001', 'Koti Plumber (Contractor Udhar)', '+91 98480aa111', 18500.0, 'Apartment plumbing project materials'),
            ],
            'products': [
                ('aaaaaaaa-2222-0000-0000-000000000001', 'PVC Pipe 1 inch 10ft (పీవీసీ పైపు)', 'PVC Pipe', 'Plumbing & Pipes', 'length', 'bundle', 'length', 10.0, 1250.0, 160.0, 15.0, 100.0, 40.0, 75.0),
                ('aaaaaaaa-2222-0000-0000-000000000002', 'Finolex Copper Wire 2.5 sq mm (రాగి వైరు 90మీ)', 'Copper Wire', 'Electrical Wires & Switches', 'roll', 'box', 'roll', 4.0, 9800.0, 2850.0, 5.0, 35.0, 12.0, 20.0),
                ('aaaaaaaa-2222-0000-0000-000000000003', 'Anchor Roma Modular Switch 6A (యాంకర్ స్విచ్)', 'Anchor Switch', 'Electrical Wires & Switches', 'piece', 'box', 'piece', 20.0, 640.0, 42.0, 30.0, 200.0, 60.0, 150.0),
                ('aaaaaaaa-2222-0000-0000-000000000004', 'UltraTech Cement 50kg (సిమెంట్ బస్తా)', 'Cement Bag', 'Cement & Construction', 'bag', 'bag', 'bag', 1.0, 345.0, 390.0, 25.0, 150.0, 50.0, 85.0),
                ('aaaaaaaa-2222-0000-0000-000000000005', 'Asian Paints Apex White 20L (ఏషియన్ పెయింట్)', 'Asian Paint', 'Paints & Chemicals', 'bucket', 'bucket', 'bucket', 1.0, 3250.0, 3800.0, 4.0, 25.0, 10.0, 14.0),
                ('aaaaaaaa-2222-0000-0000-000000000006', 'Steel Screws & Rawlplugs Box (స్క్రూలు బాక్స్)', 'Screws Box', 'Hand Tools & Fasteners', 'box', 'carton', 'box', 10.0, 1350.0, 180.0, 10.0, 50.0, 20.0, 35.0),
            ]
        },
        {
            'user_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
            'auth_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
            'email': 'autoparts@dukaansetu.com',
            'full_name': 'Narasimha Rao',
            'phone': '+91 98480bbbbb',
            'shop_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
            'shop_name': 'Sri Ganesh Auto Spares & Accessories',
            'shop_type': 'autoparts',
            'address': 'Auto Nagar',
            'gst': '36IIIP1111K1Z7',
            'categories': ['Engine Oils & Lubricants', 'Brake & Clutch Parts', 'Tyres & Tubes', 'Electrical & Batteries', 'Chains & Sprockets', 'Horns & Styling', 'Filters & Cables', 'Lubricants & Care'],
            'suppliers': [
                ('bbbbbbbb-0000-0000-0000-000000000001', 'Castrol India Lubricants Stockist', '+91 98480bb001', 'orders@castrolhub.com', 'Auto Market, Secunderabad'),
                ('bbbbbbbb-0000-0000-0000-000000000002', 'Hero & Bajaj Genuine Spares Agency', '+91 98480bb002', 'genuineparts@herobajaj.in', 'Ranigunj, Secunderabad'),
                ('bbbbbbbb-0000-0000-0000-000000000003', 'Amaron Batteries & MRF Tyres Hub', '+91 98480bb003', 'sales@tyrebatteryhub.com', 'Warangal Bypass Road'),
                ('bbbbbbbb-0000-0000-0000-000000000004', 'Rolon Chains & NGK Electricals Depo', '+91 98480bb004', 'supply@rolonngk.in', 'Auto Nagar, Hyderabad')
            ],
            'customers': [
                ('bbbbbbbb-1111-0000-0000-000000000001', 'Prasad Mechanic (Auto Garage Tab)', '+91 98480bb111', 12500.0, 'Engine oil cartons & brake parts'),
                ('bbbbbbbb-1111-0000-0000-000000000002', 'Ramesh Garage (Pulsar & Splendor Specialist)', '+91 98480bb222', 8200.0, 'Chain sprocket kits and disc pads monthly tab'),
                ('bbbbbbbb-1111-0000-0000-000000000003', 'Suresh (Fleet Delivery Bike Account)', '+91 98480bb333', 3400.0, 'Engine oil and clutch cable replacement')
            ],
            'products': [
                ('bbbbbbbb-2222-0000-0000-000000000001', 'Castrol Activ 4T 20W-40 1L (ఇంజన్ ఆయిల్)', 'Engine Oil', 'Engine Oils & Lubricants', 'bottle', 'box', 'bottle', 12.0, 4200.0, 420.0, 12.0, 70.0, 24.0, 45.0),
                ('bbbbbbbb-2222-0000-0000-000000000002', 'Motul 3000 4T 10W-30 1L (మోతుల్ ఇంజన్ ఆయిల్)', 'Motul Engine Oil', 'Engine Oils & Lubricants', 'bottle', 'box', 'bottle', 12.0, 4400.0, 450.0, 10.0, 50.0, 20.0, 32.0),
                ('bbbbbbbb-2222-0000-0000-000000000003', 'Hero Splendor Brake Shoes (బ్రేక్ షూస్)', 'Brake Shoes', 'Brake & Clutch Parts', 'pair', 'box', 'pair', 10.0, 1800.0, 240.0, 8.0, 50.0, 20.0, 30.0),
                ('bbbbbbbb-2222-0000-0000-000000000004', 'Bajaj Pulsar Front Disc Brake Pads (డిస్క్ ప్యాడ్లు)', 'Disc Brake Pads', 'Brake & Clutch Parts', 'pair', 'box', 'pair', 10.0, 2200.0, 290.0, 6.0, 40.0, 15.0, 22.0),
                ('bbbbbbbb-2222-0000-0000-000000000005', 'Amaron 12V Bike Battery 4Ah (బైక్ బ్యాటరీ)', 'Bike Battery', 'Electrical & Batteries', 'unit', 'unit', 'unit', 1.0, 1180.0, 1450.0, 3.0, 20.0, 6.0, 12.0),
                ('bbbbbbbb-2222-0000-0000-000000000006', 'MRF 90/90-12 Zapper Tubeless Tyre (ఎంఆర్ఎఫ్ టైరు)', 'MRF Tyre', 'Tyres & Tubes', 'piece', 'piece', 'piece', 1.0, 1380.0, 1650.0, 4.0, 25.0, 8.0, 16.0),
                ('bbbbbbbb-2222-0000-0000-000000000007', 'NGK Spark Plug 2-Wheeler (స్పార్క్ ప్లగ్)', 'Spark Plug', 'Electrical & Batteries', 'piece', 'box', 'piece', 10.0, 650.0, 95.0, 15.0, 100.0, 30.0, 60.0),
                ('bbbbbbbb-2222-0000-0000-000000000008', 'Rolon Chain Sprocket Kit Pulsar (రోలాన్ చైన్ కిట్)', 'Chain Sprocket', 'Chains & Sprockets', 'kit', 'box', 'kit', 5.0, 4200.0, 1150.0, 3.0, 20.0, 6.0, 10.0),
                ('bbbbbbbb-2222-0000-0000-000000000009', 'Bajaj Pulsar Clutch Cable (క్లచ్ కేబుల్)', 'Clutch Cable', 'Filters & Cables', 'piece', 'bundle', 'piece', 10.0, 850.0, 130.0, 6.0, 40.0, 15.0, 25.0),
                ('bbbbbbbb-2222-0000-0000-000000000010', 'Roots 12V Dual Horn Set (రూట్స్ హార్న్ సెట్)', 'Roots Horn', 'Horns & Styling', 'pair', 'box', 'pair', 5.0, 2400.0, 650.0, 4.0, 25.0, 8.0, 14.0),
                ('bbbbbbbb-2222-0000-0000-000000000011', 'Hero Splendor Air Filter (ఎయిర్ ఫిల్టర్)', 'Air Filter', 'Filters & Cables', 'piece', 'box', 'piece', 10.0, 950.0, 140.0, 8.0, 45.0, 15.0, 28.0),
                ('bbbbbbbb-2222-0000-0000-000000000012', 'Kangaroo Chain Lube Spray 500ml (చైన్ లూబ్ స్ప్రే)', 'Chain Lube', 'Lubricants & Care', 'can', 'box', 'can', 6.0, 1100.0, 250.0, 5.0, 30.0, 12.0, 18.0),
            ]
        },
        {
            'user_id': 'cccccccc-cccc-cccc-cccc-cccccccccccc',
            'auth_id': 'cccccccc-cccc-cccc-cccc-cccccccccccc',
            'email': 'vegetables@dukaansetu.com',
            'full_name': 'Yellamma',
            'phone': '+91 98480ccccc',
            'shop_id': 'cccccccc-cccc-cccc-cccc-cccccccccccc',
            'shop_name': 'Sri Lakshmi Fresh Veg & Fruits',
            'shop_type': 'vegetables',
            'address': 'Rythu Bazar',
            'gst': '36JJJP2222L1Z8',
            'categories': ['Fresh Vegetables', 'Leafy Greens', 'Onions & Potatoes', 'Fresh Fruits', 'Exotic & Salad Veg'],
            'suppliers': [
                ('cccccccc-0000-0000-0000-000000000001', 'Bowenpally Wholesale Mandi Guild', '+91 98480cc001', 'bowenpally@mandi.gov.in', 'Mandi Yard, Secunderabad'),
            ],
            'customers': [
                ('cccccccc-1111-0000-0000-000000000001', 'Balaji Fast Food Center (Daily Veggies)', '+91 98480cc111', 3800.0, 'Daily onion, tomato, cabbage supply'),
            ],
            'products': [
                ('cccccccc-2222-0000-0000-000000000001', 'Fresh Country Tomatoes / Tamata (నాటు టమాటా)', 'Tamata', 'Fresh Vegetables', 'kg', 'crate', 'kg', 25.0, 550.0, 35.0, 20.0, 120.0, 50.0, 80.0),
                ('cccccccc-2222-0000-0000-000000000002', 'Onion / Ullipaya (ఉల్లిపాయలు)', 'Ullipaya', 'Onions & Potatoes', 'kg', 'bag', 'kg', 50.0, 1100.0, 30.0, 40.0, 250.0, 100.0, 150.0),
                ('cccccccc-2222-0000-0000-000000000003', 'Potato / Bangala Dumpa (బంగాళాదుంపలు)', 'Bangala Dumpa', 'Onions & Potatoes', 'kg', 'bag', 'kg', 50.0, 1250.0, 32.0, 30.0, 200.0, 100.0, 120.0),
                ('cccccccc-2222-0000-0000-000000000004', 'Green Chillies / Pachi Mirchi (పచ్చిమిర్చి)', 'Pachi Mirchi', 'Fresh Vegetables', 'kg', 'bag', 'kg', 10.0, 450.0, 60.0, 8.0, 40.0, 15.0, 25.0),
                ('cccccccc-2222-0000-0000-000000000005', 'Fresh Palak / Spinach (పాలకూర కట్ట)', 'Palakoora', 'Leafy Greens', 'bunch', 'bundle', 'bunch', 25.0, 225.0, 15.0, 10.0, 80.0, 25.0, 50.0),
                ('cccccccc-2222-0000-0000-000000000006', 'Yelakki Small Bananas (ఎలక్కి అరటిపండ్లు)', 'Arati Pandlu', 'Fresh Fruits', 'dozen', 'crate', 'dozen', 10.0, 420.0, 60.0, 8.0, 50.0, 20.0, 35.0),
            ]
        },
        {
            'user_id': 'dddddddd-dddd-dddd-dddd-dddddddddddd',
            'auth_id': 'dddddddd-dddd-dddd-dddd-dddddddddddd',
            'email': 'electronics@dukaansetu.com',
            'full_name': 'Arun Kumar',
            'phone': '+91 98480ddddd',
            'shop_id': 'dddddddd-dddd-dddd-dddd-dddddddddddd',
            'shop_name': 'Sri Tech Zone Mobiles & Electronics',
            'shop_type': 'electronics',
            'address': 'Complex Road',
            'gst': '36KKKP3333M1Z9',
            'categories': ['Smartphones', 'Fast Chargers & Adapters', 'Bluetooth Audio & Sound', 'Powerbanks & Cables', 'Screen Guards & Covers', 'Storage & Memory', 'Smartwatches & Gadgets'],
            'suppliers': [
                ('dddddddd-0000-0000-0000-000000000001', 'Redmi & Xiaomi National Distributor', '+91 9876554001', 'xiaomidist@mobilehub.com', 'Electronics Plaza, Hyderabad'),
                ('dddddddd-0000-0000-0000-000000000002', 'boAt Audio Official Distributorship', '+91 98480dd002', 'boatdist@audio.in', 'Warangal'),
                ('dddddddd-0000-0000-0000-000000000003', 'Samsung Mobile Regional Wholesale', '+91 98480dd001', 'samsung@wholesalehub.com', 'Secunderabad'),
                ('dddddddd-0000-0000-0000-000000000004', 'SanDisk & Portronics Gadgets Agency', '+91 98480dd003', 'orders@gadgetagency.in', 'Koti, Hyderabad')
            ],
            'customers': [
                ('dddddddd-1111-0000-0000-000000000001', 'Kalyan (Engineering Student Tab)', '+91 98480dd111', 1500.0, 'Fast charger and earbuds balance'),
                ('dddddddd-1111-0000-0000-000000000002', 'Naresh (Samsung Phone EMI Account)', '+91 98480dd222', 9500.0, 'Samsung Galaxy balance installment'),
                ('dddddddd-1111-0000-0000-000000000003', 'Suresh (Display & Tempered Glass Udhar)', '+91 98480dd333', 2800.0, 'Screen replacement & 11D tempered glass')
            ],
            'products': [
                ('dddddddd-2222-0000-0000-000000000001', 'Samsung Galaxy A15 5G 128GB (శాంసంగ్ మొబైల్)', 'Samsung Mobile', 'Smartphones', 'unit', 'unit', 'unit', 1.0, 13200.0, 14999.0, 2.0, 12.0, 4.0, 8.0),
                ('dddddddd-2222-0000-0000-000000000002', 'Redmi 13C 5G 128GB (రెడ్‌మి 5G మొబైల్)', 'Redmi Mobile', 'Smartphones', 'unit', 'unit', 'unit', 1.0, 9800.0, 11499.0, 2.0, 15.0, 5.0, 9.0),
                ('dddddddd-2222-0000-0000-000000000003', 'boAt Airdopes 141 Bluetooth Earbuds (ఇయర్ బడ్స్)', 'boAt Earbuds', 'Bluetooth Audio & Sound', 'unit', 'box', 'unit', 10.0, 8900.0, 1199.0, 5.0, 35.0, 10.0, 22.0),
                ('dddddddd-2222-0000-0000-000000000004', 'boAt Rockerz 255 Pro+ Neckband (బ్లూటూత్ నెక్‌బ్యాండ్)', 'boAt Neckband', 'Bluetooth Audio & Sound', 'unit', 'box', 'unit', 10.0, 7800.0, 1099.0, 4.0, 25.0, 8.0, 16.0),
                ('dddddddd-2222-0000-0000-000000000005', 'Fast 20W Type-C Charger Adapter (టైప్-సి ఛార్జర్)', 'Fast Charger', 'Fast Chargers & Adapters', 'unit', 'box', 'unit', 10.0, 3200.0, 499.0, 10.0, 60.0, 20.0, 40.0),
                ('dddddddd-2222-0000-0000-000000000006', 'SuperVOOC 33W Fast Charger with Cable (33W ఫాస్ట్ ఛార్జర్)', '33W Charger', 'Fast Chargers & Adapters', 'unit', 'box', 'unit', 10.0, 5200.0, 799.0, 5.0, 30.0, 10.0, 18.0),
                ('dddddddd-2222-0000-0000-000000000007', '10000mAh Dual USB Power Bank (పవర్ బ్యాంక్)', 'Power Bank', 'Powerbanks & Cables', 'unit', 'box', 'unit', 5.0, 3800.0, 999.0, 3.0, 25.0, 10.0, 15.0),
                ('dddddddd-2222-0000-0000-000000000008', '20000mAh 22.5W Fast Power Bank (20000mAh పవర్ బ్యాంక్)', '20000mAh Power Bank', 'Powerbanks & Cables', 'unit', 'box', 'unit', 5.0, 6200.0, 1699.0, 2.0, 15.0, 5.0, 8.0),
                ('dddddddd-2222-0000-0000-000000000009', 'Braided 1.5m Type-C Fast Cable (యూఎస్బీ కేబుల్)', 'Type-C Cable', 'Powerbanks & Cables', 'piece', 'bundle', 'piece', 20.0, 2200.0, 199.0, 15.0, 100.0, 30.0, 65.0),
                ('dddddddd-2222-0000-0000-000000000010', '9D Edge-to-Edge Tempered Glass (స్క్రీన్ గార్డ్)', 'Screen Guard', 'Screen Guards & Covers', 'piece', 'box', 'piece', 25.0, 1250.0, 150.0, 20.0, 150.0, 50.0, 90.0),
                ('dddddddd-2222-0000-0000-000000000011', 'SanDisk 64GB Ultra MicroSD Card (మెమరీ కార్డు)', 'Memory Card', 'Storage & Memory', 'piece', 'pack', 'piece', 10.0, 3600.0, 499.0, 5.0, 30.0, 10.0, 18.0),
                ('dddddddd-2222-0000-0000-000000000012', 'Noise ColorFit Pulse Smart Watch (స్మార్ట్ వాచ్)', 'Smart Watch', 'Smartwatches & Gadgets', 'piece', 'box', 'piece', 5.0, 6500.0, 1799.0, 3.0, 15.0, 5.0, 8.0),
            ]
        }
    ]

    for item in extra_verticals:
        print(f"Inserting vertical: {item['shop_name']} ({item['shop_type']})...")
        # User
        cur.execute("""
            INSERT INTO users (id, auth_id, email, full_name, phone, language, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name;
        """, (item['user_id'], item['auth_id'], item['email'], item['full_name'], item['phone'], 'te', True, now, now))

        # Shop
        cur.execute("""
            INSERT INTO shops (id, owner_id, name, type, phone, address, city, state, gst_number, currency, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
        """, (item['shop_id'], item['user_id'], item['shop_name'], item['shop_type'], item['phone'], item['address'], 'Warangal', 'Telangana', item['gst'], 'INR', True, now, now))

        # Categories
        for cat in item['categories']:
            cur.execute("""
                INSERT INTO categories (shop_id, name, is_active, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (item['shop_id'], cat, True, now))

        # Suppliers
        for sid, sname, sphone, semail, saddr in item['suppliers']:
            cur.execute("""
                INSERT INTO suppliers (id, shop_id, name, phone, email, address, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (sid, item['shop_id'], sname, sphone, semail, saddr, True, now, now))

        # Customers
        for cid, cname, cphone, ccred, cnote in item['customers']:
            cur.execute("""
                INSERT INTO customers (id, shop_id, name, phone, total_credit, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (cid, item['shop_id'], cname, cphone, ccred, True, now, now))

            if ccred > 0:
                cur.execute("""
                    INSERT INTO borrowings (shop_id, customer_id, customer_name, status, total_value, paid_amount, remaining_balance, notes, created_by, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (item['shop_id'], cid, cname, 'ACTIVE', ccred, 0.0, ccred, cnote, item['user_id'], now, now))

        # Products & Inventory
        for pid, name, loc, cat, base, pur, sel, conv, pur_pr, sel_pr, min_st, rec_st, reo_qty, cur_st in item['products']:
            cur.execute("""
                INSERT INTO products (
                    id, shop_id, name, local_name, category, base_unit, purchase_unit, selling_unit,
                    conversion_factor, purchase_price, selling_price, minimum_stock, recommended_stock,
                    reorder_quantity, is_active, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (pid, item['shop_id'], name, loc, cat, base, pur, sel, conv, pur_pr, sel_pr, min_st, rec_st, reo_qty, True, now, now))

            cur.execute("""
                INSERT INTO inventory (shop_id, product_id, current_stock, stock_unit, last_stock_in, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (shop_id, product_id) DO UPDATE SET current_stock = EXCLUDED.current_stock;
            """, (item['shop_id'], pid, cur_st, base, now, now, now))

    cur.close()
    conn.close()
    print("\nALL 12 SHOP VERTICALS INSERTED AND SEEDED INTO SUPABASE POSTGRESQL SUCCESSFULLY!")

if __name__ == '__main__':
    seed_database()

