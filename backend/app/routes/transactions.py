"""Transaction routes — view transaction history."""
from flask import Blueprint, request
from app.utils import require_auth, success_response, error_response, get_current_shop_id
from app.utils.supabase_client import get_supabase

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('', methods=['GET'])
@require_auth
def list_transactions():
    """List transactions with optional filters."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)
    
    tx_type = request.args.get('type', '')
    product_id = request.args.get('product_id', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    try:
        supabase = get_supabase()
        query = supabase.table('transactions').select('*').eq('shop_id', shop_id).order('created_at', desc=True)
        
        if tx_type:
            query = query.eq('transaction_type', tx_type)
        if product_id:
            query = query.eq('product_id', product_id)
        
        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)
        
        result = query.execute()
        transactions = result.data or []
        
        # Get product names
        product_ids = list(set(t['product_id'] for t in transactions if t.get('product_id')))
        if product_ids:
            prods = supabase.table('products').select('id, name, category').in_('id', product_ids).execute()
            prod_map = {p['id']: p for p in (prods.data or [])}
            for tx in transactions:
                prod = prod_map.get(tx.get('product_id'), {})
                tx['product_name'] = prod.get('name', 'Unknown')
                tx['product_category'] = prod.get('category', '')
        
        # Get customer names for borrow transactions
        customer_ids = [t['customer_id'] for t in transactions if t.get('customer_id')]
        if customer_ids:
            custs = supabase.table('customers').select('id, name').in_('id', customer_ids).execute()
            cust_map = {c['id']: c['name'] for c in (custs.data or [])}
            for tx in transactions:
                if tx.get('customer_id'):
                    tx['customer_name'] = cust_map.get(tx['customer_id'], '')
        
        return success_response({"items": transactions, "total": len(transactions), "page": page})
        
    except Exception as e:
        return error_response(f"Failed to fetch transactions: {str(e)}", "FETCH_ERROR", 500)


@transactions_bp.route('/<transaction_id>', methods=['GET'])
@require_auth
def get_transaction(transaction_id):
    """Get a single transaction."""
    shop_id = get_current_shop_id()
    
    try:
        supabase = get_supabase()
        result = supabase.table('transactions').select('*').eq('id', transaction_id).eq('shop_id', shop_id).single().execute()
        
        if not result.data:
            return error_response("Transaction not found", "NOT_FOUND", 404)
        
        return success_response(result.data)
        
    except Exception as e:
        return error_response(f"Failed to fetch transaction: {str(e)}", "FETCH_ERROR", 500)
