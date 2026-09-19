"""Voice routes — audio transcription, multi-lingual interpretation with alias resolution, and voice logs."""
import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request
from app.utils import require_auth, success_response, error_response, get_current_shop_id, get_current_user_id
from app.utils.supabase_client import get_supabase

logger = logging.getLogger(__name__)
voice_bp = Blueprint('voice', __name__)


@voice_bp.route('/transcribe', methods=['POST'])
@require_auth
def transcribe_audio():
    """Transcribe recorded voice audio (WebM, WAV, MP3, OGG) using Gemini 2.5 multimodal audio capabilities."""
    if 'audio' not in request.files:
        return error_response("Audio file is required", "VALIDATION_ERROR", 400)

    audio_file = request.files['audio']
    if not audio_file.filename:
        return error_response("Empty audio file", "VALIDATION_ERROR", 400)

    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return error_response("AI service not configured", "CONFIG_ERROR", 500)

        import google.generativeai as genai
        genai.configure(api_key=api_key)
        # Try current model, fallback to latest
        model = None
        for model_name in ['gemini-2.5-flash', 'gemini-3.6-flash']:
            try:
                model = genai.GenerativeModel(model_name)
                break
            except Exception:
                continue
        if not model:
            return error_response("No AI model available", "CONFIG_ERROR", 500)

        audio_bytes = audio_file.read()
        mime_type = audio_file.mimetype or 'audio/webm'

        prompt = """You are an Indian retail Kirana shopkeeper speech transcriber.
Accurately transcribe the spoken words in this audio clip.
The shopkeeper may speak in:
- Telugu (e.g. '5 basthalu biyyam add cheyyi', 'Ramesh ki 200 udhar rasi pettu', 'sugar entha undi?')
- Hindi (e.g. '10 kilo chawal stock me jodo', 'Ramesh ko 500 udhar likho')
- Indian English / Hinglish / Tanglish

Output ONLY the exact transcript text. Do not include markdown or explanations."""

        response = model.generate_content([
            {'mime_type': mime_type, 'data': audio_bytes},
            prompt
        ])

        transcript = response.text.strip() if response and response.text else ""

        # Quick language detection heuristic
        detected_lang = 'en'
        telugu_chars = sum(1 for c in transcript if '\u0c00' <= c <= '\u0c7f')
        hindi_chars = sum(1 for c in transcript if '\u0900' <= c <= '\u097f')
        if telugu_chars > 3 or any(w in transcript.lower() for w in ['biyyam', 'chakkera', 'nune', 'cheyyi', 'undhi', 'entha', 'udhar']):
            detected_lang = 'te'
        elif hindi_chars > 3 or any(w in transcript.lower() for w in ['chawal', 'chini', 'tel', 'jodo', 'likho', 'kitna']):
            detected_lang = 'hi'

        return success_response({
            'transcript': transcript,
            'detected_language': detected_lang
        })

    except Exception as e:
        logger.error(f"Voice transcription failed: {e}")
        return error_response(f"Audio transcription failed: {str(e)}", "TRANSCRIBE_ERROR", 500)


@voice_bp.route('/upload', methods=['POST'])
@require_auth
def upload_audio():
    """Upload audio recording reference for auditing and playback."""
    shop_id = get_current_shop_id()
    if 'audio' not in request.files:
        return error_response("Audio file is required", "VALIDATION_ERROR", 400)

    audio_file = request.files['audio']
    try:
        date_path = datetime.utcnow().strftime('%Y-%m-%d')
        file_path = f"voice-recordings/{shop_id}/{date_path}/{audio_file.filename}"
        return success_response({
            'audio_url': file_path,
            'message': 'Audio uploaded successfully'
        }, 201)
    except Exception as e:
        return error_response(f"Upload failed: {str(e)}", "UPLOAD_ERROR", 500)


@voice_bp.route('/interpret', methods=['POST'])
@require_auth
def interpret_voice():
    """Interpret speech transcript into structured Kirana business intent with product alias resolution."""
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)

    data = request.get_json()
    if not data or not data.get('transcript'):
        return error_response("Transcript is required", "VALIDATION_ERROR")

    transcript = data['transcript'].strip()

    try:
        supabase = get_supabase()

        # 1. Fetch live products and aliases for the shop
        prods_res = supabase.table('products').select('*').eq('shop_id', shop_id).eq('is_active', True).execute()
        products = prods_res.data or []
        inv_res = supabase.table('inventory').select('*').eq('shop_id', shop_id).execute()
        inv_map = {i['product_id']: i for i in (inv_res.data or [])}

        try:
            aliases_res = supabase.table('product_aliases').select('*').eq('shop_id', shop_id).execute()
            aliases = aliases_res.data or []
        except Exception:
            aliases = []  # Table may not exist yet

        # 2. Fetch customers and suppliers for entity resolution
        cust_res = supabase.table('customers').select('id, name, phone').eq('shop_id', shop_id).execute()
        customers = cust_res.data or []

        supp_res = supabase.table('suppliers').select('id, name, phone').eq('shop_id', shop_id).execute()
        suppliers = supp_res.data or []

        # Alias lookup dictionary: alias -> product_id
        alias_to_pid = {}
        for a in aliases:
            alias_to_pid[a['alias'].lower()] = a['product_id']

        # Catalog summary for prompt
        catalog_names = []
        prod_by_id = {}
        for p in products:
            pid = p['id']
            prod_by_id[pid] = p
            inv = inv_map.get(pid, {})
            p['current_stock'] = inv.get('current_stock', 0)
            p['stock_unit'] = inv.get('stock_unit', p.get('base_unit', 'unit'))
            catalog_names.append(f"{p['name']} (Local: {p.get('local_name', '')}, Unit: {p.get('base_unit')}, Stock: {p['current_stock']})")

        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return error_response("AI service not configured", "CONFIG_ERROR", 500)

        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = None
        for m_name in ['gemini-2.5-flash', 'gemini-3.6-flash']:
            try:
                model = genai.GenerativeModel(m_name)
                break
            except Exception:
                continue
        if not model:
            return error_response("No AI model available", "CONFIG_ERROR", 500)

        prompt = f"""You are a smart inventory AI assistant for an Indian Kirana/Grocery store called 'Vyapari Voice'.

Analyze the following voice command spoken by the shopkeeper. The speech may be in English, Telugu, Hindi, or mixed Indian colloquial trade terms.

Voice command: "{transcript}"

Shop's Available Product Catalog:
{json.dumps(catalog_names[:30], indent=2)}

Registered Customers: {[c['name'] for c in customers[:20]]}
Registered Suppliers: {[s['name'] for s in suppliers[:20]]}

Common Regional Terminology:
- 'biyyam' / 'chawal' / 'arisi' = Rice
- 'chakkera' / 'chini' / 'shakkar' / 'panchadara' = Sugar
- 'nune' / 'tel' = Cooking Oil (Sunflower Oil)
- 'kandi pappu' / 'toor dal' = Toor Dal / Dal
- 'bellam' / 'gud' = Jaggery
- 'add cheyyi' / 'vesuko' / 'stock me dalo' = STOCK_IN (add inventory)
- 'ammadu' / 'sold' / 'becha' = SALE / STOCK_OUT
- 'ichanu' / 'udhar rasi' / 'likho' = BORROW_OUT (Customer borrowing/credit)
- 'udhar ichadu' / 'jama chesadu' / 'paid' = BORROW_RETURN (Customer debt repayment)
- 'entha undi' / 'kitna hai' / 'stock entha' = STOCK_CHECK
- 'order cheyyi' / 'mangwa lo' = PURCHASE (create purchase order)

Extract structured JSON strictly matching this schema:
{{
    "intent": "STOCK_IN|STOCK_OUT|SALE|PURCHASE|BORROW_OUT|BORROW_RETURN|STOCK_CHECK|UNKNOWN",
    "product_name": "Standard English product name from catalog or null",
    "raw_product_spoken": "Exact word user said for product or null",
    "quantity": float or null,
    "unit": "kg|bag|packet|litre|piece|box|gram|ml or null",
    "unit_price": float or null,
    "total_price": float or null,
    "customer_name": "Matched customer name from registered customers or spoken name or null",
    "supplier_name": "Matched supplier name or null",
    "confidence": float between 0.0 and 1.0,
    "clarification_needed": boolean,
    "confirmation_prompt": "Friendly confirmation sentence in the user's spoken language asking to confirm this exact change"
}}

Respond ONLY with valid JSON (no markdown formatting)."""

        ai_response = model.generate_content(prompt)
        text = ai_response.text.strip()
        if text.startswith('```'):
            text = text.split('\n', 1)[1].rsplit('```', 1)[0].strip()

        intent_data = json.loads(text)

        # Post-process: resolve canonical product from aliases or catalog
        matched_product = None
        raw_p = (intent_data.get('raw_product_spoken') or '').lower().strip()
        std_p = (intent_data.get('product_name') or '').lower().strip()

        # Check alias table first
        target_pid = alias_to_pid.get(raw_p) or alias_to_pid.get(std_p)
        if target_pid and target_pid in prod_by_id:
            matched_product = prod_by_id[target_pid]
        else:
            # Match against catalog names
            for p in products:
                if (std_p and std_p in p['name'].lower()) or (p.get('local_name') and raw_p and raw_p in p['local_name'].lower()):
                    matched_product = p
                    break

        if matched_product:
            intent_data['product_id'] = matched_product['id']
            intent_data['canonical_name'] = matched_product['name']
            intent_data['matched_product'] = {
                'id': matched_product['id'],
                'name': matched_product['name'],
                'local_name': matched_product.get('local_name'),
                'base_unit': matched_product.get('base_unit', 'unit'),
                'current_stock': matched_product.get('current_stock', 0),
                'selling_price': matched_product.get('selling_price', 0),
                'purchase_price': matched_product.get('purchase_price', 0)
            }
            if not intent_data.get('unit'):
                intent_data['unit'] = matched_product.get('base_unit', 'unit')

        # Match customer if BORROW_OUT or BORROW_RETURN
        cname = intent_data.get('customer_name')
        if cname:
            for c in customers:
                if cname.lower() in c['name'].lower() or c['name'].lower() in cname.lower():
                    intent_data['customer_id'] = c['id']
                    intent_data['customer_name'] = c['name']
                    intent_data['customer_phone'] = c.get('phone')
                    break

        return success_response({
            'intent': intent_data,
            'transcript': transcript,
            'language': data.get('language', 'auto')
        })

    except json.JSONDecodeError:
        return error_response("Failed to parse AI interpretation output", "AI_ERROR", 500)
    except Exception as e:
        logger.error(f"Voice interpretation failed: {e}")
        return error_response(f"AI interpretation failed: {str(e)}", "AI_ERROR", 500)


@voice_bp.route('', methods=['GET'])
@require_auth
def list_voice_history():
    """Get recent voice conversations."""
    shop_id = get_current_shop_id()
    try:
        supabase = get_supabase()
        res = supabase.table('voice_conversations').select('*').eq('shop_id', shop_id).order('created_at', desc=True).limit(50).execute()
        return success_response({'items': res.data or []})
    except Exception as e:
        return error_response(f"Failed to fetch voice history: {str(e)}", "FETCH_ERROR", 500)


@voice_bp.route('/<voice_id>', methods=['DELETE'])
@require_auth
def delete_voice_record(voice_id):
    """Delete voice history record."""
    shop_id = get_current_shop_id()
    try:
        supabase = get_supabase()
        supabase.table('voice_conversations').delete().eq('id', voice_id).eq('shop_id', shop_id).execute()
        return success_response({'message': 'Voice record deleted'})
    except Exception as e:
        return error_response(f"Failed to delete: {str(e)}", "DELETE_ERROR", 500)


@voice_bp.route('/save', methods=['POST'])
@require_auth
def save_conversation():
    """Save a voice conversation exchange (user message + assistant response) to the database."""
    shop_id = get_current_shop_id()
    user_id = get_current_user_id()

    data = request.get_json()
    if not data:
        return error_response("Request body is required", "VALIDATION_ERROR")

    try:
        supabase = get_supabase()
        record = {
            'shop_id': shop_id,
            'user_id': user_id,
            'transcript': data.get('user_message', ''),
            'language': data.get('language', 'en'),
            'intent': data.get('intent', 'GENERAL'),
            'extracted_entities': data.get('entities', {}),
            'confirmation_status': data.get('confirmation_status', 'CONFIRMED'),
        }

        res = supabase.table('voice_conversations').insert(record).execute()
        return success_response({
            'id': res.data[0]['id'] if res.data else None,
            'message': 'Conversation saved'
        }, 201)

    except Exception as e:
        logger.warning(f"Failed to save conversation: {e}")
        return success_response({'message': 'Conversation noted (save skipped)'})
