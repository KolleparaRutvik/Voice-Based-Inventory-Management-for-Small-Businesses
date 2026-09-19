"""DukaanSetu — Festival Inventory Demand & 15-Day Prior Recommendation Engine.

Analyzes the festival_inventory_demand_dataset.xlsx dataset, tracks the annual festival calendar,
identifies festivals within the active 15-day prior notice window, evaluates live shop inventory against
demand surge multipliers, generates smart procurement recommendations, and manages proactive notifications.
"""
import os
import logging
from datetime import datetime, date, timedelta
from app.utils.supabase_client import get_supabase

logger = logging.getLogger(__name__)

# Cached in-memory dataset
_CACHED_FESTIVAL_DATASET = None

# Default Annual Festival Calendar (anchor dates for 2026, rolling forward)
ANNUAL_FESTIVAL_CALENDAR = [
    {
        'event': 'Makar Sankranti / Pongal',
        'month': 1,
        'day': 14,
        'description': 'Harvest festival celebrated across South India with sweets, pongal, rice, and jaggery.',
        'telugu_name': 'మకర సంక్రాంతి / పొంగల్',
        'hindi_name': 'मकर संक्रांति / पोंगल'
    },
    {
        'event': 'Ugadi',
        'month': 3,
        'day': 20,
        'description': 'Telugu & Kannada New Year celebrated with Ugadi Pachadi, jaggery, raw mango, and tamarind.',
        'telugu_name': 'ఉగాది పండుగ',
        'hindi_name': 'उगादी'
    },
    {
        'event': 'Eid / Ramadan',
        'month': 3,
        'day': 31,
        'description': 'Festive season with high demand for dates, seviyan/vermicelli, dry fruits, and basmati rice.',
        'telugu_name': 'రంజాన్ / ఈద్',
        'hindi_name': 'ईद / रमजान'
    },
    {
        'event': 'Onam',
        'month': 8,
        'day': 28,
        'description': 'Harvest festival celebrated with Onam Sadya feast, rice, coconut oil, and jaggery payasam.',
        'telugu_name': 'ఓనం పండుగ',
        'hindi_name': 'ओणम'
    },
    {
        'event': 'Ganesh Chaturthi',
        'month': 9,
        'day': 14,
        'description': 'Major celebration with modak sweets, puja items, coconut, sugar, and rice.',
        'telugu_name': 'వినాయక చవితి',
        'hindi_name': 'गणेश चतुर्थी'
    },
    {
        'event': 'Navratri / Dussehra',
        'month': 10,
        'day': 2,
        'description': '9-day festive season and Vijayadashami with high demand for flour, puja items, sugar, and oil.',
        'telugu_name': 'నవరాత్రులు / విజయదశమి (దసరా)',
        'hindi_name': 'नवरात्रि / दशहरा'
    },
    {
        'event': 'Diwali / Dhanteras',
        'month': 11,
        'day': 1,
        'description': 'Festival of Lights with massive demand for edible oil, ghee, sugar, maida, dry fruits, and diyas.',
        'telugu_name': 'దీపావళి / ధనత్రయోదశి',
        'hindi_name': 'दिवाली / धनतेरस'
    },
    {
        'event': 'Wedding Season',
        'month': 11,
        'day': 15,
        'description': 'Peak auspicious wedding season requiring bulk rice, oil, sugar, spices, and pulses.',
        'telugu_name': 'పెళ్లిళ్ల సీజన్',
        'hindi_name': 'शादी का सीजन'
    },
    {
        'event': 'Christmas / New Year',
        'month': 12,
        'day': 25,
        'description': 'Year-end celebrations with high baking and beverage demand: maida, butter, sugar, coffee, tea.',
        'telugu_name': 'క్రిస్మస్ / న్యూ ఇయర్',
        'hindi_name': 'क्रिसमस / न्यू ईयर'
    }
]

# Canonical item mapping to shop products and aliases
ITEM_SYNONYM_MAP = {
    'rice': ['rice', 'biyyam', 'basmati', 'sona masoori'],
    'basmati rice': ['rice', 'biyyam', 'basmati'],
    'sugar': ['sugar', 'chakkera', 'cheeni'],
    'jaggery': ['jaggery', 'bellam', 'gud'],
    'edible oil': ['oil', 'nune', 'sunflower oil', 'cooking oil'],
    'cooking oil': ['oil', 'nune', 'sunflower oil', 'edible oil'],
    'pulses': ['toor dal', 'kandi pappu', 'dal', 'pulses', 'pappu'],
    'tea': ['tea', 'tea podi', 'red label'],
    'coffee': ['coffee', 'coffee podi', 'nescafe'],
}


def load_festival_dataset(excel_path=None):
    """Loads and caches all rows from festival_inventory_demand_dataset.xlsx."""
    global _CACHED_FESTIVAL_DATASET
    if _CACHED_FESTIVAL_DATASET is not None:
        return _CACHED_FESTIVAL_DATASET

    if not excel_path:
        cur_file = os.path.abspath(__file__)
        candidates = [
            os.path.abspath(os.path.join(os.path.dirname(cur_file), '..', '..', '..', 'database', 'festival_inventory_demand_dataset.xlsx')),
            os.path.abspath(os.path.join(os.path.dirname(cur_file), '..', '..', 'database', 'festival_inventory_demand_dataset.xlsx')),
            os.path.abspath(os.path.join(os.getcwd(), 'database', 'festival_inventory_demand_dataset.xlsx')),
            os.path.abspath(os.path.join(os.getcwd(), '..', 'database', 'festival_inventory_demand_dataset.xlsx')),
        ]
        for c in candidates:
            if os.path.exists(c):
                excel_path = c
                break

    dataset = []
    if not os.path.exists(excel_path):
        logger.warning(f"Festival dataset file not found at {excel_path}, falling back to built-in rules.")
        return []

    try:
        import openpyxl
        wb = openpyxl.load_workbook(excel_path, data_only=True)
        sheet = wb.active
        headers = [sheet.cell(1, c).value for c in range(1, sheet.max_column + 1)]
        
        for r in range(2, sheet.max_row + 1):
            row_data = {}
            for col_idx, h in enumerate(headers, start=1):
                if h:
                    row_data[h] = sheet.cell(r, col_idx).value
            
            if row_data.get('event') and row_data.get('item'):
                dataset.append({
                    'event': str(row_data.get('event')).strip(),
                    'region': str(row_data.get('region') or '').strip(),
                    'item': str(row_data.get('item')).strip(),
                    'category': str(row_data.get('category') or '').strip(),
                    'unit': str(row_data.get('unit') or 'kg').strip(),
                    'multiplier': float(row_data.get('illustrative_demand_multiplier') or 1.3),
                    'lead_time_days': int(row_data.get('supplier_lead_time_days') or 7),
                    'prep_days': int(row_data.get('recommended_prep_days') or 10),
                    'demand_level': str(row_data.get('demand_level') or 'Moderate').strip(),
                    'note': str(row_data.get('note') or '').strip()
                })
        
        _CACHED_FESTIVAL_DATASET = dataset
        logger.info(f"Successfully loaded {len(dataset)} festival demand records from {excel_path}")
        return _CACHED_FESTIVAL_DATASET

    except Exception as e:
        logger.error(f"Failed to load festival Excel dataset: {e}")
        return []


def get_festival_date(event_info, reference_date):
    """Calculates the upcoming occurrence date of a festival relative to reference_date."""
    ref = reference_date if isinstance(reference_date, date) else reference_date.date()
    target_year = ref.year
    f_date = date(target_year, event_info['month'], event_info['day'])
    
    # If the festival has already passed more than 3 days ago in the current year, check next year
    if (ref - f_date).days > 3:
        f_date = date(target_year + 1, event_info['month'], event_info['day'])
    
    return f_date


def get_upcoming_festivals(window_days=15, reference_date=None):
    """Returns all festivals with their upcoming date, countdown, and active 15-day window flag."""
    if reference_date is None:
        # Default to today (or simulated 2026-09-19)
        ref_dt = datetime.now()
    elif isinstance(reference_date, str):
        ref_dt = datetime.fromisoformat(reference_date.replace('Z', ''))
    else:
        ref_dt = reference_date

    ref_date = ref_dt.date() if isinstance(ref_dt, datetime) else ref_dt
    results = []

    for item in ANNUAL_FESTIVAL_CALENDAR:
        f_date = get_festival_date(item, ref_date)
        days_until = (f_date - ref_date).days
        
        # 15-day prior alert window criteria: 0 <= days_until <= window_days
        is_prior_window = 0 <= days_until <= window_days
        is_upcoming = 0 <= days_until <= 60

        results.append({
            'event': item['event'],
            'date': f_date.isoformat(),
            'days_until': days_until,
            'is_prior_window': is_prior_window,
            'is_upcoming': is_upcoming,
            'description': item['description'],
            'telugu_name': item['telugu_name'],
            'hindi_name': item['hindi_name']
        })

    # Sort primarily by days_until (closest first)
    results.sort(key=lambda x: (x['days_until'] < 0, x['days_until']))
    return results


def match_product_for_item(dataset_item_name, products):
    """Matches a dataset item string to a shop product using name and keywords."""
    norm_item = dataset_item_name.lower().strip()
    synonyms = ITEM_SYNONYM_MAP.get(norm_item, [norm_item])

    for p in products:
        p_name = p['name'].lower()
        p_local = (p.get('local_name') or '').lower()
        
        # Direct match
        if norm_item in p_name or norm_item in p_local:
            return p
        
        # Synonym match
        for s in synonyms:
            if s in p_name or s in p_local:
                return p
                
    return None


def analyze_festival_demand(shop_id, festival_name=None, window_days=15, reference_date=None):
    """Performs deep inventory gap analysis for an upcoming festival against shop stock."""
    dataset = load_festival_dataset()
    upcoming = get_upcoming_festivals(window_days=window_days, reference_date=reference_date)
    
    # 1. Select the target festival
    target_festival = None
    if festival_name:
        fn_clean = festival_name.lower().replace('/', ' ').strip()
        for f in upcoming:
            f_clean = f['event'].lower().replace('/', ' ')
            if fn_clean in f_clean or f_clean in fn_clean:
                target_festival = f
                break

    # If not specified or not found, pick the nearest active 15-day window festival, or closest upcoming
    if not target_festival:
        active_festivals = [f for f in upcoming if f['is_prior_window']]
        target_festival = active_festivals[0] if active_festivals else (upcoming[0] if upcoming else None)

    if not target_festival:
        return {'festival': None, 'recommendations': [], 'summary': 'No upcoming festival found'}

    selected_event_name = target_festival['event']
    days_left = target_festival['days_until']

    # 2. Filter dataset rules for this event
    event_rules = [r for r in dataset if r['event'].lower() == selected_event_name.lower()]
    if not event_rules:
        # Fallback partial match on event name
        event_rules = [r for r in dataset if any(part.strip().lower() in r['event'].lower() for part in selected_event_name.split('/'))]

    # 3. Fetch live shop products and inventory
    supabase = get_supabase()
    prods_res = supabase.table('products').select('*').eq('shop_id', shop_id).eq('is_active', True).execute()
    inv_res = supabase.table('inventory').select('*').eq('shop_id', shop_id).execute()
    suppliers_res = supabase.table('suppliers').select('*').eq('shop_id', shop_id).execute()

    products = prods_res.data or []
    inv_map = {i['product_id']: float(i.get('current_stock', 0)) for i in (inv_res.data or [])}
    supp_map = {s['id']: s for s in (suppliers_res.data or [])}
    primary_supplier = (suppliers_res.data or [{}])[0]

    recommendations = []
    seasonal_new_items = []
    total_estimated_reorder_cost = 0.0

    for rule in event_rules:
        item_name = rule['item']
        multiplier = rule['multiplier']
        lead_time = rule['lead_time_days']
        prep_days = rule['prep_days']
        unit = rule['unit']
        demand_level = rule['demand_level']

        matched_prod = match_product_for_item(item_name, products)

        if matched_prod:
            pid = matched_prod['id']
            current_stock = inv_map.get(pid, 0.0)
            base_unit = matched_prod.get('base_unit', unit)
            min_stock = float(matched_prod.get('minimum_stock', 20))
            rec_stock = float(matched_prod.get('recommended_stock', min_stock * 2)) or 50.0
            purchase_price = float(matched_prod.get('purchase_price', 0))

            # Calculated festival surge target
            surge_target = round(rec_stock * multiplier, 1)
            deficit = max(0.0, round(surge_target - current_stock, 1))

            # Lead time urgency calculation
            # If days remaining until festival <= supplier lead time, shopkeeper must order immediately!
            is_lead_time_critical = days_left <= lead_time
            is_deficit = deficit > 0

            item_cost = round(deficit * purchase_price, 2)
            total_estimated_reorder_cost += item_cost

            supp = supp_map.get(matched_prod.get('supplier_id'), primary_supplier)

            recommendations.append({
                'item_name': item_name,
                'product_id': pid,
                'product_name': matched_prod['name'],
                'local_name': matched_prod.get('local_name'),
                'category': matched_prod.get('category'),
                'current_stock': current_stock,
                'base_unit': base_unit,
                'multiplier': multiplier,
                'surge_target': surge_target,
                'deficit': deficit,
                'reorder_needed': is_deficit,
                'supplier_lead_time_days': lead_time,
                'recommended_prep_days': prep_days,
                'is_lead_time_critical': is_lead_time_critical,
                'demand_level': demand_level,
                'unit_price': purchase_price,
                'estimated_reorder_cost': item_cost,
                'supplier_id': matched_prod.get('supplier_id') or primary_supplier.get('id'),
                'supplier_name': supp.get('name', 'Local Wholesaler'),
                'is_stocked': True
            })
        else:
            # Seasonal item not yet stocked in shop inventory
            seasonal_new_items.append({
                'item_name': item_name,
                'category': rule['category'],
                'unit': unit,
                'multiplier': multiplier,
                'supplier_lead_time_days': lead_time,
                'recommended_prep_days': prep_days,
                'demand_level': demand_level,
                'is_stocked': False,
                'note': f"High festival demand ({multiplier}x). Consider procuring before festival."
            })

    # Sort recommendations: reorder needed first, then lead time critical, then highest deficit
    recommendations.sort(key=lambda x: (not x['reorder_needed'], not x['is_lead_time_critical'], -x['deficit']))

    deficit_items_count = sum(1 for r in recommendations if r['reorder_needed'])

    return {
        'festival': target_festival,
        'rules_count': len(event_rules),
        'is_prior_window': target_festival['is_prior_window'],
        'days_until': days_left,
        'recommendations': recommendations,
        'deficit_items_count': deficit_items_count,
        'seasonal_new_items': seasonal_new_items,
        'total_estimated_reorder_cost': round(total_estimated_reorder_cost, 2),
        'generated_at': datetime.utcnow().isoformat()
    }


def sync_festival_notifications(shop_id, reference_date=None):
    """Automatically synchronizes proactive notifications into PostgreSQL notifications table
    whenever a festival enters the 15-day prior notice window."""
    try:
        analysis = analyze_festival_demand(shop_id=shop_id, window_days=15, reference_date=reference_date)
        fest = analysis.get('festival')
        if not fest or not fest.get('is_prior_window'):
            return {'synced': False, 'reason': 'No festival currently in 15-day prior window'}

        event_name = fest['event']
        days_until = fest['days_until']
        deficit_count = analysis.get('deficit_items_count', 0)
        recs = [r for r in analysis.get('recommendations', []) if r['reorder_needed']]

        supabase = get_supabase()

        # Check existing unread or recent festival notifications to avoid duplicates
        existing = supabase.table('notifications').select('id, title, created_at').eq('shop_id', shop_id).eq('type', 'FESTIVAL_DEMAND').execute()
        existing_rows = existing.data or []

        # If a notification was created in the last 24 hours for this event, do not flood
        twenty_four_hours_ago = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        already_notified = any(event_name in r.get('title', '') and (r.get('created_at') or '') >= twenty_four_hours_ago for r in existing_rows)

        top_deficits = [f"{r['item_name']} (+{r['deficit']} {r['base_unit']})" for r in recs[:3]]
        deficits_text = ", ".join(top_deficits) if top_deficits else "Key festival staples"

        title = f"🎉 Upcoming Festival Alert: {event_name} in {days_until} Days"
        message = (
            f"{event_name} is arriving in {days_until} days. Demand multiplier is expected up to 1.8x. "
            f"You have {deficit_count} items with stock deficits ({deficits_text}). "
            f"Supplier lead time requires placing purchase orders now to avoid festival stockout."
        )

        notification_payload = {
            'shop_id': shop_id,
            'type': 'FESTIVAL_DEMAND',
            'title': title,
            'message': message,
            'data': {
                'festival_name': event_name,
                'days_until': days_until,
                'deficit_count': deficit_count,
                'total_cost': analysis.get('total_estimated_reorder_cost', 0),
                'top_items': [
                    {
                        'product_id': r['product_id'],
                        'product_name': r['product_name'],
                        'deficit': r['deficit'],
                        'unit': r['base_unit'],
                        'unit_price': r['unit_price'],
                        'supplier_id': r['supplier_id']
                    }
                    for r in recs
                ]
            },
            'is_read': False
        }

        if not already_notified:
            insert_res = supabase.table('notifications').insert(notification_payload).execute()
            logger.info(f"Inserted new festival demand notification for {event_name} (in {days_until} days)")
            return {'synced': True, 'notification': insert_res.data[0] if insert_res.data else None}
        else:
            return {'synced': True, 'already_notified': True, 'message': 'Notification up to date'}

    except Exception as e:
        logger.error(f"Error in sync_festival_notifications: {e}")
        return {'synced': False, 'error': str(e)}
