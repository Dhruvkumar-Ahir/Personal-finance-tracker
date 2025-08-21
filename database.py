#Authors: Adnan Syed, Dhruvkumar Satishbhai Ahir, Kartik Rajeev Patil
#Date: April 11, 2025

#Database Module for Personal Finance Tracker and Advisor.

#This module handles all database operations using SQLite3.
#It provides methods to create tables, insert data, and query data.


import sqlite3
import os
import csv
from datetime import datetime

class Database:
    """
    Database class that handles all SQLite3 operations for the finance tracker app.
    
    This class provides methods for:
    - Creating and connecting to a database
    - Creating tables for transactions and categories
    - Inserting, updating, deleting and querying data
    - Importing data from CSV files
    """
    
    def __init__(self, db_file="finance_tracker.db"):
        """
        Initialize the database connection.
        
        Args:
            db_file (str): Name of the database file. Defaults to "finance_tracker.db".
        """
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """
        Connect to the database and create a cursor.
        
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}!")
            return False
            
    def close(self):
        """
        Closes the database connection.
        """
        if self.conn:
            self.conn.close()
            
    def create_tables(self):
        """
        Creates the necessary tables if they don't already exist in the database.
        
        Creates:
        - transactions: Stores transaction data
        - categories: Stores budget categories
        
        Returns:
            bool: True if tables were created successfully, False otherwise.
        """
        try:
            #Creates a table for categories.
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY,
                category_name TEXT NOT NULL UNIQUE,
                monthly_budget REAL NOT NULL,
                priority_level TEXT NOT NULL,
                icon TEXT
            )
            ''')
            
            #Creates a table for transactions.
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                account_type TEXT,
                payment_method TEXT,
                FOREIGN KEY (category) REFERENCES categories(category_name)
            )
            ''')
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}!")
            return False
            
    def import_categories_from_csv(self, csv_file):
        """
        Imports the categories from a CSV file.
        
        Args:
            csv_file (str): Path to the CSV file.
            
        Returns:
            int: Number of categories imported.
        """
        count = 0
        
        try:
            if not os.path.exists(csv_file):
                print(f"File not found: {csv_file}!")
                return 0
                
            with open(csv_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    try:
                        self.cursor.execute('''
                        INSERT OR REPLACE INTO categories
                        (category_id, category_name, monthly_budget, priority_level, icon)
                        VALUES (?, ?, ?, ?, ?)
                        ''', (
                            int(row['category_id']),
                            row['category_name'],
                            float(row['monthly_budget']),
                            row['priority_level'],
                            row['icon']
                        ))
                        count += 1
                    except (KeyError, ValueError) as e:
                        print(f"Error processing row {row}: {e}!")
                
                self.conn.commit()
                return count
        except Exception as e:
            print(f"Error importing categories: {e}!")
            return 0
            
    def import_transactions_from_csv(self, csv_file):
        """
        Imports the transactions from a CSV file.
        
        Args:
            csv_file (str): Path to the CSV file.
            
        Returns:
            int: Number of transactions imported.
        """
        count = 0
        
        try:
            if not os.path.exists(csv_file):
                print(f"File not found: {csv_file}")
                return 0
                
            with open(csv_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    try:
                        self.cursor.execute('''
                        INSERT OR REPLACE INTO transactions
                        (transaction_id, date, amount, category, description, account_type, payment_method)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            int(row['transaction_id']),
                            row['date'],
                            float(row['amount']),
                            row['category'],
                            row['description'],
                            row['account_type'],
                            row['payment_method']
                        ))
                        count += 1
                    except (KeyError, ValueError) as e:
                        print(f"Error processing row {row}: {e}")
                
                self.conn.commit()
                return count
        except Exception as e:
            print(f"Error importing transactions: {e}!")
            return 0
    
    def get_all_categories(self):
        """
        Gets all the categories from the database.
        
        Returns:
            list: List of tuples containing category data.
        """
        try:
            self.cursor.execute("SELECT * FROM categories ORDER BY category_name")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching categories: {e}!")
            return []
            
    def get_all_transactions(self, limit=100):
        """
        Gets all the transactions from the database with an optional limit.
        
        Args:
            limit (int): Maximum number of transactions to return. Defaults to 100.
            
        Returns:
            list: List of tuples containing transaction data.
        """
        try:
            self.cursor.execute(f"SELECT * FROM transactions ORDER BY date DESC LIMIT {limit}")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching transactions: {e}!")
            return []
            
    def get_transactions_by_category(self, category):
        """
        Gets the transactions for a specific category.
        
        Args:
            category (str): Category name.
            
        Returns:
            list: List of tuples containing transaction data.
        """
        try:
            self.cursor.execute("SELECT * FROM transactions WHERE category = ? ORDER BY date DESC", (category,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching transactions by category: {e}!")
            return []
            
    def get_spending_by_category(self, start_date=None, end_date=None):
        """
        Gets the total spending amount by category within an optional date range.
        
        Args:
            start_date (str, optional): Start date in YYYY-MM-DD format.
            end_date (str, optional): End date in YYYY-MM-DD format.
            
        Returns:
            list: List of tuples containing (category, total_amount).
        """
        try:
            query = "SELECT category, SUM(amount) FROM transactions"
            
            params = []
            if start_date or end_date:
                query += " WHERE"
                
                if start_date:
                    query += " date >= ?"
                    params.append(start_date)
                    
                if end_date:
                    if start_date:
                        query += " AND"
                    query += " date <= ?"
                    params.append(end_date)
                    
            query += " GROUP BY category ORDER BY SUM(amount) DESC"
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching spending by category: {e}!")
            return []
            
    def add_transaction(self, date, amount, category, description, account_type, payment_method):
        """
        Adds a new transaction to the database.
        
        Args:
            date (str): Transaction date in YYYY-MM-DD format
            amount (float): Transaction amount
            category (str): Transaction category
            description (str): Transaction description
            account_type (str): Account type
            payment_method (str): Payment method
            
        Returns:
            int: The ID of the newly inserted transaction, or -1 if failed.
        """
        try:
            #Validates the date
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format! Please use YYYY-MM-DD format!")
                return -1
                
            #Checks if the category exists
            self.cursor.execute("SELECT category_name FROM categories WHERE category_name = ?", (category,))
            if not self.cursor.fetchone():
                print(f"Category '{category}' does not exist in the database!")
                return -1
                
            self.cursor.execute('''
            INSERT INTO transactions
            (date, amount, category, description, account_type, payment_method)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (date, amount, category, description, account_type, payment_method))
            
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding transaction: {e}!")
            return -1
            
    def get_category_budget(self, category):
        """
        Gets the monthly budget for a category.
        
        Args:
            category (str): Category name.
            
        Returns:
            float: Monthly budget amount, or 0 if category not found.
        """
        try:
            self.cursor.execute("SELECT monthly_budget FROM categories WHERE category_name = ?", (category,))
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"Error fetching category budget: {e}!")
            return 0
            
    def delete_transaction(self, transaction_id):
        """
        Deletes a transaction from the database.
        
        Args:
            transaction_id (int): ID of the transaction to delete.
            
        Returns:
            bool: True if transaction was deleted successfully, False otherwise.
        """
        try:
            self.cursor.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting transaction: {e}!")
            return False
            
    def update_transaction(self, transaction_id, date, amount, category, description, account_type, payment_method):
        """
        Updates an existing transaction in the database.
        
        Args:
            transaction_id (int): ID of the transaction to update.
            date (str): Updated transaction date in YYYY-MM-DD format.
            amount (float): Updated transaction amount.
            category (str): Updated transaction category.
            description (str): Updated transaction description.
            account_type (str): Updated account type.
            payment_method (str): Updated payment method.
            
        Returns:
            bool: True if transaction was updated successfully, False otherwise.
        """
        try:
            # Validate date
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format! Please use YYYY-MM-DD format!")
                return False
                
            # Check if category exists
            self.cursor.execute("SELECT category_name FROM categories WHERE category_name = ?", (category,))
            if not self.cursor.fetchone():
                print(f"Category '{category}' does not exist in the database!")
                return False
                
            self.cursor.execute('''
            UPDATE transactions
            SET date = ?, amount = ?, category = ?, description = ?, account_type = ?, payment_method = ?
            WHERE transaction_id = ?
            ''', (date, amount, category, description, account_type, payment_method, transaction_id))
            
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating transaction: {e}!")
            return False
            
    def get_transaction(self, transaction_id):
        """
        Gets a specific transaction by its ID.
        
        Args:
            transaction_id (int): ID of the transaction to retrieve.
            
        Returns:
            tuple: Transaction data, or None if not found.
        """
        try:
            self.cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching transaction: {e}!")
            return None