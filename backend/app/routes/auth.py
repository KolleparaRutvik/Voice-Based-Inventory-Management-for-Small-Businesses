"""Authentication routes."""
from flask import Blueprint, request, g
from app.utils import require_auth, success_response, error_response
from app.utils.supabase_client import get_supabase

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user and create their shop + seed data."""
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", "VALIDATION_ERROR")
    
    required = ['email', 'full_name', 'shop_name']
    for field in required:
        if not data.get(field):
            return error_response(f"{field} is required", "VALIDATION_ERROR")
    
    try:
        supabase = get_supabase()
        
        # Get the auth user from Supabase (they should already be signed up via frontend)
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1]
            user_response = supabase.auth.get_user(token)
            auth_id = str(user_response.user.id)
        else:
            return error_response("Authentication required for registration", "UNAUTHORIZED", 401)
        
        # Check if user already exists
        existing = supabase.table('users').select('id').eq('auth_id', auth_id).execute()
        if existing.data and len(existing.data) > 0:
            return error_response("User already registered", "ALREADY_EXISTS")
        
        # Create user profile
        user = supabase.table('users').insert({
            'auth_id': auth_id,
            'email': data['email'],
            'full_name': data['full_name'],
            'phone': data.get('phone', ''),
            'language': data.get('language', 'en'),
        }).execute()
        
        if not user.data or len(user.data) == 0:
            return error_response("Failed to create user profile", "CREATE_ERROR", 500)
        
        user_id = user.data[0]['id']
        
        # Create shop
        shop = supabase.table('shops').insert({
            'owner_id': user_id,
            'name': data['shop_name'],
            'type': data.get('shop_type', 'kirana'),
        }).execute()
        
        if not shop.data or len(shop.data) == 0:
            return error_response("Failed to create shop", "CREATE_ERROR", 500)
        
        shop_id = shop.data[0]['id']
        
        # Add user as shop member (owner)
        supabase.table('shop_members').insert({
            'shop_id': shop_id,
            'user_id': user_id,
            'role': 'owner',
        }).execute()
        
        # Seed default categories
        categories = [
            'Grains & Rice', 'Pulses & Dal', 'Spices & Masala',
            'Sugar & Jaggery', 'Oils & Ghee', 'Dairy',
            'Beverages', 'Snacks & Biscuits', 'Cleaning & Household',
            'Personal Care', 'Other',
        ]
        for cat_name in categories:
            supabase.table('categories').insert({
                'shop_id': shop_id,
                'name': cat_name,
            }).execute()
        
        # Seed sample suppliers
        suppliers_data = [
            {'shop_id': shop_id, 'name': 'ABC Traders', 'phone': '+91 9876543001'},
            {'shop_id': shop_id, 'name': 'Srinivas Wholesale', 'phone': '+91 9876543002'},
            {'shop_id': shop_id, 'name': 'Lakshmi Distributors', 'phone': '+91 9876543003'},
        ]
        for s in suppliers_data:
            supabase.table('suppliers').insert(s).execute()
        
        # Seed sample products with inventory
        sample_products = [
            {'name': 'Rice (Biyyam)', 'local_name': 'Biyyam', 'category': 'Grains & Rice', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 25, 'purchase_price': 1450, 'selling_price': 65, 'minimum_stock': 125, 'recommended_stock': 500, 'reorder_quantity': 250},
            {'name': 'Sugar (Chakkera)', 'local_name': 'Chakkera', 'category': 'Sugar & Jaggery', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 50, 'purchase_price': 2100, 'selling_price': 48, 'minimum_stock': 50, 'recommended_stock': 200, 'reorder_quantity': 100},
            {'name': 'Sunflower Oil', 'local_name': 'Nune', 'category': 'Oils & Ghee', 'base_unit': 'litre', 'purchase_unit': 'litre', 'selling_unit': 'litre', 'conversion_factor': 1, 'purchase_price': 150, 'selling_price': 165, 'minimum_stock': 10, 'recommended_stock': 50, 'reorder_quantity': 30},
            {'name': 'Toor Dal', 'local_name': 'Kandi Pappu', 'category': 'Pulses & Dal', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 25, 'purchase_price': 2750, 'selling_price': 125, 'minimum_stock': 25, 'recommended_stock': 100, 'reorder_quantity': 50},
            {'name': 'Parle-G Biscuits', 'category': 'Snacks & Biscuits', 'base_unit': 'packet', 'purchase_unit': 'carton', 'selling_unit': 'packet', 'conversion_factor': 24, 'purchase_price': 240, 'selling_price': 10, 'minimum_stock': 50, 'recommended_stock': 200, 'reorder_quantity': 96},
            {'name': 'Red Label Tea', 'category': 'Beverages', 'base_unit': 'packet', 'purchase_unit': 'box', 'selling_unit': 'packet', 'conversion_factor': 12, 'purchase_price': 1200, 'selling_price': 110, 'minimum_stock': 20, 'recommended_stock': 60, 'reorder_quantity': 36},
            {'name': 'Jaggery (Bellam)', 'local_name': 'Bellam', 'category': 'Sugar & Jaggery', 'base_unit': 'kg', 'purchase_unit': 'kg', 'selling_unit': 'kg', 'conversion_factor': 1, 'purchase_price': 55, 'selling_price': 70, 'minimum_stock': 5, 'recommended_stock': 20, 'reorder_quantity': 10},
            {'name': 'Nescafe Coffee', 'category': 'Beverages', 'base_unit': 'packet', 'purchase_unit': 'box', 'selling_unit': 'packet', 'conversion_factor': 12, 'purchase_price': 2400, 'selling_price': 220, 'minimum_stock': 10, 'recommended_stock': 36, 'reorder_quantity': 24},
        ]
        
        initial_stocks = [450, 180, 35, 65, 120, 42, 15, 30]
        
        for i, prod_data in enumerate(sample_products):
            prod_data['shop_id'] = shop_id
            prod = supabase.table('products').insert(prod_data).execute()
            
            if prod.data and len(prod.data) > 0:
                prod_id = prod.data[0]['id']
                stock = initial_stocks[i] if i < len(initial_stocks) else 10
                
                # Create inventory record
                supabase.table('inventory').insert({
                    'shop_id': shop_id,
                    'product_id': prod_id,
                    'current_stock': stock,
                    'stock_unit': prod_data['base_unit'],
                }).execute()
                
                # Create initial STOCK_IN transaction
                supabase.table('transactions').insert({
                    'shop_id': shop_id,
                    'product_id': prod_id,
                    'transaction_type': 'STOCK_IN',
                    'quantity': stock,
                    'unit': prod_data['base_unit'],
                    'quantity_in_base_unit': stock,
                    'price': prod_data['purchase_price'] / prod_data['conversion_factor'] if prod_data['conversion_factor'] > 0 else prod_data['purchase_price'],
                    'total_amount': stock * (prod_data['purchase_price'] / prod_data['conversion_factor'] if prod_data['conversion_factor'] > 0 else prod_data['purchase_price']),
                    'source': 'seed',
                    'notes': 'Initial stock',
                    'created_by': user_id,
                }).execute()
        
        return success_response({
            'user': user.data[0],
            'shop': shop.data[0],
        }, 201)
        
    except Exception as e:
        return error_response(f"Registration failed: {str(e)}", "REGISTRATION_ERROR", 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login is handled by Supabase Auth on the frontend. This endpoint validates the token."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return error_response("Email and password are required", "VALIDATION_ERROR")
    
    try:
        supabase = get_supabase()
        result = supabase.auth.sign_in_with_password({
            "email": data['email'],
            "password": data['password'],
        })
        
        if result.user:
            # Get profile
            profile = supabase.table('users').select('*').eq('auth_id', str(result.user.id)).single().execute()
            shop = None
            if profile.data:
                shop_result = supabase.table('shops').select('*').eq('owner_id', profile.data['id']).eq('is_active', True).limit(1).execute()
                if shop_result.data:
                    shop = shop_result.data[0]
            
            return success_response({
                'user': profile.data,
                'shop': shop,
                'session': {
                    'access_token': result.session.access_token,
                    'refresh_token': result.session.refresh_token,
                }
            })
        
        return error_response("Invalid credentials", "AUTH_ERROR", 401)
        
    except Exception as e:
        return error_response("Login failed. Please check your credentials.", "AUTH_ERROR", 401)


@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get current user profile and shop."""
    return success_response({
        'user': g.user,
        'shop': g.shop,
    })
