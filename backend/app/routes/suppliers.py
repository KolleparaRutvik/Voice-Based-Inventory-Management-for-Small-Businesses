"""Supplier routes — CRUD."""
from flask import Blueprint, request
from app.utils import require_auth, success_response, error_response, get_current_shop_id
from app.utils.supabase_client import get_supabase

suppliers_bp = Blueprint('suppliers', __name__)


@suppliers_bp.route('', methods=['GET'])
@require_auth
def list_suppliers():
    shop_id = get_current_shop_id()
    try:
        supabase = get_supabase()
        result = supabase.table('suppliers').select('*').eq('shop_id', shop_id).eq('is_active', True).order('name').execute()
        return success_response({"items": result.data or []})
    except Exception as e:
        return error_response(str(e), "FETCH_ERROR", 500)


@suppliers_bp.route('', methods=['POST'])
@require_auth
def create_supplier():
    shop_id = get_current_shop_id()
    data = request.get_json()
    if not data or not data.get('name'):
        return error_response("Supplier name is required", "VALIDATION_ERROR")
    try:
        supabase = get_supabase()
        result = supabase.table('suppliers').insert({
            'shop_id': shop_id,
            'name': data['name'],
            'phone': data.get('phone', ''),
            'email': data.get('email', ''),
            'address': data.get('address', ''),
            'gst_number': data.get('gst_number', ''),
            'notes': data.get('notes', ''),
        }).execute()
        return success_response(result.data[0] if result.data else None, 201)
    except Exception as e:
        return error_response(str(e), "CREATE_ERROR", 500)


@suppliers_bp.route('/<supplier_id>', methods=['GET'])
@require_auth
def get_supplier(supplier_id):
    shop_id = get_current_shop_id()
    try:
        supabase = get_supabase()
        result = supabase.table('suppliers').select('*').eq('id', supplier_id).eq('shop_id', shop_id).single().execute()
        if not result.data:
            return error_response("Supplier not found", "NOT_FOUND", 404)
        return success_response(result.data)
    except Exception as e:
        return error_response(str(e), "FETCH_ERROR", 500)


@suppliers_bp.route('/<supplier_id>', methods=['PUT'])
@require_auth
def update_supplier(supplier_id):
    shop_id = get_current_shop_id()
    data = request.get_json()
    try:
        supabase = get_supabase()
        allowed = ['name', 'phone', 'email', 'address', 'gst_number', 'notes']
        update_data = {k: v for k, v in data.items() if k in allowed}
        result = supabase.table('suppliers').update(update_data).eq('id', supplier_id).eq('shop_id', shop_id).execute()
        return success_response(result.data[0] if result.data else None)
    except Exception as e:
        return error_response(str(e), "UPDATE_ERROR", 500)


@suppliers_bp.route('/<supplier_id>', methods=['DELETE'])
@require_auth
def delete_supplier(supplier_id):
    shop_id = get_current_shop_id()
    try:
        supabase = get_supabase()
        supabase.table('suppliers').update({'is_active': False}).eq('id', supplier_id).eq('shop_id', shop_id).execute()
        return success_response({"message": "Supplier deactivated"})
    except Exception as e:
        return error_response(str(e), "DELETE_ERROR", 500)
