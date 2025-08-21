#Authors: Adnan Syed, Dhruvkumar Satishbhai Ahir, Kartik Rajeev Patil
#Date: May 02, 2025

#Transaction Clearer Module for Personal Finance Tracker and Advisor.

#This module provides dialogs for clearing transactions by date range or all at once.

import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QMessageBox, QDateEdit,
                           QGroupBox, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime

class ClearTransactionsDialog(QDialog):
    """
    Dialog for clearing transactions by date range or all at once.
    
    This dialog allows users to:
    - Clear all transactions between two dates
    - Clear all transactions from the database
    """
    
    def __init__(self, parent, finance_tracker):
        """
        Initialize the clear transactions dialog.
        
        Args:
            parent: Parent widget.
            finance_tracker: FinanceTracker instance.
        """
        super().__init__(parent)
        
        self.finance_tracker = finance_tracker
        self.init_ui()
        
    def init_ui(self):
        """
        Set up the user interface.
        """
        # Set dialog properties
        self.setWindowTitle("Clear Transactions")
        self.setMinimumWidth(450)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Date range group
        date_group = QGroupBox("Clear Transactions by Date Range")
        date_layout = QFormLayout(date_group)
        
        # Start date
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))  # Default to 1 month ago
        self.start_date_edit.setCalendarPopup(True)
        date_layout.addRow("Start Date:", self.start_date_edit)
        
        # End date
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())  # Default to today
        self.end_date_edit.setCalendarPopup(True)
        date_layout.addRow("End Date:", self.end_date_edit)
        
        # Clear by date range button
        clear_range_button = QPushButton("Clear Transactions in Range")
        clear_range_button.clicked.connect(self.clear_by_date_range)
        date_layout.addRow("", clear_range_button)
        
        main_layout.addWidget(date_group)
        
        # Separator
        separator = QLabel("")
        separator.setStyleSheet("background-color: lightgray; min-height: 1px;")
        main_layout.addWidget(separator)
        
        # Clear all group
        clear_all_group = QGroupBox("Clear All Transactions")
        clear_all_layout = QVBoxLayout(clear_all_group)
        
        warning_label = QLabel("Warning: This will permanently delete ALL transactions from the database!")
        warning_label.setStyleSheet("color: red; font-weight: bold;")
        clear_all_layout.addWidget(warning_label)
        
        clear_all_button = QPushButton("Clear All Transactions")
        clear_all_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        clear_all_button.clicked.connect(self.clear_all_transactions)
        clear_all_layout.addWidget(clear_all_button)
        
        main_layout.addWidget(clear_all_group)
        
        # Cancel button
        button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
    def clear_by_date_range(self):
        """
        Clear transactions between the specified start and end dates.
        """
        # Get date range
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        # Confirm action
        confirmation = QMessageBox.question(
            self,
            "Confirm Clear Transactions",
            f"Are you sure you want to clear all transactions between {start_date} and {end_date}?\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirmation == QMessageBox.Yes:
            # Clear transactions
            count = self.finance_tracker.clear_transactions_by_date_range(start_date, end_date)
            
            if count > 0:
                QMessageBox.information(
                    self,
                    "Transactions Cleared",
                    f"Successfully cleared {count} transactions between {start_date} and {end_date}."
                )
                self.accept()
            else:
                QMessageBox.information(
                    self,
                    "No Transactions Cleared",
                    f"No transactions found between {start_date} and {end_date}."
                )
    
    def clear_all_transactions(self):
        """
        Clear all transactions from the database.
        """
        # Double confirmation for destructive action
        confirmation1 = QMessageBox.warning(
            self,
            "Confirm Clear All Transactions",
            "Are you sure you want to clear ALL transactions from the database?\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirmation1 == QMessageBox.Yes:
            confirmation2 = QMessageBox.warning(
                self,
                "Final Confirmation",
                "ALL TRANSACTIONS WILL BE PERMANENTLY DELETED!\n\nAre you absolutely sure you want to proceed?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirmation2 == QMessageBox.Yes:
                # Clear all transactions
                count = self.finance_tracker.clear_all_transactions()
                
                if count > 0:
                    QMessageBox.information(
                        self,
                        "All Transactions Cleared",
                        f"Successfully cleared all {count} transactions from the database."
                    )
                    self.accept()
                else:
                    QMessageBox.information(
                        self,
                        "No Transactions Cleared",
                        "No transactions found in the database."
                    )