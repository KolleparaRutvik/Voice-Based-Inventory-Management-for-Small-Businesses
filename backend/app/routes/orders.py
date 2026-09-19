"""Purchase Orders routes — management, creation, tracking, and PDF generation."""
import io
from datetime import datetime
from flask import Blueprint, request, send_file
from app.utils import require_auth, success_response, error_response, get_current_shop_id, get_current_user_id
from app.utils.supabase_client import get_supabase

# ReportLab imports for professional PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('', methods=['GET'])
@require_auth
def list_purchase_orders():
    """List all purchase orders for the shop with supplier details."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)

    try:
        supabase = get_supabase()

        # Fetch orders
        orders_res = supabase.table('purchase_orders').select('*').eq('shop_id', shop_id).order('created_at', desc=True).execute()
        orders = orders_res.data or []

        # Fetch suppliers for mapping
        suppliers_res = supabase.table('suppliers').select('id, name, phone').eq('shop_id', shop_id).execute()
        suppliers_map = {s['id']: s for s in (suppliers_res.data or [])}

        results = []
        for o in orders:
            supp = suppliers_map.get(o.get('supplier_id'), {})
            results.append({
                'id': o['id'],
                'order_number': o.get('order_number') or f"PO-{o['id'][:8].upper()}",
                'supplier_id': o.get('supplier_id'),
                'supplier_name': supp.get('name', 'Direct Supplier'),
                'supplier_phone': supp.get('phone', ''),
                'status': o.get('status', 'DRAFT'),
                'subtotal': float(o.get('subtotal', 0)),
                'tax_amount': float(o.get('tax_amount', 0)),
                'total_amount': float(o.get('total_amount', 0)),
                'notes': o.get('notes'),
                'expected_date': o.get('expected_date'),
                'created_at': o.get('created_at'),
            })

        return success_response({'items': results, 'total': len(results)})

    except Exception as e:
        return error_response(f"Failed to fetch purchase orders: {str(e)}", "FETCH_ERROR", 500)


@orders_bp.route('', methods=['POST'])
@require_auth
def create_purchase_order():
    """Create a new purchase order with line items."""
    shop_id = get_current_shop_id()
    user_id = get_current_user_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)

    data = request.get_json()
    if not data or not data.get('supplier_id'):
        return error_response("Supplier is required", "VALIDATION_ERROR")

    try:
        supabase = get_supabase()

        # Generate readable order number
        order_num = f"PO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        items = data.get('items', [])
        # Support single item shorthand from simple form
        if not items and data.get('product_id'):
            items = [{
                'product_id': data['product_id'],
                'quantity': float(data.get('quantity', 1)),
                'unit': data.get('unit', 'unit'),
                'unit_price': float(data.get('unit_price', 0)),
                'total_price': float(data.get('quantity', 1)) * float(data.get('unit_price', 0))
            }]

        subtotal = sum(float(item.get('total_price', float(item.get('quantity', 1)) * float(item.get('unit_price', 0)))) for item in items)
        tax_rate = float(data.get('tax_rate', 0))
        tax_amount = round(subtotal * (tax_rate / 100), 2)
        total_amount = round(subtotal + tax_amount, 2)

        order_record = {
            'shop_id': shop_id,
            'supplier_id': data['supplier_id'],
            'order_number': data.get('order_number') or order_num,
            'status': data.get('status', 'SENT'),
            'subtotal': subtotal,
            'tax_rate': tax_rate,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'notes': data.get('notes', ''),
            'created_by': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        order_res = supabase.table('purchase_orders').insert(order_record).execute()
        if not order_res.data:
            return error_response("Failed to create purchase order", "INSERT_ERROR", 500)

        created_order = order_res.data[0]
        order_id = created_order['id']

        # Insert line items if any
        if items:
            items_to_insert = []
            for it in items:
                items_to_insert.append({
                    'purchase_order_id': order_id,
                    'product_id': it['product_id'],
                    'quantity': float(it.get('quantity', 1)),
                    'unit': it.get('unit', 'unit'),
                    'unit_price': float(it.get('unit_price', 0)),
                    'total_price': float(it.get('total_price', float(it.get('quantity', 1)) * float(it.get('unit_price', 0)))),
                    'created_at': datetime.utcnow().isoformat()
                })
            supabase.table('purchase_order_items').insert(items_to_insert).execute()

        return success_response(created_order, 201)

    except Exception as e:
        return error_response(f"Failed to create purchase order: {str(e)}", "CREATE_ERROR", 500)


@orders_bp.route('/<order_id>', methods=['GET'])
@require_auth
def get_purchase_order(order_id):
    """Get single purchase order details with line items and supplier info."""
    shop_id = get_current_shop_id()
    try:
        supabase = get_supabase()

        order_res = supabase.table('purchase_orders').select('*').eq('id', order_id).eq('shop_id', shop_id).single().execute()
        if not order_res.data:
            return error_response("Purchase order not found", "NOT_FOUND", 404)

        order = order_res.data

        # Fetch supplier
        supp_res = supabase.table('suppliers').select('*').eq('id', order['supplier_id']).single().execute()
        order['supplier'] = supp_res.data if supp_res.data else {}

        # Fetch line items with product names
        items_res = supabase.table('purchase_order_items').select('*').eq('purchase_order_id', order_id).execute()
        items = items_res.data or []

        if items:
            pids = [it['product_id'] for it in items]
            prods_res = supabase.table('products').select('id, name, local_name, sku').in_('id', pids).execute()
            prod_map = {p['id']: p for p in (prods_res.data or [])}
            for it in items:
                it['product'] = prod_map.get(it['product_id'], {})

        order['items'] = items
        return success_response(order)

    except Exception as e:
        return error_response(f"Failed to fetch order: {str(e)}", "FETCH_ERROR", 500)


@orders_bp.route('/<order_id>/status', methods=['PUT'])
@require_auth
def update_order_status(order_id):
    """Update order status (e.g., to RECEIVED and optionally restock inventory)."""
    shop_id = get_current_shop_id()
    data = request.get_json() or {}
    new_status = data.get('status')
    if not new_status:
        return error_response("Status is required", "VALIDATION_ERROR")

    try:
        supabase = get_supabase()

        # Update order status
        update_data = {
            'status': new_status,
            'updated_at': datetime.utcnow().isoformat()
        }
        if new_status == 'RECEIVED':
            update_data['received_date'] = datetime.utcnow().isoformat()

        res = supabase.table('purchase_orders').update(update_data).eq('id', order_id).eq('shop_id', shop_id).execute()

        # If RECEIVED, increment inventory for each line item
        if new_status == 'RECEIVED':
            items_res = supabase.table('purchase_order_items').select('*').eq('purchase_order_id', order_id).execute()
            for it in (items_res.data or []):
                pid = it['product_id']
                qty = float(it['quantity'])

                # Fetch current inventory
                inv_res = supabase.table('inventory').select('*').eq('shop_id', shop_id).eq('product_id', pid).single().execute()
                if inv_res.data:
                    new_curr = float(inv_res.data.get('current_stock', 0)) + qty
                    supabase.table('inventory').update({
                        'current_stock': new_curr,
                        'last_restocked_at': datetime.utcnow().isoformat(),
                        'updated_at': datetime.utcnow().isoformat()
                    }).eq('id', inv_res.data['id']).execute()

        return success_response(res.data[0] if res.data else None)

    except Exception as e:
        return error_response(f"Failed to update order status: {str(e)}", "UPDATE_ERROR", 500)


@orders_bp.route('/<order_id>/pdf', methods=['GET'])
@require_auth
def export_purchase_order_pdf(order_id):
    """Generate and return a clean PDF purchase order / invoice using ReportLab."""
    shop_id = get_current_shop_id()
    try:
        supabase = get_supabase()

        order_res = supabase.table('purchase_orders').select('*').eq('id', order_id).eq('shop_id', shop_id).single().execute()
        if not order_res.data:
            return error_response("Purchase order not found", "NOT_FOUND", 404)

        order = order_res.data
        shop_res = supabase.table('shop_details').select('*').limit(1).maybe_single().execute()
        shop = shop_res.data or {'name': 'DukaanSetu Store', 'phone': '', 'address': ''}

        supp_res = supabase.table('suppliers').select('*').eq('id', order['supplier_id']).single().execute()
        supplier = supp_res.data or {'name': 'Supplier', 'phone': '', 'address': ''}

        items_res = supabase.table('purchase_order_items').select('*').eq('purchase_order_id', order_id).execute()
        items = items_res.data or []

        pids = [it['product_id'] for it in items]
        prod_map = {}
        if pids:
            prods_res = supabase.table('products').select('id, name, local_name').in_('id', pids).execute()
            prod_map = {p['id']: p for p in (prods_res.data or [])}

        # Build PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#4B5563'),
            spaceAfter=15
        )

        bold_style = ParagraphStyle(
            'BoldStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.HexColor('#111827')
        )

        normal_style = ParagraphStyle(
            'NormStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#374151')
        )

        # Header Title
        elements.append(Paragraph("DUKAANSETU", title_style))
        elements.append(Paragraph("Purchase Order & Goods Requisition", subtitle_style))
        elements.append(Spacer(1, 10))

        # Metadata grid: Shop Details vs Order & Supplier Details
        shop_info = f"<b>{shop.get('name', 'DukaanSetu Store')}</b><br/>"
        if shop.get('address'):
            shop_info += f"{shop.get('address')}<br/>"
        if shop.get('phone'):
            shop_info += f"Phone: {shop.get('phone')}<br/>"
        if shop.get('gst_number'):
            shop_info += f"GSTIN: {shop.get('gst_number')}<br/>"

        order_info = f"<b>Order #:</b> {order.get('order_number') or order['id'][:8]}<br/>"
        order_info += f"<b>Date:</b> {order.get('created_at', '')[:10]}<br/>"
        order_info += f"<b>Status:</b> {order.get('status', 'DRAFT')}<br/>"
        order_info += f"<b>Supplier:</b> {supplier.get('name', '')}<br/>"
        if supplier.get('phone'):
            order_info += f"Supplier Phone: {supplier.get('phone')}<br/>"

        meta_table = Table(
            [[Paragraph(shop_info, normal_style), Paragraph(order_info, normal_style)]],
            colWidths=[270, 270]
        )
        meta_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 20))

        # Line items table
        table_data = [
            [
                Paragraph("<b>Item / Product</b>", bold_style),
                Paragraph("<b>Quantity</b>", bold_style),
                Paragraph("<b>Unit Price (₹)</b>", bold_style),
                Paragraph("<b>Total (₹)</b>", bold_style)
            ]
        ]

        if not items:
            table_data.append([
                Paragraph("General Inventory Restock", normal_style),
                Paragraph("1 batch", normal_style),
                Paragraph(f"₹{order.get('total_amount', 0):.2f}", normal_style),
                Paragraph(f"₹{order.get('total_amount', 0):.2f}", normal_style)
            ])
        else:
            for it in items:
                pinfo = prod_map.get(it['product_id'], {})
                pname = pinfo.get('name', 'Product')
                if pinfo.get('local_name'):
                    pname += f" ({pinfo.get('local_name')})"

                table_data.append([
                    Paragraph(pname, normal_style),
                    Paragraph(f"{it.get('quantity', 0)} {it.get('unit', '')}", normal_style),
                    Paragraph(f"₹{float(it.get('unit_price', 0)):.2f}", normal_style),
                    Paragraph(f"₹{float(it.get('total_price', 0)):.2f}", normal_style)
                ])

        # Subtotal, Tax, and Grand Total rows
        subtotal = float(order.get('subtotal', order.get('total_amount', 0)))
        tax = float(order.get('tax_amount', 0))
        total = float(order.get('total_amount', 0))

        table_data.append([
            Paragraph("", normal_style),
            Paragraph("", normal_style),
            Paragraph("<b>Subtotal:</b>", bold_style),
            Paragraph(f"₹{subtotal:.2f}", normal_style)
        ])
        if tax > 0:
            table_data.append([
                Paragraph("", normal_style),
                Paragraph("", normal_style),
                Paragraph(f"<b>Tax:</b>", bold_style),
                Paragraph(f"₹{tax:.2f}", normal_style)
            ])
        table_data.append([
            Paragraph("", normal_style),
            Paragraph("", normal_style),
            Paragraph("<b>Grand Total:</b>", bold_style),
            Paragraph(f"<b>₹{total:.2f}</b>", bold_style)
        ])

        items_table = Table(table_data, colWidths=[240, 100, 100, 100])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E5E7EB')),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, len(items) if items else 1), 0.5, colors.HexColor('#E5E7EB')),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#374151')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#EEF2F6')),
        ]))
        elements.append(items_table)

        if order.get('notes'):
            elements.append(Spacer(1, 15))
            elements.append(Paragraph(f"<b>Notes:</b> {order.get('notes')}", normal_style))

        elements.append(Spacer(1, 30))
        elements.append(Paragraph("<i>This is an electronically generated purchase order from DukaanSetu.</i>", normal_style))

        doc.build(elements)
        buffer.seek(0)

        filename = f"Purchase_Order_{order.get('order_number') or order_id[:8]}.pdf"
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return error_response(f"Failed to generate PDF: {str(e)}", "PDF_ERROR", 500)
