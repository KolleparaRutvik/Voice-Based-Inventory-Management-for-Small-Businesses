"""Authentication utilities and middleware."""
from functools import wraps
from flask import request, jsonify, g
from app.utils.supabase_client import get_supabase


DEMO_SHOP_MAP = {
    'demo-token-kirana': {
        'auth_id': '11111111-1111-1111-1111-111111111111',
        'shop_id': '22222222-2222-2222-2222-222222222222',
        'email': 'srinivas@dukaansetu.com'
    },
    'demo-token-dukaansetu': {
        'auth_id': '11111111-1111-1111-1111-111111111111',
        'shop_id': '22222222-2222-2222-2222-222222222222',
        'email': 'srinivas@dukaansetu.com'
    },
    'demo-token-vyapari': {
        'auth_id': '11111111-1111-1111-1111-111111111111',
        'shop_id': '22222222-2222-2222-2222-222222222222',
        'email': 'srinivas@dukaansetu.com'
    },
    'demo-token': {
        'auth_id': '11111111-1111-1111-1111-111111111111',
        'shop_id': '22222222-2222-2222-2222-222222222222',
        'email': 'srinivas@dukaansetu.com'
    },
    'demo-token-jewellery': {
        'auth_id': '33333333-3333-3333-3333-333333333333',
        'shop_id': '33333333-3333-3333-3333-333333333333',
        'email': 'jewellery@dukaansetu.com'
    },
    'demo-token-gold': {
        'auth_id': '33333333-3333-3333-3333-333333333333',
        'shop_id': '33333333-3333-3333-3333-333333333333',
        'email': 'jewellery@dukaansetu.com'
    },
    'demo-token-flowers': {
        'auth_id': '44444444-4444-4444-4444-444444444444',
        'shop_id': '44444444-4444-4444-4444-444444444444',
        'email': 'flowers@dukaansetu.com'
    },
    'demo-token-pushpa': {
        'auth_id': '44444444-4444-4444-4444-444444444444',
        'shop_id': '44444444-4444-4444-4444-444444444444',
        'email': 'flowers@dukaansetu.com'
    },
    'demo-token-clothing': {
        'auth_id': '55555555-5555-5555-5555-555555555555',
        'shop_id': '55555555-5555-5555-5555-555555555555',
        'email': 'clothing@dukaansetu.com'
    },
    'demo-token-pharmacy': {
        'auth_id': '66666666-6666-6666-6666-666666666666',
        'shop_id': '66666666-6666-6666-6666-666666666666',
        'email': 'pharmacy@dukaansetu.com'
    },
    'demo-token-bakery': {
        'auth_id': '77777777-7777-7777-7777-777777777777',
        'shop_id': '77777777-7777-7777-7777-777777777777',
        'email': 'bakery@dukaansetu.com'
    },
    'demo-token-restaurant': {
        'auth_id': '88888888-8888-8888-8888-888888888888',
        'shop_id': '88888888-8888-8888-8888-888888888888',
        'email': 'restaurant@dukaansetu.com'
    },
    'demo-token-teacoffee': {
        'auth_id': '99999999-9999-9999-9999-999999999999',
        'shop_id': '99999999-9999-9999-9999-999999999999',
        'email': 'teacoffee@dukaansetu.com'
    },
    'demo-token-hardware': {
        'auth_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        'shop_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        'email': 'hardware@dukaansetu.com'
    },
    'demo-token-autoparts': {
        'auth_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        'shop_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        'email': 'autoparts@dukaansetu.com'
    },
    'demo-token-vegetables': {
        'auth_id': 'cccccccc-cccc-cccc-cccc-cccccccccccc',
        'shop_id': 'cccccccc-cccc-cccc-cccc-cccccccccccc',
        'email': 'vegetables@dukaansetu.com'
    },
    'demo-token-electronics': {
        'auth_id': 'dddddddd-dddd-dddd-dddd-dddddddddddd',
        'shop_id': 'dddddddd-dddd-dddd-dddd-dddddddddddd',
        'email': 'electronics@dukaansetu.com'
    },
}


def require_auth(f):
    """Decorator to require authentication on a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({
                "success": False,
                "error": {"code": "UNAUTHORIZED", "message": "No valid authorization token provided"}
            }), 401

        token = auth_header.split('Bearer ')[1]

        # Immediate handling for demo tokens across all 12 store types
        if token in DEMO_SHOP_MAP:
            info = DEMO_SHOP_MAP[token]
            g.auth_id = info['auth_id']
            g.token = token
            supabase = get_supabase()
            profile = supabase.table('users').select('*').eq('email', info['email']).limit(1).execute()
            if profile.data and len(profile.data) > 0:
                g.user = profile.data[0]
                g.user_id = profile.data[0]['id']
            else:
                fallback_p = supabase.table('users').select('*').limit(1).execute()
                if fallback_p.data and len(fallback_p.data) > 0:
                    g.user = fallback_p.data[0]
                    g.user_id = fallback_p.data[0]['id']
            shop = supabase.table('shops').select('*').eq('id', info['shop_id']).limit(1).execute()
            if shop.data and len(shop.data) > 0:
                g.shop = shop.data[0]
                g.shop_id = shop.data[0]['id']
            else:
                fallback_s = supabase.table('shops').select('*').limit(1).execute()
                if fallback_s.data and len(fallback_s.data) > 0:
                    g.shop = fallback_s.data[0]
                    g.shop_id = fallback_s.data[0]['id']
            return f(*args, **kwargs)

        if token.startswith('user-token-'):
            user_id = token.replace('user-token-', '')
            supabase = get_supabase()
            profile = supabase.table('users').select('*').eq('id', user_id).limit(1).execute()
            if not (profile.data and len(profile.data) > 0):
                profile = supabase.table('users').select('*').eq('auth_id', user_id).limit(1).execute()
            if profile.data and len(profile.data) > 0:
                g.user = profile.data[0]
                g.user_id = profile.data[0]['id']
                g.auth_id = profile.data[0].get('auth_id', user_id)
                g.token = token
                shop = supabase.table('shops').select('*').eq('owner_id', g.user_id).limit(1).execute()
                if shop.data and len(shop.data) > 0:
                    g.shop = shop.data[0]
                    g.shop_id = shop.data[0]['id']
                else:
                    g.shop = None
                    g.shop_id = None
                return f(*args, **kwargs)

        try:
            supabase = get_supabase()
            # Verify the JWT with Supabase
            user_response = supabase.auth.get_user(token)

            if not user_response or not user_response.user:
                return jsonify({
                    "success": False,
                    "error": {"code": "UNAUTHORIZED", "message": "Invalid or expired token"}
                }), 401

            # Store user info in Flask's g object
            g.auth_user = user_response.user
            g.auth_id = user_response.user.id
            g.token = token

            # Get user profile and shop from our database
            profile = supabase.table('users').select('*').eq('auth_id', str(g.auth_id)).single().execute()
            if profile.data:
                g.user = profile.data
                g.user_id = profile.data['id']

                # Get shop
                shop = supabase.table('shops').select('*').eq('owner_id', g.user_id).eq('is_active', True).limit(1).execute()
                if shop.data and len(shop.data) > 0:
                    g.shop = shop.data[0]
                    g.shop_id = shop.data[0]['id']
                else:
                    g.shop = None
                    g.shop_id = None
            else:
                g.user = None
                g.user_id = None
                g.shop = None
                g.shop_id = None

        except Exception:
            return jsonify({
                "success": False,
                "error": {"code": "UNAUTHORIZED", "message": "Authentication failed"}
            }), 401

        return f(*args, **kwargs)
    return decorated


def get_current_shop_id():
    """Get the current user's shop ID."""
    return getattr(g, 'shop_id', None)


def get_current_user_id():
    """Get the current user's ID."""
    return getattr(g, 'user_id', None)
