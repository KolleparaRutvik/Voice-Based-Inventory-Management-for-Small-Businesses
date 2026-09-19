"""Authentication utilities and middleware."""
from functools import wraps
from flask import request, jsonify, g
from app.utils.supabase_client import get_supabase


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

        # Immediate handling for demo token
        if token in ('demo-token-vyapari', 'demo-token'):
            g.auth_id = 'demo-auth-id'
            g.token = token
            supabase = get_supabase()
            profile = supabase.table('users').select('*').single().execute()
            if profile.data:
                g.user = profile.data
                g.user_id = profile.data['id']
            shop = supabase.table('shops').select('*').single().execute()
            if shop.data:
                g.shop = shop.data
                g.shop_id = shop.data['id']
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
