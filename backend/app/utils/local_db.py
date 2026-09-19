"""Vyapari Voice — Embedded Local / Fallback Database Client.
Provides 100% compatibility with Supabase's Python query interface (.table().select().eq().execute()).
Pre-seeded with realistic Indian Kirana store data for immediate testing and offline reliability.
"""
import uuid
import re
from datetime import datetime, timezone

DEMO_USER_ID = "11111111-1111-1111-1111-111111111111"
DEMO_AUTH_ID = "demo-auth-id"
DEMO_SHOP_ID = "22222222-2222-2222-2222-222222222222"

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

    def insert(self, data):
        self.pending_op = ('insert', data)
        return self

    def update(self, data):
        self.pending_op = ('update', data)
        return self

    def delete(self):
        self.pending_op = ('delete', None)
        return self

    def _matches(self, row):
        for f in self.filters:
            op = f[0]
            field = f[1]
            val = f[2]
            row_val = row.get(field)
            if op == 'eq' and row_val != val:
                return False
            elif op == 'neq' and row_val == val:
                return False
            elif op == 'ilike':
                if val not in str(row_val or "").lower():
                    return False
            elif op == 'in' and row_val not in val:
                return False
            elif op == 'gte' and not (row_val is not None and row_val >= val):
                return False
            elif op == 'lte' and not (row_val is not None and row_val <= val):
                return False
        return True

    def execute(self):
        rows = self.store.get(self.table_name, [])

        if self.pending_op:
            op_type, op_data = self.pending_op
            now = datetime.now(timezone.utc).isoformat()

            if op_type == 'insert':
                items = op_data if isinstance(op_data, list) else [op_data]
                inserted = []
                for item in items:
                    new_item = dict(item)
                    if 'id' not in new_item:
                        new_item['id'] = str(uuid.uuid4())
                    if 'created_at' not in new_item:
                        new_item['created_at'] = now
                    if 'updated_at' not in new_item:
                        new_item['updated_at'] = now
                    rows.append(new_item)
                    inserted.append(new_item)
                return QueryResult(inserted if isinstance(op_data, list) else [inserted[0]])

            elif op_type == 'update':
                updated = []
                for row in rows:
                    if self._matches(row):
                        for k, v in op_data.items():
                            row[k] = v
                        row['updated_at'] = now
                        updated.append(dict(row))
                return QueryResult(updated)

            elif op_type == 'delete':
                remaining = []
                deleted = []
                for row in rows:
                    if self._matches(row):
                        deleted.append(row)
                    else:
                        remaining.append(row)
                self.store[self.table_name] = remaining
                return QueryResult(deleted)

        # Query / Select
        filtered = [dict(r) for r in rows if self._matches(r)]

        # Sorting
        if self.sort_field:
            filtered.sort(
                key=lambda x: (x.get(self.sort_field) is None, x.get(self.sort_field)),
                reverse=self.sort_desc
            )

        # Limit
        if self.limit_val is not None:
            filtered = filtered[:self.limit_val]

        # Column projection
        if self.selected_cols:
            projected = []
            for r in filtered:
                projected.append({k: r.get(k) for k in self.selected_cols if k in r})
            filtered = projected

        if self.is_single:
            return QueryResult(filtered[0] if filtered else None)

        return QueryResult(filtered)


class MockAuthUser:
    def __init__(self, user_id=DEMO_USER_ID, email="demo@vyapari.com"):
        self.id = user_id
        self.email = email


class MockAuthResponse:
    def __init__(self, user):
        self.user = user


class MockAuth:
    def __init__(self, store):
        self.store = store

    def get_user(self, token):
        # Any valid bearer token or demo token returns the demo/active user
        users = self.store.get('users', [])
        user = users[0] if users else None
        user_id = user['auth_id'] if user else DEMO_AUTH_ID
        email = user['email'] if user else "demo@vyapari.com"
        return MockAuthResponse(MockAuthUser(user_id=user_id, email=email))

    def sign_in_with_password(self, credentials):
        users = self.store.get('users', [])
        email = credentials.get('email', '')
        for u in users:
            if u.get('email', '').lower() == email.lower():
                user_obj = MockAuthUser(user_id=u['auth_id'], email=u['email'])
                res = MockAuthResponse(user_obj)
                res.session = type('Session', (), {
                    'access_token': 'demo-token-vyapari',
                    'refresh_token': 'demo-refresh-token'
                })()
                return res
        # Default demo fallback
        user_obj = MockAuthUser(user_id=DEMO_AUTH_ID, email=email or "demo@vyapari.com")
        res = MockAuthResponse(user_obj)
        res.session = type('Session', (), {
            'access_token': 'demo-token-vyapari',
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

        # User
        self.store['users'] = [{
            'id': DEMO_USER_ID,
            'auth_id': DEMO_AUTH_ID,
            'email': 'srinivas@vyapari.com',
            'full_name': 'Srinivas Kumar',
            'phone': '+91 9876543210',
            'language': 'te',
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }]

        # Shop
        self.store['shops'] = [{
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
        }]

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
