"""Analytics routes — dashboard stats."""
from flask import Blueprint
from datetime import datetime, timedelta
from app.utils import require_auth, success_response, error_response, get_current_shop_id
from app.utils.supabase_client import get_supabase

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard():
    """Get dashboard analytics data."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)
    
    try:
        supabase = get_supabase()
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Get today's transactions
        today_tx = supabase.table('transactions').select('*').eq('shop_id', shop_id).gte('created_at', f'{today}T00:00:00').execute()
        transactions = today_tx.data or []
        
        today_sales = sum(t.get('total_amount', 0) for t in transactions if t['transaction_type'] in ('SALE', 'STOCK_OUT'))
        today_purchases = sum(t.get('total_amount', 0) for t in transactions if t['transaction_type'] in ('PURCHASE', 'STOCK_IN'))
        
        # Get inventory stats
        inv = supabase.table('inventory').select('*').eq('shop_id', shop_id).execute()
        prods = supabase.table('products').select('*').eq('shop_id', shop_id).eq('is_active', True).execute()
        prod_map = {p['id']: p for p in (prods.data or [])}
        
        total_value = 0
        low_stock_items = []
        
        for item in (inv.data or []):
            prod = prod_map.get(item['product_id'])
            if not prod:
                continue
            unit_cost = prod['purchase_price'] / prod['conversion_factor'] if prod.get('conversion_factor', 0) > 0 else prod.get('purchase_price', 0)
            total_value += item['current_stock'] * unit_cost
            
            if item['current_stock'] <= prod.get('minimum_stock', 0):
                low_stock_items.append({
                    'id': item['id'],
                    'product_id': item['product_id'],
                    'product_name': prod['name'],
                    'current_stock': item['current_stock'],
                    'stock_unit': item['stock_unit'],
                    'minimum_stock': prod.get('minimum_stock', 0),
                    'is_low_stock': True,
                })
        
        # Get active borrowings
        borrowings = supabase.table('borrowings').select('*').eq('shop_id', shop_id).in_('status', ['ACTIVE', 'PARTIALLY_RETURNED']).execute()
        borrowed_value = sum(b.get('remaining_balance', 0) for b in (borrowings.data or []))
        
        # Calculate estimated margin (selling value - purchase cost of inventory)
        sell_value = 0
        for item in (inv.data or []):
            prod = prod_map.get(item['product_id'])
            if prod:
                sell_value += item['current_stock'] * prod.get('selling_price', 0)
        estimated_margin = sell_value - total_value
        
        # Recent transactions (last 10)
        recent = supabase.table('transactions').select('*').eq('shop_id', shop_id).order('created_at', desc=True).limit(10).execute()
        recent_items = recent.data or []
        
        # Add product names
        for tx in recent_items:
            prod = prod_map.get(tx.get('product_id'))
            tx['product_name'] = prod['name'] if prod else 'Unknown'
        
        # ── Fast-moving & slow-moving products (30-day sales velocity) ──
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        tx_30d = supabase.table('transactions').select('product_id, quantity, transaction_type').eq('shop_id', shop_id).gte('created_at', thirty_days_ago).execute()

        sales_by_product = {}
        for tx in (tx_30d.data or []):
            if tx.get('transaction_type') in ('SALE', 'STOCK_OUT', 'BORROW_OUT'):
                pid = tx['product_id']
                sales_by_product[pid] = sales_by_product.get(pid, 0) + float(tx.get('quantity', 0))

        # Build velocity list for all active products
        velocity_list = []
        for p in (prods.data or []):
            pid = p['id']
            total_sold = sales_by_product.get(pid, 0)
            velocity_list.append({
                'product_id': pid,
                'product_name': p['name'],
                'category': p.get('category', ''),
                'total_sold_30d': round(total_sold, 1),
                'avg_daily': round(total_sold / 30.0, 2),
                'unit': p.get('base_unit', 'unit'),
            })

        # Sort by total_sold descending
        velocity_list.sort(key=lambda x: x['total_sold_30d'], reverse=True)
        fast_moving = velocity_list[:5]
        slow_moving = sorted(velocity_list, key=lambda x: x['total_sold_30d'])[:5]

        return success_response({
            'today_sales': round(today_sales, 2),
            'today_purchases': round(today_purchases, 2),
            'inventory_value': round(total_value, 2),
            'estimated_margin': round(estimated_margin, 2),
            'total_products': len(prods.data or []),
            'low_stock_count': len(low_stock_items),
            'active_borrowings': len(borrowings.data or []),
            'borrowed_value': round(borrowed_value, 2),
            'recent_transactions': recent_items,
            'low_stock_products': low_stock_items,
            'fast_moving': fast_moving,
            'slow_moving': slow_moving,
        })
        
    except Exception as e:
        return error_response(f"Failed to load dashboard: {str(e)}", "ANALYTICS_ERROR", 500)

