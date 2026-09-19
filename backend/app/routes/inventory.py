"""Inventory routes — stock in, stock out, view inventory."""
from flask import Blueprint, request, g
from app.utils import require_auth, success_response, error_response, get_current_shop_id, get_current_user_id
from app.utils.supabase_client import get_supabase

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('', methods=['GET'])
@require_auth
def list_inventory():
    """Get all inventory items with product details."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)
    
    try:
        supabase = get_supabase()
        
        # Get inventory with product data
        inv_result = supabase.table('inventory').select('*').eq('shop_id', shop_id).execute()
        inventory_items = inv_result.data or []
        
        # Get products
        prod_result = supabase.table('products').select('*').eq('shop_id', shop_id).eq('is_active', True).execute()
        prod_map = {p['id']: p for p in (prod_result.data or [])}
        
        items = []
        for inv in inventory_items:
            product = prod_map.get(inv['product_id'])
            if not product:
                continue
            
            unit_cost = product['purchase_price'] / product['conversion_factor'] if product.get('conversion_factor', 0) > 0 else product.get('purchase_price', 0)
            
            items.append({
                'id': inv['id'],
                'shop_id': inv['shop_id'],
                'product_id': inv['product_id'],
                'current_stock': inv['current_stock'],
                'stock_unit': inv['stock_unit'],
                'last_stock_in': inv.get('last_stock_in'),
                'last_stock_out': inv.get('last_stock_out'),
                'product_name': product['name'],
                'product_category': product.get('category', ''),
                'purchase_price': unit_cost,
                'selling_price': product.get('selling_price', 0),
                'minimum_stock': product.get('minimum_stock', 0),
                'stock_value': round(inv['current_stock'] * unit_cost, 2),
                'is_low_stock': inv['current_stock'] <= product.get('minimum_stock', 0),
            })
        
        # Sort by name
        items.sort(key=lambda x: x['product_name'])
        
        return success_response({"items": items, "total": len(items)})
        
    except Exception as e:
        return error_response(f"Failed to fetch inventory: {str(e)}", "FETCH_ERROR", 500)


@inventory_bp.route('/stock-in', methods=['POST'])
@require_auth
def stock_in():
    """Add stock to inventory."""
    shop_id = get_current_shop_id()
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", "VALIDATION_ERROR")
    if not data.get('product_id'):
        return error_response("Product is required", "VALIDATION_ERROR")
    if not data.get('quantity') or data['quantity'] <= 0:
        return error_response("Quantity must be positive", "VALIDATION_ERROR")
    
    try:
        supabase = get_supabase()
        
        # Get product to know conversion factor
        product = supabase.table('products').select('*').eq('id', data['product_id']).eq('shop_id', shop_id).single().execute()
        if not product.data:
            return error_response("Product not found", "NOT_FOUND", 404)
        
        prod = product.data
        quantity = float(data['quantity'])
        unit = data.get('unit', prod['purchase_unit'])
        price = float(data.get('price', prod.get('purchase_price', 0)))
        
        # Convert to base units
        if unit == prod['base_unit']:
            quantity_base = quantity
        elif unit == prod['purchase_unit']:
            quantity_base = quantity * prod.get('conversion_factor', 1)
        else:
            quantity_base = quantity  # Assume same unit if unknown
        
        # Create transaction
        tx = supabase.table('transactions').insert({
            'shop_id': shop_id,
            'product_id': data['product_id'],
            'transaction_type': 'STOCK_IN',
            'quantity': quantity,
            'unit': unit,
            'quantity_in_base_unit': quantity_base,
            'price': price,
            'total_amount': round(quantity * price, 2),
            'supplier_id': data.get('supplier_id') or None,
            'source': data.get('source', 'manual'),
            'notes': data.get('notes', ''),
            'created_by': user_id,
        }).execute()
        
        # Update inventory
        inv = supabase.table('inventory').select('*').eq('product_id', data['product_id']).eq('shop_id', shop_id).execute()
        
        if inv.data and len(inv.data) > 0:
            new_stock = inv.data[0]['current_stock'] + quantity_base
            supabase.table('inventory').update({
                'current_stock': new_stock,
                'last_stock_in': 'now()',
            }).eq('id', inv.data[0]['id']).execute()
        else:
            supabase.table('inventory').insert({
                'shop_id': shop_id,
                'product_id': data['product_id'],
                'current_stock': quantity_base,
                'stock_unit': prod['base_unit'],
                'last_stock_in': 'now()',
            }).execute()
        
        # Check and resolve any low stock alerts
        supabase.table('stock_alerts').update({
            'is_resolved': True,
            'resolved_at': 'now()',
        }).eq('product_id', data['product_id']).eq('shop_id', shop_id).eq('is_resolved', False).execute()
        
        return success_response({
            'transaction': tx.data[0] if tx.data else None,
            'message': f'{quantity} {unit} of {prod["name"]} added to inventory',
        }, 201)
        
    except Exception as e:
        return error_response(f"Failed to add stock: {str(e)}", "STOCK_IN_ERROR", 500)


@inventory_bp.route('/stock-out', methods=['POST'])
@require_auth
def stock_out():
    """Remove stock from inventory."""
    shop_id = get_current_shop_id()
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", "VALIDATION_ERROR")
    if not data.get('product_id'):
        return error_response("Product is required", "VALIDATION_ERROR")
    if not data.get('quantity') or data['quantity'] <= 0:
        return error_response("Quantity must be positive", "VALIDATION_ERROR")
    
    try:
        supabase = get_supabase()
        
        # Get product
        product = supabase.table('products').select('*').eq('id', data['product_id']).eq('shop_id', shop_id).single().execute()
        if not product.data:
            return error_response("Product not found", "NOT_FOUND", 404)
        
        prod = product.data
        quantity = float(data['quantity'])
        unit = data.get('unit', prod['selling_unit'])
        price = float(data.get('price', prod.get('selling_price', 0)))
        tx_type = data.get('transaction_type', 'STOCK_OUT')
        
        # Convert to base units
        if unit == prod['base_unit']:
            quantity_base = quantity
        elif unit == prod['purchase_unit']:
            quantity_base = quantity * prod.get('conversion_factor', 1)
        else:
            quantity_base = quantity
        
        # Check sufficient stock
        inv = supabase.table('inventory').select('*').eq('product_id', data['product_id']).eq('shop_id', shop_id).execute()
        current_stock = inv.data[0]['current_stock'] if inv.data else 0
        
        if current_stock < quantity_base:
            return error_response(
                f"Insufficient stock. Available: {current_stock} {prod['base_unit']}",
                "INSUFFICIENT_STOCK"
            )
        
        # Create transaction
        tx = supabase.table('transactions').insert({
            'shop_id': shop_id,
            'product_id': data['product_id'],
            'transaction_type': tx_type,
            'quantity': quantity,
            'unit': unit,
            'quantity_in_base_unit': quantity_base,
            'price': price,
            'total_amount': round(quantity * price, 2),
            'customer_id': data.get('customer_id') or None,
            'source': data.get('source', 'manual'),
            'notes': data.get('notes', ''),
            'created_by': user_id,
        }).execute()
        
        # Update inventory
        new_stock = current_stock - quantity_base
        supabase.table('inventory').update({
            'current_stock': new_stock,
            'last_stock_out': 'now()',
        }).eq('product_id', data['product_id']).eq('shop_id', shop_id).execute()
        
        # Check low stock
        if new_stock <= prod.get('minimum_stock', 0):
            # Create low stock alert
            existing_alert = supabase.table('stock_alerts').select('id').eq('product_id', data['product_id']).eq('shop_id', shop_id).eq('is_resolved', False).execute()
            if not existing_alert.data:
                supabase.table('stock_alerts').insert({
                    'shop_id': shop_id,
                    'product_id': data['product_id'],
                    'alert_type': 'LOW_STOCK',
                    'current_stock': new_stock,
                    'threshold': prod.get('minimum_stock', 0),
                }).execute()
                
                # Create notification
                supabase.table('notifications').insert({
                    'shop_id': shop_id,
                    'type': 'LOW_STOCK',
                    'title': f'Low Stock: {prod["name"]}',
                    'message': f'{prod["name"]} is running low. Current stock: {new_stock} {prod["base_unit"]}. Minimum: {prod.get("minimum_stock", 0)} {prod["base_unit"]}.',
                    'data': {'product_id': data['product_id'], 'current_stock': new_stock},
                }).execute()
        
        return success_response({
            'transaction': tx.data[0] if tx.data else None,
            'message': f'{quantity} {unit} of {prod["name"]} removed from inventory',
            'remaining_stock': new_stock,
        }, 201)
        
    except Exception as e:
        return error_response(f"Failed to remove stock: {str(e)}", "STOCK_OUT_ERROR", 500)
