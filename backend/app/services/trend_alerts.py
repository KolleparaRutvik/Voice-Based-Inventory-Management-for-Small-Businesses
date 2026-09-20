"""DukaanSetu — Trend-Based Stock & Sales Alert Engine.
Analyzes sales velocity, inventory depletion rates, upcoming demand surges,
and generates proactive alerts for all 12 retail verticals.
"""
import logging
from datetime import datetime, timedelta, timezone
from app.utils.supabase_client import get_supabase

logger = logging.getLogger(__name__)


def generate_trend_alerts(shop_id):
    """Analyze sales velocity and stock trends to produce proactive actionable alerts for the shop.
    Returns a list of structured alert dictionaries.
    """
    alerts = []
    if not shop_id:
        return alerts

    try:
        supabase = get_supabase()

        # 1. Fetch products & inventory
        prods_res = supabase.table('products').select('*').eq('shop_id', shop_id).eq('is_active', True).execute()
        products = prods_res.data or []
        if not products:
            return alerts

        inv_res = supabase.table('inventory').select('*').eq('shop_id', shop_id).execute()
        inv_map = {i['product_id']: i for i in (inv_res.data or [])}

        # 2. Fetch sales transactions in the past 14 days
        two_weeks_ago = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
        tx_res = supabase.table('transactions').select('*').eq('shop_id', shop_id).in_('transaction_type', ['SALE', 'STOCK_OUT']).gte('created_at', two_weeks_ago).execute()
        transactions = tx_res.data or []

        # Aggregate sales per product
        sales_7d = {}
        sales_14d = {}
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

        for tx in transactions:
            pid = tx.get('product_id')
            if not pid:
                continue
            qty = float(tx.get('quantity_in_base_unit') or tx.get('quantity') or 0)
            created = tx.get('created_at', '')

            sales_14d[pid] = sales_14d.get(pid, 0.0) + qty
            if created >= seven_days_ago:
                sales_7d[pid] = sales_7d.get(pid, 0.0) + qty

        # 3. Analyze each product for trends and stock thresholds
        for p in products:
            pid = p['id']
            pname = p.get('name', 'Product')
            base_u = p.get('base_unit', 'unit')
            min_stk = float(p.get('minimum_stock') or 10.0)
            rec_stk = float(p.get('recommended_stock') or 50.0)
            reorder_qty = float(p.get('reorder_quantity') or 20.0)

            inv = inv_map.get(pid, {})
            current_stk = float(inv.get('current_stock', 0.0))

            qty_sold_7d = sales_7d.get(pid, 0.0)
            daily_velocity = qty_sold_7d / 7.0

            # Calculate days of stock remaining
            days_left = (current_stk / daily_velocity) if daily_velocity > 0 else (999 if current_stk > min_stk else 2)

            # Check 1: Critical Low Stock
            if current_stk <= min_stk:
                alerts.append({
                    'id': f"alert-low-{pid}",
                    'type': 'LOW_STOCK',
                    'urgency': 'HIGH',
                    'title': f"🔴 {pname} Running Low",
                    'message': f"Stock is down to {current_stk} {base_u} (minimum required: {min_stk} {base_u}). Reorder {reorder_qty} {base_u} immediately.",
                    'product_id': pid,
                    'product_name': pname,
                    'current_stock': current_stk,
                    'threshold': min_stk,
                    'recommended_reorder': reorder_qty,
                    'unit': base_u,
                    'created_at': datetime.now(timezone.utc).isoformat()
                })

            # Check 2: Fast-Moving Surge
            elif daily_velocity > 0 and days_left < 5:
                alerts.append({
                    'id': f"alert-fast-{pid}",
                    'type': 'FAST_MOVING',
                    'urgency': 'HIGH',
                    'title': f"⚡ {pname} Selling Fast",
                    'message': f"Sales rate is {daily_velocity:.1f} {base_u}/day. Only {days_left:.1f} days of inventory remaining ({current_stk} {base_u} left).",
                    'product_id': pid,
                    'product_name': pname,
                    'current_stock': current_stk,
                    'daily_velocity': round(daily_velocity, 1),
                    'days_remaining': round(days_left, 1),
                    'recommended_reorder': reorder_qty,
                    'unit': base_u,
                    'created_at': datetime.now(timezone.utc).isoformat()
                })

            # Check 3: Near Threshold Warning
            elif current_stk <= min_stk * 1.3:
                alerts.append({
                    'id': f"alert-reorder-{pid}",
                    'type': 'REORDER_NOW',
                    'urgency': 'MEDIUM',
                    'title': f"⚠️ {pname} Reorder Recommended",
                    'message': f"Stock at {current_stk} {base_u}, nearing safe buffer {min_stk * 1.3:.0f} {base_u}. Consider ordering {reorder_qty} {base_u}.",
                    'product_id': pid,
                    'product_name': pname,
                    'current_stock': current_stk,
                    'threshold': min_stk,
                    'recommended_reorder': reorder_qty,
                    'unit': base_u,
                    'created_at': datetime.now(timezone.utc).isoformat()
                })

        # 4. Check upcoming festival / seasonal surges
        try:
            from app.services.festival_service import analyze_festival_demand
            fest_analysis = analyze_festival_demand(shop_id=shop_id, window_days=15)
            fest = fest_analysis.get('festival')
            if fest:
                ev_name = fest.get('event', 'Upcoming Festival')
                d_until = fest.get('days_until', 0)
                recs = [r for r in fest_analysis.get('recommendations', []) if r.get('reorder_needed')]
                if recs:
                    top_rec = recs[0]
                    alerts.append({
                        'id': f"alert-fest-{fest.get('id', 'event')}",
                        'type': 'FESTIVAL_SURGE',
                        'urgency': 'HIGH' if d_until <= 5 else 'MEDIUM',
                        'title': f"🎉 {ev_name} Demand Spike ({d_until} days left)",
                        'message': f"{ev_name} demand projected to increase 1.5x-1.8x. {len(recs)} key products require advance stock procurement (e.g. {top_rec.get('item_name')}).",
                        'data': {'event': ev_name, 'days_left': d_until, 'items_needed': len(recs)},
                        'created_at': datetime.now(timezone.utc).isoformat()
                    })
        except Exception as f_err:
            logger.debug(f"Festival trend alert check skipped: {f_err}")

    except Exception as e:
        logger.error(f"Error generating trend alerts: {e}")

    return alerts


def get_voice_trend_insights(shop_id, language='te'):
    """Generate conversational spoken and written answer for voice inquiries about shop trends:
    'What items are selling fast?', 'ఏ వస్తువులు ఎక్కువగా అమ్ముడవుతున్నాయి?', etc.
    """
    alerts = generate_trend_alerts(shop_id)

    fast_items = [a for a in alerts if a.get('type') in ('FAST_MOVING', 'LOW_STOCK')]
    fest_alert = next((a for a in alerts if a.get('type') == 'FESTIVAL_SURGE'), None)

    # Fallback to top products if no sales alerts yet
    if not fast_items:
        try:
            supabase = get_supabase()
            p_res = supabase.table('products').select('*').eq('shop_id', shop_id).limit(4).execute()
            top_prods = [p['name'] for p in (p_res.data or [])]
        except Exception:
            top_prods = ['Top inventory items']

        if language == 'te':
            answer = f"ప్రస్తుతం మీ స్టాక్ స్థిరంగా ఉంది. రెగ్యులర్ డిమాండ్ ఉన్న వస్తువులు: {', '.join(top_prods[:3])}. అన్ని సజావుగా ఉన్నాయి."
            voice_text = f"స్టాక్ స్థిరంగా ఉంది. ప్రధాన వస్తువులు: {', '.join(top_prods[:2])}."
        elif language == 'hi':
            answer = f"वर्तमान में आपका स्टॉक स्थिर है। मुख्य मांग वाले सामान: {', '.join(top_prods[:3])}।"
            voice_text = f"स्टॉक सामान्य है। मुख्य वस्तुएं: {', '.join(top_prods[:2])}।"
        else:
            answer = f"Your stock levels are stable. Core demanded items: {', '.join(top_prods[:3])}."
            voice_text = f"Stock is stable. Main items: {', '.join(top_prods[:2])}."

        return {'answer': answer, 'voice_text': voice_text, 'alerts': alerts}

    # Format fast items
    names = [a.get('product_name', 'Item') for a in fast_items[:3]]
    names_str = ", ".join(names)

    if language == 'te':
        answer = f"ప్రస్తుతం మీ దుకాణంలో ఎక్కువగా కదులుతున్న మరియు స్టాక్ తక్కువగా ఉన్న వస్తువులు: {names_str}."
        if fest_alert:
            answer += f"\nఅలాగే {fest_alert['title']} దృష్ట్యా ముందస్తుగా సరుకు ఆర్డర్ చేయడం మంచిది."
        else:
            answer += "\nస్టాక్ ఔట్ కాకుండా వెంటనే రీఆర్డర్ చేసుకోండి."
        voice_text = f"ఎక్కువగా అమ్ముడవుతున్న మరియు స్టాక్ తక్కువగా ఉన్న వస్తువులు: {names_str}. రీఆర్డర్ చేయడం మంచిది."

    elif language == 'hi':
        answer = f"वर्तमान में सबसे तेजी से बिकने वाले और कम स्टॉक वाले सामान: {names_str}."
        if fest_alert:
            answer += f"\nसाथ ही {fest_alert['title']} को ध्यान में रखते हुए अतिरिक्त माल मंगाएं।"
        else:
            answer += "\nकृपया स्टॉक खत्म होने से पहले सप्लायर को ऑर्डर दें।"
        voice_text = f"तेजी से बिकने वाले सामान: {names_str}. तुरंत रीऑर्डर करें।"

    else:
        answer = f"Fastest moving and low-stock items right now: {names_str}."
        if fest_alert:
            answer += f"\nUpcoming festival alert: {fest_alert['title']}."
        else:
            answer += "\nConsider placing reorders before stockouts occur."
        voice_text = f"Trending and low stock items: {names_str}. Reorder recommended."

    return {
        'answer': answer,
        'voice_text': voice_text,
        'alerts': alerts,
        'fast_items': names
    }
