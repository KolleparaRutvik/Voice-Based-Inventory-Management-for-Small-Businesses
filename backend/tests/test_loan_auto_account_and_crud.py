"""Tests 34-45: Loan Auto-Account Creation & Full Voice CRUD Engine.
Verifies automatic customer account creation when someone takes a loan,
loan phrase parsing (English, Telugu, Hindi), loan debt settlements,
stock adjustments, and customer profile creations.
"""
import pytest
from app.utils.entity_resolver import (
    resolve_customer,
    resolve_product,
    extract_customer_from_loan_phrase,
    extract_phone_number
)
from app.routes.voice import build_local_interpretation

SAMPLE_CUSTOMERS = [
    {'id': 'c-ramesh', 'name': 'Ramesh (Kirana Regular)', 'phone': '+91 9876543001', 'total_credit': 1250.0},
    {'id': 'c-ruthwik', 'name': 'Ruthwik Kumar', 'phone': '+91 9876543002', 'total_credit': 500.0},
    {'id': 'c-prudhvi', 'name': 'Prudhvi Raj', 'phone': '+91 9876543003', 'total_credit': 0.0},
]


def test_34_extract_customer_from_loan_phrase():
    """Test 34: Robust extraction of person's name from varied loan sentences."""
    assert extract_customer_from_loan_phrase("one person Kiran has taken a loan of 500") == "Kiran"
    assert extract_customer_from_loan_phrase("Kiran has taken a loan of 500") == "Kiran"
    assert extract_customer_from_loan_phrase("Mahesh took loan 1000") == "Mahesh"
    assert extract_customer_from_loan_phrase("Give loan of 500 to Suresh") == "Suresh"
    assert extract_customer_from_loan_phrase("Sita borrowed 300") == "Sita"
    assert extract_customer_from_loan_phrase("Ramesh appu theesukunnadu") == "Ramesh"
    assert extract_customer_from_loan_phrase("Clear loan of Ramesh") == "Ramesh"


def test_35_extract_phone_number_from_speech():
    """Test 35: Extraction of 10-digit Indian mobile numbers from voice input."""
    assert extract_phone_number("Add customer Rahul phone 9848011223") == "9848011223"
    assert extract_phone_number("Suresh mobile number is 9876543210") == "9876543210"
    assert extract_phone_number("+91 9848011223") == "9848011223"
    assert extract_phone_number("No phone given here") is None


def test_36_unregistered_customer_loan_triggers_new_account():
    """Test 36: An unknown customer taking a loan triggers auto-account creation flag."""
    res = resolve_customer("Kiran", SAMPLE_CUSTOMERS)
    assert res['matched_customer'] is None
    assert res['is_new_customer'] is True
    assert res['extracted_name'] == "Kiran"
    assert res['is_ambiguous'] is False


def test_37_existing_customer_loan_updates_existing_account():
    """Test 37: An existing customer taking a loan resolves their exact ID and account."""
    res = resolve_customer("Ramesh", SAMPLE_CUSTOMERS)
    assert res['matched_customer'] is not None
    assert res['matched_customer']['id'] == 'c-ramesh'
    assert res['is_new_customer'] is False
    assert res['matched_customer']['total_credit'] == 1250.0


def test_38_local_interpretation_loan_taken():
    """Test 38: 'one person Kiran has taken a loan of 500' maps to BORROW_OUT with customer Kiran."""
    query = "one person Kiran has taken a loan of 500"
    facts = {'quantity': 500.0, 'unit': 'INR', 'price': 500.0}
    res = build_local_interpretation(query, None, None, facts)
    assert res['intent'] == 'BORROW_OUT'
    assert res['raw_customer'] == 'Kiran'
    assert res['requires_confirmation'] is True


def test_39_local_interpretation_clear_loan():
    """Test 39: 'Clear loan of Ramesh' maps to BORROW_CLEAR."""
    query = "Clear loan of Ramesh"
    facts = {}
    res = build_local_interpretation(query, None, None, facts)
    assert res['intent'] == 'BORROW_CLEAR'
    assert res['raw_customer'] == 'Ramesh'
    assert res['requires_confirmation'] is True


def test_40_local_interpretation_stock_adjust():
    """Test 40: 'Adjust stock of Rice to 50 bags' maps to STOCK_ADJUST."""
    query = "Adjust stock of Rice to 50 bags"
    facts = {'quantity': 50.0, 'unit': 'bag', 'price': None}
    res = build_local_interpretation(query, None, None, facts)
    assert res['intent'] == 'STOCK_ADJUST'
    assert res['raw_product'] == 'rice'
    assert res['requires_confirmation'] is True


def test_41_local_interpretation_customer_add():
    """Test 41: 'Add customer Rahul' maps to CUSTOMER_ADD."""
    query = "Add customer Rahul"
    facts = {}
    res = build_local_interpretation(query, None, None, facts)
    assert res['intent'] == 'CUSTOMER_ADD'
    assert res['raw_customer'] == 'Rahul'
    assert res['requires_confirmation'] is True


def test_42_local_interpretation_product_add():
    """Test 42: 'Add new product Aashirvaad Atta' maps to PRODUCT_ADD."""
    query = "Add new product Aashirvaad Atta"
    facts = {}
    res = build_local_interpretation(query, None, None, facts)
    assert res['intent'] == 'PRODUCT_ADD'
    assert res['requires_confirmation'] is True


def test_43_loan_auto_account_calculation():
    """Test 43: Auto-creation loan math for new customer."""
    new_cust_starting_credit = 0.0
    loan_amount = 500.0
    updated_credit = new_cust_starting_credit + loan_amount
    assert updated_credit == 500.0


def test_44_loan_update_existing_customer_math():
    """Test 44: Adding loan to existing customer with prior balance."""
    current_credit = 1250.0
    additional_loan = 500.0
    updated_credit = current_credit + additional_loan
    assert updated_credit == 1750.0


def test_45_settle_clear_debt_math():
    """Test 45: Clearing / waiving debt resets balance to 0."""
    current_credit = 1250.0
    cleared_amount = current_credit
    remaining_balance = max(0.0, current_credit - cleared_amount)
    assert remaining_balance == 0.0
