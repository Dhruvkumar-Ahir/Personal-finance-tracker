#Authors: Adnan Syed, Dhruvkumar Satishbhai Ahir, Kartik Rajeev Patil
#Date: May 02, 2025

#Multi-Transaction Module for Personal Finance Tracker and Advisor.

#This module provides a dialog for adding multiple transactions at once.

import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QMessageBox, QDateEdit, QComboBox,
                           QLineEdit, QScrollArea, QWidget, QFormLayout,
                           QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime

class MultiTransactionDialog(QDialog):
    """
    Dialog for adding multiple transactions at once.
    
    This dialog allows users to:
    - Add multiple transaction entries in a single view
    - Validate each transaction before saving
    - Save all transactions to the database at once
    """
    
    def __init__(self, parent, finance_tracker):
        """
        Initialize the multi-transaction dialog.
        
        Args:
            parent: Parent widget.
            finance_tracker: FinanceTracker instance.
        """
        super().__init__(parent)
        
        self.finance_tracker = finance_tracker
        self.transaction_forms = []  # List to store transaction form groups
        self.init_ui()
        
    def init_ui(self):
        """
        Set up the user interface.
        """
        # Set dialog properties
        self.setWindowTitle("Add Multiple Transactions")
        self.setMinimumWidth(750)
        self.setMinimumHeight(500)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Header section
        header_layout = QHBoxLayout()
        title_label = QLabel("Add Multiple Transactions")
        title_label.setFont(title_label.font())
        title_label.font().setBold(True)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)
        
        # Create a scroll area for transaction forms
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # Create container widget for scroll area
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        self.transactions_layout = QVBoxLayout(scroll_content)
        
        # Add initial transaction form
        self.add_transaction_form()
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Add more transactions button
        add_more_button = QPushButton("Add Another Transaction")
        add_more_button.clicked.connect(self.add_transaction_form)
        button_layout.addWidget(add_more_button)
        
        # Remove last transaction button
        self.remove_button = QPushButton("Remove Last Transaction")
        self.remove_button.clicked.connect(self.remove_transaction_form)
        self.remove_button.setEnabled(False)  # Disabled until we have more than one transaction
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch(1)
        
        # Save and cancel buttons
        save_button = QPushButton("Save All Transactions")
        save_button.clicked.connect(self.save_transactions)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
        
    def add_transaction_form(self):
        """
        Add a new transaction form to the layout.
        """
        # Create a group box for this transaction
        form_index = len(self.transaction_forms) + 1
        group_box = QGroupBox(f"Transaction #{form_index}")
        form_layout = QFormLayout(group_box)
        
        # Date field
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", date_edit)
        
        # Amount field
        amount_edit = QLineEdit()
        amount_edit.setPlaceholderText("Enter amount")
        form_layout.addRow("Amount:", amount_edit)
        
        # Category dropdown
        category_combo = QComboBox()
        category_combo.addItems(self.finance_tracker.get_category_names())
        form_layout.addRow("Category:", category_combo)
        
        # Description field
        description_edit = QLineEdit()
        description_edit.setPlaceholderText("Enter description")
        form_layout.addRow("Description:", description_edit)
        
        # Account type dropdown
        account_combo = QComboBox()
        account_combo.addItems(["Checking", "Savings", "Credit"])
        form_layout.addRow("Account Type:", account_combo)
        
        # Payment method dropdown
        payment_combo = QComboBox()
        payment_combo.addItems(["Cash", "Debit Card", "Credit Card", "Bank Transfer", "Mobile Payment"])
        form_layout.addRow("Payment Method:", payment_combo)
        
        # Add the form to the list
        form_data = {
            'group_box': group_box,
            'date_edit': date_edit,
            'amount_edit': amount_edit,
            'category_combo': category_combo,
            'description_edit': description_edit,
            'account_combo': account_combo,
            'payment_combo': payment_combo
        }
        
        self.transaction_forms.append(form_data)
        
        # Add the group box to the layout
        self.transactions_layout.addWidget(group_box)
        
        # Enable the remove button if we have more than one transaction
        if len(self.transaction_forms) > 1:
            self.remove_button.setEnabled(True)
            
    def remove_transaction_form(self):
        """
        Remove the last transaction form from the layout.
        """
        if len(self.transaction_forms) > 1:
            # Get the last form
            form_data = self.transaction_forms.pop()
            
            # Remove the group box from the layout
            self.transactions_layout.removeWidget(form_data['group_box'])
            
            # Delete the group box
            form_data['group_box'].deleteLater()
            
            # Disable the remove button if only one transaction remains
            if len(self.transaction_forms) == 1:
                self.remove_button.setEnabled(False)
                
    def save_transactions(self):
        """
        Save all transactions to the database.
        """
        successful_count = 0
        failed_count = 0
        error_messages = []
        
        # Process each transaction form
        for form_index, form_data in enumerate(self.transaction_forms):
            try:
                # Get values from form
                date = form_data['date_edit'].date().toString("yyyy-MM-dd")
                
                # Validate amount
                try:
                    amount_text = form_data['amount_edit'].text()
                    if not amount_text:
                        raise ValueError(f"Transaction #{form_index+1}: Amount is required")
                        
                    amount = float(amount_text)
                    if amount <= 0:
                        raise ValueError(f"Transaction #{form_index+1}: Amount must be positive")
                except ValueError as e:
                    if "could not convert string to float" in str(e):
                        error_messages.append(f"Transaction #{form_index+1}: Invalid amount format")
                    else:
                        error_messages.append(str(e))
                    failed_count += 1
                    continue
                    
                category = form_data['category_combo'].currentText()
                description = form_data['description_edit'].text()
                account_type = form_data['account_combo'].currentText()
                payment_method = form_data['payment_combo'].currentText()
                
                # Add transaction
                result = self.finance_tracker.add_transaction(
                    date, amount, category, description, account_type, payment_method
                )
                
                if result > 0:
                    successful_count += 1
                else:
                    failed_count += 1
                    error_messages.append(f"Transaction #{form_index+1}: Failed to add to database")
                    
            except Exception as e:
                failed_count += 1
                error_messages.append(f"Transaction #{form_index+1}: {str(e)}")
                
        # Show results
        if successful_count > 0:
            message = f"Successfully added {successful_count} transactions."
            
            if failed_count > 0:
                message += f"\n\nFailed to add {failed_count} transactions:"
                for error in error_messages:
                    message += f"\n- {error}"
                    
                QMessageBox.warning(self, "Partial Success", message)
            else:
                QMessageBox.information(self, "Success", message)
                self.accept()
        else:
            message = f"Failed to add any transactions:"
            for error in error_messages:
                message += f"\n- {error}"
                
            QMessageBox.critical(self, "Error", message)
