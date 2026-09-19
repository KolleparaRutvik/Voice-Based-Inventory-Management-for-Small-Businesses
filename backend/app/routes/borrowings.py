"""Borrowings routes — create borrowing, return items."""
from flask import Blueprint, request
from app.utils import require_auth, success_response, error_response, get_current_shop_id, get_current_user_id
from app.utils.supabase_client import get_supabase

borrowings_bp = Blueprint('borrowings', __name__)


@borrowings_bp.route('', methods=['GET'])
@require_auth
def list_borrowings():
    shop_id = get_current_shop_id()
    status = request.args.get('status', '')
    try:
        supabase = get_supabase()
        query = supabase.table('borrowings').select('*').eq('shop_id', shop_id).order('created_at', desc=True)
        if status:
            query = query.eq('status', status)
        result = query.execute()
        return success_response({"items": result.data or []})
    except Exception as e:
        return error_response(str(e), "FETCH_ERROR", 500)


@borrowings_bp.route('', methods=['POST'])
@require_auth
def create_borrowing():
    shop_id = get_current_shop_id()
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or not data.get('customer_name'):
        return error_response("Customer name is required", "VALIDATION_ERROR")
    
    items = data.get('items') or []
    direct_amount = float(data.get('amount') or data.get('total_value') or 0)
    
    if not items and direct_amount <= 0:
        return error_response("Either borrowing items or a borrowing amount is required", "VALIDATION_ERROR")
    
    try:
        supabase = get_supabase()
        
        # Create or find customer
        customer_name = data['customer_name']
        customer_id = data.get('customer_id')
        cust = None
        if customer_id:
            cust = supabase.table('customers').select('*').eq('shop_id', shop_id).eq('id', customer_id).limit(1).execute()
        if not cust or not cust.data:
            cust = supabase.table('customers').select('*').eq('shop_id', shop_id).ilike('name', customer_name).limit(1).execute()
        
        if cust.data and len(cust.data) > 0:
            customer_id = cust.data[0]['id']
            cust_record = cust.data[0]
        else:
            new_cust = supabase.table('customers').insert({
                'shop_id': shop_id,
                'name': customer_name,
                'phone': data.get('customer_phone', ''),
            }).execute()
            customer_id = new_cust.data[0]['id']
            cust_record = new_cust.data[0]
        
        # Create borrowing
        total_value = direct_amount if not items else 0
        borrowing = supabase.table('borrowings').insert({
            'shop_id': shop_id,
            'customer_id': customer_id,
            'customer_name': customer_name,
            'status': 'ACTIVE',
            'total_value': total_value,
            'remaining_balance': total_value,
            'due_date': data.get('due_date'),
            'notes': data.get('notes', 'Udhar credit entry'),
            'created_by': user_id,
        }).execute()
        
        borrowing_id = borrowing.data[0]['id']
        
        # Process items if present
        if items:
            total_value = 0
            for item in items:
                prod = supabase.table('products').select('*').eq('id', item['product_id']).eq('shop_id', shop_id).single().execute()
                if not prod.data:
                    continue
                
                product = prod.data
                quantity = float(item['quantity'])
                unit = item.get('unit', product['selling_unit'])
                price = float(item.get('price', product.get('selling_price', 0)))
                item_total = quantity * price
                total_value += item_total
                
                # Create borrowing item
                supabase.table('borrowing_items').insert({
                    'borrowing_id': borrowing_id,
                    'shop_id': shop_id,
                    'product_id': item['product_id'],
                    'quantity': quantity,
                    'unit': unit,
                    'price': price,
                    'total_amount': item_total,
                }).execute()
                
                # Convert to base units and update inventory
                if unit == product['base_unit']:
                    quantity_base = quantity
                elif unit == product['purchase_unit']:
                    quantity_base = quantity * product.get('conversion_factor', 1)
                else:
                    quantity_base = quantity
                
                inv = supabase.table('inventory').select('*').eq('product_id', item['product_id']).eq('shop_id', shop_id).execute()
                if inv.data:
                    new_stock = max(0, inv.data[0]['current_stock'] - quantity_base)
                    supabase.table('inventory').update({'current_stock': new_stock}).eq('id', inv.data[0]['id']).execute()
                
                # Create BORROW_OUT transaction
                supabase.table('transactions').insert({
                    'shop_id': shop_id,
                    'product_id': item['product_id'],
                    'transaction_type': 'BORROW_OUT',
                    'quantity': quantity,
                    'unit': unit,
                    'quantity_in_base_unit': quantity_base,
                    'price': price,
                    'total_amount': item_total,
                    'customer_id': customer_id,
                    'borrowing_id': borrowing_id,
                    'voice_conversation_id': data.get('voice_conversation_id'),
                    'source': data.get('source', 'manual'),
                    'created_by': user_id,
                }).execute()
        else:
            # Create a general BORROW_OUT monetary transaction entry
            supabase.table('transactions').insert({
                'shop_id': shop_id,
                'transaction_type': 'BORROW_OUT',
                'quantity': 1,
                'unit': 'credit',
                'price': total_value,
                'total_amount': total_value,
                'customer_id': customer_id,
                'borrowing_id': borrowing_id,
                'voice_conversation_id': data.get('voice_conversation_id'),
                'source': data.get('source', 'voice'),
                'notes': data.get('notes', f'Direct udhar for {customer_name}'),
                'created_by': user_id,
            }).execute()
        
        # Update borrowing totals
        supabase.table('borrowings').update({
            'total_value': total_value,
            'remaining_balance': total_value,
        }).eq('id', borrowing_id).execute()
        
        # Update customer credit balance
        old_credit = float(cust_record.get('total_credit') or 0)
        new_credit = old_credit + total_value
        supabase.table('customers').update({
            'total_credit': new_credit,
        }).eq('id', customer_id).execute()

        # Insert customer credit ledger entry
        try:
            supabase.table('customer_credit').insert({
                'shop_id': shop_id,
                'customer_id': customer_id,
                'credit_type': 'BORROW',
                'amount': total_value,
                'running_balance': new_credit,
                'reference_id': borrowing_id,
                'notes': data.get('notes', 'Udhar credit'),
                'created_by': user_id,
            }).execute()
        except Exception:
            pass
        
        return success_response({
            'borrowing_id': borrowing_id,
            'customer_id': customer_id,
            'customer_name': customer_name,
            'total_value': total_value,
            'remaining_balance': total_value,
            'message': f'Udhar of ₹{total_value} recorded for {customer_name}',
        }, 201)
        
    except Exception as e:
        return error_response(f"Failed to create borrowing: {str(e)}", "CREATE_ERROR", 500)


@borrowings_bp.route('/<borrowing_id>/return', methods=['POST'])
@require_auth
def return_borrowing(borrowing_id):
    """Process a borrowing return."""
    shop_id = get_current_shop_id()
    user_id = get_current_user_id()
    data = request.get_json()
    
    try:
        supabase = get_supabase()
        
        borrowing = supabase.table('borrowings').select('*').eq('id', borrowing_id).eq('shop_id', shop_id).single().execute()
        if not borrowing.data:
            return error_response("Borrowing not found", "NOT_FOUND", 404)
        
        borrow = borrowing.data
        
        for item in (data.get('items', [])):
            # Update borrowing item
            bi = supabase.table('borrowing_items').select('*').eq('id', item['borrowing_item_id']).single().execute()
            if not bi.data:
                continue
            
            return_qty = float(item['return_quantity'])
            new_returned = bi.data['returned_quantity'] + return_qty
            
            status = 'RETURNED' if new_returned >= bi.data['quantity'] else 'PARTIALLY_RETURNED'
            supabase.table('borrowing_items').update({
                'returned_quantity': new_returned,
                'status': status,
            }).eq('id', item['borrowing_item_id']).execute()
            
            # Return to inventory
            prod = supabase.table('products').select('*').eq('id', bi.data['product_id']).single().execute()
            if prod.data:
                product = prod.data
                if bi.data['unit'] == product['base_unit']:
                    qty_base = return_qty
                elif bi.data['unit'] == product['purchase_unit']:
                    qty_base = return_qty * product.get('conversion_factor', 1)
                else:
                    qty_base = return_qty
                
                inv = supabase.table('inventory').select('*').eq('product_id', bi.data['product_id']).eq('shop_id', shop_id).execute()
                if inv.data:
                    supabase.table('inventory').update({
                        'current_stock': inv.data[0]['current_stock'] + qty_base,
                    }).eq('id', inv.data[0]['id']).execute()
            
            # Create BORROW_RETURN transaction
            supabase.table('transactions').insert({
                'shop_id': shop_id,
                'product_id': bi.data['product_id'],
                'transaction_type': 'BORROW_RETURN',
                'quantity': return_qty,
                'unit': bi.data['unit'],
                'borrowing_id': borrowing_id,
                'customer_id': borrow['customer_id'],
                'source': 'manual',
                'created_by': user_id,
            }).execute()
        
        # Check if all items returned
        all_items = supabase.table('borrowing_items').select('*').eq('borrowing_id', borrowing_id).execute()
        all_returned = all(i['returned_quantity'] >= i['quantity'] for i in (all_items.data or []))
        
        new_status = 'RETURNED' if all_returned else 'PARTIALLY_RETURNED'
        supabase.table('borrowings').update({'status': new_status}).eq('id', borrowing_id).execute()
        
        return success_response({'message': 'Return processed', 'status': new_status})
        
    except Exception as e:
        return error_response(f"Failed to process return: {str(e)}", "RETURN_ERROR", 500)


@borrowings_bp.route('/<borrowing_id>/payment', methods=['POST'])
@require_auth
def record_payment(borrowing_id):
    """Record a cash payment against a borrowing balance."""
    shop_id = get_current_shop_id()
    user_id = get_current_user_id()
    data = request.get_json()

    if not data or not data.get('amount'):
        return error_response("Payment amount is required", "VALIDATION_ERROR")

    amount = float(data['amount'])
    if amount <= 0:
        return error_response("Payment amount must be positive", "VALIDATION_ERROR")

    try:
        supabase = get_supabase()

        borrowing = supabase.table('borrowings').select('*').eq('id', borrowing_id).eq('shop_id', shop_id).single().execute()
        if not borrowing.data:
            return error_response("Borrowing not found", "NOT_FOUND", 404)

        borrow = borrowing.data
        old_balance = float(borrow.get('remaining_balance') or borrow.get('total_value', 0))
        old_paid = float(borrow.get('paid_amount', 0))

        new_paid = old_paid + amount
        new_balance = max(0, old_balance - amount)
        new_status = 'RETURNED' if new_balance <= 0 else borrow['status']

        supabase.table('borrowings').update({
            'paid_amount': new_paid,
            'remaining_balance': new_balance,
            'status': new_status,
        }).eq('id', borrowing_id).execute()

        # Record in customer_credit ledger
        supabase.table('customer_credit').insert({
            'shop_id': shop_id,
            'customer_id': borrow['customer_id'],
            'credit_type': 'PAYMENT',
            'amount': amount,
            'running_balance': new_balance,
            'reference_id': borrowing_id,
            'notes': data.get('notes', f'Cash payment of ₹{amount}'),
            'created_by': user_id,
        }).execute()

        # Update customer total_credit
        cust = supabase.table('customers').select('total_credit').eq('id', borrow['customer_id']).single().execute()
        if cust.data:
            new_total = max(0, float(cust.data.get('total_credit', 0)) - amount)
            supabase.table('customers').update({'total_credit': new_total}).eq('id', borrow['customer_id']).execute()

        return success_response({
            'message': f'Payment of ₹{amount} recorded',
            'remaining_balance': new_balance,
            'status': new_status,
        })

    except Exception as e:
        return error_response(f"Failed to record payment: {str(e)}", "PAYMENT_ERROR", 500)
