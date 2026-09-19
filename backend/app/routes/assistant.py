"""DukaanSetu — AI Business & Conversational Assistant (Modes 1, 2, 3).
Handles conversational multi-turn context, demand forecasting, stock inquiries, and 1-click action cards.
Includes multi-model fallback and deterministic database calculation engine.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request
from app.utils import require_auth, success_response, error_response, get_current_shop_id
from app.utils.supabase_client import get_supabase

logger = logging.getLogger(__name__)
assistant_bp = Blueprint('assistant', __name__)

CANDIDATE_MODELS = ['gemini-2.5-flash', 'gemini-3.6-flash']


@assistant_bp.route('/query', methods=['POST'])
@require_auth
def ask_assistant():
    """Answer natural language business & stock questions with multi-turn context and business intelligence."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)

    data = request.get_json()
    if not data or not data.get('question'):
        return error_response("Question is required", "VALIDATION_ERROR")

    question = data['question'].strip()
    history = data.get('conversation_history', [])

    try:
        supabase = get_supabase()

        # 1. Fetch live products & inventory
        prods_res = supabase.table('products').select('*').eq('shop_id', shop_id).eq('is_active', True).execute()
        inv_res = supabase.table('inventory').select('*').eq('shop_id', shop_id).execute()
        inv_map = {i['product_id']: i for i in (inv_res.data or [])}

        catalog_summary = []
        for p in (prods_res.data or []):
            pid = p['id']
            inv = inv_map.get(pid, {})
            current_stock = float(inv.get('current_stock', 0))
            stock_unit = inv.get('stock_unit', p.get('base_unit', 'unit'))
            catalog_summary.append({
                'id': pid,
                'name': p['name'],
                'local_name': p.get('local_name'),
                'category': p.get('category'),
                'current_stock': current_stock,
                'stock_unit': stock_unit,
                'selling_price': float(p.get('selling_price', 0)),
                'purchase_price': float(p.get('purchase_price', 0)),
                'minimum_stock': float(p.get('minimum_stock', 0)),
                'is_low_stock': current_stock <= float(p.get('minimum_stock', 0)),
                'supplier_id': p.get('supplier_id')
            })

        # 2. Fetch past 30 days sales transactions
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        tx_res = supabase.table('transactions').select('product_id, quantity, unit, transaction_type').eq('shop_id', shop_id).gte('created_at', thirty_days_ago).execute()

        sales_velocity_map = {}
        for tx in (tx_res.data or []):
            if tx.get('transaction_type') in ('SALE', 'STOCK_OUT'):
                pid = tx['product_id']
                sales_velocity_map[pid] = sales_velocity_map.get(pid, 0) + float(tx.get('quantity', 0))

        for item in catalog_summary:
            sold_30d = sales_velocity_map.get(item['id'], 0)
            item['sales_last_30_days'] = sold_30d
            item['avg_daily_sales'] = round(sold_30d / 30.0, 2)
            item['days_of_stock_left'] = round(item['current_stock'] / item['avg_daily_sales'], 1) if item['avg_daily_sales'] > 0 else 999

        # 3. Fetch active customer credit / borrowings
        borrow_res = supabase.table('borrowings').select('*').eq('shop_id', shop_id).in_('status', ['ACTIVE', 'PARTIALLY_RETURNED', 'OVERDUE']).execute()
        borrowings_summary = []
        for b in (borrow_res.data or []):
            borrowings_summary.append({
                'customer': b.get('customer_name'),
                'balance_due': float(b.get('remaining_balance') or b.get('total_value') or 0),
                'due_date': b.get('due_date'),
                'is_overdue': b.get('status') == 'OVERDUE'
            })

        # 4. Fetch suppliers
        supp_res = supabase.table('suppliers').select('id, name, phone').eq('shop_id', shop_id).execute()
        suppliers_summary = supp_res.data or []

        # 5. Build prompt tailored to shop type
        shop_type = (getattr(g, 'shop', {}) or {}).get('type', 'kirana')
        shop_name = (getattr(g, 'shop', {}) or {}).get('name', 'DukaanSetu Store')
        if shop_type == 'jewellery':
            advisor_role = f"an expert Jewellery & Gold Bullion AI business advisor for '{shop_name}'. You advise on gold rates, gram-level margins, bridal bookings, and customer gold loans."
        elif shop_type == 'flowers':
            advisor_role = f"an expert Floral & Fresh Produce AI business advisor for '{shop_name}'. You advise on fresh flower stock, garland pricing, perishable wastage prevention, and festival pooja demand."
        else:
            advisor_role = f"an expert Kirana & retail business AI assistant for '{shop_name}' in India."

        prompt = f"""You are 'DukaanSetu', {advisor_role}

The shopkeeper asked:
"{question}"

Previous Conversation History (use this to resolve follow-ups like 'saripothunda?', 'it', 'that', 'order it'):
{json.dumps(history[-6:], indent=2)}

LIVE Database Reality of this Shop:
Available Products & Real Sales Velocity:
{json.dumps(catalog_summary, indent=2)}

Active Customer Udhar (Credits):
{json.dumps(borrowings_summary, indent=2)}

Suppliers:
{json.dumps(suppliers_summary, indent=2)}

Assistant Capabilities:
- Mode 1: Action execution. If user says 'Order 5 bags' or agrees to restock, provide 'suggested_action'.
- Mode 2: Question answering.
- Mode 3: Business Intelligence (e.g. 'Next week ki saripothunda?' -> 7 days consumption vs current_stock).

Language Guidelines:
- If Telugu (e.g. 'biyyam', 'entha undi', 'saripothunda'), respond in conversational Telugu (Telugu script or bilingual).
- If Hindi, respond in natural Hindi.
- If English, respond in Indian English.
- Spoken version (voice_text) must be 1-2 concise sentences.

Return strictly a JSON object with this structure (no markdown fences):
{{
    "answer": "Full written response with numbers and reasoning",
    "voice_text": "Short spoken version (1-2 sentences) for audio TTS",
    "topic": "STOCK_CHECK|CREDIT_CHECK|BUSINESS_INSIGHT|REORDER_ADVICE|ACTION|GENERAL",
    "language": "te|hi|en",
    "suggested_action": null or {{
        "action_type": "CREATE_PURCHASE_ORDER|ADD_STOCK|RECORD_BORROWING",
        "product_id": "UUID from products list or null",
        "product_name": "Product Name",
        "quantity": float,
        "unit": "kg|bag|packet|litre|piece",
        "supplier_id": "UUID or null",
        "customer_name": "Customer Name or null",
        "title": "Action title for button",
        "description": "Brief description of the action"
    }}
}}"""

        api_key = os.getenv('GEMINI_API_KEY')
        ai_response_text = None

        if api_key:
            import google.generativeai as genai
            genai.configure(api_key=api_key)

            for model_name in CANDIDATE_MODELS:
                try:
                    m = genai.GenerativeModel(model_name)
                    res = m.generate_content(prompt)
                    if res and res.text:
                        ai_response_text = res.text.strip()
                        break
                except Exception as m_err:
                    logger.warning(f"Model {model_name} failed: {m_err}")
                    continue

        if ai_response_text:
            if ai_response_text.startswith('```'):
                ai_response_text = ai_response_text.split('\n', 1)[1].rsplit('```', 1)[0].strip()
            try:
                parsed = json.loads(ai_response_text)
                return success_response(parsed)
            except Exception:
                pass

        # Deterministic Intelligence Fallback Engine using LIVE database facts
        return success_response(build_deterministic_answer(question, history, catalog_summary, borrowings_summary))

    except Exception as e:
        logger.error(f"Error in ask_assistant: {e}")
        return error_response(f"Assistant error: {str(e)}", "ASSISTANT_ERROR", 500)


def build_deterministic_answer(question, history, catalog, borrowings):
    """Accurately answers using pure live database calculation if Gemini API hits rate limits."""
    q = question.lower()

    # Find relevant product from question or history
    target_product = None
    for item in catalog:
        name = item['name'].lower()
        local = (item.get('local_name') or '').lower()
        if name in q or (local and local in q):
            target_product = item
            break

    # If pronoun or follow-up, look back in history
    if not target_product and history:
        for prev in reversed(history):
            prev_txt = (prev.get('content') or '').lower()
            for item in catalog:
                name = item['name'].lower()
                local = (item.get('local_name') or '').lower()
                if name in prev_txt or (local and local in prev_txt):
                    target_product = item
                    break
            if target_product:
                break

    # Never default to catalog[0] if no product found
    if not target_product:
        # Check if question is udhar / credit check first
        if 'udhar' in q or 'credit' in q or 'ivvali' in q or 'appu' in q or 'who owes' in q:
            if borrowings:
                names = [f"{b['customer']} (₹{b['balance_due']:,})" for b in borrowings if b.get('balance_due', 0) > 0]
                ans = f"బాకీ ఉన్న కస్టమర్లు: {', '.join(names[:5])}." if names else "ప్రస్తుతానికి ఎటువంటి కస్టమర్ అప్పులు బాకీ లేవు."
            else:
                ans = "ప్రస్తుతానికి ఎటువంటి కస్టమర్ అప్పులు బాకీ లేవు."
            return {
                "answer": ans,
                "voice_text": ans,
                "topic": "CREDIT_CHECK",
                "language": "te",
                "suggested_action": None
            }
        
        # Product not specified
        return {
            "answer": "ఏ వస్తువు వివరాలు కావాలో దయచేసి చెప్పండి (ఉదాహరణకు: రైస్, షుగర్, లేదా ఆయిల్).",
            "voice_text": "ఏ వస్తువు వివరాలు కావాలో చెప్పండి.",
            "topic": "CLARIFICATION",
            "language": "te",
            "suggested_action": None
        }

    # Mode 3: Next week check / saripothunda?
    if 'saripothunda' in q or 'enough' in q or 'next week' in q or 'saripoda' in q:
        stock = target_product['current_stock']
        unit = target_product['stock_unit']
        velocity = target_product['avg_daily_sales']
        needed_7d = round(velocity * 7, 1) if velocity > 0 else 25

        if stock >= needed_7d:
            ans = f"అవును, {target_product['name']} ప్రస్తుత స్టాక్ {stock} {unit} ఉంది. వచ్చే వారం వినియోగానికి (సుమారు {needed_7d} {unit}) ఇది సులభంగా సరిపోతుంది."
            v_ans = f"అవును, {target_product['name']} స్టాక్ సరిపోతుంది. ప్రస్తుతం {stock} {unit} ఉంది."
        else:
            ans = f"లేదు, {target_product['name']} స్టాక్ {stock} {unit} మాత్రమే ఉంది. వచ్చే వారం సరిపోవడానికి కనీసం {needed_7d} {unit} కావాలి. వెంటనే రీఆర్డర్ చేసుకోండి."
            v_ans = f"స్టాక్ తక్కువగా ఉంది. రీఆర్డర్ చేయడం మంచిది."

        return {
            "answer": ans,
            "voice_text": v_ans,
            "topic": "BUSINESS_INSIGHT",
            "language": "te",
            "suggested_action": {
                "action_type": "CREATE_PURCHASE_ORDER",
                "product_id": target_product['id'],
                "product_name": target_product['name'],
                "quantity": max(5, round(needed_7d - stock)),
                "unit": target_product['stock_unit'],
                "supplier_id": target_product.get('supplier_id'),
                "title": f"Order {target_product['name']}",
                "description": f"Create purchase order for {target_product['name']}"
            } if stock < needed_7d else None
        }

    # Mode 2: Stock check
    if 'stock' in q or 'entha undi' in q or 'kitna' in q or 'undha' in q:
        stock = target_product['current_stock']
        unit = target_product['stock_unit']
        ans = f"ప్రస్తుతం మీ దగ్గర {target_product['name']} స్టాక్ {stock} {unit} ఉంది."
        return {
            "answer": ans,
            "voice_text": f"{target_product['name']} స్టాక్ {stock} {unit} ఉంది.",
            "topic": "STOCK_CHECK",
            "language": "te",
            "suggested_action": None
        }

    # Mode 2: Udhar / Credit check
    if 'udhar' in q or 'credit' in q or 'ivvali' in q:
        if borrowings:
            names = [f"{b['customer']} (₹{b['balance_due']:,})" for b in borrowings[:3]]
            ans = f"బాకీ ఉన్న కస్టమర్లు: {', '.join(names)}."
        else:
            ans = "ప్రస్తుతానికి ఎటువంటి కస్టమర్ అప్పులు బాకీ లేవు."
        return {
            "answer": ans,
            "voice_text": ans,
            "topic": "CREDIT_CHECK",
            "language": "te",
            "suggested_action": None
        }

    # General live summary
    stock = target_product['current_stock']
    unit = target_product['stock_unit']
    return {
        "answer": f"{target_product['name']} స్టాక్ {stock} {unit} ఉంది. వ్యాపారి వాయిస్ మీకు ఎలా సహాయపడుతుంది?",
        "voice_text": f"{target_product['name']} స్టాక్ {stock} {unit} ఉంది.",
        "topic": "GENERAL",
        "language": "te",
        "suggested_action": None
    }
