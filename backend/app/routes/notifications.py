"""Notifications routes."""
from flask import Blueprint
from app.utils import require_auth, success_response, error_response, get_current_shop_id
from app.utils.supabase_client import get_supabase
from app.services.festival_service import sync_festival_notifications
from app.services.trend_alerts import generate_trend_alerts

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/trends', methods=['GET'])
@require_auth
def get_shop_trend_alerts():
    """Get active trend-based stock alerts and demand velocity insights for the current shop."""
    shop_id = get_current_shop_id()
    try:
        alerts = generate_trend_alerts(shop_id)
        return success_response({"alerts": alerts, "count": len(alerts)})
    except Exception as e:
        return error_response(str(e), "TREND_ALERTS_ERROR", 500)


@notifications_bp.route('', methods=['GET'])
@require_auth
def list_notifications():
    shop_id = get_current_shop_id()
    try:
        # Proactively sync festival demand recommendations if within 15-day prior alert window
        try:
            sync_festival_notifications(shop_id=shop_id)
        except Exception:
            pass

        # Proactively sync trend alerts into notifications
        try:
            supabase = get_supabase()
            trend_alerts = generate_trend_alerts(shop_id)
            for t_alert in trend_alerts[:4]:
                t_type = t_alert.get('type', 'TREND_ALERT')
                t_title = t_alert.get('title', 'Trend Alert')
                # Check if this alert title exists recently
                exist = supabase.table('notifications').select('id').eq('shop_id', shop_id).eq('title', t_title).limit(1).execute()
                if not exist.data or len(exist.data) == 0:
                    from datetime import datetime, timezone
                    supabase.table('notifications').insert({
                        'shop_id': shop_id,
                        'type': t_type,
                        'title': t_title,
                        'message': t_alert.get('message', ''),
                        'data': t_alert,
                        'is_read': False,
                        'created_at': datetime.now(timezone.utc).isoformat()
                    }).execute()
        except Exception:
            pass

        supabase = get_supabase()

        # Proactively ensure shop-specific inventory & udhar alerts exist
        try:
            existing = supabase.table('notifications').select('id').eq('shop_id', shop_id).limit(2).execute()
            if not existing.data or len(existing.data) < 2:
                # 1. Check for low stock products
                prods_res = supabase.table('products').select('*').eq('shop_id', shop_id).limit(10).execute()
                inv_res = supabase.table('inventory').select('*').eq('shop_id', shop_id).limit(10).execute()
                inv_map = {i['product_id']: float(i.get('current_stock', 0)) for i in (inv_res.data or [])}

                from datetime import datetime, timezone
                now = datetime.now(timezone.utc).isoformat()

                for p in (prods_res.data or []):
                    c_st = inv_map.get(p['id'], 0)
                    min_st = float(p.get('minimum_stock', 10))
                    if c_st <= min_st * 1.5:
                        supabase.table('notifications').insert({
                            'shop_id': shop_id,
                            'type': 'LOW_STOCK',
                            'title': f"Stock Alert: {p['name']}",
                            'message': f"Current stock ({c_st} {p.get('base_unit', '')}) is near minimum threshold ({min_st} {p.get('base_unit', '')}). Restock recommended!",
                            'data': {'product_name': p['name'], 'current_stock': c_st},
                            'is_read': False,
                            'created_at': now
                        }).execute()
                        break

                # 2. Check for customer udhar
                custs_res = supabase.table('customers').select('*').eq('shop_id', shop_id).gt('total_credit', 0).limit(1).execute()
                if custs_res.data and len(custs_res.data) > 0:
                    cust = custs_res.data[0]
                    supabase.table('notifications').insert({
                        'shop_id': shop_id,
                        'type': 'PAYMENT_REMINDER',
                        'title': f"Udhar Balance: {cust['name']}",
                        'message': f"Customer has a pending credit balance of ₹{cust['total_credit']:,.2f}.",
                        'data': {'customer_name': cust['name'], 'balance': cust['total_credit']},
                        'is_read': False,
                        'created_at': now
                    }).execute()
        except Exception:
            pass

        result = supabase.table('notifications').select('*').eq('shop_id', shop_id).order('created_at', desc=True).limit(50).execute()
        return success_response({"items": result.data or []})
    except Exception as e:
        return error_response(str(e), "FETCH_ERROR", 500)


@notifications_bp.route('/<notification_id>/read', methods=['POST'])
@require_auth
def mark_read(notification_id):
    shop_id = get_current_shop_id()
    try:
        supabase = get_supabase()
        supabase.table('notifications').update({
            'is_read': True,
            'read_at': 'now()',
        }).eq('id', notification_id).eq('shop_id', shop_id).execute()
        return success_response({"message": "Marked as read"})
    except Exception as e:
        return error_response(str(e), "UPDATE_ERROR", 500)
