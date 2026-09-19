"""Notifications routes."""
from flask import Blueprint
from app.utils import require_auth, success_response, error_response, get_current_shop_id
from app.utils.supabase_client import get_supabase

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('', methods=['GET'])
@require_auth
def list_notifications():
    shop_id = get_current_shop_id()
    try:
        supabase = get_supabase()
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
