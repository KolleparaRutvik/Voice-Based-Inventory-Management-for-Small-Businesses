"""Reorder recommendations routes — AI and rule-based inventory planning."""
from flask import Blueprint
from datetime import datetime, timedelta
from app.utils import require_auth, success_response, error_response, get_current_shop_id
from app.utils.supabase_client import get_supabase

reorder_bp = Blueprint('reorder', __name__)


@reorder_bp.route('/recommendations', methods=['GET'])
@require_auth
def get_reorder_recommendations():
    """Calculate intelligent reorder recommendations based on live stock and sales velocity."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)

    try:
        supabase = get_supabase()

        # 1. Fetch live products, inventory, and suppliers
        prods_res = supabase.table('products').select('*').eq('shop_id', shop_id).eq('is_active', True).execute()
        inv_res = supabase.table('inventory').select('*').eq('shop_id', shop_id).execute()
        suppliers_res = supabase.table('suppliers').select('*').eq('shop_id', shop_id).execute()

        products = prods_res.data or []
        inv_map = {i['product_id']: i for i in (inv_res.data or [])}
        supplier_map = {s['id']: s for s in (suppliers_res.data or [])}

        # 2. Fetch past 30 days sales transactions to compute sales velocity
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        tx_res = supabase.table('transactions').select('product_id, quantity, unit, transaction_type').eq('shop_id', shop_id).gte('created_at', thirty_days_ago).execute()

        sales_by_product = {}
        for tx in (tx_res.data or []):
            if tx.get('transaction_type') in ('SALE', 'STOCK_OUT'):
                pid = tx['product_id']
                sales_by_product[pid] = sales_by_product.get(pid, 0) + float(tx.get('quantity', 0))

        recommendations = []
        for p in products:
            pid = p['id']
            inv = inv_map.get(pid, {})
            current_stock = float(inv.get('current_stock', 0))
            min_stock = float(p.get('minimum_stock', 0))
            rec_stock = float(p.get('recommended_stock', 0)) or (min_stock * 2)
            reorder_qty = float(p.get('reorder_quantity', 0)) or min_stock
            base_unit = p.get('base_unit', 'kg')
            purchase_unit = p.get('purchase_unit', base_unit)
            conv_factor = float(p.get('conversion_factor', 1)) or 1

            total_sold_30d = sales_by_product.get(pid, 0)
            avg_daily_sales = round(total_sold_30d / 30.0, 2)

            # Days of inventory remaining
            days_remaining = round(current_stock / avg_daily_sales, 1) if avg_daily_sales > 0 else 999

            needs_reorder = False
            urgency = 'NORMAL'
            reason = ''

            if current_stock <= min_stock:
                needs_reorder = True
                urgency = 'HIGH' if current_stock <= (min_stock * 0.5) else 'MEDIUM'
                reason = f"Current stock ({current_stock} {base_unit}) is at or below minimum safety limit ({min_stock} {base_unit})."
            elif days_remaining <= 7:
                needs_reorder = True
                urgency = 'HIGH' if days_remaining <= 3 else 'MEDIUM'
                reason = f"At average sales velocity ({avg_daily_sales} {base_unit}/day), stock will deplete in {days_remaining} days."

            if needs_reorder:
                # Calculate recommended quantity
                deficit = max(rec_stock - current_stock, reorder_qty)
                # Convert to purchase units
                qty_in_purchase_unit = round(deficit / conv_factor, 1) if conv_factor > 1 else round(deficit, 0)
                if qty_in_purchase_unit <= 0:
                    qty_in_purchase_unit = 1

                supplier = supplier_map.get(p.get('supplier_id'), {})

                recommendations.append({
                    'product_id': pid,
                    'product_name': p['name'],
                    'local_name': p.get('local_name'),
                    'category': p.get('category'),
                    'current_stock': current_stock,
                    'base_unit': base_unit,
                    'purchase_unit': purchase_unit,
                    'conversion_factor': conv_factor,
                    'minimum_stock': min_stock,
                    'recommended_stock': rec_stock,
                    'recommended_quantity': qty_in_purchase_unit,
                    'recommended_quantity_base': deficit,
                    'estimated_cost': round(qty_in_purchase_unit * float(p.get('purchase_price', 0)), 2),
                    'urgency': urgency,
                    'days_remaining': days_remaining if days_remaining != 999 else None,
                    'avg_daily_sales': avg_daily_sales,
                    'reason': reason,
                    'supplier_id': p.get('supplier_id'),
                    'supplier_name': supplier.get('name', 'Local Wholesaler'),
                    'supplier_phone': supplier.get('phone'),
                })

        # Sort recommendations by urgency: HIGH -> MEDIUM -> NORMAL
        urgency_order = {'HIGH': 0, 'MEDIUM': 1, 'NORMAL': 2}
        recommendations.sort(key=lambda x: (urgency_order.get(x['urgency'], 3), x['current_stock']))

        return success_response({
            'items': recommendations,
            'total': len(recommendations),
            'generated_at': datetime.utcnow().isoformat()
        })

    except Exception as e:
        return error_response(f"Failed to generate reorder recommendations: {str(e)}", "REORDER_ERROR", 500)
