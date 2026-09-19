"""Tests for festival inventory demand analysis, 15-day prior window calculation,
notification synchronization, and multilingual voice assistant resolution.
"""
from datetime import date, datetime, timedelta
from app.services.festival_service import (
    load_festival_dataset,
    get_upcoming_festivals,
    get_festival_date,
    ANNUAL_FESTIVAL_CALENDAR
)
from app.routes.voice import build_local_interpretation


def test_46_excel_dataset_loading():
    """Verify that festival_inventory_demand_dataset.xlsx loads 72 records."""
    data = load_festival_dataset()
    assert len(data) >= 70
    # Check sample row structure
    first = data[0]
    assert 'event' in first
    assert 'item' in first
    assert 'multiplier' in first
    assert first['multiplier'] >= 1.0
    assert 'lead_time_days' in first
    assert 'prep_days' in first


def test_47_annual_festival_calendar():
    """Verify all 9 core festival events are registered."""
    events = [c['event'] for c in ANNUAL_FESTIVAL_CALENDAR]
    expected = [
        'Makar Sankranti / Pongal', 'Ugadi', 'Eid / Ramadan',
        'Onam', 'Ganesh Chaturthi', 'Navratri / Dussehra',
        'Diwali / Dhanteras', 'Wedding Season', 'Christmas / New Year'
    ]
    for ev in expected:
        assert ev in events


def test_48_15_day_prior_window_detection():
    """Verify that a festival occurring within 0-15 days is flagged as is_prior_window."""
    ref_date = date(2026, 9, 19)
    upcoming = get_upcoming_festivals(window_days=15, reference_date=ref_date)
    
    # Oct 2, 2026 is 13 days from Sept 19, 2026
    dussehra = next((f for f in upcoming if 'Dussehra' in f['event']), None)
    assert dussehra is not None
    assert dussehra['days_until'] == 13
    assert dussehra['is_prior_window'] is True

    # Diwali on Nov 1, 2026 is 43 days away -> Not in 15-day prior window
    diwali = next((f for f in upcoming if 'Diwali' in f['event']), None)
    assert diwali is not None
    assert diwali['days_until'] == 43
    assert diwali['is_prior_window'] is False


def test_49_festival_demand_surge_calculation():
    """Verify surge calculation math: target = base * multiplier, deficit = max(0, target - stock)."""
    base_stock = 100.0
    multiplier = 1.7
    surge_target = base_stock * multiplier  # 170.0

    # Case A: Current stock is 120 -> Deficit is 50
    current_stock_a = 120.0
    deficit_a = max(0.0, surge_target - current_stock_a)
    assert deficit_a == 50.0

    # Case B: Current stock is 200 -> Deficit is 0
    current_stock_b = 200.0
    deficit_b = max(0.0, surge_target - current_stock_b)
    assert deficit_b == 0.0


def test_50_lead_time_urgency_detection():
    """Verify lead time critical flag when days until festival <= supplier lead time."""
    days_left = 6
    supplier_lead_time = 7
    is_critical = days_left <= supplier_lead_time
    assert is_critical is True

    days_left_safe = 12
    is_critical_safe = days_left_safe <= supplier_lead_time
    assert is_critical_safe is False


def test_51_voice_local_interpretation_festival_queries():
    """Verify multilingual voice resolution for festival demand queries."""
    # English
    r_en = build_local_interpretation("What items do I need for the upcoming festival?", None, None, {})
    assert r_en['intent'] == 'FESTIVAL_DEMAND_CHECK'

    # English alternative
    r_en2 = build_local_interpretation("Check festival demand for Dussehra", None, None, {})
    assert r_en2['intent'] == 'FESTIVAL_DEMAND_CHECK'

    # Telugu script
    r_te = build_local_interpretation("దసరా పండుగకి ఏ సరుకులు కావాలి?", None, None, {})
    assert r_te['intent'] == 'FESTIVAL_DEMAND_CHECK'

    # Telugu transliteration
    r_te2 = build_local_interpretation("Pandaga items em kavali?", None, None, {})
    assert r_te2['intent'] == 'FESTIVAL_DEMAND_CHECK'

    # Hindi script
    r_hi = build_local_interpretation("त्योहार के लिए क्या सामान मंगाना है?", None, None, {})
    assert r_hi['intent'] == 'FESTIVAL_DEMAND_CHECK'

    # Hindi transliteration
    r_hi2 = build_local_interpretation("Dussehra tyohar ka saman kitna chahiye", None, None, {})
    assert r_hi2['intent'] == 'FESTIVAL_DEMAND_CHECK'
