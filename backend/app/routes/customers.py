"""Customer management routes — profiles and customer credit/Udhar tracking."""
from flask import Blueprint, request
from app.utils import require_auth, success_response, error_response, get_current_shop_id
from app.utils.supabase_client import get_supabase

customers_bp = Blueprint('customers', __name__)


@customers_bp.route('', methods=['GET'])
@require_auth
def list_customers():
    """List all customers for the shop with live credit and borrowing statistics."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)

    search = request.args.get('search', '').strip().lower()

    try:
        supabase = get_supabase()

        # Fetch customers
        cust_res = supabase.table('customers').select('*').eq('shop_id', shop_id).order('name').execute()
        customers = cust_res.data or []

        # Fetch active borrowings to compute live balance
        borrow_res = supabase.table('borrowings').select('*').eq('shop_id', shop_id).in_('status', ['ACTIVE', 'PARTIALLY_RETURNED', 'OVERDUE']).execute()
        borrowings = borrow_res.data or []

        # Aggregate balances by customer_id and customer_name
        balance_by_id = {}
        balance_by_name = {}
        active_count_by_id = {}
        for b in borrowings:
            cid = b.get('customer_id')
            cname = (b.get('customer_name') or '').strip().lower()
            bal = float(b.get('remaining_balance') or b.get('total_value') or 0)
            if cid:
                balance_by_id[cid] = balance_by_id.get(cid, 0) + bal
                active_count_by_id[cid] = active_count_by_id.get(cid, 0) + 1
            if cname:
                balance_by_name[cname] = balance_by_name.get(cname, 0) + bal

        results = []
        for c in customers:
            cid = c['id']
            cname = c.get('name', '').strip().lower()
            current_balance = balance_by_id.get(cid) or balance_by_name.get(cname) or float(c.get('credit_balance', 0))

            if search:
                matches_name = search in c.get('name', '').lower()
                matches_phone = search in c.get('phone', '').lower()
                if not (matches_name or matches_phone):
                    continue

            results.append({
                'id': cid,
                'shop_id': c['shop_id'],
                'name': c['name'],
                'phone': c.get('phone'),
                'address': c.get('address'),
                'credit_limit': float(c.get('credit_limit', 5000)),
                'current_balance': round(current_balance, 2),
                'active_borrowings_count': active_count_by_id.get(cid, 1 if current_balance > 0 else 0),
                'is_overdue': any(b.get('status') == 'OVERDUE' for b in borrowings if b.get('customer_id') == cid or (b.get('customer_name') or '').lower() == cname),
                'created_at': c.get('created_at'),
            })

        return success_response({'items': results, 'total': len(results)})

    except Exception as e:
        return error_response(f"Failed to fetch customers: {str(e)}", "FETCH_ERROR", 500)


@customers_bp.route('', methods=['POST'])
@require_auth
def create_customer():
    """Create a new customer profile."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)

    data = request.get_json()
    if not data or not data.get('name'):
        return error_response("Customer name is required", "VALIDATION_ERROR")

    try:
        supabase = get_supabase()

        customer_data = {
            'shop_id': shop_id,
            'name': data['name'].strip(),
            'phone': data.get('phone', '').strip(),
            'address': data.get('address', '').strip(),
            'credit_limit': float(data.get('credit_limit', 5000)),
            'credit_balance': 0,
            'trust_score': float(data.get('trust_score', 100)),
        }

        res = supabase.table('customers').insert(customer_data).execute()
        if res.data and len(res.data) > 0:
            return success_response(res.data[0], 201)
        return error_response("Failed to insert customer", "INSERT_ERROR", 500)

    except Exception as e:
        return error_response(f"Failed to create customer: {str(e)}", "CREATE_ERROR", 500)


@customers_bp.route('/<customer_id>', methods=['GET'])
@require_auth
def get_customer(customer_id):
    """Get single customer profile and full ledger history."""
    shop_id = get_current_shop_id()
    try:
        supabase = get_supabase()
        cust_res = supabase.table('customers').select('*').eq('id', customer_id).eq('shop_id', shop_id).single().execute()
        if not cust_res.data:
            return error_response("Customer not found", "NOT_FOUND", 404)

        customer = cust_res.data

        # Fetch customer borrowings
        borrow_res = supabase.table('borrowings').select('*').eq('shop_id', shop_id).eq('customer_id', customer_id).order('created_at', desc=True).execute()
        customer['borrowings'] = borrow_res.data or []

        return success_response(customer)

    except Exception as e:
        return error_response(f"Failed to fetch customer: {str(e)}", "FETCH_ERROR", 500)


@customers_bp.route('/<customer_id>', methods=['PUT'])
@require_auth
def update_customer(customer_id):
    """Update customer details."""
    shop_id = get_current_shop_id()
    data = request.get_json()
    if not data:
        return error_response("Request body is required", "VALIDATION_ERROR")

    try:
        supabase = get_supabase()
        allowed = ['name', 'phone', 'address', 'credit_limit', 'notes']
        update_data = {k: v for k, v in data.items() if k in allowed}

        res = supabase.table('customers').update(update_data).eq('id', customer_id).eq('shop_id', shop_id).execute()
        return success_response(res.data[0] if res.data else None)

    except Exception as e:
        return error_response(f"Failed to update customer: {str(e)}", "UPDATE_ERROR", 500)
