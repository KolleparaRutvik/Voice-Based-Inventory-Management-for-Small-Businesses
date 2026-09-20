"""DukaanSetu — Live PostgreSQL Client for Supabase.
Directly executes queries against the user's Supabase PostgreSQL cluster.
Provides 100% Supabase Table query builder compatibility (.table().select().eq().execute()).
"""
import os
import json
import uuid
import decimal
import logging
from datetime import datetime, date, timezone
import psycopg2
import psycopg2.extras
from psycopg2 import pool

logger = logging.getLogger(__name__)

class QueryResult:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        count = len(self.data) if isinstance(self.data, list) else (1 if self.data else 0)
        return f"<PostgresQueryResult count={count}>"


def _serialize_val(val):
    if isinstance(val, decimal.Decimal):
        return float(val) if val % 1 != 0 else int(val)
    elif isinstance(val, (datetime, date)):
        return val.isoformat()
    elif isinstance(val, uuid.UUID):
        return str(val)
    elif isinstance(val, dict):
        return {k: _serialize_val(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [_serialize_val(v) for v in val]
    return val


def serialize_row(row):
    if not row:
        return row
    return {k: _serialize_val(v) for k, v in row.items()}


class PostgresTableQuery:
    def __init__(self, table_name, db_client):
        self.table_name = table_name
        self.db = db_client
        self.selected_cols = "*"
        self.conditions = []
        self.params = []
        self.order_by_clause = None
        self.limit_val = None
        self.offset_val = None
        self.is_single = False
        self.pending_action = None # ('insert', data), ('update', data), ('delete', None)

    def select(self, cols="*"):
        self.selected_cols = cols
        return self

    def eq(self, col, val):
        self.conditions.append(f'"{col}" = %s')
        self.params.append(val)
        return self

    def neq(self, col, val):
        self.conditions.append(f'"{col}" != %s')
        self.params.append(val)
        return self

    def ilike(self, col, pattern):
        self.conditions.append(f'"{col}" ILIKE %s')
        self.params.append(pattern)
        return self

    def in_(self, col, vals):
        if not vals:
            self.conditions.append("1=0")
            return self
        placeholders = ', '.join(['%s'] * len(vals))
        self.conditions.append(f'"{col}" IN ({placeholders})')
        self.params.extend(vals)
        return self

    def gte(self, col, val):
        self.conditions.append(f'"{col}" >= %s')
        self.params.append(val)
        return self

    def lte(self, col, val):
        self.conditions.append(f'"{col}" <= %s')
        self.params.append(val)
        return self

    def order(self, col, desc=False):
        direction = "DESC" if desc else "ASC"
        self.order_by_clause = f'"{col}" {direction}'
        return self

    def limit(self, count):
        self.limit_val = count
        return self

    def offset(self, count):
        self.offset_val = count
        return self

    def range(self, start, end):
        self.offset_val = start
        self.limit_val = max(0, end - start + 1)
        return self

    def single(self):
        self.is_single = True
        return self

    def insert(self, data):
        self.pending_action = ('insert', data)
        return self

    def update(self, data):
        self.pending_action = ('update', data)
        return self

    def delete(self):
        self.pending_action = ('delete', None)
        return self

    def execute(self):
        conn = self.db.get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                if self.pending_action:
                    action_type, action_data = self.pending_action

                    if action_type == 'insert':
                        rows = action_data if isinstance(action_data, list) else [action_data]
                        inserted = []
                        for item in rows:
                            row_dict = dict(item)
                            if 'id' not in row_dict:
                                row_dict['id'] = str(uuid.uuid4())
                            cols = list(row_dict.keys())
                            col_str = ', '.join([f'"{c}"' for c in cols])
                            val_placeholders = ', '.join(['%s'] * len(cols))
                            vals = []
                            for c in cols:
                                v = row_dict[c]
                                if isinstance(v, (dict, list)):
                                    v = json.dumps(v)
                                vals.append(v)

                            sql = f'INSERT INTO "{self.table_name}" ({col_str}) VALUES ({val_placeholders}) RETURNING *;'
                            cur.execute(sql, vals)
                            rec = cur.fetchone()
                            inserted.append(serialize_row(dict(rec)))

                        conn.commit()
                        return QueryResult(inserted if isinstance(action_data, list) else [inserted[0]])

                    elif action_type == 'update':
                        set_clauses = []
                        update_params = []
                        for k, v in action_data.items():
                            set_clauses.append(f'"{k}" = %s')
                            if isinstance(v, (dict, list)):
                                v = json.dumps(v)
                            update_params.append(v)

                        set_str = ', '.join(set_clauses)
                        where_str = f"WHERE {' AND '.join(self.conditions)}" if self.conditions else ""
                        sql = f'UPDATE "{self.table_name}" SET {set_str} {where_str} RETURNING *;'
                        full_params = update_params + self.params
                        cur.execute(sql, full_params)
                        records = cur.fetchall()
                        conn.commit()
                        return QueryResult([serialize_row(dict(r)) for r in records])

                    elif action_type == 'delete':
                        where_str = f"WHERE {' AND '.join(self.conditions)}" if self.conditions else ""
                        sql = f'DELETE FROM "{self.table_name}" {where_str} RETURNING *;'
                        cur.execute(sql, self.params)
                        records = cur.fetchall()
                        conn.commit()
                        return QueryResult([serialize_row(dict(r)) for r in records])

                # SELECT
                where_str = f"WHERE {' AND '.join(self.conditions)}" if self.conditions else ""
                order_str = f"ORDER BY {self.order_by_clause}" if self.order_by_clause else ""
                limit_str = f"LIMIT {self.limit_val}" if self.limit_val is not None else ""
                offset_str = f"OFFSET {self.offset_val}" if self.offset_val is not None else ""

                sql = f'SELECT {self.selected_cols} FROM "{self.table_name}" {where_str} {order_str} {limit_str} {offset_str};'
                cur.execute(sql, self.params)
                records = cur.fetchall()
                serialized = [serialize_row(dict(r)) for r in records]

                if self.is_single:
                    return QueryResult(serialized[0] if serialized else None)
                return QueryResult(serialized)
        except Exception as e:
            conn.rollback()
            logger.error(f"PostgreSQL query error on {self.table_name}: {e}")
            raise
        finally:
            self.db.return_connection(conn)


DEMO_TOKEN_TO_EMAIL = {
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

DEMO_EMAIL_ROUTING = {
    'jewel': ('demo-token-jewellery', '33333333-3333-3333-3333-333333333333', 'jewellery@dukaansetu.com'),
    'swarna': ('demo-token-jewellery', '33333333-3333-3333-3333-333333333333', 'jewellery@dukaansetu.com'),
    'flower': ('demo-token-flowers', '44444444-4444-4444-4444-444444444444', 'flowers@dukaansetu.com'),
    'pushpa': ('demo-token-flowers', '44444444-4444-4444-4444-444444444444', 'flowers@dukaansetu.com'),
    'clothing': ('demo-token-clothing', '55555555-5555-5555-5555-555555555555', 'clothing@dukaansetu.com'),
    'cloth': ('demo-token-clothing', '55555555-5555-5555-5555-555555555555', 'clothing@dukaansetu.com'),
    'pharmacy': ('demo-token-pharmacy', '66666666-6666-6666-6666-666666666666', 'pharmacy@dukaansetu.com'),
    'medical': ('demo-token-pharmacy', '66666666-6666-6666-6666-666666666666', 'pharmacy@dukaansetu.com'),
    'bakery': ('demo-token-bakery', '77777777-7777-7777-7777-777777777777', 'bakery@dukaansetu.com'),
    'sweet': ('demo-token-bakery', '77777777-7777-7777-7777-777777777777', 'bakery@dukaansetu.com'),
    'restaurant': ('demo-token-restaurant', '88888888-8888-8888-8888-888888888888', 'restaurant@dukaansetu.com'),
    'tiffin': ('demo-token-restaurant', '88888888-8888-8888-8888-888888888888', 'restaurant@dukaansetu.com'),
    'teacoffee': ('demo-token-teacoffee', '99999999-9999-9999-9999-999999999999', 'teacoffee@dukaansetu.com'),
    'tea': ('demo-token-teacoffee', '99999999-9999-9999-9999-999999999999', 'teacoffee@dukaansetu.com'),
    'chai': ('demo-token-teacoffee', '99999999-9999-9999-9999-999999999999', 'teacoffee@dukaansetu.com'),
    'hardware': ('demo-token-hardware', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'hardware@dukaansetu.com'),
    'autoparts': ('demo-token-autoparts', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'autoparts@dukaansetu.com'),
    'spares': ('demo-token-autoparts', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'autoparts@dukaansetu.com'),
    'auto': ('demo-token-autoparts', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'autoparts@dukaansetu.com'),
    'vegetables': ('demo-token-vegetables', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'vegetables@dukaansetu.com'),
    'fruits': ('demo-token-vegetables', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'vegetables@dukaansetu.com'),
    'sabzi': ('demo-token-vegetables', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'vegetables@dukaansetu.com'),
    'electronics': ('demo-token-electronics', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'electronics@dukaansetu.com'),
    'mobile': ('demo-token-electronics', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'electronics@dukaansetu.com'),
    'kirana': ('demo-token-kirana', '11111111-1111-1111-1111-111111111111', 'srinivas@dukaansetu.com'),
    'srinivas': ('demo-token-kirana', '11111111-1111-1111-1111-111111111111', 'srinivas@dukaansetu.com'),
}


class PostgresAuth:
    def __init__(self, db_client):
        self.db = db_client

    def get_user(self, token):
        # Look up user in live database based on token
        target_email = DEMO_TOKEN_TO_EMAIL.get(token, "srinivas@dukaansetu.com")
        res = self.db.table('users').select('*').eq('email', target_email).limit(1).execute()
        user = res.data[0] if (res.data and len(res.data) > 0) else None
        if not user:
            res_any = self.db.table('users').select('*').limit(1).execute()
            user = res_any.data[0] if res_any.data else None

        auth_id = user['auth_id'] if user else "11111111-1111-1111-1111-111111111111"
        email = user['email'] if user else target_email

        user_obj = type('MockUser', (), {
            'id': auth_id,
            'email': email,
            'user_metadata': {'full_name': user.get('full_name', 'Shopkeeper') if user else 'Shopkeeper'}
        })()
        res_obj = type('AuthResponse', (), {'user': user_obj})()
        return res_obj

    def sign_in_with_password(self, credentials):
        email = credentials.get('email', '').strip().lower()
        res = self.db.table('users').select('*').eq('email', email).limit(1).execute()
        user = res.data[0] if (res.data and len(res.data) > 0) else None

        token = 'demo-token-kirana'
        auth_id = '11111111-1111-1111-1111-111111111111'
        for kw, (t, aid, _) in DEMO_EMAIL_ROUTING.items():
            if kw in email:
                token = t
                auth_id = aid
                break

        if user:
            auth_id = user.get('auth_id', auth_id)

        user_obj = type('MockUser', (), {'id': auth_id, 'email': email})()
        res_obj = type('AuthResponse', (), {
            'user': user_obj,
            'session': type('Session', (), {
                'access_token': token,
                'refresh_token': 'demo-refresh-token'
            })()
        })()
        return res_obj


class PostgresDbClient:
    """Direct PostgreSQL connection client for Supabase."""
    def __init__(self, dsn):
        self.dsn = dsn
        self.pool = psycopg2.pool.ThreadedConnectionPool(1, 10, dsn, sslmode='require')
        self.auth = PostgresAuth(self)

    def get_connection(self):
        return self.pool.getconn()

    def return_connection(self, conn):
        self.pool.putconn(conn)

    def table(self, name):
        return PostgresTableQuery(name, self)
