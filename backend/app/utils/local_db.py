"""DukaanSetu — Embedded Local / Fallback Database Client.
Provides 100% compatibility with Supabase's Python query interface (.table().select().eq().execute()).
Provides realistic Indian Kirana store data for immediate testing and offline reliability.
"""
import uuid
import re
from datetime import datetime, timezone

DEMO_USER_ID = "11111111-1111-1111-1111-111111111111"
DEMO_AUTH_ID = "demo-auth-id"
DEMO_SHOP_ID = "22222222-2222-2222-2222-222222222222"

DEMO_JEWEL_USER_ID = "33333333-3333-3333-3333-333333333333"
DEMO_JEWEL_AUTH_ID = "33333333-3333-3333-3333-333333333333"
DEMO_JEWEL_SHOP_ID = "33333333-3333-3333-3333-333333333333"

DEMO_FLOWER_USER_ID = "44444444-4444-4444-4444-444444444444"
DEMO_FLOWER_AUTH_ID = "44444444-4444-4444-4444-444444444444"
DEMO_FLOWER_SHOP_ID = "44444444-4444-4444-4444-444444444444"

class QueryResult:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"<QueryResult count={len(self.data) if isinstance(self.data, list) else 1}>"


class TableQuery:
    def __init__(self, table_name, store):
        self.table_name = table_name
        self.store = store
        self.selected_cols = None
        self.filters = []
        self.sort_field = None
        self.sort_desc = False
        self.limit_val = None
        self.is_single = False
        self.pending_op = None # ('insert', data), ('update', data), ('delete', None)

    def select(self, cols="*"):
        self.selected_cols = [c.strip() for c in cols.split(",")] if cols != "*" else None
        return self

    def eq(self, field, value):
        self.filters.append(('eq', field, value))
        return self

    def neq(self, field, value):
        self.filters.append(('neq', field, value))
        return self

    def ilike(self, field, pattern):
        # Convert SQL LIKE pattern (e.g. %query%) to case-insensitive match
        clean_pat = pattern.replace("%", "").lower()
        self.filters.append(('ilike', field, clean_pat))
        return self

    def in_(self, field, values):
        self.filters.append(('in', field, set(values)))
        return self

    def gte(self, field, value):
        self.filters.append(('gte', field, value))
        return self

    def lte(self, field, value):
        self.filters.append(('lte', field, value))
        return self

    def order(self, field, desc=False):
        self.sort_field = field
        self.sort_desc = desc
        return self

    def limit(self, count):
        self.limit_val = count
        return self

    def single(self):
        self.is_single = True
        return self

    def maybe_single(self):
        self.is_single = True
        return self

    def insert(self, data):
        self.pending_op = ('insert', data)
        return self

    def update(self, data):
        self.pending_op = ('update', data)
        return self

    def delete(self):
        self.pending_op = ('delete', None)
        return self

    def execute(self):
        table_rows = self.store.get(self.table_name, [])

        if self.pending_op:
            op, payload = self.pending_op
            now = datetime.now(timezone.utc).isoformat()

            if op == 'insert':
                records = payload if isinstance(payload, list) else [payload]
                inserted = []
                for rec in records:
                    row = dict(rec)
                    if 'id' not in row:
                        row['id'] = str(uuid.uuid4())
                    if 'created_at' not in row:
                        row['created_at'] = now
                    if 'updated_at' not in row:
                        row['updated_at'] = now
                    table_rows.append(row)
                    inserted.append(row)
                self.store[self.table_name] = table_rows
                return QueryResult(inserted[0] if self.is_single else inserted)

            elif op == 'update':
                updated = []
                for row in table_rows:
                    if self._matches(row):
                        row.update(payload)
                        row['updated_at'] = now
                        updated.append(row)
                return QueryResult(updated[0] if (self.is_single and updated) else updated)

            elif op == 'delete':
                remaining = []
                deleted = []
                for row in table_rows:
                    if self._matches(row):
                        deleted.append(row)
                    else:
                        remaining.append(row)
                self.store[self.table_name] = remaining
                return QueryResult(deleted)

        # Query Read Operation
        filtered = [r for r in table_rows if self._matches(r)]

        if self.sort_field:
            filtered.sort(key=lambda x: x.get(self.sort_field, '') or '', reverse=self.sort_desc)

        if self.limit_val is not None:
            filtered = filtered[:self.limit_val]

        if self.selected_cols:
            filtered = [{k: r.get(k) for k in self.selected_cols if k in r} for r in filtered]

        if self.is_single:
            return QueryResult(filtered[0] if filtered else None)

        return QueryResult(filtered)

    def _matches(self, row):
        for op, field, val in self.filters:
            row_val = row.get(field)
            if op == 'eq' and str(row_val) != str(val):
                return False
            if op == 'neq' and str(row_val) == str(val):
                return False
            if op == 'ilike' and val not in str(row_val).lower():
                return False
            if op == 'in' and str(row_val) not in [str(v) for v in val]:
                return False
            if op == 'gte' and (row_val is None or row_val < val):
                return False
            if op == 'lte' and (row_val is None or row_val > val):
                return False
        return True


class MockAuthUser:
    def __init__(self, user_id=DEMO_USER_ID, email="demo@dukaansetu.com"):
        self.id = user_id
        self.email = email


class MockAuthResponse:
    def __init__(self, user):
        self.user = user


class MockAuth:
    def __init__(self, store):
        self.store = store

    def get_user(self, token):
        users = self.store.get('users', [])
        target_email = "jewellery@dukaansetu.com" if token in ('demo-token-jewellery', 'demo-token-gold') else (
            "flowers@dukaansetu.com" if token in ('demo-token-flowers', 'demo-token-pushpa') else "srinivas@dukaansetu.com"
        )
        user = next((u for u in users if u.get('email') == target_email), None) or (users[0] if users else None)
        user_id = user['auth_id'] if user else DEMO_AUTH_ID
        email = user['email'] if user else target_email
        return MockAuthResponse(MockAuthUser(user_id=user_id, email=email))

    def sign_in_with_password(self, credentials):
        users = self.store.get('users', [])
        email = credentials.get('email', '').strip().lower()
        token = 'demo-token-jewellery' if ('jewel' in email or 'swarna' in email) else (
            'demo-token-flowers' if ('flower' in email or 'pushpa' in email) else 'demo-token-dukaansetu'
        )
        for u in users:
            if u.get('email', '').lower() == email:
                user_obj = MockAuthUser(user_id=u['auth_id'], email=u['email'])
                res = MockAuthResponse(user_obj)
                res.session = type('Session', (), {
                    'access_token': token,
                    'refresh_token': 'demo-refresh-token'
                })()
                return res

        auth_id = DEMO_JEWEL_AUTH_ID if 'jewel' in email else (
            DEMO_FLOWER_AUTH_ID if 'flower' in email else DEMO_AUTH_ID
        )
        user_obj = MockAuthUser(user_id=auth_id, email=email or "demo@dukaansetu.com")
        res = MockAuthResponse(user_obj)
        res.session = type('Session', (), {
            'access_token': token,
            'refresh_token': 'demo-refresh-token'
        })()
        return res


class LocalDbClient:
    """In-memory Supabase replacement seeded with realistic Kirana store catalog."""
    def __init__(self):
        self.store = {}
        self.auth = MockAuth(self.store)
        self.storage = type('MockStorage', (), {
            'from_': lambda self, bucket: type('Bucket', (), {
                'upload': lambda *args, **kwargs: {'path': 'voice-recordings/demo.wav'}
            })()
        })()
        self._init_seed_data()

    def table(self, name):
        if name not in self.store:
            self.store[name] = []
        return TableQuery(name, self.store)

    def _init_seed_data(self):
        now = datetime.now(timezone.utc).isoformat()

        # Users (Kirana, Jewellery, Flowers)
        self.store['users'] = [
            {
                'id': DEMO_USER_ID,
                'auth_id': DEMO_AUTH_ID,
                'email': 'srinivas@dukaansetu.com',
                'full_name': 'Srinivas Kumar',
                'phone': '+91 9876543210',
                'language': 'te',
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_JEWEL_USER_ID,
                'auth_id': DEMO_JEWEL_AUTH_ID,
                'email': 'jewellery@dukaansetu.com',
                'full_name': 'Rajesh Varma (Gold Merchant)',
                'phone': '+91 9848012345',
                'language': 'te',
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_FLOWER_USER_ID,
                'auth_id': DEMO_FLOWER_AUTH_ID,
                'email': 'flowers@dukaansetu.com',
                'full_name': 'Anand Rao (Pushpa Merchant)',
                'phone': '+91 9440156789',
                'language': 'te',
                'is_active': True,
                'created_at': now,
                'updated_at': now
            }
        ]

        # Shops (Kirana, Jewellery, Flowers)
        self.store['shops'] = [
            {
                'id': DEMO_SHOP_ID,
                'owner_id': DEMO_USER_ID,
                'name': 'Sri Lakshmi Kirana Store',
                'type': 'kirana',
                'phone': '+91 9876543210',
                'address': 'Main Road, Hanamkonda',
                'city': 'Warangal',
                'state': 'Telangana',
                'gst_number': '36AAAAA0000A1Z5',
                'currency': 'INR',
                'tax_rate': 0,
                'settings': {},
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_JEWEL_SHOP_ID,
                'owner_id': DEMO_JEWEL_USER_ID,
                'name': 'Sri Swarna Mahal Jewellers',
                'type': 'jewellery',
                'phone': '+91 9848012345',
                'address': 'MG Road, Pot Market, Secunderabad',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'gst_number': '36AABCS1234F1Z9',
                'currency': 'INR',
                'tax_rate': 3,
                'settings': {},
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_FLOWER_SHOP_ID,
                'owner_id': DEMO_FLOWER_USER_ID,
                'name': 'Sri Venkateswara Flower Mart',
                'type': 'flowers',
                'phone': '+91 9440156789',
                'address': 'Flower Market Lane, Subedari, Warangal',
                'city': 'Warangal',
                'state': 'Telangana',
                'gst_number': '36BBMFP5678K1ZQ',
                'currency': 'INR',
                'tax_rate': 0,
                'settings': {},
                'is_active': True,
                'created_at': now,
                'updated_at': now
            }
        ]

        # Categories
        cat_names = [
            'Grains & Rice', 'Pulses & Dal', 'Spices & Masala',
            'Sugar & Jaggery', 'Oils & Ghee', 'Dairy',
            'Beverages', 'Snacks & Biscuits', 'Cleaning & Household',
            'Personal Care', 'Other'
        ]
        self.store['categories'] = [{
            'id': str(uuid.uuid4()),
            'shop_id': DEMO_SHOP_ID,
            'name': name,
            'is_active': True,
            'created_at': now
        } for name in cat_names]

        # Suppliers
        supp_data = [
            ('ABC Traders', '+91 9876543001', 'abc@traders.com', 'Wholesale Market, Warangal'),
            ('Srinivas Wholesale', '+91 9876543002', 'srinivas@wholesale.com', 'Grain Market, Warangal'),
            ('Lakshmi Distributors', '+91 9876543003', 'lakshmi@dist.com', 'Industrial Area, Hyderabad')
        ]
        suppliers = []
        for name, phone, email, addr in supp_data:
            s_id = str(uuid.uuid4())
            suppliers.append({
                'id': s_id,
                'shop_id': DEMO_SHOP_ID,
                'name': name,
                'phone': phone,
                'email': email,
                'address': addr,
                'is_active': True,
                'created_at': now,
                'updated_at': now
            })
        self.store['suppliers'] = suppliers

        # Customers
        cust_data = [
            ('Ramesh (Kirana Regular)', '+91 9848022334', 1250.0),
            ('Suresh (Teacher)', '+91 9848033445', 450.0),
            ('Anil (Auto Driver)', '+91 9848044556', 0.0)
        ]
        customers = []
        for name, phone, credit in cust_data:
            c_id = str(uuid.uuid4())
            customers.append({
                'id': c_id,
                'shop_id': DEMO_SHOP_ID,
                'name': name,
                'phone': phone,
                'total_credit': credit,
                'is_active': True,
                'created_at': now,
                'updated_at': now
            })
        self.store['customers'] = customers

        # Products & Inventory
        catalog = [
            {
                'id': 'p1111111-0000-0000-0000-000000000001',
                'name': 'Rice (Biyyam)', 'local_name': 'Biyyam', 'category': 'Grains & Rice',
                'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg',
                'conversion_factor': 25.0, 'purchase_price': 1450.0, 'selling_price': 65.0,
                'minimum_stock': 125.0, 'recommended_stock': 500.0, 'reorder_quantity': 250.0,
                'current_stock': 450.0
            },
            {
                'id': 'p1111111-0000-0000-0000-000000000002',
                'name': 'Sugar (Chakkera)', 'local_name': 'Chakkera', 'category': 'Sugar & Jaggery',
                'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg',
                'conversion_factor': 50.0, 'purchase_price': 2100.0, 'selling_price': 48.0,
                'minimum_stock': 50.0, 'recommended_stock': 200.0, 'reorder_quantity': 100.0,
                'current_stock': 180.0
            },
            {
                'id': 'p1111111-0000-0000-0000-000000000003',
                'name': 'Sunflower Oil (Nune)', 'local_name': 'Nune', 'category': 'Oils & Ghee',
                'base_unit': 'litre', 'purchase_unit': 'litre', 'selling_unit': 'litre',
                'conversion_factor': 1.0, 'purchase_price': 150.0, 'selling_price': 165.0,
                'minimum_stock': 10.0, 'recommended_stock': 50.0, 'reorder_quantity': 30.0,
                'current_stock': 35.0
            },
            {
                'id': 'p1111111-0000-0000-0000-000000000004',
                'name': 'Toor Dal (Kandi Pappu)', 'local_name': 'Kandi Pappu', 'category': 'Pulses & Dal',
                'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg',
                'conversion_factor': 25.0, 'purchase_price': 2750.0, 'selling_price': 125.0,
                'minimum_stock': 25.0, 'recommended_stock': 100.0, 'reorder_quantity': 50.0,
                'current_stock': 65.0
            },
            {
                'id': 'p1111111-0000-0000-0000-000000000005',
                'name': 'Parle-G Biscuits', 'local_name': 'Parle-G', 'category': 'Snacks & Biscuits',
                'base_unit': 'packet', 'purchase_unit': 'carton', 'selling_unit': 'packet',
                'conversion_factor': 24.0, 'purchase_price': 240.0, 'selling_price': 10.0,
                'minimum_stock': 50.0, 'recommended_stock': 200.0, 'reorder_quantity': 96.0,
                'current_stock': 120.0
            },
            {
                'id': 'p1111111-0000-0000-0000-000000000006',
                'name': 'Red Label Tea', 'local_name': 'Tea Podi', 'category': 'Beverages',
                'base_unit': 'packet', 'purchase_unit': 'box', 'selling_unit': 'packet',
                'conversion_factor': 12.0, 'purchase_price': 1200.0, 'selling_price': 110.0,
                'minimum_stock': 20.0, 'recommended_stock': 60.0, 'reorder_quantity': 36.0,
                'current_stock': 42.0
            },
            {
                'id': 'p1111111-0000-0000-0000-000000000007',
                'name': 'Jaggery (Bellam)', 'local_name': 'Bellam', 'category': 'Sugar & Jaggery',
                'base_unit': 'kg', 'purchase_unit': 'kg', 'selling_unit': 'kg',
                'conversion_factor': 1.0, 'purchase_price': 55.0, 'selling_price': 70.0,
                'minimum_stock': 20.0, 'recommended_stock': 50.0, 'reorder_quantity': 25.0,
                'current_stock': 8.0 # Low stock alert trigger!
            },
            {
                'id': 'p1111111-0000-0000-0000-000000000008',
                'name': 'Nescafe Coffee', 'local_name': 'Coffee Podi', 'category': 'Beverages',
                'base_unit': 'packet', 'purchase_unit': 'box', 'selling_unit': 'packet',
                'conversion_factor': 12.0, 'purchase_price': 2400.0, 'selling_price': 220.0,
                'minimum_stock': 10.0, 'recommended_stock': 36.0, 'reorder_quantity': 24.0,
                'current_stock': 30.0
            }
        ]

        self.store['products'] = []
        self.store['inventory'] = []
        self.store['transactions'] = []

        for p in catalog:
            stock = p.pop('current_stock')
            p['shop_id'] = DEMO_SHOP_ID
            p['is_active'] = True
            p['supplier_id'] = suppliers[0]['id']
            p['created_at'] = now
            p['updated_at'] = now
            self.store['products'].append(p)

            # Inventory entry
            self.store['inventory'].append({
                'id': str(uuid.uuid4()),
                'shop_id': DEMO_SHOP_ID,
                'product_id': p['id'],
                'current_stock': stock,
                'stock_unit': p['base_unit'],
                'last_stock_in': now,
                'last_stock_out': now,
                'created_at': now,
                'updated_at': now
            })

            # Initial stock-in transaction
            unit_cost = p['purchase_price'] / p['conversion_factor'] if p['conversion_factor'] > 0 else p['purchase_price']
            self.store['transactions'].append({
                'id': str(uuid.uuid4()),
                'shop_id': DEMO_SHOP_ID,
                'product_id': p['id'],
                'transaction_type': 'STOCK_IN',
                'quantity': stock,
                'unit': p['base_unit'],
                'quantity_in_base_unit': stock,
                'price': round(unit_cost, 2),
                'total_amount': round(stock * unit_cost, 2),
                'source': 'manual',
                'notes': 'Initial opening stock',
                'created_by': DEMO_USER_ID,
                'created_at': now
            })

        # Low stock alert for Jaggery
        self.store['stock_alerts'] = [{
            'id': str(uuid.uuid4()),
            'shop_id': DEMO_SHOP_ID,
            'product_id': 'p1111111-0000-0000-0000-000000000007',
            'alert_type': 'LOW_STOCK',
            'current_stock': 8.0,
            'threshold': 20.0,
            'is_resolved': False,
            'created_at': now
        }]

        # Notifications
        self.store['notifications'] = [{
            'id': str(uuid.uuid4()),
            'shop_id': DEMO_SHOP_ID,
            'user_id': DEMO_USER_ID,
            'type': 'LOW_STOCK',
            'title': 'Low Stock Alert: Jaggery (Bellam)',
            'message': 'Current stock (8.0 kg) is below minimum threshold (20.0 kg). Time to reorder!',
            'data': {'product_name': 'Jaggery (Bellam)', 'current_stock': 8.0},
            'is_read': False,
            'created_at': now
        }]

        # Active Borrowing for Ramesh
        b_id = str(uuid.uuid4())
        self.store['borrowings'] = [{
            'id': b_id,
            'shop_id': DEMO_SHOP_ID,
            'customer_id': customers[0]['id'],
            'customer_name': customers[0]['name'],
            'status': 'ACTIVE',
            'total_value': 1250.0,
            'paid_amount': 0.0,
            'remaining_balance': 1250.0,
            'notes': 'Monthly ration credit',
            'created_by': DEMO_USER_ID,
            'created_at': now,
            'updated_at': now
        }]
        self.store['borrowing_items'] = [{
            'id': str(uuid.uuid4()),
            'borrowing_id': b_id,
            'shop_id': DEMO_SHOP_ID,
            'product_id': 'p1111111-0000-0000-0000-000000000001',
            'quantity': 10.0,
            'unit': 'kg',
            'returned_quantity': 0.0,
            'price': 65.0,
            'total_amount': 650.0,
            'status': 'ACTIVE',
            'created_at': now,
            'updated_at': now
        }]

        self.store['voice_conversations'] = []

        # ============================================================
        # JEWELLERY SHOP DATA (Sri Swarna Mahal Jewellers)
        # ============================================================
        jewel_cats = ['Gold Jewellery (22K 916)', 'Silver Ornaments & Articles (92.5)', 'Diamond & Gemstone Jewellery', 'Bullion & Gold Coins (24K)', 'Pooja Silverware']
        for c in jewel_cats:
            self.store['categories'].append({'id': str(uuid.uuid4()), 'shop_id': DEMO_JEWEL_SHOP_ID, 'name': c, 'is_active': True, 'created_at': now})

        jewel_supps = [
            {'id': str(uuid.uuid4()), 'shop_id': DEMO_JEWEL_SHOP_ID, 'name': 'Kalyan Bullion Wholesalers', 'phone': '+91 9848099001', 'email': 'kalyan@bullion.com', 'address': 'Bullion St, Secunderabad', 'is_active': True, 'created_at': now, 'updated_at': now},
            {'id': str(uuid.uuid4()), 'shop_id': DEMO_JEWEL_SHOP_ID, 'name': 'Zaveri Bazar Gold Exporters', 'phone': '+91 9848099002', 'email': 'orders@zaverigold.com', 'address': 'Zaveri Bazaar, Mumbai', 'is_active': True, 'created_at': now, 'updated_at': now}
        ]
        self.store['suppliers'].extend(jewel_supps)

        jewel_custs = [
            {'id': str(uuid.uuid4()), 'shop_id': DEMO_JEWEL_SHOP_ID, 'name': 'Suresh Goud (Gold Loan / Udhar)', 'phone': '+91 9848122331', 'total_credit': 35000.0, 'is_active': True, 'created_at': now, 'updated_at': now},
            {'id': str(uuid.uuid4()), 'shop_id': DEMO_JEWEL_SHOP_ID, 'name': 'Padma Priya (Bridal Set Advance)', 'phone': '+91 9848122332', 'total_credit': 60000.0, 'is_active': True, 'created_at': now, 'updated_at': now}
        ]
        self.store['customers'].extend(jewel_custs)

        jewel_catalog = [
            {'id': 'p2222222-0000-0000-0000-000000000001', 'name': '22K Gold Chain (తాళి / నెక్లెస్ గొలుసు)', 'local_name': 'Bhangaru Golusu', 'category': 'Gold Jewellery (22K 916)', 'base_unit': 'gram', 'purchase_unit': 'gram', 'selling_unit': 'gram', 'conversion_factor': 1.0, 'purchase_price': 6850.0, 'selling_price': 7250.0, 'minimum_stock': 20.0, 'recommended_stock': 200.0, 'reorder_quantity': 50.0, 'current_stock': 145.0},
            {'id': 'p2222222-0000-0000-0000-000000000002', 'name': '22K Gold Bangles (బంగారు గాజులు)', 'local_name': 'Bhangaru Gajulu', 'category': 'Gold Jewellery (22K 916)', 'base_unit': 'gram', 'purchase_unit': 'gram', 'selling_unit': 'gram', 'conversion_factor': 1.0, 'purchase_price': 6850.0, 'selling_price': 7250.0, 'minimum_stock': 40.0, 'recommended_stock': 300.0, 'reorder_quantity': 80.0, 'current_stock': 220.0},
            {'id': 'p2222222-0000-0000-0000-000000000003', 'name': '22K Gold Ring (బంగారు ఉంగరం)', 'local_name': 'Bhangaru Ungaram', 'category': 'Gold Jewellery (22K 916)', 'base_unit': 'gram', 'purchase_unit': 'gram', 'selling_unit': 'gram', 'conversion_factor': 1.0, 'purchase_price': 6850.0, 'selling_price': 7300.0, 'minimum_stock': 10.0, 'recommended_stock': 100.0, 'reorder_quantity': 30.0, 'current_stock': 45.0},
            {'id': 'p2222222-0000-0000-0000-000000000004', 'name': '92.5 Silver Anklets / Pattilu (వెండి పట్టీలు)', 'local_name': 'Vendi Pattilu', 'category': 'Silver Ornaments & Articles (92.5)', 'base_unit': 'gram', 'purchase_unit': 'gram', 'selling_unit': 'gram', 'conversion_factor': 1.0, 'purchase_price': 82.0, 'selling_price': 95.0, 'minimum_stock': 100.0, 'recommended_stock': 1000.0, 'reorder_quantity': 250.0, 'current_stock': 650.0},
            {'id': 'p2222222-0000-0000-0000-000000000005', 'name': 'Silver Kamakshi Pooja Lamp (వెండి కామాక్షి దీపం)', 'local_name': 'Vendi Deepam', 'category': 'Pooja Silverware', 'base_unit': 'gram', 'purchase_unit': 'gram', 'selling_unit': 'gram', 'conversion_factor': 1.0, 'purchase_price': 80.0, 'selling_price': 92.0, 'minimum_stock': 100.0, 'recommended_stock': 800.0, 'reorder_quantity': 200.0, 'current_stock': 480.0},
            {'id': 'p2222222-0000-0000-0000-000000000006', 'name': '24K Pure Gold Coin 999 (బంగారు నాణెం)', 'local_name': 'Bhangaru Coin', 'category': 'Bullion & Gold Coins (24K)', 'base_unit': 'gram', 'purchase_unit': 'pavan', 'selling_unit': 'gram', 'conversion_factor': 8.0, 'purchase_price': 60000.0, 'selling_price': 63200.0, 'minimum_stock': 16.0, 'recommended_stock': 160.0, 'reorder_quantity': 40.0, 'current_stock': 80.0}
        ]
        for p in jewel_catalog:
            stock = p.pop('current_stock')
            p['shop_id'] = DEMO_JEWEL_SHOP_ID
            p['is_active'] = True
            p['supplier_id'] = jewel_supps[0]['id']
            p['created_at'] = now
            p['updated_at'] = now
            self.store['products'].append(p)
            self.store['inventory'].append({
                'id': str(uuid.uuid4()), 'shop_id': DEMO_JEWEL_SHOP_ID, 'product_id': p['id'],
                'current_stock': stock, 'stock_unit': p['base_unit'], 'last_stock_in': now, 'last_stock_out': now,
                'created_at': now, 'updated_at': now
            })

        # Active Gold Udhar for Suresh Goud
        jb_id = str(uuid.uuid4())
        self.store['borrowings'].append({
            'id': jb_id, 'shop_id': DEMO_JEWEL_SHOP_ID, 'customer_id': jewel_custs[0]['id'],
            'customer_name': jewel_custs[0]['name'], 'status': 'ACTIVE', 'total_value': 35000.0,
            'paid_amount': 0.0, 'remaining_balance': 35000.0, 'notes': 'Gold token balance on 22K bangles order',
            'created_by': DEMO_JEWEL_USER_ID, 'created_at': now, 'updated_at': now
        })

        # ============================================================
        # FLOWER SHOP DATA (Sri Venkateswara Flower Mart)
        # ============================================================
        flower_cats = ['Loose Flowers (విడి పూలు)', 'Garlands & Dandalu (పూల దండలు)', 'Fragrant Leaves & Foliage (మరువం / ధవనం)', 'Pooja & Temple Offerings', 'Bridal & Special Decor (కళ్యాణ పూలు)']
        for c in flower_cats:
            self.store['categories'].append({'id': str(uuid.uuid4()), 'shop_id': DEMO_FLOWER_SHOP_ID, 'name': c, 'is_active': True, 'created_at': now})

        flower_supps = [
            {'id': str(uuid.uuid4()), 'shop_id': DEMO_FLOWER_SHOP_ID, 'name': 'Gudur Wholesale Flower Mandi', 'phone': '+91 9440199001', 'email': 'gudur@flowermandi.com', 'address': 'Mandi Rd, Nellore', 'is_active': True, 'created_at': now, 'updated_at': now},
            {'id': str(uuid.uuid4()), 'shop_id': DEMO_FLOWER_SHOP_ID, 'name': 'Hosur Rose Farmers Guild', 'phone': '+91 9440199002', 'email': 'hosur@rosefarmers.org', 'address': 'Greenhouse Hub, Hosur', 'is_active': True, 'created_at': now, 'updated_at': now}
        ]
        self.store['suppliers'].extend(flower_supps)

        flower_custs = [
            {'id': str(uuid.uuid4()), 'shop_id': DEMO_FLOWER_SHOP_ID, 'name': 'Ravi Wedding Decorators (Event Booking)', 'phone': '+91 9440211221', 'total_credit': 8500.0, 'is_active': True, 'created_at': now, 'updated_at': now},
            {'id': str(uuid.uuid4()), 'shop_id': DEMO_FLOWER_SHOP_ID, 'name': 'Bhadrakali Temple Trust (Pooja Account)', 'phone': '+91 9440211222', 'total_credit': 4200.0, 'is_active': True, 'created_at': now, 'updated_at': now}
        ]
        self.store['customers'].extend(flower_custs)

        flower_catalog = [
            {'id': 'p3333333-0000-0000-0000-000000000001', 'name': 'Jasmine / Mallepoolu (మల్లెపూలు)', 'local_name': 'Mallepoolu', 'category': 'Loose Flowers (విడి పూలు)', 'base_unit': 'mora', 'purchase_unit': 'basket', 'selling_unit': 'mora', 'conversion_factor': 25.0, 'purchase_price': 1000.0, 'selling_price': 60.0, 'minimum_stock': 10.0, 'recommended_stock': 60.0, 'reorder_quantity': 20.0, 'current_stock': 45.0},
            {'id': 'p3333333-0000-0000-0000-000000000002', 'name': 'Yellow Marigold / Banthi (పసుపు బంతిపూలు)', 'local_name': 'Banthipoolu', 'category': 'Loose Flowers (విడి పూలు)', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 20.0, 'purchase_price': 1000.0, 'selling_price': 80.0, 'minimum_stock': 15.0, 'recommended_stock': 100.0, 'reorder_quantity': 30.0, 'current_stock': 65.0},
            {'id': 'p3333333-0000-0000-0000-000000000003', 'name': 'Red Dutch Roses (ఎరుపు గులాబీలు)', 'local_name': 'Gulabi Poolu', 'category': 'Loose Flowers (విడి పూలు)', 'base_unit': 'bundle', 'purchase_unit': 'bundle', 'selling_unit': 'stem', 'conversion_factor': 20.0, 'purchase_price': 180.0, 'selling_price': 15.0, 'minimum_stock': 2.0, 'recommended_stock': 15.0, 'reorder_quantity': 5.0, 'current_stock': 8.0},
            {'id': 'p3333333-0000-0000-0000-000000000004', 'name': 'Chrysanthemum / Chamanthi (చామంతిపూలు)', 'local_name': 'Chamanthi', 'category': 'Loose Flowers (విడి పూలు)', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 10.0, 'purchase_price': 1200.0, 'selling_price': 180.0, 'minimum_stock': 8.0, 'recommended_stock': 50.0, 'reorder_quantity': 15.0, 'current_stock': 35.0},
            {'id': 'p3333333-0000-0000-0000-000000000005', 'name': 'Pink Lotus / Kamalam (తామరపూలు)', 'local_name': 'Kamalam', 'category': 'Pooja & Temple Offerings', 'base_unit': 'piece', 'purchase_unit': 'bundle', 'selling_unit': 'piece', 'conversion_factor': 25.0, 'purchase_price': 375.0, 'selling_price': 25.0, 'minimum_stock': 10.0, 'recommended_stock': 100.0, 'reorder_quantity': 30.0, 'current_stock': 60.0},
            {'id': 'p3333333-0000-0000-0000-000000000006', 'name': 'Wedding Rose & Jasmine Garlands (కళ్యాణ దండలు)', 'local_name': 'Kalyana Dandalu', 'category': 'Bridal & Special Decor (కళ్యాణ పూలు)', 'base_unit': 'set', 'purchase_unit': 'set', 'selling_unit': 'set', 'conversion_factor': 1.0, 'purchase_price': 2200.0, 'selling_price': 3500.0, 'minimum_stock': 1.0, 'recommended_stock': 6.0, 'reorder_quantity': 2.0, 'current_stock': 4.0}
        ]
        for p in flower_catalog:
            stock = p.pop('current_stock')
            p['shop_id'] = DEMO_FLOWER_SHOP_ID
            p['is_active'] = True
            p['supplier_id'] = flower_supps[0]['id']
            p['created_at'] = now
            p['updated_at'] = now
            self.store['products'].append(p)
            self.store['inventory'].append({
                'id': str(uuid.uuid4()), 'shop_id': DEMO_FLOWER_SHOP_ID, 'product_id': p['id'],
                'current_stock': stock, 'stock_unit': p['base_unit'], 'last_stock_in': now, 'last_stock_out': now,
                'created_at': now, 'updated_at': now
            })

        # Active Flower Udhar for Ravi Wedding Decorators
        fb_id = str(uuid.uuid4())
        self.store['borrowings'].append({
            'id': fb_id, 'shop_id': DEMO_FLOWER_SHOP_ID, 'customer_id': flower_custs[0]['id'],
            'customer_name': flower_custs[0]['name'], 'status': 'ACTIVE', 'total_value': 8500.0,
            'paid_amount': 0.0, 'remaining_balance': 8500.0, 'notes': 'Mandapam flower garland booking advance',
            'created_by': DEMO_FLOWER_USER_ID, 'created_at': now, 'updated_at': now
        })
