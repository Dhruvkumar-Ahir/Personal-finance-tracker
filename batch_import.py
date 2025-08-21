#Authors: Adnan Syed, Dhruvkumar Satishbhai Ahir, Kartik Rajeev Patil
#Date: May 02, 2025

#Batch Import Module for Personal Finance Tracker and Advisor.

#This module handles importing multiple transactions at once from CSV files.

import csv
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QTableWidget, 
                           QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt
from datetime import datetime

class BatchImportDialog(QDialog):
    """
    Dialog for batch importing multiple transactions from a CSV file.
    
    This dialog allows users to:
    - Select a CSV file containing multiple transactions
    - Preview the transactions before importing
    - Import selected transactions into the finance tracker
    """
    
    def __init__(self, parent, finance_tracker):
        """
        Initialize the batch import dialog.
        
        Args:
            parent: Parent widget.
            finance_tracker: FinanceTracker instance.
        """
        super().__init__(parent)
        
        self.finance_tracker = finance_tracker
        self.transactions = []
        self.init_ui()
        
    def init_ui(self):
        """
        Set up the user interface.
        """
        # Set dialog properties
        self.setWindowTitle("Batch Import Transactions")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # File selection section
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Select CSV File:"))
        
        self.file_path_label = QLabel("No file selected")
        file_layout.addWidget(self.file_path_label)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_files)
        file_layout.addWidget(browse_button)
        
        layout.addLayout(file_layout)
        
        # Preview section
        preview_label = QLabel("Transaction Preview:")
        layout.addWidget(preview_label)
        
        self.preview_table = QTableWidget(0, 7)
        self.preview_table.setHorizontalHeaderLabels([
            "Date", "Amount", "Category", "Description", 
            "Account Type", "Payment Method", "Import"
        ])
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.preview_table)
        
        # Information label
        info_label = QLabel("CSV Format: transaction_id,date,amount,category,description,account_type,payment_method")
        info_label.setStyleSheet("color: gray;")
        layout.addWidget(info_label)
        
        # Alternative format info
        alt_info_label = QLabel("Alternative Format: date,amount,category,description,account_type,payment_method")
        alt_info_label.setStyleSheet("color: gray;")
        layout.addWidget(alt_info_label)
        
        # Button section
        button_layout = QHBoxLayout()
        
        self.import_button = QPushButton("Import Selected")
        self.import_button.setEnabled(False)
        self.import_button.clicked.connect(self.import_transactions)
        button_layout.addWidget(self.import_button)
        
        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_button)
        
        deselect_all_button = QPushButton("Deselect All")
        deselect_all_button.clicked.connect(self.deselect_all)
        button_layout.addWidget(deselect_all_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
    def browse_files(self):
        """
        Open a file dialog to select a CSV file.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            self.load_csv_preview(file_path)
        
    def load_csv_preview(self, file_path):
        """
        Load the CSV file and display a preview of the transactions.
        
        Args:
            file_path (str): Path to the CSV file.
        """
        try:
            self.transactions = []
            
            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file)
                
                # Skip header row
                header = next(csv_reader, None)
                
                if not header:
                    QMessageBox.warning(self, "Empty File", "The CSV file appears to be empty.")
                    return
                
                # Determine CSV format based on header
                has_transaction_id = len(header) > 6 and header[0].lower() == "transaction_id"
                
                # Process based on format
                if has_transaction_id:
                    # Format: transaction_id,date,amount,category,description,account_type,payment_method
                    for row in csv_reader:
                        if len(row) >= 7:
                            transaction = {
                                'date': row[1],
                                'amount': row[2],
                                'category': row[3],
                                'description': row[4],
                                'account_type': row[5],
                                'payment_method': row[6]
                            }
                            self.transactions.append(transaction)
                else:
                    # Alternative format: date,amount,category,description,account_type,payment_method
                    if len(header) >= 6:
                        # First row might be a header or data
                        # Check if first cell looks like a date
                        try:
                            datetime.strptime(header[0], "%Y-%m-%d")
                            # It's a data row, not a header
                            transaction = {
                                'date': header[0],
                                'amount': header[1],
                                'category': header[2],
                                'description': header[3],
                                'account_type': header[4],
                                'payment_method': header[5]
                            }
                            self.transactions.append(transaction)
                        except ValueError:
                            # It was a header row, just continue
                            pass
                            
                        # Process the rest of the file
                        for row in csv_reader:
                            if len(row) >= 6:
                                transaction = {
                                    'date': row[0],
                                    'amount': row[1],
                                    'category': row[2],
                                    'description': row[3],
                                    'account_type': row[4],
                                    'payment_method': row[5]
                                }
                                self.transactions.append(transaction)
                    else:
                        QMessageBox.warning(
                            self, 
                            "Invalid CSV Format", 
                            "The CSV file does not have the required columns. Please use one of these formats:\n\n"
                            "transaction_id,date,amount,category,description,account_type,payment_method\n\n"
                            "OR\n\n"
                            "date,amount,category,description,account_type,payment_method"
                        )
                        return
                            
                # Update the preview table
                self.update_preview_table()
                
                # Enable import button if transactions are loaded
                self.import_button.setEnabled(len(self.transactions) > 0)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV file: {str(e)}")
            
    def update_preview_table(self):
        """
        Update the preview table with the loaded transactions.
        """
        # Clear the table
        self.preview_table.setRowCount(0)
        
        # Check if we have categories from the finance tracker
        categories = self.finance_tracker.get_category_names()
        
        # Add transactions to the table
        for transaction in self.transactions:
            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)
            
            # Date
            date_item = QTableWidgetItem(transaction['date'])
            self.preview_table.setItem(row, 0, date_item)
            
            # Validate date
            try:
                datetime.strptime(transaction['date'], "%Y-%m-%d")
            except ValueError:
                date_item.setBackground(Qt.red)
                date_item.setToolTip("Invalid date format. Use YYYY-MM-DD.")
                
            # Amount
            amount_item = QTableWidgetItem(transaction['amount'])
            self.preview_table.setItem(row, 1, amount_item)
            
            # Validate amount
            try:
                amount = float(transaction['amount'])
                if amount <= 0:
                    amount_item.setBackground(Qt.red)
                    amount_item.setToolTip("Amount must be positive.")
            except ValueError:
                amount_item.setBackground(Qt.red)
                amount_item.setToolTip("Invalid amount. Must be a number.")
                
            # Category
            category_item = QTableWidgetItem(transaction['category'])
            self.preview_table.setItem(row, 2, category_item)
            
            # Validate category
            if transaction['category'] not in categories:
                category_item.setBackground(Qt.yellow)
                category_item.setToolTip("Category not found in database.")
                
            # Description
            self.preview_table.setItem(row, 3, QTableWidgetItem(transaction['description']))
            
            # Account Type
            self.preview_table.setItem(row, 4, QTableWidgetItem(transaction['account_type']))
            
            # Payment Method
            self.preview_table.setItem(row, 5, QTableWidgetItem(transaction['payment_method']))
            
            # Import checkbox
            import_checkbox = QTableWidgetItem()
            import_checkbox.setCheckState(Qt.Checked)
            self.preview_table.setItem(row, 6, import_checkbox)
            
    def select_all(self):
        """
        Select all transactions for import.
        """
        for row in range(self.preview_table.rowCount()):
            item = self.preview_table.item(row, 6)
            if item:
                item.setCheckState(Qt.Checked)
                
    def deselect_all(self):
        """
        Deselect all transactions for import.
        """
        for row in range(self.preview_table.rowCount()):
            item = self.preview_table.item(row, 6)
            if item:
                item.setCheckState(Qt.Unchecked)
                
    def import_transactions(self):
        """
        Import the selected transactions into the finance tracker.
        """
        successful_imports = 0
        failed_imports = 0
        error_messages = []
        
        categories = self.finance_tracker.get_category_names()
        
        for row in range(self.preview_table.rowCount()):
            # Check if the row is selected for import
            import_item = self.preview_table.item(row, 6)
            if import_item and import_item.checkState() == Qt.Checked:
                # Get transaction data
                date = self.preview_table.item(row, 0).text()
                amount_str = self.preview_table.item(row, 1).text()
                category = self.preview_table.item(row, 2).text()
                description = self.preview_table.item(row, 3).text()
                account_type = self.preview_table.item(row, 4).text()
                payment_method = self.preview_table.item(row, 5).text()
                
                try:
                    # Validate date
                    try:
                        datetime.strptime(date, "%Y-%m-%d")
                    except ValueError:
                        raise ValueError(f"Invalid date format in row {row+1}: {date}")
                        
                    # Validate amount
                    try:
                        amount = float(amount_str)
                        if amount <= 0:
                            raise ValueError(f"Amount must be positive in row {row+1}: {amount}")
                    except ValueError as ve:
                        if "Amount must be positive" in str(ve):
                            raise ve
                        else:
                            raise ValueError(f"Invalid amount in row {row+1}: {amount_str}")
                            
                    # Validate category
                    if category not in categories:
                        # Attempt to create the category with a default budget
                        confirmation = QMessageBox.question(
                            self,
                            "Category Not Found",
                            f"The category '{category}' does not exist in the database. Would you like to create it with a default monthly budget of $200?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )
                        
                        if confirmation == QMessageBox.Yes:
                            # Add the category (this would need to be implemented in the finance_tracker)
                            try:
                                # Use database directly since we don't have a method in finance_tracker for this
                                self.finance_tracker.db.cursor.execute('''
                                INSERT INTO categories
                                (category_name, monthly_budget, priority_level, icon)
                                VALUES (?, ?, ?, ?)
                                ''', (category, 200.00, "Medium", "default"))
                                self.finance_tracker.db.conn.commit()
                                
                                # Update local categories list
                                categories = self.finance_tracker.get_category_names()
                            except Exception as e:
                                raise ValueError(f"Failed to create new category: {str(e)}")
                        else:
                            raise ValueError(f"Category not found in row {row+1}: {category}")
                            
                    # Add transaction
                    result = self.finance_tracker.add_transaction(
                        date, amount, category, description, account_type, payment_method
                    )
                    
                    if result > 0:
                        successful_imports += 1
                    else:
                        failed_imports += 1
                        error_messages.append(f"Failed to add transaction in row {row+1}")
                        
                except Exception as e:
                    failed_imports += 1
                    error_messages.append(f"Error in row {row+1}: {str(e)}")
                    
        # Show results
        message = f"Import complete: {successful_imports} transactions imported successfully."
        
        if failed_imports > 0:
            message += f"\n{failed_imports} transactions failed to import."
            if error_messages:
                message += "\n\nErrors:"
                for error in error_messages[:10]:  # Show at most 10 errors
                    message += f"\n- {error}"
                if len(error_messages) > 10:
                    message += f"\n- ...and {len(error_messages) - 10} more errors"
            
            QMessageBox.warning(self, "Import Results", message)
        else:
            QMessageBox.information(self, "Import Results", message)
        
        # Accept the dialog only if some transactions were imported successfully
        if successful_imports > 0:
            self.accept()
        else:
            # Keep the dialog open if no transactions were imported
            pass