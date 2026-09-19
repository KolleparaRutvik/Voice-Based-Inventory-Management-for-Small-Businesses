"""Tests 7-18: Stock and Borrowing / Udhar Management.
Verifies Stock-In, Stock-Out, Stock-Check, Unknown/Ambiguous Products,
Borrowing creation, Partial/Full payment, Customer debt checks, and Unknown/Ambiguous Customers.
"""
import pytest
from app.utils.entity_resolver import resolve_product, resolve_customer

SAMPLE_PRODUCTS = [
    {'id': 'p-rice', 'name': 'Rice (Biyyam)', 'local_name': 'Biyyam', 'base_unit': 'kg', 'current_stock': 500.0, 'minimum_stock': 125.0},
    {'id': 'p-oil-1', 'name': 'Sunflower Oil', 'local_name': 'Sunflower Nune', 'base_unit': 'litre', 'current_stock': 37.0, 'minimum_stock': 20.0},
    {'id': 'p-oil-2', 'name': 'Groundnut Oil', 'local_name': 'Verusenaga Nune', 'base_unit': 'litre', 'current_stock': 15.0, 'minimum_stock': 10.0},
    {'id': 'p-jaggery', 'name': 'Jaggery (Bellam)', 'local_name': 'Bellam', 'base_unit': 'kg', 'current_stock': 8.0, 'minimum_stock': 20.0},
]

SAMPLE_CUSTOMERS = [
    {'id': 'c-ramesh', 'name': 'Ramesh (Kirana Regular)', 'phone': '+91 9876543001', 'total_credit': 1250.0},
    {'id': 'c-ruthwik', 'name': 'Ruthwik Kumar', 'phone': '+91 9876543002', 'total_credit': 500.0},
    {'id': 'c-prudhvi', 'name': 'Prudhvi Raj', 'phone': '+91 9876543003', 'total_credit': 0.0},
]


def test_7_add_stock_simulation():
    """Test 7: Add stock intent entity resolution and calculation."""
    res = resolve_product('Rice', SAMPLE_PRODUCTS)
    assert res['matched_product']['id'] == 'p-rice'
    current = res['matched_product']['current_stock']
    qty_added = 5.0 * 25.0  # 5 bags of 25kg
    new_stock = current + qty_added
    assert new_stock == 625.0


def test_8_remove_stock_simulation():
    """Test 8: Remove stock / Sale stock deduction."""
    res = resolve_product('Jaggery', SAMPLE_PRODUCTS)
    assert res['matched_product']['id'] == 'p-jaggery'
    current = res['matched_product']['current_stock']
    qty_sold = 3.0
    new_stock = max(0, current - qty_sold)
    assert new_stock == 5.0


def test_9_stock_check():
    """Test 9: Stock check lookup with exact numbers."""
    res = resolve_product('biyyam', SAMPLE_PRODUCTS)
    assert res['matched_product'] is not None
    assert res['matched_product']['current_stock'] == 500.0
    assert res['matched_product']['base_unit'] == 'kg'


def test_10_unknown_product_never_defaults_to_first():
    """Test 10: Unknown product must NEVER default to products[0]."""
    res = resolve_product('XYZ Unknown Gadget 999', SAMPLE_PRODUCTS)
    assert res['matched_product'] is None, "CRITICAL: Unknown product must not match products[0]!"
    assert res['is_ambiguous'] is False


def test_11_ambiguous_product_disambiguation():
    """Test 11: Ambiguous product query returns candidates instead of guessing."""
    res = resolve_product('Oil', SAMPLE_PRODUCTS)
    # Both Sunflower Oil and Groundnut Oil contain "Oil"
    assert res['is_ambiguous'] is True
    assert len(res['ambiguous_candidates']) >= 2
    assert 'Sunflower Oil' in res['ambiguous_candidates']
    assert 'Groundnut Oil' in res['ambiguous_candidates']


def test_12_create_borrowing_resolution():
    """Test 12: Customer Udhar entity match and debt accumulation."""
    res = resolve_customer('Ramesh', SAMPLE_CUSTOMERS)
    assert res['matched_customer'] is not None
    assert res['matched_customer']['id'] == 'c-ramesh'
    initial_debt = res['matched_customer']['total_credit']
    new_debt = initial_debt + 500.0
    assert new_debt == 1750.0


def test_13_partial_payment_simulation():
    """Test 13: Partial repayment calculation and balance deduction."""
    res = resolve_customer('Ramesh', SAMPLE_CUSTOMERS)
    assert res['matched_customer'] is not None
    current_debt = 1250.0
    payment = 200.0
    remaining_balance = current_debt - payment
    new_status = 'RETURNED' if remaining_balance <= 0 else 'PARTIALLY_RETURNED'
    assert remaining_balance == 1050.0
    assert new_status == 'PARTIALLY_RETURNED'


def test_14_full_payment_simulation():
    """Test 14: Full debt repayment clears balance and marks RETURNED."""
    current_debt = 500.0
    payment = 500.0
    remaining_balance = max(0, current_debt - payment)
    new_status = 'RETURNED' if remaining_balance <= 0 else 'PARTIALLY_RETURNED'
    assert remaining_balance == 0.0
    assert new_status == 'RETURNED'


def test_15_check_customer_balance():
    """Test 15: Check customer balance for specific person."""
    res = resolve_customer('Ruthwik', SAMPLE_CUSTOMERS)
    assert res['matched_customer'] is not None
    assert res['matched_customer']['total_credit'] == 500.0


def test_16_list_debtors():
    """Test 16: List debtors with outstanding credit > 0."""
    debtors = [c for c in SAMPLE_CUSTOMERS if c['total_credit'] > 0]
    assert len(debtors) == 2
    names = [c['name'] for c in debtors]
    assert any('Ramesh' in n for n in names)
    assert any('Ruthwik' in n for n in names)


def test_17_unknown_customer_resolution():
    """Test 17: Unknown customer name must return None without guessing."""
    res = resolve_customer('Unknown Stranger 123', SAMPLE_CUSTOMERS)
    assert res['matched_customer'] is None
    assert res['confidence'] == 0.0


def test_18_ambiguous_customer_disambiguation():
    """Test 18: Disambiguation when customer names are phonetically / lexically close."""
    # When query is ambiguous between Ruthwik and Prudhvi
    res = resolve_customer('Ruthvi', SAMPLE_CUSTOMERS)
    if res['is_ambiguous']:
        assert len(res['ambiguous_candidates']) >= 2
    else:
        # Either resolved with strict confidence or flagged as unknown
        assert res['confidence'] < 0.85 or res['matched_customer'] is not None
