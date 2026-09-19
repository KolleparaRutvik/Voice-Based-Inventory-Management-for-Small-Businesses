"""Product routes — CRUD operations."""
from flask import Blueprint, request, g
from app.utils import require_auth, success_response, error_response, get_current_shop_id
from app.utils.supabase_client import get_supabase

products_bp = Blueprint('products', __name__)


@products_bp.route('', methods=['GET'])
@require_auth
def list_products():
    """List all products for the current shop."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)
    
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    try:
        supabase = get_supabase()
        query = supabase.table('products').select('*').eq('shop_id', shop_id).eq('is_active', True).order('name')
        
        if search:
            query = query.ilike('name', f'%{search}%')
        if category:
            query = query.eq('category', category)
        
        result = query.execute()
        products = result.data or []
        
        # Get inventory for each product
        inv_result = supabase.table('inventory').select('product_id, current_stock, stock_unit').eq('shop_id', shop_id).execute()
        inv_map = {i['product_id']: i for i in (inv_result.data or [])}
        
        for product in products:
            inv = inv_map.get(product['id'], {})
            product['current_stock'] = inv.get('current_stock', 0)
            product['stock_unit'] = inv.get('stock_unit', product['base_unit'])
            # Calculate stock value
            unit_cost = product['purchase_price'] / product['conversion_factor'] if product.get('conversion_factor', 0) > 0 else product.get('purchase_price', 0)
            product['stock_value'] = round(product['current_stock'] * unit_cost, 2)
        
        return success_response({"items": products, "total": len(products)})
        
    except Exception as e:
        return error_response(f"Failed to fetch products: {str(e)}", "FETCH_ERROR", 500)


@products_bp.route('', methods=['POST'])
@require_auth
def create_product():
    """Create a new product."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)
    
    data = request.get_json()
    if not data or not data.get('name'):
        return error_response("Product name is required", "VALIDATION_ERROR")
    
    try:
        supabase = get_supabase()
        
        product_data = {
            'shop_id': shop_id,
            'name': data['name'],
            'local_name': data.get('local_name', ''),
            'category': data.get('category', ''),
            'base_unit': data.get('base_unit', 'kg'),
            'purchase_unit': data.get('purchase_unit', 'kg'),
            'selling_unit': data.get('selling_unit', 'kg'),
            'conversion_factor': data.get('conversion_factor', 1),
            'purchase_price': data.get('purchase_price', 0),
            'selling_price': data.get('selling_price', 0),
            'minimum_stock': data.get('minimum_stock', 0),
            'recommended_stock': data.get('recommended_stock', 0),
            'reorder_quantity': data.get('reorder_quantity', 0),
            'supplier_id': data.get('supplier_id') or None,
        }
        
        result = supabase.table('products').insert(product_data).execute()
        
        if result.data and len(result.data) > 0:
            product = result.data[0]
            
            # Create inventory record with 0 stock
            supabase.table('inventory').insert({
                'shop_id': shop_id,
                'product_id': product['id'],
                'current_stock': 0,
                'stock_unit': product_data['base_unit'],
            }).execute()
            
            # Create price history entries
            if product_data['purchase_price'] > 0:
                supabase.table('product_price_history').insert({
                    'shop_id': shop_id,
                    'product_id': product['id'],
                    'price_type': 'purchase',
                    'new_price': product_data['purchase_price'],
                    'reason': 'Initial price',
                }).execute()
            if product_data['selling_price'] > 0:
                supabase.table('product_price_history').insert({
                    'shop_id': shop_id,
                    'product_id': product['id'],
                    'price_type': 'selling',
                    'new_price': product_data['selling_price'],
                    'reason': 'Initial price',
                }).execute()
            
            return success_response(product, 201)
        
        return error_response("Failed to create product", "CREATE_ERROR", 500)
        
    except Exception as e:
        return error_response(f"Failed to create product: {str(e)}", "CREATE_ERROR", 500)


@products_bp.route('/<product_id>', methods=['GET'])
@require_auth
def get_product(product_id):
    """Get a single product with its inventory."""
    shop_id = get_current_shop_id()
    
    try:
        supabase = get_supabase()
        result = supabase.table('products').select('*').eq('id', product_id).eq('shop_id', shop_id).single().execute()
        
        if not result.data:
            return error_response("Product not found", "NOT_FOUND", 404)
        
        product = result.data
        
        # Get inventory
        inv = supabase.table('inventory').select('*').eq('product_id', product_id).eq('shop_id', shop_id).execute()
        if inv.data and len(inv.data) > 0:
            product['current_stock'] = inv.data[0]['current_stock']
        else:
            product['current_stock'] = 0
        
        return success_response(product)
        
    except Exception as e:
        return error_response(f"Failed to fetch product: {str(e)}", "FETCH_ERROR", 500)


@products_bp.route('/<product_id>', methods=['PUT'])
@require_auth
def update_product(product_id):
    """Update a product."""
    shop_id = get_current_shop_id()
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", "VALIDATION_ERROR")
    
    try:
        supabase = get_supabase()
        
        # Verify product belongs to shop
        existing = supabase.table('products').select('id, purchase_price, selling_price').eq('id', product_id).eq('shop_id', shop_id).single().execute()
        if not existing.data:
            return error_response("Product not found", "NOT_FOUND", 404)
        
        # Track price changes
        old_product = existing.data
        if 'purchase_price' in data and data['purchase_price'] != old_product.get('purchase_price'):
            supabase.table('product_price_history').insert({
                'shop_id': shop_id,
                'product_id': product_id,
                'price_type': 'purchase',
                'old_price': old_product.get('purchase_price'),
                'new_price': data['purchase_price'],
                'reason': 'Price updated',
            }).execute()
        if 'selling_price' in data and data['selling_price'] != old_product.get('selling_price'):
            supabase.table('product_price_history').insert({
                'shop_id': shop_id,
                'product_id': product_id,
                'price_type': 'selling',
                'old_price': old_product.get('selling_price'),
                'new_price': data['selling_price'],
                'reason': 'Price updated',
            }).execute()
        
        # Update allowed fields only
        allowed = ['name', 'local_name', 'category', 'base_unit', 'purchase_unit', 'selling_unit',
                   'conversion_factor', 'purchase_price', 'selling_price', 'minimum_stock',
                   'recommended_stock', 'reorder_quantity', 'supplier_id', 'description']
        update_data = {k: v for k, v in data.items() if k in allowed}
        
        result = supabase.table('products').update(update_data).eq('id', product_id).eq('shop_id', shop_id).execute()
        
        return success_response(result.data[0] if result.data else None)
        
    except Exception as e:
        return error_response(f"Failed to update product: {str(e)}", "UPDATE_ERROR", 500)


@products_bp.route('/<product_id>', methods=['DELETE'])
@require_auth
def delete_product(product_id):
    """Soft-delete a product (set is_active to false)."""
    shop_id = get_current_shop_id()
    
    try:
        supabase = get_supabase()
        result = supabase.table('products').update({'is_active': False}).eq('id', product_id).eq('shop_id', shop_id).execute()
        
        if result.data:
            return success_response({"message": "Product deactivated"})
        return error_response("Product not found", "NOT_FOUND", 404)
        
    except Exception as e:
        return error_response(f"Failed to delete product: {str(e)}", "DELETE_ERROR", 500)
