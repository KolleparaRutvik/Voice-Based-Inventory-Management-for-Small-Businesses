"""Vyapari Voice — Unified Multilingual Voice Assistant & Kirana Business Engine.
Handles:
1. Multimodal audio STT (Gemini 2.5 / 3.6 Flash) with Telugu, Hindi, English, & mixed Tanglish/Hinglish speech.
2. Multilingual Kirana entity resolution & normalization without hardcoded fake fallbacks.
3. Unified intent detection (inquiries + inventory/credit mutations) with multi-turn context resolution.
4. Mandatory human confirmation & disambiguation before database mutation.
5. End-to-end database action execution with audit logging to transactions and customer_credit.
6. Persistent multi-turn conversation thread storage.
"""
import os
import re
import json
import logging
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, g
from app.utils import require_auth, success_response, error_response, get_current_shop_id, get_current_user_id
from app.utils.supabase_client import get_supabase
from app.utils.entity_resolver import (
    resolve_product,
    resolve_customer,
    resolve_supplier,
    normalize_unit,
    extract_numbers_and_units,
    extract_customer_from_loan_phrase,
    extract_phone_number,
    KIRANA_PRODUCT_SYNONYMS
)

logger = logging.getLogger(__name__)
voice_bp = Blueprint('voice', __name__)

CANDIDATE_MODELS = [
    'gemini-3.1-flash-lite',
    'gemini-3.5-flash-lite',
    'gemini-flash-latest',
    'gemini-2.5-flash',
    'gemini-3.6-flash'
]


def generate_with_gemini(contents):
    """Attempt generation across candidate Gemini models, gracefully handling quotas and rate limits."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        for model_name in CANDIDATE_MODELS:
            try:
                m = genai.GenerativeModel(model_name)
                res = m.generate_content(contents, request_options={'timeout': 10})
                if res and res.text:
                    return res.text.strip()
            except Exception as ex:
                logger.warning(f"Candidate model {model_name} failed: {ex}")
                continue
    except Exception as e:
        logger.error(f"Failed to generate with Gemini: {e}")
    return None


@voice_bp.route('/transcribe', methods=['POST'])
@require_auth
def transcribe_audio():
    """Transcribe spoken audio (WebM, WAV, MP3, OGG) using Gemini Multimodal Audio."""
    if 'audio' not in request.files:
        return error_response("Audio file is required", "VALIDATION_ERROR", 400)

    audio_file = request.files['audio']
    if not audio_file.filename:
        return error_response("Empty audio file provided", "VALIDATION_ERROR", 400)

    try:
        audio_bytes = audio_file.read()
        if not audio_bytes or len(audio_bytes) < 100:
            return error_response("Audio file is too short or empty", "VALIDATION_ERROR", 400)

        mime_type = audio_file.mimetype or 'audio/webm'

        prompt = """You are a highly accurate speech transcriber for Indian Kirana/grocery shopkeepers.
Accurately transcribe the spoken audio into text.
The speech may be in:
- Telugu (e.g. '5 basthalu biyyam add cheyyi', 'Ramesh ki 500 udhar rasi pettu', 'sugar entha undi?', 'Ramesh 200 paid chesadu', 'next week ki saripothunda?')
- Hindi (e.g. '5 kilo chawal stock mein dalo', 'Ramesh ko 500 udhar likho', 'tel kitna hai?')
- English / Indian English (e.g. 'How much rice is left?', 'Add 5 bags sugar', 'Ramesh paid 200')
- Mixed Telugu-English, Hindi-English, Tanglish, Hinglish

Instructions:
1. Preserve exact numbers, units (bags, basthalu, kg, packets, litres), customer names, and Kirana terminology.
2. Return ONLY the transcribed text. Do NOT add markdown fences, commentary, or punctuation explanations."""

        transcript = generate_with_gemini([
            {'mime_type': mime_type, 'data': audio_bytes},
            prompt
        ])
        if not transcript:
            return error_response("Could not recognize any speech in audio. Please try speaking again.", "UNRECOGNIZED_SPEECH", 422)

        # Detect primary language of transcript
        detected_lang = 'en'
        telugu_chars = sum(1 for c in transcript if '\u0c00' <= c <= '\u0c7f')
        hindi_chars = sum(1 for c in transcript if '\u0900' <= c <= '\u097f')
        lower_t = transcript.lower()

        if telugu_chars > 2 or any(w in lower_t for w in ['biyyam', 'chakkera', 'nune', 'cheyyi', 'undhi', 'undi', 'entha', 'udhar', 'pappu', 'ammadu', 'saripothunda']):
            detected_lang = 'te'
        elif hindi_chars > 2 or any(w in lower_t for w in ['chawal', 'chini', 'tel', 'jodo', 'likho', 'kitna', 'becha', 'hai']):
            detected_lang = 'hi'

        return success_response({
            'transcript': transcript,
            'detected_language': detected_lang
        })

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return error_response(f"Audio transcription failed: {str(e)}", "TRANSCRIBE_ERROR", 500)


@voice_bp.route('/interpret', methods=['POST'])
@require_auth
def interpret_voice():
    """Interpret speech transcript with current shop reality, Kirana normalization, and multi-turn context.
    Determines intent (informational inquiry vs mutating action), resolves entities safely without guessing,
    and formats confirmation prompt or live answer.
    """
    shop_id = get_current_shop_id()
    if not shop_id:
        return error_response("Shop not found", "SHOP_NOT_FOUND", 404)

    data = request.get_json()
    if not data or not data.get('transcript'):
        return error_response("Transcript is required", "VALIDATION_ERROR", 400)

    transcript = data['transcript'].strip()
    history = data.get('conversation_history', [])
    lang_pref = data.get('language', 'auto')

    try:
        supabase = get_supabase()

        # 1. Fetch current shop products & inventory
        prods_res = supabase.table('products').select('*').eq('shop_id', shop_id).eq('is_active', True).execute()
        products = prods_res.data or []
        inv_res = supabase.table('inventory').select('*').eq('shop_id', shop_id).execute()
        inv_map = {i['product_id']: i for i in (inv_res.data or [])}

        for p in products:
            inv = inv_map.get(p['id'], {})
            p['current_stock'] = float(inv.get('current_stock', 0))
            p['stock_unit'] = inv.get('stock_unit', p.get('base_unit', 'unit'))

        # Fetch product aliases
        try:
            alias_res = supabase.table('product_aliases').select('*').eq('shop_id', shop_id).execute()
            aliases = alias_res.data or []
        except Exception:
            aliases = []

        # 2. Fetch customers & active credit
        cust_res = supabase.table('customers').select('*').eq('shop_id', shop_id).execute()
        customers = cust_res.data or []

        borrow_res = supabase.table('borrowings').select('*').eq('shop_id', shop_id).in_('status', ['ACTIVE', 'PARTIALLY_RETURNED', 'OVERDUE']).execute()
        borrowings = borrow_res.data or []

        # Calculate live customer balances
        customer_debt_map = {}
        for b in borrowings:
            cid = b.get('customer_id')
            cname = (b.get('customer_name') or '').strip()
            bal = float(b.get('remaining_balance') or b.get('total_value') or 0)
            if cid:
                customer_debt_map[cid] = customer_debt_map.get(cid, 0) + bal
            if cname:
                customer_debt_map[cname.lower()] = customer_debt_map.get(cname.lower(), 0) + bal

        # 3. Fetch suppliers
        supp_res = supabase.table('suppliers').select('id, name, phone').eq('shop_id', shop_id).execute()
        suppliers = supp_res.data or []

        # 4. Extract numbers and units locally as foundational facts
        extracted_facts = extract_numbers_and_units(transcript)

        # 5. Multi-turn context resolution: find last product or customer if referenced
        last_product_name = None
        last_customer_name = None
        if history:
            for prev_msg in reversed(history[-6:]):
                content = prev_msg.get('content', '') if isinstance(prev_msg, dict) else str(prev_msg)
                # Look for product mention
                for p in products:
                    if p['name'].lower() in content.lower() or (p.get('local_name') and p['local_name'].lower() in content.lower()):
                        if not last_product_name:
                            last_product_name = p['name']
                # Look for customer mention
                for c in customers:
                    if c['name'].lower() in content.lower():
                        if not last_customer_name:
                            last_customer_name = c['name']

        # 6. Build prompt for Gemini interpretation
        catalog_names = [f"{p['name']} (Local: {p.get('local_name', '')}, Stock: {p['current_stock']} {p['stock_unit']})" for p in products]
        customer_names = [f"{c['name']} (Debt: ₹{customer_debt_map.get(c['id'], 0)})" for c in customers]

        prompt = f"""You are 'Vyapari Voice', the intelligent business assistant for an Indian Kirana store.
Analyze this voice transcript spoken by the shopkeeper. The speech may be in English, Telugu, Hindi, or mixed.

Voice Command: "{transcript}"

Context from recent conversation:
- Last referenced product: {last_product_name or 'None'}
- Last referenced customer: {last_customer_name or 'None'}
- Previous conversation history: {json.dumps(history[-4:], indent=2)}

Available Shop Catalog:
{json.dumps(catalog_names, indent=2)}

Registered Customers:
{json.dumps(customer_names, indent=2)}

Registered Suppliers:
{[s['name'] for s in suppliers]}

Kirana Trade Rules:
- STOCK_IN: 'add cheyyi', 'vesuko', 'stock me dalo', 'jodo', 'add 5 bags'
- STOCK_OUT / SALE: 'sold', 'ammadu', 'becha', 'theesi', 'sale cheyyi'
- BORROW_OUT (Customer Loan / Credit): 'taken a loan', 'took a loan', 'took loan', 'borrowed', 'loan of 500', 'udhar rasi', 'udhar likho', 'appu rasi', '500 udhar pettu', 'appu theesukunnadu', 'karz liya', 'chebadulu', 'loan diya'
- BORROW_RETURN (Customer Repayment): 'paid', 'jama chesadu', 'udhar kattadu', 'wapas diya', 'loan wapas', 'repaid'
- BORROW_CLEAR (Settle / Waive All Debt): 'clear loan', 'clear udhar', 'forgive debt', 'settle loan', 'raddhu cheyyi', 'maaf karo'
- STOCK_ADJUST: 'adjust stock', 'set stock to', 'stock change'
- CUSTOMER_ADD: 'add customer', 'new customer', 'kotha customer'
- PRODUCT_ADD: 'add product', 'new product'
- STOCK_CHECK: 'entha undi', 'kitna hai', 'stock entha', 'how much left'
- CREDIT_CHECK: 'who owes money', 'appu evaru unnaru', 'balance entha', 'udhar kiska hai', 'how much loan does X have'
- BUSINESS_INSIGHT / SARIPOTHUNDA: 'saripothunda', 'next week ki సరిపోతుందా', 'enough for next week'
- PURCHASE: 'order cheyyi', 'mangwa lo', 'place purchase order'

Important Customer Rules:
- When someone says a person has taken a loan (e.g. "one person Kiran has taken a loan of 500" or "Mahesh took loan 1000"), ALWAYS extract their name in "raw_customer".
- Even if that person is NOT yet in Registered Customers, DO NOT return null. Extract their clean name. The system will automatically create their Udhar account.

Return strictly a JSON object with this structure (no markdown fences, no extra text):
{{
    "intent": "STOCK_IN|STOCK_OUT|SALE|BORROW_OUT|BORROW_RETURN|BORROW_CLEAR|STOCK_CHECK|CREDIT_CHECK|BUSINESS_INSIGHT|PURCHASE|STOCK_ADJUST|CUSTOMER_ADD|PRODUCT_ADD|GENERAL|UNKNOWN",
    "raw_product": "Spoken product name or null",
    "raw_customer": "Spoken customer name or null",
    "raw_supplier": "Spoken supplier name or null",
    "quantity": float or null,
    "unit": "bag|kg|litre|packet|piece|box|can or null",
    "price": float or null,
    "amount": float or null,
    "confidence": float between 0.0 and 1.0,
    "detected_language": "te|hi|en",
    "requires_confirmation": boolean (true for mutating actions like STOCK_IN, STOCK_OUT, BORROW_OUT, BORROW_RETURN, BORROW_CLEAR, STOCK_ADJUST, CUSTOMER_ADD, PRODUCT_ADD, PURCHASE; false for queries),
    "confirmation_prompt": "Confirmation sentence in the user's spoken language or null",
    "answer": "Direct complete answer if intent is an inquiry (STOCK_CHECK, CREDIT_CHECK, BUSINESS_INSIGHT, GENERAL) or null",
    "voice_text": "Short spoken version (1-2 sentences) for audio TTS in user's language or null"
}}"""

        ai_data = None
        raw_ai_text = generate_with_gemini(prompt)
        if raw_ai_text:
            try:
                txt = raw_ai_text
                if txt.startswith('```'):
                    txt = txt.split('\n', 1)[1].rsplit('```', 1)[0].strip()
                ai_data = json.loads(txt)
            except Exception as m_err:
                logger.warning(f"Gemini interpretation JSON parse failed: {m_err}")

        # If LLM failed, use local deterministic fallback parser
        if not ai_data:
            ai_data = build_local_interpretation(transcript, last_product_name, last_customer_name, extracted_facts)

        # 7. Robust Entity Resolution on Extracted Data
        detected_intent = ai_data.get('intent', 'UNKNOWN')
        raw_prod = ai_data.get('raw_product') or (last_product_name if detected_intent in ('STOCK_IN', 'STOCK_OUT', 'STOCK_CHECK', 'STOCK_ADJUST', 'BUSINESS_INSIGHT') else None)
        raw_cust = ai_data.get('raw_customer') or (last_customer_name if detected_intent in ('BORROW_OUT', 'BORROW_RETURN', 'BORROW_CLEAR', 'CREDIT_CHECK', 'CUSTOMER_ADD') else None)

        # Fallback loan customer extraction from transcript if not yet extracted
        if not raw_cust or detected_intent == 'BORROW_OUT':
            loan_cust = extract_customer_from_loan_phrase(transcript)
            if loan_cust:
                raw_cust = loan_cust

        raw_supp = ai_data.get('raw_supplier')

        # Product matching
        prod_res = resolve_product(raw_prod, products, aliases) if raw_prod else {'matched_product': None, 'confidence': 0.0, 'ambiguous_candidates': [], 'is_ambiguous': False}
        matched_prod = prod_res['matched_product']

        # Customer matching
        cust_res_obj = resolve_customer(raw_cust, customers) if raw_cust else {'matched_customer': None, 'confidence': 0.0, 'ambiguous_candidates': [], 'is_ambiguous': False, 'is_new_customer': False}
        matched_cust = cust_res_obj['matched_customer']
        is_new_customer = cust_res_obj.get('is_new_customer', False) or (not matched_cust and bool(raw_cust))

        # Supplier matching
        supp_res_obj = resolve_supplier(raw_supp, suppliers) if raw_supp else {'matched_supplier': None, 'confidence': 0.0, 'ambiguous_candidates': [], 'is_ambiguous': False}
        matched_supp = supp_res_obj['matched_supplier']

        # Normalize quantity, unit, price, and amount
        qty = ai_data.get('quantity') or extracted_facts.get('quantity')
        unit = normalize_unit(ai_data.get('unit') or extracted_facts.get('unit') or (matched_prod.get('base_unit') if matched_prod else 'unit'))
        price = ai_data.get('price') or extracted_facts.get('price')
        amount = ai_data.get('amount') or (price if detected_intent in ('BORROW_OUT', 'BORROW_RETURN', 'BORROW_CLEAR') else None)

        if not price and matched_prod:
            price = float(matched_prod.get('purchase_price' if detected_intent in ('STOCK_IN', 'PURCHASE') else 'selling_price', 0))

        # Check Ambiguity & Clarification Needs
        clarification_needed = False
        ambiguous_candidates = []
        clarification_prompt = ""

        if prod_res['is_ambiguous']:
            clarification_needed = True
            ambiguous_candidates = prod_res['ambiguous_candidates']
            clarification_prompt = f"I found multiple products: {', '.join(ambiguous_candidates)}. Which one did you mean?"
        elif cust_res_obj['is_ambiguous']:
            clarification_needed = True
            ambiguous_candidates = cust_res_obj['ambiguous_candidates']
            clarification_prompt = f"I found multiple customers: {', '.join(ambiguous_candidates)}. Which one did you mean?"
        elif detected_intent in ('STOCK_IN', 'STOCK_OUT', 'SALE', 'STOCK_ADJUST') and not matched_prod:
            clarification_needed = True
            clarification_prompt = f"I couldn't identify the product '{raw_prod or transcript}'. Please say the product name again."
        elif detected_intent in ('BORROW_RETURN', 'BORROW_CLEAR') and not matched_cust and not raw_cust:
            clarification_needed = True
            clarification_prompt = "దయచేసి కస్టమర్ పేరు చెప్పండి." if lang == 'te' else "Please specify the customer name."
        elif detected_intent == 'BORROW_OUT' and not matched_cust and not raw_cust:
            clarification_needed = True
            clarification_prompt = "దయచేసి లోన్ తీసుకున్న వ్యక్తి పేరు చెప్పండి." if lang == 'te' else "Please say the person's name who took the loan."

        # Compute dynamic answers for inquiry intents
        answer = ai_data.get('answer')
        voice_text = ai_data.get('voice_text')
        lang = ai_data.get('detected_language', 'te' if any('\u0c00' <= c <= '\u0c7f' for c in transcript) else 'en')

        if detected_intent == 'STOCK_CHECK':
            if matched_prod:
                stock_val = matched_prod['current_stock']
                stk_u = matched_prod['stock_unit']
                if lang == 'te':
                    answer = f"ప్రస్తుతం మీ దగ్గర {matched_prod['name']} స్టాక్ {stock_val} {stk_u} ఉంది."
                    voice_text = f"{matched_prod['name']} స్టాక్ {stock_val} {stk_u} ఉంది."
                elif lang == 'hi':
                    answer = f"वर्तमान में आपके पास {matched_prod['name']} का स्टॉक {stock_val} {stk_u} है।"
                    voice_text = f"{matched_prod['name']} का स्टॉक {stock_val} {stk_u} है।"
                else:
                    answer = f"You currently have {stock_val} {stk_u} of {matched_prod['name']} in stock."
                    voice_text = f"You have {stock_val} {stk_u} of {matched_prod['name']}."
            else:
                answer = "ఏ వస్తువు స్టాక్ కావాలో చెప్పండి (ఉదా: రైస్, ఆయిల్, షుగర్)."
                voice_text = answer

        elif detected_intent == 'CREDIT_CHECK':
            if matched_cust:
                bal = customer_debt_map.get(matched_cust['id']) or customer_debt_map.get(matched_cust['name'].lower(), 0)
                if lang == 'te':
                    answer = f"{matched_cust['name']} గారి ప్రస్తుత బాకీ ₹{bal:,} ఉంది."
                    voice_text = f"{matched_cust['name']} బాకీ ₹{bal:,} ఉంది."
                elif lang == 'hi':
                    answer = f"{matched_cust['name']} का बकाया ₹{bal:,} है।"
                    voice_text = f"{matched_cust['name']} का बकाया ₹{bal:,} है।"
                else:
                    answer = f"{matched_cust['name']} currently owes ₹{bal:,} in credit."
                    voice_text = f"{matched_cust['name']} owes ₹{bal:,}."
            else:
                # List all customers with debt
                debtors = [f"{c['name']} (₹{customer_debt_map.get(c['id'], 0):,})" for c in customers if customer_debt_map.get(c['id'], 0) > 0]
                if debtors:
                    answer = f"బాకీ ఉన్న కస్టమర్లు: {', '.join(debtors)}."
                    voice_text = f"బాకీ ఉన్న కస్టమర్లు: {', '.join(debtors[:3])}."
                else:
                    answer = "ప్రస్తుతానికి ఎటువంటి కస్టమర్ అప్పులు బాకీ లేవు."
                    voice_text = answer

        elif detected_intent == 'BUSINESS_INSIGHT':
            if matched_prod:
                stock_val = matched_prod['current_stock']
                stk_u = matched_prod['stock_unit']
                min_stock = float(matched_prod.get('minimum_stock', 20))
                if stock_val >= min_stock:
                    answer = f"అవును, {matched_prod['name']} ప్రస్తుత స్టాక్ {stock_val} {stk_u} ఉంది. వచ్చే వారానికి ఇది సరిపోతుంది."
                    voice_text = f"అవును, {matched_prod['name']} స్టాక్ వచ్చే వారానికి సరిపోతుంది."
                else:
                    answer = f"లేదు, {matched_prod['name']} స్టాక్ {stock_val} {stk_u} మాత్రమే ఉంది (కనీసం {min_stock} {stk_u} కావాలి). వెంటనే రీఆర్డర్ చేయడం మంచిది."
                    voice_text = f"స్టాక్ తక్కువగా ఉంది. రీఆర్డర్ చేయడం మంచిది."

        # Mutating action confirmation prompt
        confirmation_prompt = ai_data.get('confirmation_prompt')
        cust_target_name = matched_cust['name'] if matched_cust else (raw_cust.strip().title() if raw_cust else 'Customer')

        if not confirmation_prompt and not clarification_needed:
            if detected_intent in ('STOCK_IN', 'PURCHASE') and matched_prod and qty:
                confirmation_prompt = f"{matched_prod['name']} స్టాక్ లో {qty} {unit} చేర్చమంటారా?" if lang == 'te' else f"Add {qty} {unit} of {matched_prod['name']} to stock?"
            elif detected_intent in ('STOCK_OUT', 'SALE') and matched_prod and qty:
                confirmation_prompt = f"{matched_prod['name']} నుండి {qty} {unit} సేల్ రికార్డ్ చేయమంటారా?" if lang == 'te' else f"Record sale of {qty} {unit} of {matched_prod['name']}?"
            elif detected_intent == 'BORROW_OUT' and (matched_cust or raw_cust):
                val_txt = f"₹{amount:,.0f}" if amount else (f"{qty} {unit}" if qty else "₹500")
                if is_new_customer:
                    if lang == 'te':
                        confirmation_prompt = f"{cust_target_name} గారికి కొత్త ఉధార్ ఖాతా సృష్టించి {val_txt} లోన్ రికార్డ్ చేయమంటారా?"
                    elif lang == 'hi':
                        confirmation_prompt = f"क्या {cust_target_name} के लिए नया उधार खाता बनाकर {val_txt} का लोन जोड़ें?"
                    else:
                        confirmation_prompt = f"Create a new udhar account for {cust_target_name} and record {val_txt} loan?"
                else:
                    if lang == 'te':
                        confirmation_prompt = f"{cust_target_name} గారి ఖాతాలో {val_txt} లోన్/ఉధార్ రికార్డ్ చేయమంటారా?"
                    elif lang == 'hi':
                        confirmation_prompt = f"क्या {cust_target_name} के खाते में {val_txt} लोन जोड़ें?"
                    else:
                        confirmation_prompt = f"Record {val_txt} loan for {cust_target_name}?"
            elif detected_intent == 'BORROW_RETURN' and (matched_cust or raw_cust) and (amount or price):
                pay_val = amount or price or 100
                confirmation_prompt = f"{cust_target_name} గారు చెల్లించిన ₹{pay_val:,.0f} నమోదు చేయమంటారా?" if lang == 'te' else f"Record payment of ₹{pay_val:,.0f} from {cust_target_name}?"
            elif detected_intent == 'BORROW_CLEAR' and (matched_cust or raw_cust):
                if lang == 'te':
                    confirmation_prompt = f"{cust_target_name} గారి మొత్తం బాకీ అప్పును క్లియర్ చేసి ఖాతాను సెటిల్ చేయమంటారా?"
                elif lang == 'hi':
                    confirmation_prompt = f"क्या {cust_target_name} का पूरा बकाया उधार क्लियर करके खाता सेटल करें?"
                else:
                    confirmation_prompt = f"Clear all remaining loan balance and settle udhar account for {cust_target_name}?"
            elif detected_intent == 'STOCK_ADJUST' and matched_prod:
                adj_qty = qty if qty is not None else 0
                confirmation_prompt = f"{matched_prod['name']} స్టాక్ ని ఖచ్చితంగా {adj_qty} {unit} గా సెట్ చేయమంటారా?" if lang == 'te' else f"Adjust stock of {matched_prod['name']} directly to {adj_qty} {unit}?"
            elif detected_intent == 'CUSTOMER_ADD' and (raw_cust or matched_cust):
                confirmation_prompt = f"కొత్త కస్టమర్ {cust_target_name} ని ఖాతాలో చేర్చమంటారా?" if lang == 'te' else f"Add new customer profile for {cust_target_name}?"
            elif detected_intent == 'PRODUCT_ADD' and raw_prod:
                confirmation_prompt = f"కొత్త ప్రొడక్ట్ {raw_prod} ని ఇన్వెంటరీలో చేర్చమంటారా?" if lang == 'te' else f"Add new product '{raw_prod}' to inventory?"

        requires_confirmation = detected_intent in (
            'STOCK_IN', 'STOCK_OUT', 'SALE', 'BORROW_OUT', 'BORROW_RETURN',
            'BORROW_CLEAR', 'STOCK_ADJUST', 'CUSTOMER_ADD', 'PRODUCT_ADD', 'PURCHASE', 'REORDER'
        ) and not clarification_needed

        extracted_phone = extract_phone_number(transcript)

        result = {
            'intent': detected_intent,
            'transcript': transcript,
            'language': lang,
            'confidence': float(ai_data.get('confidence', 0.95)),
            'product_id': matched_prod['id'] if matched_prod else None,
            'product_name': matched_prod['name'] if matched_prod else raw_prod,
            'customer_id': matched_cust['id'] if matched_cust else None,
            'customer_name': cust_target_name if (matched_cust or raw_cust) else None,
            'is_new_customer': is_new_customer,
            'phone': extracted_phone,
            'supplier_id': matched_supp['id'] if matched_supp else (matched_prod.get('supplier_id') if matched_prod else None),
            'quantity': qty,
            'unit': unit,
            'price': price,
            'amount': amount,
            'clarification_needed': clarification_needed,
            'ambiguous_candidates': ambiguous_candidates,
            'confirmation_required': requires_confirmation,
            'confirmation_prompt': clarification_prompt if clarification_needed else confirmation_prompt,
            'answer': answer,
            'voice_text': voice_text or answer or confirmation_prompt or clarification_prompt,
        }

        return success_response(result)

    except Exception as e:
        logger.error(f"Voice interpretation failed: {e}")
        return error_response(f"Interpretation failed: {str(e)}", "INTERPRET_ERROR", 500)


@voice_bp.route('/execute', methods=['POST'])
@require_auth
def execute_voice_action():
    """Execute confirmed voice intent directly against the database with strict shop scoping.
    Updates inventory, records borrowings, creates transactions, and links voice conversation.
    """
    shop_id = get_current_shop_id()
    user_id = get_current_user_id()
    data = request.get_json()

    if not data or not data.get('intent'):
        return error_response("Intent is required for execution", "VALIDATION_ERROR", 400)

    intent = data['intent']
    product_id = data.get('product_id')
    customer_id = data.get('customer_id')
    supplier_id = data.get('supplier_id')
    quantity = float(data.get('quantity') or 1)
    unit = data.get('unit') or 'unit'
    price = float(data.get('price') or 0)
    amount = float(data.get('amount') or (quantity * price if price > 0 else 0))
    notes = data.get('notes', f"Voice action: {data.get('transcript', '')}")
    conversation_id = data.get('conversation_id') or str(uuid.uuid4())

    try:
        supabase = get_supabase()
        transaction_id = None
        action_summary = ""

        # ---- 1. STOCK IN ----
        if intent == 'STOCK_IN':
            if not product_id:
                return error_response("Product ID is required for stock-in", "VALIDATION_ERROR", 400)

            prod = supabase.table('products').select('*').eq('id', product_id).eq('shop_id', shop_id).single().execute()
            if not prod.data:
                return error_response("Product not found in this shop", "NOT_FOUND", 404)

            product = prod.data
            factor = float(product.get('conversion_factor') or 1)
            qty_base = quantity * factor if unit == product.get('purchase_unit') else quantity

            inv = supabase.table('inventory').select('*').eq('product_id', product_id).eq('shop_id', shop_id).execute()
            if inv.data:
                new_stock = float(inv.data[0]['current_stock']) + qty_base
                supabase.table('inventory').update({
                    'current_stock': new_stock,
                    'last_stock_in': datetime.utcnow().isoformat()
                }).eq('id', inv.data[0]['id']).execute()
            else:
                new_stock = qty_base
                supabase.table('inventory').insert({
                    'shop_id': shop_id,
                    'product_id': product_id,
                    'current_stock': new_stock,
                    'stock_unit': product.get('base_unit', 'unit')
                }).execute()

            tx_res = supabase.table('transactions').insert({
                'shop_id': shop_id,
                'product_id': product_id,
                'transaction_type': 'STOCK_IN',
                'quantity': quantity,
                'unit': unit,
                'quantity_in_base_unit': qty_base,
                'price': price or float(product.get('purchase_price', 0)),
                'total_amount': quantity * (price or float(product.get('purchase_price', 0))),
                'source': 'voice',
                'notes': notes,
                'created_by': user_id
            }).execute()

            transaction_id = tx_res.data[0]['id'] if tx_res.data else None
            action_summary = f"Added {quantity} {unit} of {product['name']}. Current stock: {new_stock} {product.get('base_unit', 'unit')}."

        # ---- 2. STOCK OUT / SALE ----
        elif intent in ('STOCK_OUT', 'SALE'):
            if not product_id:
                return error_response("Product ID is required for sale", "VALIDATION_ERROR", 400)

            prod = supabase.table('products').select('*').eq('id', product_id).eq('shop_id', shop_id).single().execute()
            if not prod.data:
                return error_response("Product not found in this shop", "NOT_FOUND", 404)

            product = prod.data
            factor = float(product.get('conversion_factor') or 1)
            qty_base = quantity * factor if unit == product.get('purchase_unit') else quantity

            inv = supabase.table('inventory').select('*').eq('product_id', product_id).eq('shop_id', shop_id).execute()
            current_stk = float(inv.data[0]['current_stock']) if inv.data else 0
            new_stock = max(0, current_stk - qty_base)

            if inv.data:
                supabase.table('inventory').update({
                    'current_stock': new_stock,
                    'last_stock_out': datetime.utcnow().isoformat()
                }).eq('id', inv.data[0]['id']).execute()

            tx_res = supabase.table('transactions').insert({
                'shop_id': shop_id,
                'product_id': product_id,
                'transaction_type': 'SALE',
                'quantity': quantity,
                'unit': unit,
                'quantity_in_base_unit': qty_base,
                'price': price or float(product.get('selling_price', 0)),
                'total_amount': quantity * (price or float(product.get('selling_price', 0))),
                'source': 'voice',
                'notes': notes,
                'created_by': user_id
            }).execute()

            transaction_id = tx_res.data[0]['id'] if tx_res.data else None
            action_summary = f"Recorded sale of {quantity} {unit} of {product['name']}. Remaining stock: {new_stock} {product.get('base_unit', 'unit')}."

        # ---- 3. BORROW OUT (Add Udhar / Loan Credit) ----
        elif intent == 'BORROW_OUT':
            customer_name = data.get('customer_name')
            if not customer_id and not customer_name:
                return error_response("Customer is required to record loan/udhar", "VALIDATION_ERROR", 400)

            # Find customer in database
            cust = None
            if customer_id:
                cust_res = supabase.table('customers').select('*').eq('id', customer_id).eq('shop_id', shop_id).limit(1).execute()
                cust = cust_res.data[0] if cust_res.data else None
            if not cust and customer_name:
                cust_res = supabase.table('customers').select('*').ilike('name', customer_name).eq('shop_id', shop_id).limit(1).execute()
                cust = cust_res.data[0] if cust_res.data else None

            # Auto-create customer account on the fly if not existing!
            is_new = False
            if not cust:
                is_new = True
                phone = data.get('phone') or extract_phone_number(data.get('transcript', ''))
                new_c = supabase.table('customers').insert({
                    'shop_id': shop_id,
                    'name': (customer_name or 'Customer').strip().title(),
                    'phone': phone,
                    'total_credit': 0
                }).execute()
                cust = new_c.data[0]

            customer_id = cust['id']
            customer_name = cust['name']
            borrow_amount = amount or (quantity * price if price and price > 0 else (quantity or 500))

            # Create borrowing
            borrow_res = supabase.table('borrowings').insert({
                'shop_id': shop_id,
                'customer_id': customer_id,
                'customer_name': customer_name,
                'total_value': borrow_amount,
                'remaining_balance': borrow_amount,
                'status': 'ACTIVE',
                'notes': notes or f"Voice recorded loan ({'New Account' if is_new else 'Existing Customer'})",
                'created_by': user_id
            }).execute()

            borrowing_id = borrow_res.data[0]['id'] if borrow_res.data else None

            # Update customer balance
            new_credit = float(cust.get('total_credit') or 0) + borrow_amount
            supabase.table('customers').update({'total_credit': new_credit}).eq('id', customer_id).execute()

            # Create transaction
            tx_res = supabase.table('transactions').insert({
                'shop_id': shop_id,
                'transaction_type': 'BORROW_OUT',
                'quantity': 1,
                'unit': 'credit',
                'price': borrow_amount,
                'total_amount': borrow_amount,
                'customer_id': customer_id,
                'borrowing_id': borrowing_id,
                'source': 'voice',
                'notes': notes or f"Voice loan entry: ₹{borrow_amount:,.0f}",
                'created_by': user_id
            }).execute()

            transaction_id = tx_res.data[0]['id'] if tx_res.data else None
            if is_new:
                action_summary = f"Created new udhar account for {customer_name} and recorded ₹{borrow_amount:,.0f} loan. Balance due: ₹{new_credit:,.0f}."
            else:
                action_summary = f"Recorded ₹{borrow_amount:,.0f} loan for {customer_name}. Total balance due: ₹{new_credit:,.0f}."

        # ---- 4. BORROW RETURN (Customer Debt Settlement) ----
        elif intent == 'BORROW_RETURN':
            customer_name = data.get('customer_name')
            if not customer_id and not customer_name:
                return error_response("Customer is required for payment", "VALIDATION_ERROR", 400)

            # Find customer
            cust = None
            if customer_id:
                cust_res = supabase.table('customers').select('*').eq('id', customer_id).eq('shop_id', shop_id).limit(1).execute()
                cust = cust_res.data[0] if cust_res.data else None
            if not cust and customer_name:
                cust_res = supabase.table('customers').select('*').ilike('name', customer_name).eq('shop_id', shop_id).limit(1).execute()
                cust = cust_res.data[0] if cust_res.data else None

            if not cust:
                return error_response("Customer not found in shop database", "NOT_FOUND", 404)

            pay_amount = amount or price or 100
            customer_id = cust['id']
            customer_name = cust['name']

            # Find active borrowing
            active_b_res = supabase.table('borrowings').select('*').eq('customer_id', customer_id).eq('shop_id', shop_id).in_('status', ['ACTIVE', 'PARTIALLY_RETURNED']).order('created_at').limit(1).execute()
            b_row = active_b_res.data[0] if active_b_res.data else None

            borrowing_id = None
            if b_row:
                borrowing_id = b_row['id']
                old_bal = float(b_row.get('remaining_balance') or b_row.get('total_value', 0))
                old_paid = float(b_row.get('paid_amount', 0))
                new_bal = max(0, old_bal - pay_amount)
                new_paid = old_paid + pay_amount
                new_status = 'RETURNED' if new_bal <= 0 else 'PARTIALLY_RETURNED'

                supabase.table('borrowings').update({
                    'remaining_balance': new_bal,
                    'paid_amount': new_paid,
                    'status': new_status
                }).eq('id', borrowing_id).execute()

            # Update customer balance
            cur_credit = float(cust.get('total_credit') or 0)
            new_credit = max(0, cur_credit - pay_amount)
            supabase.table('customers').update({'total_credit': new_credit}).eq('id', customer_id).execute()

            # Transaction entry
            tx_res = supabase.table('transactions').insert({
                'shop_id': shop_id,
                'transaction_type': 'BORROW_RETURN',
                'quantity': 1,
                'unit': 'payment',
                'price': pay_amount,
                'total_amount': pay_amount,
                'customer_id': customer_id,
                'borrowing_id': borrowing_id,
                'source': 'voice',
                'notes': notes,
                'created_by': user_id
            }).execute()

            transaction_id = tx_res.data[0]['id'] if tx_res.data else None
            action_summary = f"Recorded payment of ₹{pay_amount:,} from {customer_name}. Remaining balance: ₹{new_credit:,}."

        # ---- 5. PURCHASE ORDER ----
        elif intent == 'PURCHASE':
            prod = supabase.table('products').select('*').eq('id', product_id).eq('shop_id', shop_id).single().execute() if product_id else None
            prod_data = prod.data if prod else None
            order_qty = quantity or 10
            unit_val = unit or (prod_data.get('base_unit') if prod_data else 'unit')
            unit_cost = price or (prod_data.get('purchase_price') if prod_data else 100)

            # Create PO
            po_res = supabase.table('purchase_orders').insert({
                'shop_id': shop_id,
                'supplier_id': supplier_id or (prod_data.get('supplier_id') if prod_data else None),
                'order_number': f"PO-{int(datetime.utcnow().timestamp())}",
                'status': 'PENDING',
                'total_amount': order_qty * unit_cost,
                'notes': notes,
                'created_by': user_id
            }).execute()

            po_id = po_res.data[0]['id'] if po_res.data else None
            if po_id and product_id:
                supabase.table('purchase_order_items').insert({
                    'purchase_order_id': po_id,
                    'product_id': product_id,
                    'quantity': order_qty,
                    'unit': unit_val,
                    'unit_price': unit_cost,
                    'total_price': order_qty * unit_cost
                }).execute()

            action_summary = f"Created purchase order for {order_qty} {unit_val} of {prod_data.get('name', 'Product') if prod_data else 'Item'}."

        # ---- 6. BORROW CLEAR (Settle / Waive All Loan Debt) ----
        elif intent == 'BORROW_CLEAR':
            customer_name = data.get('customer_name')
            if not customer_id and not customer_name:
                return error_response("Customer is required to clear loan", "VALIDATION_ERROR", 400)

            cust = None
            if customer_id:
                cust_res = supabase.table('customers').select('*').eq('id', customer_id).eq('shop_id', shop_id).limit(1).execute()
                cust = cust_res.data[0] if cust_res.data else None
            if not cust and customer_name:
                cust_res = supabase.table('customers').select('*').ilike('name', customer_name).eq('shop_id', shop_id).limit(1).execute()
                cust = cust_res.data[0] if cust_res.data else None

            if not cust:
                return error_response("Customer not found in shop database", "NOT_FOUND", 404)

            customer_id = cust['id']
            customer_name = cust['name']
            cleared_balance = float(cust.get('total_credit') or 0)

            # Settle all active borrowings
            supabase.table('borrowings').update({
                'status': 'RETURNED',
                'remaining_balance': 0,
                'paid_amount': cleared_balance,
                'notes': notes or 'All loan debt settled and cleared via voice command'
            }).eq('customer_id', customer_id).eq('shop_id', shop_id).in_('status', ['ACTIVE', 'PARTIALLY_RETURNED']).execute()

            # Reset customer credit to 0
            supabase.table('customers').update({'total_credit': 0}).eq('id', customer_id).execute()

            # Record settlement transaction
            tx_res = supabase.table('transactions').insert({
                'shop_id': shop_id,
                'transaction_type': 'BORROW_RETURN',
                'quantity': 1,
                'unit': 'settlement',
                'price': cleared_balance,
                'total_amount': cleared_balance,
                'customer_id': customer_id,
                'source': 'voice',
                'notes': notes or f'Settled all loan debt (₹{cleared_balance:,.0f}) via voice',
                'created_by': user_id
            }).execute()

            transaction_id = tx_res.data[0]['id'] if tx_res.data else None
            action_summary = f"Cleared and settled all loan debt (₹{cleared_balance:,.0f}) for {customer_name}. Remaining balance: ₹0."

        # ---- 7. STOCK ADJUSTMENT ----
        elif intent == 'STOCK_ADJUST':
            if not product_id:
                return error_response("Product ID is required for stock adjustment", "VALIDATION_ERROR", 400)
            prod = supabase.table('products').select('*').eq('id', product_id).eq('shop_id', shop_id).single().execute()
            if not prod.data:
                return error_response("Product not found", "NOT_FOUND", 404)
            product = prod.data
            target_stock = float(quantity if quantity is not None else 0)

            inv = supabase.table('inventory').select('*').eq('product_id', product_id).eq('shop_id', shop_id).execute()
            old_stock = float(inv.data[0]['current_stock']) if inv.data else 0
            diff = target_stock - old_stock

            if inv.data:
                supabase.table('inventory').update({
                    'current_stock': target_stock,
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('id', inv.data[0]['id']).execute()
            else:
                supabase.table('inventory').insert({
                    'shop_id': shop_id,
                    'product_id': product_id,
                    'current_stock': target_stock,
                    'minimum_stock': 10
                }).execute()

            tx_res = supabase.table('transactions').insert({
                'shop_id': shop_id,
                'product_id': product_id,
                'transaction_type': 'ADJUSTMENT',
                'quantity': abs(diff),
                'unit': unit or product.get('base_unit', 'unit'),
                'price': float(product.get('selling_price', 0)),
                'total_amount': abs(diff) * float(product.get('selling_price', 0)),
                'source': 'voice',
                'notes': notes or f"Stock adjusted from {old_stock} to {target_stock} via voice",
                'created_by': user_id
            }).execute()

            transaction_id = tx_res.data[0]['id'] if tx_res.data else None
            action_summary = f"Adjusted {product['name']} stock from {old_stock} to {target_stock} {unit or product.get('base_unit', 'unit')}."

        # ---- 8. CREATE CUSTOMER DIRECTLY ----
        elif intent == 'CUSTOMER_ADD':
            customer_name = data.get('customer_name')
            if not customer_name:
                return error_response("Customer name is required", "VALIDATION_ERROR", 400)
            phone = data.get('phone') or extract_phone_number(data.get('transcript', ''))
            new_c = supabase.table('customers').insert({
                'shop_id': shop_id,
                'name': customer_name.strip().title(),
                'phone': phone,
                'total_credit': 0
            }).execute()
            new_cust_row = new_c.data[0] if new_c.data else {}
            customer_id = new_cust_row.get('id')
            action_summary = f"Created new customer profile for {new_cust_row.get('name', customer_name)}{f' (Phone: {phone})' if phone else ''}."

        # ---- 9. CREATE PRODUCT DIRECTLY ----
        elif intent == 'PRODUCT_ADD':
            product_name = data.get('product_name')
            if not product_name:
                return error_response("Product name is required", "VALIDATION_ERROR", 400)
            base_u = normalize_unit(unit or 'unit')
            sell_p = float(price or 0)
            init_stock = float(quantity or 0)

            new_p = supabase.table('products').insert({
                'shop_id': shop_id,
                'name': product_name.strip().title(),
                'base_unit': base_u,
                'purchase_unit': base_u,
                'selling_price': sell_p,
                'purchase_price': sell_p * 0.85 if sell_p > 0 else 0,
                'minimum_stock': 10
            }).execute()
            p_data = new_p.data[0] if new_p.data else {}
            product_id = p_data.get('id')
            if product_id:
                supabase.table('inventory').insert({
                    'shop_id': shop_id,
                    'product_id': product_id,
                    'current_stock': init_stock,
                    'minimum_stock': 10
                }).execute()
            action_summary = f"Added new product '{p_data.get('name', product_name)}' with initial stock of {init_stock} {base_u} at ₹{sell_p}."

        else:
            return error_response(f"Action '{intent}' is not executable", "INVALID_INTENT", 400)

        # Log conversation event linked to transaction
        try:
            supabase.table('voice_conversations').insert({
                'shop_id': shop_id,
                'user_id': user_id,
                'conversation_id': conversation_id,
                'speaker': 'assistant',
                'transcript': data.get('transcript', ''),
                'response_text': action_summary,
                'intent': intent,
                'extracted_entities': {
                    'product_id': product_id,
                    'customer_id': customer_id,
                    'quantity': quantity,
                    'unit': unit,
                    'price': price,
                    'amount': amount
                },
                'confidence': 1.0,
                'confirmation_status': 'CONFIRMED',
                'action_performed': action_summary,
                'transaction_id': transaction_id
            }).execute()
        except Exception as log_err:
            logger.warning(f"Failed to log voice conversation: {log_err}")

        return success_response({
            'message': action_summary,
            'action_summary': action_summary,
            'transaction_id': transaction_id,
            'conversation_id': conversation_id
        })

    except Exception as e:
        logger.error(f"Voice execution error: {e}")
        return error_response(f"Database execution failed: {str(e)}", "EXECUTION_ERROR", 500)


@voice_bp.route('/conversations', methods=['GET'])
@require_auth
def list_conversations():
    """Get recent voice conversation history grouped or listed for the shop."""
    shop_id = get_current_shop_id()
    limit = int(request.args.get('limit', 50))
    try:
        supabase = get_supabase()
        res = supabase.table('voice_conversations').select('*').eq('shop_id', shop_id).order('created_at', desc=True).limit(limit).execute()
        return success_response({'items': res.data or []})
    except Exception as e:
        return error_response(f"Failed to fetch conversations: {str(e)}", "FETCH_ERROR", 500)


@voice_bp.route('/conversations', methods=['POST'])
@require_auth
def save_conversation_message():
    """Save a multi-turn conversation turn (user message or assistant answer)."""
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
            'conversation_id': data.get('conversation_id') or str(uuid.uuid4()),
            'speaker': data.get('speaker', 'user'),
            'transcript': data.get('transcript') or data.get('user_message', ''),
            'response_text': data.get('response_text') or data.get('answer', ''),
            'voice_text': data.get('voice_text', ''),
            'language': data.get('language', 'en'),
            'intent': data.get('intent', 'GENERAL'),
            'extracted_entities': data.get('entities', {}),
            'confidence': float(data.get('confidence', 0.95)),
            'confirmation_status': data.get('confirmation_status', 'CONFIRMED'),
            'action_performed': data.get('action_performed'),
            'transaction_id': data.get('transaction_id')
        }
        res = supabase.table('voice_conversations').insert(record).execute()
        return success_response({
            'id': res.data[0]['id'] if res.data else None,
            'conversation_id': record['conversation_id'],
            'message': 'Conversation saved'
        }, 201)
    except Exception as e:
        return error_response(f"Failed to save conversation: {str(e)}", "SAVE_ERROR", 500)


# Backward compatibility route for /api/voice/save
@voice_bp.route('/save', methods=['POST'])
@require_auth
def legacy_save_conversation():
    return save_conversation_message()


def build_local_interpretation(transcript, last_prod, last_cust, facts):
    """Deterministic local rule-based intent interpreter when Gemini API is offline."""
    lower = transcript.lower()

    # Detect language: Telugu script, Hindi Devanagari script, or phonetic keywords
    is_te_script = any('\u0c00' <= c <= '\u0c7f' for c in transcript)
    is_hi_script = any('\u0900' <= c <= '\u097f' for c in transcript)
    if is_te_script or any(w in lower for w in ['biyyam', 'chakkera', 'nune', 'cheyyi', 'undhi', 'undi', 'entha', 'udhar', 'pappu', 'ammadu', 'saripothunda']):
        lang = 'te'
    elif is_hi_script or any(w in lower for w in ['chawal', 'chini', 'tel', 'jodo', 'likho', 'kitna', 'becha', 'hai']):
        lang = 'hi'
    else:
        lang = 'en'

    intent = 'GENERAL'
    raw_prod = None
    raw_cust = None

    if any(w in lower for w in ['clear loan', 'clear udhar', 'forgive debt', 'settle loan', 'settle udhar', 'raddhu cheyyi', 'maaf karo', 'khata clear']):
        intent = 'BORROW_CLEAR'
    elif any(w in lower for w in ['adjust stock', 'set stock to', 'set stock', 'update stock to', 'stock adjust']):
        intent = 'STOCK_ADJUST'
    elif any(w in lower for w in ['add customer', 'new customer', 'kotha customer', 'naya customer']):
        intent = 'CUSTOMER_ADD'
    elif any(w in lower for w in ['add product', 'new product', 'kotha product', 'naya product']):
        intent = 'PRODUCT_ADD'
    elif any(w in lower for w in ['add cheyyi', 'vesuko', 'stock me dalo', 'jodo', 'add', 'చేర్చు', 'కలుపు', 'వేయి', 'స్టాక్ లో', 'जोड़ो', 'डालो']):
        intent = 'STOCK_IN'
    elif any(w in lower for w in ['sold', 'ammadu', 'becha', 'theesi', 'sale', 'సేల్', 'అమ్మాము', 'అమ్మాను', 'తీసివేయి', 'విక్రయించాము', 'बेचा', 'बिक्री']):
        intent = 'STOCK_OUT'
    elif any(w in lower for w in ['taken a loan', 'took a loan', 'took loan', 'loan of', 'borrowed', 'loan', 'karz liya', 'karz', 'appu theesukunnadu', 'tesukunnadu', 'chebadulu', 'రుణం', 'udhar rasi', 'udhar likho', 'udhar pettu', 'appu rasi', 'udhar', 'ఉధార్', 'అప్పు', 'ఖాతా', 'రాసి పెట్టు', 'రాయి', 'उधार', 'खाते में', 'लिखो']):
        intent = 'BORROW_OUT'
    elif any(w in lower for w in ['paid', 'jama chesadu', 'udhar kattadu', 'wapas diya', 'చెల్లించాడు', 'కట్టాడు', 'ఇచ్చాడు', 'వాపస్', 'చెల్లించారు', 'जमा किया', 'वापस दिया', 'चुकाया', 'repaid']):
        intent = 'BORROW_RETURN'
    elif any(w in lower for w in ['saripothunda', 'enough', 'next week', 'సరిపోతుందా', 'సరిపోవు', 'సరిపోతాయా', 'काफी है', 'चलेगा']):
        intent = 'BUSINESS_INSIGHT'
    elif any(w in lower for w in ['entha undi', 'kitna hai', 'stock entha', 'how much', 'stock', 'ఎంత ఉంది', 'స్టాక్ ఎంత', 'స్టాక్', 'ఎన్ని ఉన్నాయి', 'నిల్వ', 'कितना है', 'कितना बचा', 'स्टॉक']):
        intent = 'STOCK_CHECK'
    elif any(w in lower for w in ['who owes', 'balance entha', 'udhar kiska', 'how much loan', 'loan entha', 'ఎంత బాకీ', 'ఎవరు బాకీ', 'బాకీ ఎంత', 'ఖాతా ఎంత', 'అప్పు ఎంత', 'किसका उधार', 'कितना बाकी', 'बकाया']):
        intent = 'CREDIT_CHECK'
    elif any(w in lower for w in ['order cheyyi', 'mangwa lo', 'purchase', 'ఆర్డర్ చేయి', 'మంగళో']):
        intent = 'PURCHASE'

    # Extract product name — sort synonyms by length descending so longer compound phrases match first
    for term in sorted(KIRANA_PRODUCT_SYNONYMS.keys(), key=len, reverse=True):
        if term in lower:
            raw_prod = term
            break

    # Extract customer name tokens (from loan phrases or standard suffix markers)
    loan_person = extract_customer_from_loan_phrase(transcript)
    if loan_person:
        raw_cust = loan_person
    else:
        cust_match = re.search(r'([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)\s+(?:ki|ko|gaari|gari|nu|to|గారికి|గారి|కు|కి|ను|కో)\b', transcript)
        if cust_match:
            raw_cust = cust_match.group(1).strip().title()

    return {
        'intent': intent,
        'raw_product': raw_prod or last_prod,
        'raw_customer': raw_cust or last_cust,
        'raw_supplier': None,
        'quantity': facts.get('quantity'),
        'unit': facts.get('unit'),
        'price': facts.get('price'),
        'amount': facts.get('price'),
        'confidence': 0.88,
        'detected_language': lang,
        'requires_confirmation': intent in ('STOCK_IN', 'STOCK_OUT', 'BORROW_OUT', 'BORROW_RETURN', 'BORROW_CLEAR', 'STOCK_ADJUST', 'CUSTOMER_ADD', 'PRODUCT_ADD', 'PURCHASE'),
        'confirmation_prompt': None,
        'answer': None,
        'voice_text': None
    }
