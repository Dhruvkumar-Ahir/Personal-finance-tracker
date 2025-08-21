#Authors: Adnan Syed, Dhruvkumar Satishbhai Ahir, Kartik Rajeev Patil
#Date: May 02, 2025

#Main Module for Personal Finance Tracker and Advisor.

#This is the entry point for the application. It initializes the database,
#creates the finance tracker, and launches the GUI.


import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from database import Database
from finance_tracker import FinanceTracker
from gui import FinanceTrackerGUI

def check_data_files():
    """
    Check if the data files exist and return their paths.
    
    Returns:
        tuple: (transactions_file, categories_file) paths if they exist, else None.
    """
    # Look for data files in the data directory
    data_dir = "data"
    
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    transactions_file = os.path.join(data_dir, "transactions.csv")
    categories_file = os.path.join(data_dir, "categories.csv")
    
    return transactions_file, categories_file

def main():
    """
    Main function to run the application.
    
    This function:
    1. Creates the application
    2. Initializes the database
    3. Imports data from CSV files if available
    4. Creates the finance tracker and GUI
    5. Shows the GUI and runs the application
    """
    # Create application
    app = QApplication(sys.argv)
    
    # Show splash screen
    splash_pixmap = QPixmap(600, 300)
    splash_pixmap.fill(Qt.white)
    splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
    splash.show()
    
    # Message to display on splash screen
    splash.showMessage("Loading Personal Finance Tracker...", 
                      Qt.AlignCenter | Qt.AlignBottom, Qt.black)
    
    # Initialize database
    db = Database()
    if not db.connect():
        splash.close()
        QMessageBox.critical(None, "Database Error", "Failed to connect to the database.")
        return
    
    # Create tables
    if not db.create_tables():
        splash.close()
        QMessageBox.critical(None, "Database Error", "Failed to create database tables.")
        return
    
    # Update splash message
    splash.showMessage("Checking for data files...", 
                      Qt.AlignCenter | Qt.AlignBottom, Qt.black)
    
    # Import data from CSV files if available
    transactions_file, categories_file = check_data_files()
    
    # First check if any categories exist in the database
    db.cursor.execute("SELECT COUNT(*) FROM categories")
    category_count_db = db.cursor.fetchone()[0]
    
    if category_count_db == 0:
        # No categories in database, try to import from CSV first
        if os.path.exists(categories_file):
            splash.showMessage(f"Importing categories from {categories_file}...", 
                              Qt.AlignCenter | Qt.AlignBottom, Qt.black)
            imported_count = db.import_categories_from_csv(categories_file)
            print(f"Imported {imported_count} categories from {categories_file}")
        
        # If still no categories, add defaults
        db.cursor.execute("SELECT COUNT(*) FROM categories")
        if db.cursor.fetchone()[0] == 0:
            splash.showMessage("Adding default categories...", 
                              Qt.AlignCenter | Qt.AlignBottom, Qt.black)
            add_default_categories(db)
    
    # Now check for transactions
    db.cursor.execute("SELECT COUNT(*) FROM transactions")
    transaction_count_db = db.cursor.fetchone()[0]
    
    if transaction_count_db == 0 and os.path.exists(transactions_file):
        splash.showMessage(f"Importing transactions from {transactions_file}...", 
                          Qt.AlignCenter | Qt.AlignBottom, Qt.black)
        imported_count = db.import_transactions_from_csv(transactions_file)
        print(f"Imported {imported_count} transactions from {transactions_file}")
    
    # Update splash message
    splash.showMessage("Creating finance tracker...", 
                      Qt.AlignCenter | Qt.AlignBottom, Qt.black)
    
    # Create finance tracker
    finance_tracker = FinanceTracker(db)
    
    # Update splash message
    splash.showMessage("Initializing user interface...", 
                      Qt.AlignCenter | Qt.AlignBottom, Qt.black)
    
    # Create GUI
    gui = FinanceTrackerGUI(finance_tracker)
    
    # Close splash screen after a delay
    QTimer.singleShot(1000, splash.close)
    
    # Show GUI
    gui.show()
    
    # Execute application
    result = app.exec_()
    
    # Clean up
    db.close()
    
    return result

def add_default_categories(db):
    """
    Add default categories if no categories exist.
    
    This function adds a set of common budget categories with default monthly
    budget allocations when the application is run for the first time.
    
    Args:
        db: Database instance.
    """
    default_categories = [
        (1, "Groceries", 500.00, "High", "grocery"),
        (2, "Dining", 300.00, "Medium", "food"),
        (3, "Entertainment", 200.00, "Low", "movie"),
        (4, "Utilities", 350.00, "High", "utility"),
        (5, "Transportation", 250.00, "Medium", "car"),
        (6, "Shopping", 200.00, "Low", "cart"),
        (7, "Housing", 1000.00, "High", "home"),
        (8, "Healthcare", 200.00, "High", "medical"),
        (9, "Education", 100.00, "Medium", "book"),
        (10, "Personal Care", 100.00, "Low", "personal")
    ]
    
    try:
        for category in default_categories:
            db.cursor.execute('''
            INSERT INTO categories
            (category_id, category_name, monthly_budget, priority_level, icon)
            VALUES (?, ?, ?, ?, ?)
            ''', category)
            
        db.conn.commit()
        print("Added default categories")
    except Exception as e:
        print(f"Error adding default categories: {e}")

if __name__ == "__main__":
    main()