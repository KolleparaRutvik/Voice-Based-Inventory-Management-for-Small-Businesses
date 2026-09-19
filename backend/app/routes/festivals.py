"""Festival routes — Endpoints for upcoming festival calendar, demand surge analysis,
15-day prior notifications sync, and 1-click purchase order generation.
"""
import time
import logging
from flask import Blueprint, request
from app.utils import require_auth, success_response, error_response, get_current_shop_id, get_current_user_id
from app.utils.supabase_client import get_supabase
from app.services.festival_service import (
    get_upcoming_festivals,
    analyze_festival_demand,
    sync_festival_notifications
)

logger = logging.getLogger(__name__)

festivals_bp = Blueprint('festivals', __name__)


@festivals_bp.route('/upcoming', methods=['GET'])
@require_auth
def list_upcoming_festivals():
    """Lists upcoming Indian festivals with days remaining and 15-day prior notice window status."""
    try:
        window_days = int(request.args.get('window_days', 15))
        ref_date = request.args.get('reference_date')
        festivals = get_upcoming_festivals(window_days=window_days, reference_date=ref_date)
        return success_response({'items': festivals})
    except Exception as e:
        logger.error(f"Error fetching upcoming festivals: {e}")
        return error_response(str(e), "FETCH_ERROR", 500)


@festivals_bp.route('/recommendations', methods=['GET'])
@require_auth
def get_festival_recommendations():
    """Calculates festival demand surge gap analysis against live shop inventory."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)

    try:
        festival_name = request.args.get('festival')
        window_days = int(request.args.get('window_days', 15))
        ref_date = request.args.get('reference_date')

        analysis = analyze_festival_demand(
            shop_id=shop_id,
            festival_name=festival_name,
            window_days=window_days,
            reference_date=ref_date
        )
        return success_response(analysis)
    except Exception as e:
        logger.error(f"Error computing festival recommendations: {e}")
        return error_response(str(e), "ANALYSIS_ERROR", 500)


@festivals_bp.route('/sync-notifications', methods=['POST'])
@require_auth
def sync_notifications():
    """Explicitly triggers festival notification synchronization for festivals in 15-day window."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)

    try:
        data = request.get_json(silent=True) or {}
        ref_date = data.get('reference_date')
        result = sync_festival_notifications(shop_id=shop_id, reference_date=ref_date)
        return success_response(result)
    except Exception as e:
        logger.error(f"Error syncing festival notifications: {e}")
        return error_response(str(e), "SYNC_ERROR", 500)


@festivals_bp.route('/create-po', methods=['POST'])
@require_auth
def create_festival_po():
    """1-Click creation of a purchase order for festival deficit items."""
    shop_id = get_current_shop_id()
    user_id = get_current_user_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)

    data = request.get_json()
    if not data or not data.get('items'):
        return error_response("Items list is required to generate purchase order", "VALIDATION_ERROR", 400)

    festival_name = data.get('festival_name', 'Upcoming Festival')
    items = data['items']

    try:
        supabase = get_supabase()

        # Find or select supplier
        supplier_id = data.get('supplier_id')
        if not supplier_id:
            supp_res = supabase.table('suppliers').select('id').eq('shop_id', shop_id).limit(1).execute()
            if supp_res.data:
                supplier_id = supp_res.data[0]['id']

        if not supplier_id:
            return error_response("No supplier available for this shop", "SUPPLIER_NOT_FOUND", 400)

        # Calculate totals
        total_amount = sum(float(it.get('quantity', 0)) * float(it.get('unit_price', 0)) for it in items)
        po_number = f"PO-FEST-{int(time.time())}"

        # Insert PO
        po_res = supabase.table('purchase_orders').insert({
            'shop_id': shop_id,
            'supplier_id': supplier_id,
            'order_number': po_number,
            'total_amount': total_amount,
            'status': 'PENDING',
            'notes': f"Festival demand auto-order for {festival_name}. Recommended prior to festival rush.",
            'created_by': user_id
        }).execute()

        if not po_res.data:
            raise Exception("Failed to insert purchase order into database")

        po_id = po_res.data[0]['id']

        # Insert PO items
        for it in items:
            supabase.table('purchase_order_items').insert({
                'order_id': po_id,
                'product_id': it.get('product_id'),
                'quantity': float(it.get('quantity', 1)),
                'unit_price': float(it.get('unit_price', 0)),
                'total_price': float(it.get('quantity', 1)) * float(it.get('unit_price', 0))
            }).execute()

        # Add an audit / notification log
        supabase.table('notifications').insert({
            'shop_id': shop_id,
            'type': 'ORDER_CREATED',
            'title': f"📦 Festival Purchase Order Created ({po_number})",
            'message': f"Generated purchase order of ₹{total_amount:,.2f} for {len(items)} items ahead of {festival_name}.",
            'data': {'po_id': po_id, 'po_number': po_number, 'festival': festival_name},
            'is_read': False
        }).execute()

        return success_response({
            'message': f"Purchase order {po_number} created successfully for {festival_name}!",
            'po_id': po_id,
            'po_number': po_number,
            'total_amount': total_amount,
            'items_count': len(items)
        })

    except Exception as e:
        logger.error(f"Failed to create festival PO: {e}")
        return error_response(f"PO creation failed: {str(e)}", "PO_ERROR", 500)
