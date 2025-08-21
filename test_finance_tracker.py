#Authors: Adnan Syed, Dhruvkumar Satishbhai Ahir, Kartik Rajeev Patil
#Date: May 02, 2025

#Comprehensive Test Module for Personal Finance Tracker and Advisor.

#This module contains extensive tests for the database, finance tracker,
#data visualization, and transaction processing components.

import sys
import os
import pytest
import sqlite3
from datetime import datetime, timedelta
import calendar
import tempfile
import shutil

# Add parent directory to path for importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from finance_tracker import FinanceTracker

# Use a temporary database for testing
TEST_DB = "test_finance.db"

@pytest.fixture
def cleanup_test_db():
    """
    Fixture to clean up test database before and after tests.
    """
    # Remove test database if it exists before test
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
        
    # Execute test
    yield
    
    # Remove test database after test
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

@pytest.fixture
def database(cleanup_test_db):
    """
    Fixture to create a test database with sample data.
    
    Returns:
        Database: A database instance for testing.
    """
    db = Database(TEST_DB)
    db.connect()
    db.create_tables()
    
    # Add sample categories
    categories = [
        (1, "Groceries", 500.00, "High", "grocery"),
        (2, "Dining", 300.00, "Medium", "food"),
        (3, "Entertainment", 200.00, "Low", "movie"),
        (4, "Utilities", 350.00, "High", "utility"),
        (5, "Transportation", 250.00, "Medium", "car")
    ]
    
    for category in categories:
        db.cursor.execute('''
        INSERT INTO categories
        (category_id, category_name, monthly_budget, priority_level, icon)
        VALUES (?, ?, ?, ?, ?)
        ''', category)
    
    # Add sample transactions
    # Create transactions spanning multiple months
    today = datetime.now()
    current_month = today.replace(day=15).strftime("%Y-%m-%d")
    last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=15).strftime("%Y-%m-%d")
    two_months_ago = (today.replace(day=1) - timedelta(days=32)).replace(day=15).strftime("%Y-%m-%d")
    
    transactions = [
        (1001, current_month, 45.67, "Groceries", "Current Month Grocery", "Checking", "Debit Card"),
        (1002, current_month, 35.50, "Dining", "Current Month Dining", "Credit", "Credit Card"),
        (1003, current_month, 25.99, "Entertainment", "Current Month Entertainment", "Credit", "Credit Card"),
        (1004, last_month, 42.30, "Groceries", "Last Month Grocery", "Checking", "Debit Card"),
        (1005, last_month, 28.75, "Dining", "Last Month Dining", "Credit", "Credit Card"),
        (1006, two_months_ago, 33.45, "Utilities", "Two Months Ago Utility", "Checking", "Bank Transfer"),
        (1007, two_months_ago, 22.50, "Transportation", "Two Months Ago Transportation", "Credit", "Credit Card")
    ]
    
    for transaction in transactions:
        db.cursor.execute('''
        INSERT INTO transactions
        (transaction_id, date, amount, category, description, account_type, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', transaction)
    
    db.conn.commit()
    
    return db

@pytest.fixture
def finance_tracker(database):
    """
    Fixture to create a finance tracker with the test database.
    
    Args:
        database: The test database fixture.
        
    Returns:
        FinanceTracker: A finance tracker instance for testing.
    """
    return FinanceTracker(database)

@pytest.fixture
def temp_csv_dir():
    """
    Fixture to create a temporary directory for CSV files.
    
    Returns:
        str: Path to temporary directory.
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

#Test 1: Database Creation and Tables
def test_database_creation(database):
    """
    Test that the database is created and tables exist with the correct schema.
    
    Args:
        database: The test database fixture.
    """
    # Check that tables exist
    database.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = database.cursor.fetchall()
    table_names = [table[0] for table in tables]
    
    # Verify both tables exist
    assert "categories" in table_names
    assert "transactions" in table_names
    
    # Verify categories table schema
    database.cursor.execute("PRAGMA table_info(categories)")
    category_columns = database.cursor.fetchall()
    category_column_names = [col[1] for col in category_columns]
    
    assert "category_id" in category_column_names
    assert "category_name" in category_column_names
    assert "monthly_budget" in category_column_names
    assert "priority_level" in category_column_names
    assert "icon" in category_column_names
    
    # Verify transactions table schema
    database.cursor.execute("PRAGMA table_info(transactions)")
    transaction_columns = database.cursor.fetchall()
    transaction_column_names = [col[1] for col in transaction_columns]
    
    assert "transaction_id" in transaction_column_names
    assert "date" in transaction_column_names
    assert "amount" in transaction_column_names
    assert "category" in transaction_column_names
    assert "description" in transaction_column_names
    assert "account_type" in transaction_column_names
    assert "payment_method" in transaction_column_names

#Test 2: Budget Calculation with Different Time Periods
def test_budget_calculation_time_periods(finance_tracker):
    """
    Test that budget usage is calculated correctly for different time periods.
    
    Args:
        finance_tracker: The finance tracker fixture.
    """
    # Get budget usage for current month
    current_month_usage = finance_tracker.calculate_budget_usage("month")
    
    # Convert to dictionary for easier checking
    current_month_dict = {category: (spent, budget, percentage) 
                          for category, spent, budget, percentage in current_month_usage}
    
    # Check Groceries budget for current month
    assert "Groceries" in current_month_dict
    groceries_spent, groceries_budget, groceries_percentage = current_month_dict["Groceries"]
    assert groceries_spent == 45.67
    assert groceries_budget == 500.00
    assert groceries_percentage == pytest.approx(45.67 / 500.00 * 100)
    
    # Check Dining budget for current month
    assert "Dining" in current_month_dict
    dining_spent, dining_budget, dining_percentage = current_month_dict["Dining"]
    assert dining_spent == 35.50
    assert dining_budget == 300.00
    assert dining_percentage == pytest.approx(35.50 / 300.00 * 100)
    
    # Get budget usage for previous month
    prev_month_usage = finance_tracker.calculate_budget_usage("prev_month")
    
    # Convert to dictionary for easier checking
    prev_month_dict = {category: (spent, budget, percentage) 
                       for category, spent, budget, percentage in prev_month_usage}
    
    # Check Groceries budget for previous month
    assert "Groceries" in prev_month_dict
    groceries_spent, groceries_budget, groceries_percentage = prev_month_dict["Groceries"]
    assert groceries_spent == 42.30
    assert groceries_budget == 500.00
    assert groceries_percentage == pytest.approx(42.30 / 500.00 * 100)
    
    # Get budget usage for current year (should use multiplier for the budget)
    year_usage = finance_tracker.calculate_budget_usage("year")
    
    # Convert to dictionary for easier checking
    year_dict = {category: (spent, budget, percentage) 
                for category, spent, budget, percentage in year_usage}
    
    # Check Utilities budget for the year (only appears in two_months_ago)
    assert "Utilities" in year_dict
    utilities_spent, utilities_budget, utilities_percentage = year_dict["Utilities"]
    assert utilities_spent == 33.45
    
    # Budget should be multiplied by 12 for annual view
    assert utilities_budget == pytest.approx(350.00 * 12)
    assert utilities_percentage == pytest.approx(33.45 / (350.00 * 12) * 100)

#Test 3: Transaction Addition and Retrieval
def test_transaction_addition_retrieval(finance_tracker):
    """
    Test adding a new transaction and retrieving transactions by various criteria.
    
    Args:
        finance_tracker: The finance tracker fixture.
    """
    # Get initial transaction count
    initial_transactions = finance_tracker.get_recent_transactions(20)
    initial_count = len(initial_transactions)
    
    # Add a new transaction
    new_transaction_id = finance_tracker.add_transaction(
        datetime.now().strftime("%Y-%m-%d"),
        75.25,
        "Groceries",
        "Test Transaction",
        "Checking",
        "Debit Card"
    )
    
    # Check that transaction was added successfully
    assert new_transaction_id > 0
    
    # Get updated transaction count
    updated_transactions = finance_tracker.get_recent_transactions(20)
    assert len(updated_transactions) == initial_count + 1
    
    # Get the added transaction
    added_transaction = finance_tracker.get_transaction(new_transaction_id)
    assert added_transaction is not None
    assert added_transaction[2] == 75.25  # Amount
    assert added_transaction[3] == "Groceries"  # Category
    assert added_transaction[4] == "Test Transaction"  # Description
    
    # Get transactions by category
    groceries_transactions = finance_tracker.get_transactions_by_category("Groceries")
    assert len(groceries_transactions) >= 3  # At least 3 (2 from fixture + 1 added)
    
    # Find the new transaction in category-filtered results
    new_transaction_in_category = False
    for transaction in groceries_transactions:
        if transaction[0] == new_transaction_id:
            new_transaction_in_category = True
            break
    
    assert new_transaction_in_category

#Test 4: Spending Trend Analysis
def test_spending_trend_analysis(finance_tracker):
    """
    Test that spending trends are correctly calculated over multiple months.
    
    Args:
        finance_tracker: The finance tracker fixture.
    """
    # Get spending trend for the last 3 months
    trend_data = finance_tracker.get_spending_trend(3)
    
    # Check that we have data for 3 months
    assert len(trend_data) == 3
    
    # Extract month strings for easier comparison
    this_month = datetime.now().strftime("%b %Y")
    
    # Get previous month
    last_month_date = datetime.now().replace(day=1) - timedelta(days=1)
    last_month = last_month_date.strftime("%b %Y")
    
    # Get two months ago
    two_months_ago_date = last_month_date.replace(day=1) - timedelta(days=1)
    two_months_ago = two_months_ago_date.strftime("%b %Y")
    
    # Check that all months are in the trend data
    assert this_month in trend_data
    assert last_month in trend_data
    assert two_months_ago in trend_data
    
    # Check spending amounts for each month
    assert trend_data[this_month] == pytest.approx(45.67 + 35.50 + 25.99)  # Sum of current month transactions
    assert trend_data[last_month] == pytest.approx(42.30 + 28.75)  # Sum of last month transactions
    assert trend_data[two_months_ago] == pytest.approx(33.45 + 22.50)  # Sum of two months ago transactions

#Test 5: Transaction Update and Deletion
def test_transaction_update_deletion(finance_tracker):
    """
    Test updating and deleting transactions.
    
    Args:
        finance_tracker: The finance tracker fixture.
    """
    # Add a test transaction
    test_transaction_id = finance_tracker.add_transaction(
        datetime.now().strftime("%Y-%m-%d"),
        50.00,
        "Groceries",
        "Transaction to Update",
        "Checking",
        "Debit Card"
    )
    
    # Verify the transaction was added
    assert test_transaction_id > 0
    original_transaction = finance_tracker.get_transaction(test_transaction_id)
    assert original_transaction is not None
    assert original_transaction[2] == 50.00  # Original amount
    
    # Update the transaction
    update_success = finance_tracker.update_transaction(
        test_transaction_id,
        datetime.now().strftime("%Y-%m-%d"),
        75.00,  # New amount
        "Dining",  # New category
        "Updated Transaction",  # New description
        "Credit",  # New account type
        "Credit Card"  # New payment method
    )
    
    # Verify the update was successful
    assert update_success is True
    
    # Get the updated transaction
    updated_transaction = finance_tracker.get_transaction(test_transaction_id)
    assert updated_transaction is not None
    assert updated_transaction[2] == 75.00  # Updated amount
    assert updated_transaction[3] == "Dining"  # Updated category
    assert updated_transaction[4] == "Updated Transaction"  # Updated description
    assert updated_transaction[5] == "Credit"  # Updated account type
    assert updated_transaction[6] == "Credit Card"  # Updated payment method
    
    # Delete the transaction
    delete_success = finance_tracker.delete_transaction(test_transaction_id)
    
    # Verify the deletion was successful
    assert delete_success is True
    
    # Try to get the deleted transaction
    deleted_transaction = finance_tracker.get_transaction(test_transaction_id)
    assert deleted_transaction is None

#Test 6: Over Budget Categories
def test_over_budget_categories(finance_tracker, database):
    """
    Test identifying categories that are over budget.
    
    Args:
        finance_tracker: The finance tracker fixture.
        database: The database fixture.
    """
    # Initially there should be no over-budget categories
    initial_over_budget = finance_tracker.get_over_budget_categories()
    assert len(initial_over_budget) == 0
    
    # Update a category's budget to be less than the spending
    database.cursor.execute('''
    UPDATE categories
    SET monthly_budget = 20.00
    WHERE category_name = 'Dining'
    ''')
    database.conn.commit()
    
    # Now there should be one over-budget category
    updated_over_budget = finance_tracker.get_over_budget_categories()
    assert len(updated_over_budget) == 1
    
    # Verify it's the Dining category
    over_budget_category = updated_over_budget[0]
    assert over_budget_category[0] == "Dining"
    
    # Verify spending, budget, and percentage
    spent, budget, percentage = over_budget_category[1], over_budget_category[2], over_budget_category[3]
    assert spent == 35.50  # Current month dining spending
    assert budget == 20.00  # Updated budget
    assert percentage == pytest.approx(35.50 / 20.00 * 100)  # Should be over 100%
    assert percentage > 100

#Test 7: CSV Import Functionality
def test_csv_import(finance_tracker, database, temp_csv_dir):
    """
    Test importing transactions from a CSV file.
    
    Args:
        finance_tracker: The finance tracker fixture.
        database: The database fixture.
        temp_csv_dir: Temporary directory for CSV files.
    """
    # Create a test CSV file
    csv_file = os.path.join(temp_csv_dir, "test_transactions.csv")
    with open(csv_file, 'w') as f:
        f.write("transaction_id,date,amount,category,description,account_type,payment_method\n")
        f.write("2001,2025-05-01,22.99,Groceries,CSV Import Test 1,Checking,Debit Card\n")
        f.write("2002,2025-05-02,15.50,Entertainment,CSV Import Test 2,Credit,Credit Card\n")
        f.write("2003,2025-05-03,45.75,Dining,CSV Import Test 3,Credit,Credit Card\n")
    
    # Get initial transaction count
    database.cursor.execute("SELECT COUNT(*) FROM transactions")
    initial_count = database.cursor.fetchone()[0]
    
    # Import transactions from CSV
    import_count = database.import_transactions_from_csv(csv_file)
    
    # Verify correct number of transactions were imported
    assert import_count == 3
    
    # Get updated transaction count
    database.cursor.execute("SELECT COUNT(*) FROM transactions")
    updated_count = database.cursor.fetchone()[0]
    
    # Verify the transaction count increased by the number of imported transactions
    assert updated_count == initial_count + 3
    
    # Verify the imported transactions are in the database
    database.cursor.execute("SELECT * FROM transactions WHERE description LIKE 'CSV Import Test%'")
    imported_transactions = database.cursor.fetchall()
    
    assert len(imported_transactions) == 3
    
    # Verify details of one of the imported transactions
    database.cursor.execute("SELECT * FROM transactions WHERE description = 'CSV Import Test 2'")
    test_transaction = database.cursor.fetchone()
    
    assert test_transaction is not None
    assert test_transaction[2] == 15.50  # Amount
    assert test_transaction[3] == "Entertainment"  # Category
    assert test_transaction[5] == "Credit"  # Account type
    assert test_transaction[6] == "Credit Card"  # Payment method