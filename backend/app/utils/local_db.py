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

DEMO_CLOTH_USER_ID = "55555555-5555-5555-5555-555555555555"
DEMO_CLOTH_AUTH_ID = "55555555-5555-5555-5555-555555555555"
DEMO_CLOTH_SHOP_ID = "55555555-5555-5555-5555-555555555555"

DEMO_PHARMA_USER_ID = "66666666-6666-6666-6666-666666666666"
DEMO_PHARMA_AUTH_ID = "66666666-6666-6666-6666-666666666666"
DEMO_PHARMA_SHOP_ID = "66666666-6666-6666-6666-666666666666"

DEMO_BAKERY_USER_ID = "77777777-7777-7777-7777-777777777777"
DEMO_BAKERY_AUTH_ID = "77777777-7777-7777-7777-777777777777"
DEMO_BAKERY_SHOP_ID = "77777777-7777-7777-7777-777777777777"

DEMO_REST_USER_ID = "88888888-8888-8888-8888-888888888888"
DEMO_REST_AUTH_ID = "88888888-8888-8888-8888-888888888888"
DEMO_REST_SHOP_ID = "88888888-8888-8888-8888-888888888888"

DEMO_TEA_USER_ID = "99999999-9999-9999-9999-999999999999"
DEMO_TEA_AUTH_ID = "99999999-9999-9999-9999-999999999999"
DEMO_TEA_SHOP_ID = "99999999-9999-9999-9999-999999999999"

DEMO_HARDWARE_USER_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
DEMO_HARDWARE_AUTH_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
DEMO_HARDWARE_SHOP_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

DEMO_AUTO_USER_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
DEMO_AUTO_AUTH_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
DEMO_AUTO_SHOP_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"

DEMO_VEG_USER_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"
DEMO_VEG_AUTH_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"
DEMO_VEG_SHOP_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"

DEMO_ELEC_USER_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"
DEMO_ELEC_AUTH_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"
DEMO_ELEC_SHOP_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"

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


LOCAL_TOKEN_TO_EMAIL = {
    'demo-token-kirana': 'srinivas@dukaansetu.com',
    'demo-token-dukaansetu': 'srinivas@dukaansetu.com',
    'demo-token-vyapari': 'srinivas@dukaansetu.com',
    'demo-token': 'srinivas@dukaansetu.com',
    'demo-token-jewellery': 'jewellery@dukaansetu.com',
    'demo-token-gold': 'jewellery@dukaansetu.com',
    'demo-token-flowers': 'flowers@dukaansetu.com',
    'demo-token-pushpa': 'flowers@dukaansetu.com',
    'demo-token-clothing': 'clothing@dukaansetu.com',
    'demo-token-pharmacy': 'pharmacy@dukaansetu.com',
    'demo-token-bakery': 'bakery@dukaansetu.com',
    'demo-token-restaurant': 'restaurant@dukaansetu.com',
    'demo-token-teacoffee': 'teacoffee@dukaansetu.com',
    'demo-token-hardware': 'hardware@dukaansetu.com',
    'demo-token-autoparts': 'autoparts@dukaansetu.com',
    'demo-token-vegetables': 'vegetables@dukaansetu.com',
    'demo-token-electronics': 'electronics@dukaansetu.com',
}

LOCAL_EMAIL_MAP = {
    'jewel': ('demo-token-jewellery', DEMO_JEWEL_AUTH_ID, 'jewellery@dukaansetu.com'),
    'swarna': ('demo-token-jewellery', DEMO_JEWEL_AUTH_ID, 'jewellery@dukaansetu.com'),
    'flower': ('demo-token-flowers', DEMO_FLOWER_AUTH_ID, 'flowers@dukaansetu.com'),
    'pushpa': ('demo-token-flowers', DEMO_FLOWER_AUTH_ID, 'flowers@dukaansetu.com'),
    'clothing': ('demo-token-clothing', DEMO_CLOTH_AUTH_ID, 'clothing@dukaansetu.com'),
    'cloth': ('demo-token-clothing', DEMO_CLOTH_AUTH_ID, 'clothing@dukaansetu.com'),
    'pharmacy': ('demo-token-pharmacy', DEMO_PHARMA_AUTH_ID, 'pharmacy@dukaansetu.com'),
    'medical': ('demo-token-pharmacy', DEMO_PHARMA_AUTH_ID, 'pharmacy@dukaansetu.com'),
    'bakery': ('demo-token-bakery', DEMO_BAKERY_AUTH_ID, 'bakery@dukaansetu.com'),
    'sweet': ('demo-token-bakery', DEMO_BAKERY_AUTH_ID, 'bakery@dukaansetu.com'),
    'restaurant': ('demo-token-restaurant', DEMO_REST_AUTH_ID, 'restaurant@dukaansetu.com'),
    'tiffin': ('demo-token-restaurant', DEMO_REST_AUTH_ID, 'restaurant@dukaansetu.com'),
    'teacoffee': ('demo-token-teacoffee', DEMO_TEA_AUTH_ID, 'teacoffee@dukaansetu.com'),
    'tea': ('demo-token-teacoffee', DEMO_TEA_AUTH_ID, 'teacoffee@dukaansetu.com'),
    'chai': ('demo-token-teacoffee', DEMO_TEA_AUTH_ID, 'teacoffee@dukaansetu.com'),
    'hardware': ('demo-token-hardware', DEMO_HARDWARE_AUTH_ID, 'hardware@dukaansetu.com'),
    'autoparts': ('demo-token-autoparts', DEMO_AUTO_AUTH_ID, 'autoparts@dukaansetu.com'),
    'spares': ('demo-token-autoparts', DEMO_AUTO_AUTH_ID, 'autoparts@dukaansetu.com'),
    'auto': ('demo-token-autoparts', DEMO_AUTO_AUTH_ID, 'autoparts@dukaansetu.com'),
    'vegetables': ('demo-token-vegetables', DEMO_VEG_AUTH_ID, 'vegetables@dukaansetu.com'),
    'fruits': ('demo-token-vegetables', DEMO_VEG_AUTH_ID, 'vegetables@dukaansetu.com'),
    'sabzi': ('demo-token-vegetables', DEMO_VEG_AUTH_ID, 'vegetables@dukaansetu.com'),
    'electronics': ('demo-token-electronics', DEMO_ELEC_AUTH_ID, 'electronics@dukaansetu.com'),
    'mobile': ('demo-token-electronics', DEMO_ELEC_AUTH_ID, 'electronics@dukaansetu.com'),
    'kirana': ('demo-token-kirana', DEMO_AUTH_ID, 'srinivas@dukaansetu.com'),
    'srinivas': ('demo-token-kirana', DEMO_AUTH_ID, 'srinivas@dukaansetu.com'),
}


class MockAuth:
    def __init__(self, store):
        self.store = store

    def get_user(self, token):
        users = self.store.get('users', [])
        target_email = LOCAL_TOKEN_TO_EMAIL.get(token, "srinivas@dukaansetu.com")
        user = next((u for u in users if u.get('email') == target_email), None) or (users[0] if users else None)
        user_id = user['auth_id'] if user else DEMO_AUTH_ID
        email = user['email'] if user else target_email
        return MockAuthResponse(MockAuthUser(user_id=user_id, email=email))

    def sign_in_with_password(self, credentials):
        users = self.store.get('users', [])
        email = credentials.get('email', '').strip().lower()

        token = 'demo-token-kirana'
        auth_id = DEMO_AUTH_ID
        for kw, (t, aid, _) in LOCAL_EMAIL_MAP.items():
            if kw in email:
                token = t
                auth_id = aid
                break

        for u in users:
            if u.get('email', '').lower() == email:
                user_obj = MockAuthUser(user_id=u['auth_id'], email=u['email'])
                res = MockAuthResponse(user_obj)
                res.session = type('Session', (), {
                    'access_token': token,
                    'refresh_token': 'demo-refresh-token'
                })()
                return res

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
            },
            {
                'id': DEMO_CLOTH_USER_ID,
                'auth_id': DEMO_CLOTH_AUTH_ID,
                'email': 'clothing@dukaansetu.com',
                'full_name': 'Venkata Ramana (Textiles)',
                'phone': '+91 9848055555',
                'language': 'te',
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_PHARMA_USER_ID,
                'auth_id': DEMO_PHARMA_AUTH_ID,
                'email': 'pharmacy@dukaansetu.com',
                'full_name': 'Dr. Suresh Reddy (Pharmacist)',
                'phone': '+91 9848066666',
                'language': 'te',
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_BAKERY_USER_ID,
                'auth_id': DEMO_BAKERY_AUTH_ID,
                'email': 'bakery@dukaansetu.com',
                'full_name': 'Raju Mithaiwala (Baker & Confectioner)',
                'phone': '+91 9848077777',
                'language': 'te',
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_REST_USER_ID,
                'auth_id': DEMO_REST_AUTH_ID,
                'email': 'restaurant@dukaansetu.com',
                'full_name': 'Lakshmi Devi (Restaurateur)',
                'phone': '+91 9848088888',
                'language': 'te',
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_TEA_USER_ID,
                'auth_id': DEMO_TEA_AUTH_ID,
                'email': 'teacoffee@dukaansetu.com',
                'full_name': 'Ramu Chaiwala (Cafe Owner)',
                'phone': '+91 9848099999',
                'language': 'te',
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_HARDWARE_USER_ID,
                'auth_id': DEMO_HARDWARE_AUTH_ID,
                'email': 'hardware@dukaansetu.com',
                'full_name': 'Mahesh Kumar (Hardware Merchant)',
                'phone': '+91 98480aaaaa',
                'language': 'te',
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_AUTO_USER_ID,
                'auth_id': DEMO_AUTO_AUTH_ID,
                'email': 'autoparts@dukaansetu.com',
                'full_name': 'Narasimha Rao (Spares Specialist)',
                'phone': '+91 98480bbbbb',
                'language': 'te',
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_VEG_USER_ID,
                'auth_id': DEMO_VEG_AUTH_ID,
                'email': 'vegetables@dukaansetu.com',
                'full_name': 'Yellamma (Produce Merchant)',
                'phone': '+91 98480ccccc',
                'language': 'te',
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_ELEC_USER_ID,
                'auth_id': DEMO_ELEC_AUTH_ID,
                'email': 'electronics@dukaansetu.com',
                'full_name': 'Arun Kumar (Electronics & Mobile)',
                'phone': '+91 98480ddddd',
                'language': 'te',
                'is_active': True,
                'created_at': now,
                'updated_at': now
            }
        ]

        # Shops (12 Verticals)
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
            },
            {
                'id': DEMO_CLOTH_SHOP_ID,
                'owner_id': DEMO_CLOTH_USER_ID,
                'name': 'Sri Raghavendra Cloth Emporium',
                'type': 'clothing',
                'phone': '+91 9848055555',
                'address': 'Main Cloth Bazaar, Hanamkonda',
                'city': 'Warangal',
                'state': 'Telangana',
                'gst_number': '36CCCP5555E1Z1',
                'currency': 'INR',
                'tax_rate': 5,
                'settings': {},
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_PHARMA_SHOP_ID,
                'owner_id': DEMO_PHARMA_USER_ID,
                'name': 'Sri Durga Medical & General Stores',
                'type': 'pharmacy',
                'phone': '+91 9848066666',
                'address': 'Hospital Road, Subedari',
                'city': 'Warangal',
                'state': 'Telangana',
                'gst_number': '36DDDP6666F1Z2',
                'currency': 'INR',
                'tax_rate': 12,
                'settings': {},
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_BAKERY_SHOP_ID,
                'owner_id': DEMO_BAKERY_USER_ID,
                'name': 'Sri Sai Sweet Home & Bakery',
                'type': 'bakery',
                'phone': '+91 9848077777',
                'address': 'Nakkalagutta Junction',
                'city': 'Warangal',
                'state': 'Telangana',
                'gst_number': '36EEEP7777G1Z3',
                'currency': 'INR',
                'tax_rate': 5,
                'settings': {},
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_REST_SHOP_ID,
                'owner_id': DEMO_REST_USER_ID,
                'name': 'Sri Annapurna Tiffin & Meals',
                'type': 'restaurant',
                'phone': '+91 9848088888',
                'address': 'Bus Stand Road',
                'city': 'Warangal',
                'state': 'Telangana',
                'gst_number': '36FFFP8888H1Z4',
                'currency': 'INR',
                'tax_rate': 5,
                'settings': {},
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_TEA_SHOP_ID,
                'owner_id': DEMO_TEA_USER_ID,
                'name': 'Sri Balaji Irani Tea & Coffee Point',
                'type': 'teacoffee',
                'phone': '+91 9848099999',
                'address': 'Station Road',
                'city': 'Warangal',
                'state': 'Telangana',
                'gst_number': '36GGGP9999I1Z5',
                'currency': 'INR',
                'tax_rate': 0,
                'settings': {},
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_HARDWARE_SHOP_ID,
                'owner_id': DEMO_HARDWARE_USER_ID,
                'name': 'Sri Hanuman Hardware & Electricals',
                'type': 'hardware',
                'phone': '+91 98480aaaaa',
                'address': 'Industrial Estate',
                'city': 'Warangal',
                'state': 'Telangana',
                'gst_number': '36HHHP0000J1Z6',
                'currency': 'INR',
                'tax_rate': 18,
                'settings': {},
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_AUTO_SHOP_ID,
                'owner_id': DEMO_AUTO_USER_ID,
                'name': 'Sri Ganesh Auto Spares & Accessories',
                'type': 'autoparts',
                'phone': '+91 98480bbbbb',
                'address': 'Auto Nagar',
                'city': 'Warangal',
                'state': 'Telangana',
                'gst_number': '36IIIP1111K1Z7',
                'currency': 'INR',
                'tax_rate': 18,
                'settings': {},
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_VEG_SHOP_ID,
                'owner_id': DEMO_VEG_USER_ID,
                'name': 'Sri Lakshmi Fresh Veg & Fruits',
                'type': 'vegetables',
                'phone': '+91 98480ccccc',
                'address': 'Rythu Bazar',
                'city': 'Warangal',
                'state': 'Telangana',
                'gst_number': '36JJJP2222L1Z8',
                'currency': 'INR',
                'tax_rate': 0,
                'settings': {},
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': DEMO_ELEC_SHOP_ID,
                'owner_id': DEMO_ELEC_USER_ID,
                'name': 'Sri Tech Zone Mobiles & Electronics',
                'type': 'electronics',
                'phone': '+91 98480ddddd',
                'address': 'Complex Road',
                'city': 'Warangal',
                'state': 'Telangana',
                'gst_number': '36KKKP3333M1Z9',
                'currency': 'INR',
                'tax_rate': 18,
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

        # ============================================================
        # HELPER TO SEED REMAINING 9 SHOP VERTICALS
        # ============================================================
        additional_shops = [
            {
                'shop_id': DEMO_CLOTH_SHOP_ID,
                'user_id': DEMO_CLOTH_USER_ID,
                'categories': ["Men's Wear", "Women's Sarees & Dresses", "Kids Wear", "Handloom & Silk", "Fabrics & Tailoring"],
                'suppliers': [
                    {'name': 'Surat Silk Mills Wholesalers', 'phone': '+91 9848055001', 'email': 'surat@silkmills.com', 'address': 'Textile Hub, Surat'},
                    {'name': 'Raymond & Arvind Fabrics Depot', 'phone': '+91 9848055002', 'email': 'raymond@fabrics.com', 'address': 'Secunderabad'}
                ],
                'customers': [
                    {'name': 'Ravi Teja (Wedding Shopping Udhar)', 'phone': '+91 9848055111', 'credit': 14500.0, 'notes': 'Pattu sarees and suit fabrics balance'},
                    {'name': 'Smt. Sujatha (Chit Saree Account)', 'phone': '+91 9848055222', 'credit': 4200.0, 'notes': 'Monthly saree installment'}
                ],
                'products': [
                    {'id': 'p4444444-0000-0000-0000-000000000001', 'name': 'Kanchi Pattu Saree (కంచి పట్టు చీర)', 'local_name': 'Pattu Cheera', 'category': "Handloom & Silk", 'base_unit': 'piece', 'purchase_unit': 'piece', 'selling_unit': 'piece', 'conversion_factor': 1.0, 'purchase_price': 4800.0, 'selling_price': 6500.0, 'minimum_stock': 5.0, 'recommended_stock': 40.0, 'reorder_quantity': 15.0, 'current_stock': 28.0},
                    {'id': 'p4444444-0000-0000-0000-000000000002', 'name': "Cotton Men's Formal Shirt (కాటన్ షర్టు)", 'local_name': 'Cotton Shirt', 'category': "Men's Wear", 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 10.0, 'purchase_price': 5200.0, 'selling_price': 750.0, 'minimum_stock': 20.0, 'recommended_stock': 120.0, 'reorder_quantity': 40.0, 'current_stock': 85.0},
                    {'id': 'p4444444-0000-0000-0000-000000000003', 'name': "Levi's Denim Jeans 32/34 (జీన్స్ ప్యాంట్)", 'local_name': 'Jeans Pant', 'category': "Men's Wear", 'base_unit': 'piece', 'purchase_unit': 'piece', 'selling_unit': 'piece', 'conversion_factor': 1.0, 'purchase_price': 1050.0, 'selling_price': 1450.0, 'minimum_stock': 10.0, 'recommended_stock': 60.0, 'reorder_quantity': 20.0, 'current_stock': 45.0},
                    {'id': 'p4444444-0000-0000-0000-000000000004', 'name': "Women's Cotton Kurti / Dupatta Set (కుర్తీ సెట్)", 'local_name': 'Kurti Set', 'category': "Women's Sarees & Dresses", 'base_unit': 'set', 'purchase_unit': 'set', 'selling_unit': 'set', 'conversion_factor': 1.0, 'purchase_price': 620.0, 'selling_price': 890.0, 'minimum_stock': 15.0, 'recommended_stock': 80.0, 'reorder_quantity': 25.0, 'current_stock': 60.0},
                    {'id': 'p4444444-0000-0000-0000-000000000005', 'name': 'Pure Cotton Dhoti & Kanduva (ధోవతి & కండువా)', 'local_name': 'Dhovati Kanduva', 'category': "Men's Wear", 'base_unit': 'set', 'purchase_unit': 'set', 'selling_unit': 'set', 'conversion_factor': 1.0, 'purchase_price': 310.0, 'selling_price': 450.0, 'minimum_stock': 10.0, 'recommended_stock': 70.0, 'reorder_quantity': 20.0, 'current_stock': 50.0},
                    {'id': 'p4444444-0000-0000-0000-000000000006', 'name': 'School Uniform Fabric Set (స్కూల్ యూనిఫామ్)', 'local_name': 'Uniform Fabric', 'category': "Fabrics & Tailoring", 'base_unit': 'meter', 'purchase_unit': 'roll', 'selling_unit': 'meter', 'conversion_factor': 50.0, 'purchase_price': 11000.0, 'selling_price': 320.0, 'minimum_stock': 30.0, 'recommended_stock': 250.0, 'reorder_quantity': 100.0, 'current_stock': 150.0},
                ]
            },
            {
                'shop_id': DEMO_PHARMA_SHOP_ID,
                'user_id': DEMO_PHARMA_USER_ID,
                'categories': ['Tablets & Capsules', 'Syrups & Suspensions', 'Injections & Insulins', 'First Aid & Ointments', 'Health & Wellness Devices'],
                'suppliers': [
                    {'name': 'Apollo Pharma Wholesale Dist', 'phone': '+91 9848066001', 'email': 'orders@apollodist.com', 'address': 'Pharma City, Hyderabad'},
                    {'name': "Reddy's Laboratories Stockist", 'phone': '+91 9848066002', 'email': 'stockist@drreddys.com', 'address': 'Warangal'}
                ],
                'customers': [
                    {'name': 'Krishna Murthy (Senior Citizen BP/Sugar Udhar)', 'phone': '+91 9848066111', 'credit': 3250.0, 'notes': 'Monthly regular prescription tab'},
                    {'name': 'Madhavi Latha (Pediatric Tab)', 'phone': '+91 9848066222', 'credit': 850.0, 'notes': 'Baby syrup and vitamins'}
                ],
                'products': [
                    {'id': 'p5555555-0000-0000-0000-000000000001', 'name': 'Dolo 650mg Tablets (డోలో 650)', 'local_name': 'Dolo 650', 'category': 'Tablets & Capsules', 'base_unit': 'strip', 'purchase_unit': 'box', 'selling_unit': 'strip', 'conversion_factor': 15.0, 'purchase_price': 360.0, 'selling_price': 32.0, 'minimum_stock': 30.0, 'recommended_stock': 200.0, 'reorder_quantity': 60.0, 'current_stock': 150.0},
                    {'id': 'p5555555-0000-0000-0000-000000000002', 'name': 'Crocin Advance 500mg (క్రోసిన్)', 'local_name': 'Crocin', 'category': 'Tablets & Capsules', 'base_unit': 'strip', 'purchase_unit': 'box', 'selling_unit': 'strip', 'conversion_factor': 20.0, 'purchase_price': 380.0, 'selling_price': 25.0, 'minimum_stock': 25.0, 'recommended_stock': 150.0, 'reorder_quantity': 50.0, 'current_stock': 120.0},
                    {'id': 'p5555555-0000-0000-0000-000000000003', 'name': 'Benadryl Cough Syrup 100ml (దగ్గు మందు)', 'local_name': 'Daggu Mandhu', 'category': 'Syrups & Suspensions', 'base_unit': 'bottle', 'purchase_unit': 'box', 'selling_unit': 'bottle', 'conversion_factor': 12.0, 'purchase_price': 1050.0, 'selling_price': 115.0, 'minimum_stock': 10.0, 'recommended_stock': 60.0, 'reorder_quantity': 24.0, 'current_stock': 40.0},
                    {'id': 'p5555555-0000-0000-0000-000000000004', 'name': 'Human Mixtard 30/70 Insulin (ఇన్సులిన్)', 'local_name': 'Insulin Vial', 'category': 'Injections & Insulins', 'base_unit': 'vial', 'purchase_unit': 'pack', 'selling_unit': 'vial', 'conversion_factor': 5.0, 'purchase_price': 780.0, 'selling_price': 185.0, 'minimum_stock': 5.0, 'recommended_stock': 30.0, 'reorder_quantity': 10.0, 'current_stock': 18.0},
                    {'id': 'p5555555-0000-0000-0000-000000000005', 'name': 'ORS Electral Powder 21.8g (ఓఆర్ఎస్)', 'local_name': 'ORS Sachet', 'category': 'First Aid & Ointments', 'base_unit': 'sachet', 'purchase_unit': 'box', 'selling_unit': 'sachet', 'conversion_factor': 25.0, 'purchase_price': 420.0, 'selling_price': 22.0, 'minimum_stock': 40.0, 'recommended_stock': 300.0, 'reorder_quantity': 100.0, 'current_stock': 200.0},
                    {'id': 'p5555555-0000-0000-0000-000000000006', 'name': 'Digital BP Monitor (బీపీ మిషన్)', 'local_name': 'BP Monitor', 'category': 'Health & Wellness Devices', 'base_unit': 'piece', 'purchase_unit': 'piece', 'selling_unit': 'piece', 'conversion_factor': 1.0, 'purchase_price': 1150.0, 'selling_price': 1450.0, 'minimum_stock': 2.0, 'recommended_stock': 15.0, 'reorder_quantity': 5.0, 'current_stock': 8.0},
                ]
            },
            {
                'shop_id': DEMO_BAKERY_SHOP_ID,
                'user_id': DEMO_BAKERY_USER_ID,
                'categories': ['Fresh Cakes & Pastries', 'Traditional Sweets', 'Savory Puffs & Samosas', 'Daily Breads & Buns', 'Cookies & Biscuits'],
                'suppliers': [
                    {'name': 'Vijaya Dairy Milk Supply', 'phone': '+91 9848077001', 'email': 'vijaya@dairy.gov.in', 'address': 'Dairy Farm, Warangal'},
                    {'name': 'Royal Bakers Flour Wholesale', 'phone': '+91 9848077002', 'email': 'royalflour@bakers.com', 'address': 'Mill Area, Hyderabad'}
                ],
                'customers': [
                    {'name': 'Modern High School (Party Order Udhar)', 'phone': '+91 9848077111', 'credit': 5200.0, 'notes': 'Annual day samosa & cake boxes'},
                    {'name': 'Srinivasa Caterers (Sweet Boxes)', 'phone': '+91 9848077222', 'credit': 8400.0, 'notes': 'Mysore pak and kaju katli boxes for wedding'}
                ],
                'products': [
                    {'id': 'p6666666-0000-0000-0000-000000000001', 'name': 'Black Forest Cake 1kg (బ్లాక్ ఫారెస్ట్ కేక్)', 'local_name': 'Black Forest Cake', 'category': 'Fresh Cakes & Pastries', 'base_unit': 'kg', 'purchase_unit': 'kg', 'selling_unit': 'kg', 'conversion_factor': 1.0, 'purchase_price': 380.0, 'selling_price': 550.0, 'minimum_stock': 3.0, 'recommended_stock': 20.0, 'reorder_quantity': 8.0, 'current_stock': 12.0},
                    {'id': 'p6666666-0000-0000-0000-000000000002', 'name': 'Fresh Milk Bread 400g (పాల బ్రెడ్)', 'local_name': 'Milk Bread', 'category': 'Daily Breads & Buns', 'base_unit': 'packet', 'purchase_unit': 'crate', 'selling_unit': 'packet', 'conversion_factor': 20.0, 'purchase_price': 600.0, 'selling_price': 40.0, 'minimum_stock': 15.0, 'recommended_stock': 100.0, 'reorder_quantity': 40.0, 'current_stock': 60.0},
                    {'id': 'p6666666-0000-0000-0000-000000000003', 'name': 'Ghee Mysore Pak (నెయ్యి మైసూర్ పాక్)', 'local_name': 'Mysore Pak', 'category': 'Traditional Sweets', 'base_unit': 'kg', 'purchase_unit': 'tray', 'selling_unit': 'kg', 'conversion_factor': 5.0, 'purchase_price': 1750.0, 'selling_price': 480.0, 'minimum_stock': 5.0, 'recommended_stock': 40.0, 'reorder_quantity': 15.0, 'current_stock': 25.0},
                    {'id': 'p6666666-0000-0000-0000-000000000004', 'name': 'Kaju Katli (కాజు కట్లి)', 'local_name': 'Kaju Katli', 'category': 'Traditional Sweets', 'base_unit': 'kg', 'purchase_unit': 'tray', 'selling_unit': 'kg', 'conversion_factor': 5.0, 'purchase_price': 3200.0, 'selling_price': 850.0, 'minimum_stock': 4.0, 'recommended_stock': 25.0, 'reorder_quantity': 10.0, 'current_stock': 15.0},
                    {'id': 'p6666666-0000-0000-0000-000000000005', 'name': 'Egg & Veg Puff (పఫ్స్)', 'local_name': 'Puff', 'category': 'Savory Puffs & Samosas', 'base_unit': 'piece', 'purchase_unit': 'tray', 'selling_unit': 'piece', 'conversion_factor': 30.0, 'purchase_price': 480.0, 'selling_price': 25.0, 'minimum_stock': 20.0, 'recommended_stock': 150.0, 'reorder_quantity': 60.0, 'current_stock': 90.0},
                    {'id': 'p6666666-0000-0000-0000-000000000006', 'name': 'Osmania Tea Biscuits (ఉస్మానియా బిస్కెట్లు)', 'local_name': 'Osmania Biscuits', 'category': 'Cookies & Biscuits', 'base_unit': 'box', 'purchase_unit': 'carton', 'selling_unit': 'box', 'conversion_factor': 12.0, 'purchase_price': 1080.0, 'selling_price': 120.0, 'minimum_stock': 10.0, 'recommended_stock': 60.0, 'reorder_quantity': 24.0, 'current_stock': 45.0},
                ]
            },
            {
                'shop_id': DEMO_REST_SHOP_ID,
                'user_id': DEMO_REST_USER_ID,
                'categories': ['Breakfast Tiffins', 'Meals & Biryani', 'Kitchen Raw Materials', 'Curries & Starters', 'Beverages'],
                'suppliers': [
                    {'name': 'Rythu Bazar Vegetable Wholesalers', 'phone': '+91 9848088001', 'email': 'rythu@mandi.gov.in', 'address': 'Wholesale Mandi, Warangal'},
                    {'name': 'Modern Poultry & Meat Supply', 'phone': '+91 9848088002', 'email': 'poultry@meatdist.com', 'address': 'Subedari'}
                ],
                'customers': [
                    {'name': 'Subba Rao (Monthly Mess Account)', 'phone': '+91 9848088111', 'credit': 3200.0, 'notes': 'Monthly lunch thali subscription'},
                    {'name': 'Govt Polytechnic Staff Union', 'phone': '+91 9848088222', 'credit': 4600.0, 'notes': 'Tiffins and tea tab'}
                ],
                'products': [
                    {'id': 'p7777777-0000-0000-0000-000000000001', 'name': 'Special Chicken Dum Biryani (చికెన్ దమ్ బిర్యానీ)', 'local_name': 'Chicken Biryani', 'category': 'Meals & Biryani', 'base_unit': 'plate', 'purchase_unit': 'plate', 'selling_unit': 'plate', 'conversion_factor': 1.0, 'purchase_price': 130.0, 'selling_price': 220.0, 'minimum_stock': 10.0, 'recommended_stock': 80.0, 'reorder_quantity': 25.0, 'current_stock': 50.0},
                    {'id': 'p7777777-0000-0000-0000-000000000002', 'name': 'Ghee Masala Dosa (నెయ్యి మసాలా దోశ)', 'local_name': 'Masala Dosa', 'category': 'Breakfast Tiffins', 'base_unit': 'plate', 'purchase_unit': 'plate', 'selling_unit': 'plate', 'conversion_factor': 1.0, 'purchase_price': 30.0, 'selling_price': 60.0, 'minimum_stock': 20.0, 'recommended_stock': 150.0, 'reorder_quantity': 50.0, 'current_stock': 120.0},
                    {'id': 'p7777777-0000-0000-0000-000000000003', 'name': 'Steamed Idli Sambar (ఇడ్లీ సాంబార్)', 'local_name': 'Idli Sambar', 'category': 'Breakfast Tiffins', 'base_unit': 'plate', 'purchase_unit': 'plate', 'selling_unit': 'plate', 'conversion_factor': 1.0, 'purchase_price': 18.0, 'selling_price': 40.0, 'minimum_stock': 25.0, 'recommended_stock': 200.0, 'reorder_quantity': 60.0, 'current_stock': 150.0},
                    {'id': 'p7777777-0000-0000-0000-000000000004', 'name': 'South Indian Thali Meals (పూర్తి భోజనం)', 'local_name': 'Bhojanam', 'category': 'Meals & Biryani', 'base_unit': 'plate', 'purchase_unit': 'plate', 'selling_unit': 'plate', 'conversion_factor': 1.0, 'purchase_price': 65.0, 'selling_price': 110.0, 'minimum_stock': 15.0, 'recommended_stock': 100.0, 'reorder_quantity': 30.0, 'current_stock': 80.0},
                    {'id': 'p7777777-0000-0000-0000-000000000005', 'name': 'Raw Basmati Rice Bulk 25kg (బిర్యానీ బియ్యం)', 'local_name': 'Basmati Rice Bag', 'category': 'Kitchen Raw Materials', 'base_unit': 'bag', 'purchase_unit': 'bag', 'selling_unit': 'bag', 'conversion_factor': 1.0, 'purchase_price': 2100.0, 'selling_price': 2400.0, 'minimum_stock': 3.0, 'recommended_stock': 20.0, 'reorder_quantity': 10.0, 'current_stock': 15.0},
                    {'id': 'p7777777-0000-0000-0000-000000000006', 'name': 'Cooking Sunflower Oil Tin 15L (వంట నూనె)', 'local_name': 'Oil Tin', 'category': 'Kitchen Raw Materials', 'base_unit': 'can', 'purchase_unit': 'can', 'selling_unit': 'can', 'conversion_factor': 1.0, 'purchase_price': 1650.0, 'selling_price': 1850.0, 'minimum_stock': 2.0, 'recommended_stock': 12.0, 'reorder_quantity': 5.0, 'current_stock': 8.0},
                ]
            },
            {
                'shop_id': DEMO_TEA_SHOP_ID,
                'user_id': DEMO_TEA_USER_ID,
                'categories': ['Hot Beverages', 'Tea Stall Snacks', 'Raw Ingredients', 'Bottled Drinks', 'Biscuits & Mints'],
                'suppliers': [
                    {'name': 'Sangam Dairy Whole Buffalo Milk', 'phone': '+91 9848099001', 'email': 'sangam@dairy.com', 'address': 'Milk Chilling Hub, Warangal'},
                    {'name': 'Brooke Bond & Nescafe Depot', 'phone': '+91 9848099002', 'email': 'tea@huldist.com', 'address': 'Hyderabad'}
                ],
                'customers': [
                    {'name': 'Court Auto Drivers Union (Weekly Tea Tab)', 'phone': '+91 9848099111', 'credit': 1850.0, 'notes': 'Daily morning and evening tea tab'},
                    {'name': 'LIC Office Staff (Daily Tea & Samosa)', 'phone': '+91 9848099222', 'credit': 1200.0, 'notes': 'Monthly office refreshment'}
                ],
                'products': [
                    {'id': 'p8888888-0000-0000-0000-000000000001', 'name': 'Special Irani Dum Chai (ఇరానీ దమ్ చాయ్)', 'local_name': 'Irani Chai', 'category': 'Hot Beverages', 'base_unit': 'cup', 'purchase_unit': 'cup', 'selling_unit': 'cup', 'conversion_factor': 1.0, 'purchase_price': 6.0, 'selling_price': 15.0, 'minimum_stock': 50.0, 'recommended_stock': 500.0, 'reorder_quantity': 200.0, 'current_stock': 350.0},
                    {'id': 'p8888888-0000-0000-0000-000000000002', 'name': 'South Indian Filter Coffee (ఫిల్టర్ కాఫీ)', 'local_name': 'Filter Coffee', 'category': 'Hot Beverages', 'base_unit': 'cup', 'purchase_unit': 'cup', 'selling_unit': 'cup', 'conversion_factor': 1.0, 'purchase_price': 9.0, 'selling_price': 20.0, 'minimum_stock': 30.0, 'recommended_stock': 250.0, 'reorder_quantity': 100.0, 'current_stock': 180.0},
                    {'id': 'p8888888-0000-0000-0000-000000000003', 'name': 'Hot Onion Samosa (ఉల్లి సమోసా)', 'local_name': 'Samosa', 'category': 'Tea Stall Snacks', 'base_unit': 'piece', 'purchase_unit': 'piece', 'selling_unit': 'piece', 'conversion_factor': 1.0, 'purchase_price': 4.5, 'selling_price': 10.0, 'minimum_stock': 20.0, 'recommended_stock': 180.0, 'reorder_quantity': 60.0, 'current_stock': 120.0},
                    {'id': 'p8888888-0000-0000-0000-000000000004', 'name': 'Mirchi Bajji (మిర్చి బజ్జీ)', 'local_name': 'Mirchi Bajji', 'category': 'Tea Stall Snacks', 'base_unit': 'plate', 'purchase_unit': 'plate', 'selling_unit': 'plate', 'conversion_factor': 1.0, 'purchase_price': 14.0, 'selling_price': 30.0, 'minimum_stock': 15.0, 'recommended_stock': 100.0, 'reorder_quantity': 35.0, 'current_stock': 80.0},
                    {'id': 'p8888888-0000-0000-0000-000000000005', 'name': 'Buffalo Milk 1 Litre (గేదె పాలు)', 'local_name': 'Paalu', 'category': 'Raw Ingredients', 'base_unit': 'litre', 'purchase_unit': 'can', 'selling_unit': 'litre', 'conversion_factor': 20.0, 'purchase_price': 1200.0, 'selling_price': 70.0, 'minimum_stock': 10.0, 'recommended_stock': 60.0, 'reorder_quantity': 30.0, 'current_stock': 40.0},
                    {'id': 'p8888888-0000-0000-0000-000000000006', 'name': 'Sugar Commercial 50kg (చక్కెర బస్తా)', 'local_name': 'Chakkera Bag', 'category': 'Raw Ingredients', 'base_unit': 'bag', 'purchase_unit': 'bag', 'selling_unit': 'bag', 'conversion_factor': 1.0, 'purchase_price': 1950.0, 'selling_price': 2050.0, 'minimum_stock': 2.0, 'recommended_stock': 8.0, 'reorder_quantity': 4.0, 'current_stock': 5.0},
                ]
            },
            {
                'shop_id': DEMO_HARDWARE_SHOP_ID,
                'user_id': DEMO_HARDWARE_USER_ID,
                'categories': ['Plumbing & Pipes', 'Electrical Wires & Switches', 'Cement & Construction', 'Paints & Chemicals', 'Hand Tools & Fasteners'],
                'suppliers': [
                    {'name': 'Supreme Pipes & Sanitary Wholesalers', 'phone': '+91 98480aa001', 'email': 'supreme@pipesdist.com', 'address': 'Industrial Area, Hyderabad'},
                    {'name': 'Finolex Wires & UltraTech Depot', 'phone': '+91 98480aa002', 'email': 'finolex@wiresstock.com', 'address': 'Warangal'}
                ],
                'customers': [
                    {'name': 'Koti Plumber (Contractor Udhar)', 'phone': '+91 98480aa111', 'credit': 18500.0, 'notes': 'Apartment plumbing project materials'},
                    {'name': 'Satyam Electrician (Running Credit)', 'phone': '+91 98480aa222', 'credit': 9200.0, 'notes': 'Wiring and switch boxes'}
                ],
                'products': [
                    {'id': 'paaaaaa-0000-0000-0000-000000000001', 'name': 'PVC Pipe 1 inch 10ft (పీవీసీ పైపు)', 'local_name': 'PVC Pipe', 'category': 'Plumbing & Pipes', 'base_unit': 'length', 'purchase_unit': 'bundle', 'selling_unit': 'length', 'conversion_factor': 10.0, 'purchase_price': 1250.0, 'selling_price': 160.0, 'minimum_stock': 15.0, 'recommended_stock': 100.0, 'reorder_quantity': 40.0, 'current_stock': 75.0},
                    {'id': 'paaaaaa-0000-0000-0000-000000000002', 'name': 'Finolex Copper Wire 2.5 sq mm (రాగి వైరు 90మీ)', 'local_name': 'Copper Wire', 'category': 'Electrical Wires & Switches', 'base_unit': 'roll', 'purchase_unit': 'box', 'selling_unit': 'roll', 'conversion_factor': 4.0, 'purchase_price': 9800.0, 'selling_price': 2850.0, 'minimum_stock': 5.0, 'recommended_stock': 35.0, 'reorder_quantity': 12.0, 'current_stock': 20.0},
                    {'id': 'paaaaaa-0000-0000-0000-000000000003', 'name': 'Anchor Roma Modular Switch 6A (యాంకర్ స్విచ్)', 'local_name': 'Anchor Switch', 'category': 'Electrical Wires & Switches', 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 20.0, 'purchase_price': 640.0, 'selling_price': 42.0, 'minimum_stock': 30.0, 'recommended_stock': 200.0, 'reorder_quantity': 60.0, 'current_stock': 150.0},
                    {'id': 'paaaaaa-0000-0000-0000-000000000004', 'name': 'UltraTech Cement 50kg (సిమెంట్ బస్తా)', 'local_name': 'Cement Bag', 'category': 'Cement & Construction', 'base_unit': 'bag', 'purchase_unit': 'bag', 'selling_unit': 'bag', 'conversion_factor': 1.0, 'purchase_price': 345.0, 'selling_price': 390.0, 'minimum_stock': 25.0, 'recommended_stock': 150.0, 'reorder_quantity': 50.0, 'current_stock': 85.0},
                    {'id': 'paaaaaa-0000-0000-0000-000000000005', 'name': 'Asian Paints Apex White 20L (ఏషియన్ పెయింట్)', 'local_name': 'Asian Paint', 'category': 'Paints & Chemicals', 'base_unit': 'bucket', 'purchase_unit': 'bucket', 'selling_unit': 'bucket', 'conversion_factor': 1.0, 'purchase_price': 3250.0, 'selling_price': 3800.0, 'minimum_stock': 4.0, 'recommended_stock': 25.0, 'reorder_quantity': 10.0, 'current_stock': 14.0},
                    {'id': 'paaaaaa-0000-0000-0000-000000000006', 'name': 'Steel Screws & Rawlplugs Box (స్క్రూలు బాక్స్)', 'local_name': 'Screws Box', 'category': 'Hand Tools & Fasteners', 'base_unit': 'box', 'purchase_unit': 'carton', 'selling_unit': 'box', 'conversion_factor': 10.0, 'purchase_price': 1350.0, 'selling_price': 180.0, 'minimum_stock': 10.0, 'recommended_stock': 50.0, 'reorder_quantity': 20.0, 'current_stock': 35.0},
                ]
            },
            {
                'shop_id': DEMO_AUTO_SHOP_ID,
                'user_id': DEMO_AUTO_USER_ID,
                'categories': ['Engine Oils & Lubricants', 'Brake & Clutch Parts', 'Tyres & Tubes', 'Electrical & Bulbs', 'Cables & Filters'],
                'suppliers': [
                    {'name': 'Castrol India Lubricants Stockist', 'phone': '+91 98480bb001', 'email': 'orders@castrolhub.com', 'address': 'Auto Market, Secunderabad'},
                    {'name': 'Hero & Bajaj Genuine Spares Wholesale', 'phone': '+91 98480bb002', 'email': 'spares@automarket.com', 'address': 'Warangal'}
                ],
                'customers': [
                    {'name': 'Prasad Mechanic (Auto Garage Tab)', 'phone': '+91 98480bb111', 'credit': 12500.0, 'notes': 'Engine oil cartons & brake parts'},
                    {'name': 'Venu Two-Wheeler Works', 'phone': '+91 98480bb222', 'credit': 7800.0, 'notes': 'Tyres and battery replacement balance'}
                ],
                'products': [
                    {'id': 'pbbbbbb-0000-0000-0000-000000000001', 'name': 'Castrol Activ 4T 20W-40 1L (ఇంజన్ ఆయిల్)', 'local_name': 'Engine Oil', 'category': 'Engine Oils & Lubricants', 'base_unit': 'bottle', 'purchase_unit': 'box', 'selling_unit': 'bottle', 'conversion_factor': 12.0, 'purchase_price': 4200.0, 'selling_price': 420.0, 'minimum_stock': 12.0, 'recommended_stock': 70.0, 'reorder_quantity': 24.0, 'current_stock': 45.0},
                    {'id': 'pbbbbbb-0000-0000-0000-000000000002', 'name': 'Hero Splendor Brake Shoes (బ్రేక్ షూస్)', 'local_name': 'Brake Shoes', 'category': 'Brake & Clutch Parts', 'base_unit': 'set', 'purchase_unit': 'box', 'selling_unit': 'set', 'conversion_factor': 10.0, 'purchase_price': 1800.0, 'selling_price': 240.0, 'minimum_stock': 8.0, 'recommended_stock': 50.0, 'reorder_quantity': 20.0, 'current_stock': 30.0},
                    {'id': 'pbbbbbb-0000-0000-0000-000000000003', 'name': 'Amaron 12V Bike Battery 4Ah (బైక్ బ్యాటరీ)', 'local_name': 'Bike Battery', 'category': 'Electrical & Bulbs', 'base_unit': 'unit', 'purchase_unit': 'unit', 'selling_unit': 'unit', 'conversion_factor': 1.0, 'purchase_price': 1180.0, 'selling_price': 1450.0, 'minimum_stock': 3.0, 'recommended_stock': 20.0, 'reorder_quantity': 6.0, 'current_stock': 12.0},
                    {'id': 'pbbbbbb-0000-0000-0000-000000000004', 'name': 'MRF Nylogrip Tyre 2.75-18 (ఎంఆర్ఎఫ్ టైరు)', 'local_name': 'MRF Tyre', 'category': 'Tyres & Tubes', 'base_unit': 'piece', 'purchase_unit': 'piece', 'selling_unit': 'piece', 'conversion_factor': 1.0, 'purchase_price': 1380.0, 'selling_price': 1650.0, 'minimum_stock': 4.0, 'recommended_stock': 25.0, 'reorder_quantity': 8.0, 'current_stock': 16.0},
                    {'id': 'pbbbbbb-0000-0000-0000-000000000005', 'name': 'Clutch Cable for Bajaj Pulsar (క్లచ్ కేబుల్)', 'local_name': 'Clutch Cable', 'category': 'Cables & Filters', 'base_unit': 'piece', 'purchase_unit': 'bundle', 'selling_unit': 'piece', 'conversion_factor': 10.0, 'purchase_price': 850.0, 'selling_price': 130.0, 'minimum_stock': 6.0, 'recommended_stock': 40.0, 'reorder_quantity': 15.0, 'current_stock': 25.0},
                    {'id': 'pbbbbbb-0000-0000-0000-000000000006', 'name': 'Spark Plug NGK 2-Wheeler (స్పార్క్ ప్లగ్)', 'local_name': 'Spark Plug', 'category': 'Electrical & Bulbs', 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 10.0, 'purchase_price': 650.0, 'selling_price': 95.0, 'minimum_stock': 15.0, 'recommended_stock': 100.0, 'reorder_quantity': 30.0, 'current_stock': 60.0},
                ]
            },
            {
                'shop_id': DEMO_VEG_SHOP_ID,
                'user_id': DEMO_VEG_USER_ID,
                'categories': ['Fresh Vegetables', 'Leafy Greens', 'Onions & Potatoes', 'Fresh Fruits', 'Exotic & Salad Veg'],
                'suppliers': [
                    {'name': 'Bowenpally Wholesale Mandi Guild', 'phone': '+91 98480cc001', 'email': 'bowenpally@mandi.gov.in', 'address': 'Mandi Yard, Secunderabad'},
                    {'name': 'Kothapet Fruit Commission Market', 'phone': '+91 98480cc002', 'email': 'kothapet@fruits.com', 'address': 'Fruit Market, Hyderabad'}
                ],
                'customers': [
                    {'name': 'Balaji Fast Food Center (Daily Veggies)', 'phone': '+91 98480cc111', 'credit': 3800.0, 'notes': 'Daily onion, tomato, cabbage supply'},
                    {'name': 'Raghavendra Mess (Vegetables)', 'phone': '+91 98480cc222', 'credit': 2400.0, 'notes': 'Weekly leafy greens and potatoes'}
                ],
                'products': [
                    {'id': 'pcccccc-0000-0000-0000-000000000001', 'name': 'Fresh Country Tomatoes / Tamata (నాటు టమాటా)', 'local_name': 'Tamata', 'category': 'Fresh Vegetables', 'base_unit': 'kg', 'purchase_unit': 'crate', 'selling_unit': 'kg', 'conversion_factor': 25.0, 'purchase_price': 550.0, 'selling_price': 35.0, 'minimum_stock': 20.0, 'recommended_stock': 120.0, 'reorder_quantity': 50.0, 'current_stock': 80.0},
                    {'id': 'pcccccc-0000-0000-0000-000000000002', 'name': 'Onion / Ullipaya (ఉల్లిపాయలు)', 'local_name': 'Ullipaya', 'category': 'Onions & Potatoes', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 50.0, 'purchase_price': 1100.0, 'selling_price': 30.0, 'minimum_stock': 40.0, 'recommended_stock': 250.0, 'reorder_quantity': 100.0, 'current_stock': 150.0},
                    {'id': 'pcccccc-0000-0000-0000-000000000003', 'name': 'Potato / Bangala Dumpa (బంగాళాదుంపలు)', 'local_name': 'Bangala Dumpa', 'category': 'Onions & Potatoes', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 50.0, 'purchase_price': 1250.0, 'selling_price': 32.0, 'minimum_stock': 30.0, 'recommended_stock': 200.0, 'reorder_quantity': 100.0, 'current_stock': 120.0},
                    {'id': 'pcccccc-0000-0000-0000-000000000004', 'name': 'Green Chillies / Pachi Mirchi (పచ్చిమిర్చి)', 'local_name': 'Pachi Mirchi', 'category': 'Fresh Vegetables', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 10.0, 'purchase_price': 450.0, 'selling_price': 60.0, 'minimum_stock': 8.0, 'recommended_stock': 40.0, 'reorder_quantity': 15.0, 'current_stock': 25.0},
                    {'id': 'pcccccc-0000-0000-0000-000000000005', 'name': 'Fresh Palak / Spinach (పాలకూర కట్ట)', 'local_name': 'Palakoora', 'category': 'Leafy Greens', 'base_unit': 'bunch', 'purchase_unit': 'bundle', 'selling_unit': 'bunch', 'conversion_factor': 25.0, 'purchase_price': 225.0, 'selling_price': 15.0, 'minimum_stock': 10.0, 'recommended_stock': 80.0, 'reorder_quantity': 25.0, 'current_stock': 50.0},
                    {'id': 'pcccccc-0000-0000-0000-000000000006', 'name': 'Yelakki Small Bananas (ఎలక్కి అరటిపండ్లు)', 'local_name': 'Arati Pandlu', 'category': 'Fresh Fruits', 'base_unit': 'dozen', 'purchase_unit': 'crate', 'selling_unit': 'dozen', 'conversion_factor': 10.0, 'purchase_price': 420.0, 'selling_price': 60.0, 'minimum_stock': 8.0, 'recommended_stock': 50.0, 'reorder_quantity': 20.0, 'current_stock': 35.0},
                ]
            },
            {
                'shop_id': DEMO_ELEC_SHOP_ID,
                'user_id': DEMO_ELEC_USER_ID,
                'categories': ['Smartphones', 'Fast Chargers & Adapters', 'Bluetooth Audio', 'Screen Guards & Covers', 'Powerbanks & Cables'],
                'suppliers': [
                    {'name': 'Redington India Mobile Wholesale', 'phone': '+91 98480dd001', 'email': 'redington@mobilehub.com', 'address': 'Electronics Plaza, Hyderabad'},
                    {'name': 'boAt Audio Official Distributorship', 'phone': '+91 98480dd002', 'email': 'boatdist@audio.in', 'address': 'Warangal'}
                ],
                'customers': [
                    {'name': 'Naresh (Phone EMI / Udhar Account)', 'phone': '+91 98480dd111', 'credit': 9500.0, 'notes': 'Samsung Galaxy balance installment'},
                    {'name': 'Sandeep (College Student Audio Tab)', 'phone': '+91 98480dd222', 'credit': 1199.0, 'notes': 'boAt earbuds pending balance'}
                ],
                'products': [
                    {'id': 'pdddddd-0000-0000-0000-000000000001', 'name': 'Samsung Galaxy A15 5G 128GB (శాంసంగ్ మొబైల్)', 'local_name': 'Samsung Mobile', 'category': 'Smartphones', 'base_unit': 'unit', 'purchase_unit': 'unit', 'selling_unit': 'unit', 'conversion_factor': 1.0, 'purchase_price': 13200.0, 'selling_price': 14999.0, 'minimum_stock': 2.0, 'recommended_stock': 12.0, 'reorder_quantity': 4.0, 'current_stock': 8.0},
                    {'id': 'pdddddd-0000-0000-0000-000000000002', 'name': 'boAt Airdopes 141 Bluetooth Earbuds (ఇయర్ బడ్స్)', 'local_name': 'boAt Earbuds', 'category': 'Bluetooth Audio', 'base_unit': 'unit', 'purchase_unit': 'box', 'selling_unit': 'unit', 'conversion_factor': 10.0, 'purchase_price': 8900.0, 'selling_price': 1199.0, 'minimum_stock': 5.0, 'recommended_stock': 35.0, 'reorder_quantity': 10.0, 'current_stock': 22.0},
                    {'id': 'pdddddd-0000-0000-0000-000000000003', 'name': 'Fast 20W Type-C Charger Adapter (టైప్-సి ఛార్జర్)', 'local_name': 'Fast Charger', 'category': 'Fast Chargers & Adapters', 'base_unit': 'unit', 'purchase_unit': 'box', 'selling_unit': 'unit', 'conversion_factor': 10.0, 'purchase_price': 3200.0, 'selling_price': 499.0, 'minimum_stock': 10.0, 'recommended_stock': 60.0, 'reorder_quantity': 20.0, 'current_stock': 40.0},
                    {'id': 'pdddddd-0000-0000-0000-000000000004', 'name': '10000mAh Dual USB Power Bank (పవర్ బ్యాంక్)', 'local_name': 'Power Bank', 'category': 'Powerbanks & Cables', 'base_unit': 'unit', 'purchase_unit': 'box', 'selling_unit': 'unit', 'conversion_factor': 5.0, 'purchase_price': 3800.0, 'selling_price': 999.0, 'minimum_stock': 3.0, 'recommended_stock': 25.0, 'reorder_quantity': 10.0, 'current_stock': 15.0},
                    {'id': 'pdddddd-0000-0000-0000-000000000005', 'name': 'Braided 1.5m Type-C Fast Cable (యూఎస్బీ కేబుల్)', 'local_name': 'Type-C Cable', 'category': 'Powerbanks & Cables', 'base_unit': 'piece', 'purchase_unit': 'bundle', 'selling_unit': 'piece', 'conversion_factor': 20.0, 'purchase_price': 2200.0, 'selling_price': 199.0, 'minimum_stock': 15.0, 'recommended_stock': 100.0, 'reorder_quantity': 30.0, 'current_stock': 65.0},
                    {'id': 'pdddddd-0000-0000-0000-000000000006', 'name': '9D Edge-to-Edge Tempered Glass (స్క్రీన్ గార్డ్)', 'local_name': 'Screen Guard', 'category': 'Screen Guards & Covers', 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 25.0, 'purchase_price': 1250.0, 'selling_price': 150.0, 'minimum_stock': 20.0, 'recommended_stock': 150.0, 'reorder_quantity': 50.0, 'current_stock': 90.0},
                ]
            }
        ]

        for s_info in additional_shops:
            sid = s_info['shop_id']
            uid = s_info['user_id']

            # Categories
            for cat_name in s_info['categories']:
                self.store['categories'].append({
                    'id': str(uuid.uuid4()), 'shop_id': sid, 'name': cat_name, 'is_active': True, 'created_at': now
                })

            # Suppliers
            s_map = []
            for supp in s_info['suppliers']:
                s_id = str(uuid.uuid4())
                s_map.append(s_id)
                self.store['suppliers'].append({
                    'id': s_id, 'shop_id': sid, 'name': supp['name'], 'phone': supp['phone'],
                    'email': supp['email'], 'address': supp['address'], 'is_active': True,
                    'created_at': now, 'updated_at': now
                })

            # Customers & Borrowings
            for cust in s_info['customers']:
                c_id = str(uuid.uuid4())
                self.store['customers'].append({
                    'id': c_id, 'shop_id': sid, 'name': cust['name'], 'phone': cust['phone'],
                    'total_credit': cust['credit'], 'is_active': True, 'created_at': now, 'updated_at': now
                })
                if cust['credit'] > 0:
                    self.store['borrowings'].append({
                        'id': str(uuid.uuid4()), 'shop_id': sid, 'customer_id': c_id,
                        'customer_name': cust['name'], 'status': 'ACTIVE', 'total_value': cust['credit'],
                        'paid_amount': 0.0, 'remaining_balance': cust['credit'], 'notes': cust.get('notes', 'Credit account'),
                        'created_by': uid, 'created_at': now, 'updated_at': now
                    })

            # Products & Inventory
            for prod in s_info['products']:
                st = prod.pop('current_stock')
                prod['shop_id'] = sid
                prod['is_active'] = True
                prod['supplier_id'] = s_map[0] if s_map else None
                prod['created_at'] = now
                prod['updated_at'] = now
                self.store['products'].append(prod)
                self.store['inventory'].append({
                    'id': str(uuid.uuid4()), 'shop_id': sid, 'product_id': prod['id'],
                    'current_stock': st, 'stock_unit': prod['base_unit'],
                    'last_stock_in': now, 'last_stock_out': now, 'created_at': now, 'updated_at': now
                })
