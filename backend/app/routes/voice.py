"""Voice routes — upload, transcribe, interpret, history."""
from flask import Blueprint, request
from app.utils import require_auth, success_response, error_response, get_current_shop_id, get_current_user_id
from app.utils.supabase_client import get_supabase

voice_bp = Blueprint('voice', __name__)


@voice_bp.route('/upload', methods=['POST'])
@require_auth
def upload_audio():
    """Upload audio recording."""
    shop_id = get_current_shop_id()
    
    if 'audio' not in request.files:
        return error_response("Audio file is required", "VALIDATION_ERROR")
    
    audio_file = request.files['audio']
    
    try:
        supabase = get_supabase()
        
        # Upload to Supabase Storage
        from datetime import datetime
        date_path = datetime.utcnow().strftime('%Y-%m-%d')
        file_path = f"voice-recordings/{shop_id}/{date_path}/{audio_file.filename}"
        
        # For now, store the path reference
        # Actual storage upload would use supabase.storage.from_('voice-recordings').upload(...)
        
        return success_response({
            'audio_url': file_path,
            'message': 'Audio uploaded successfully',
        }, 201)
        
    except Exception as e:
        return error_response(f"Upload failed: {str(e)}", "UPLOAD_ERROR", 500)


@voice_bp.route('/interpret', methods=['POST'])
@require_auth
def interpret_voice():
    """Use AI to interpret voice transcript into structured intent."""
    data = request.get_json()
    if not data or not data.get('transcript'):
        return error_response("Transcript is required", "VALIDATION_ERROR")
    
    try:
        import os
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return error_response("AI service not configured", "CONFIG_ERROR", 500)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""You are a smart inventory assistant for an Indian kirana/grocery shop.
        
Analyze the following voice command and extract structured data.
The user may speak in English, Telugu, Hindi, or mixed language.

Common Telugu words:
- biyyam = rice
- chakkera = sugar  
- nune = oil
- pappu = dal
- bellam = jaggery
- add cheyyi / vesuko = add/stock in
- ammadu / sold = sold/sale
- icha / ichanu = gave (borrowing)
- vachayi = came/arrived (stock in)
- entha undi = how much is there (stock check)
- return chesadu = returned

Voice command: "{data['transcript']}"

Respond ONLY with valid JSON (no markdown, no code blocks):
{{
    "intent": "STOCK_IN|STOCK_OUT|SALE|PURCHASE|BORROW_OUT|BORROW_RETURN|STOCK_CHECK|QUERY|UNKNOWN",
    "product": "product name in English or null",
    "quantity": number or null,
    "unit": "kg|gram|litre|ml|piece|packet|box|bag|carton|dozen|quintal or null",
    "price": number or null,
    "supplier": "supplier name or null",
    "customer": "customer name or null",
    "confidence": 0.0 to 1.0
}}"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse JSON from response
        import json
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('\n', 1)[1].rsplit('```', 1)[0]
        
        intent_data = json.loads(response_text)
        
        return success_response({
            'intent': intent_data,
            'transcript': data['transcript'],
            'language': data.get('language', 'auto'),
        })
        
    except json.JSONDecodeError:
        return error_response("Failed to parse AI response", "AI_ERROR", 500)
    except Exception as e:
        return error_response(f"AI interpretation failed: {str(e)}", "AI_ERROR", 500)


@voice_bp.route('', methods=['GET'])
@require_auth
def list_voice_history():
    """Get voice conversation history."""
    shop_id = get_current_shop_id()
    
    try:
        supabase = get_supabase()
        result = supabase.table('voice_conversations').select('*').eq('shop_id', shop_id).order('created_at', desc=True).limit(50).execute()
        
        return success_response({"items": result.data or []})
        
    except Exception as e:
        return error_response(f"Failed to fetch voice history: {str(e)}", "FETCH_ERROR", 500)


@voice_bp.route('/<voice_id>', methods=['DELETE'])
@require_auth
def delete_voice_record(voice_id):
    """Delete a voice conversation record."""
    shop_id = get_current_shop_id()
    
    try:
        supabase = get_supabase()
        supabase.table('voice_conversations').delete().eq('id', voice_id).eq('shop_id', shop_id).execute()
        return success_response({"message": "Voice record deleted"})
    except Exception as e:
        return error_response(f"Failed to delete: {str(e)}", "DELETE_ERROR", 500)
