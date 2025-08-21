#Authors: Adnan Syed, Dhruvkumar Satishbhai Ahir, Kartik Rajeev Patil
#Date: May 02, 2025

#GUI Module for Personal Finance Tracker and Advisor.

#This module implements the graphical user interface using PyQt5.
#It provides a user-friendly way to interact with the finance tracker.


import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QPushButton, QComboBox, 
                            QTableWidget, QTableWidgetItem, QLineEdit,
                            QDateEdit, QMessageBox, QTabWidget, QFormLayout,
                            QGroupBox, QSplitter, QFrame, QHeaderView,
                            QDialog, QDialogButtonBox, QFileDialog, QStackedWidget,
                            QScrollArea)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont, QIcon
import datetime

# Import our custom modules
from batch_import import BatchImportDialog
from data_visualizer import FinanceDataVisualizer
from multi_transaction import MultiTransactionDialog
from transaction_clearer import ClearTransactionsDialog

class FinanceTrackerGUI(QMainWindow):
    """
    Main GUI window for the Finance Tracker application.
    
    This class handles:
    - Creating and organizing the user interface
    - Connecting UI elements to the finance tracker functionality
    - Displaying financial data to the user
    - Providing interactive visualizations
    """
    
    def __init__(self, finance_tracker):
        """
        Initialize the GUI window.
        
        Args:
            finance_tracker: FinanceTracker instance for business logic.
        """
        super().__init__()
        
        self.finance_tracker = finance_tracker
        # Create the data visualizer instance
        self.data_visualizer = FinanceDataVisualizer(finance_tracker)
        self.init_ui()
        
    def init_ui(self):
        """
        Set up the user interface with all necessary components.
        """
        # Set up main window
        self.setWindowTitle("Personal Finance Tracker")
        self.setGeometry(100, 100, 1100, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget for main sections
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Dashboard tab
        dashboard_tab = QWidget()
        tabs.addTab(dashboard_tab, "Dashboard")
        dashboard_layout = QVBoxLayout(dashboard_tab)
        
        # Dashboard header with title and refresh button
        header_layout = QHBoxLayout()
        dashboard_layout.addLayout(header_layout)
        
        header_label = QLabel("Financial Dashboard")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(header_label)
        
        refresh_button = QPushButton("Refresh Data")
        refresh_button.clicked.connect(self.refresh_dashboard)
        header_layout.addWidget(refresh_button)
        header_layout.addStretch(1)
        
        # Time period filter for dashboard
        time_filter_layout = QHBoxLayout()
        time_filter_layout.addWidget(QLabel("Time Period:"))
        self.time_period_combo = QComboBox()
        self.time_period_combo.addItems(["Current Month", "Previous Month", "Current Year", "All Time"])
        self.time_period_combo.currentIndexChanged.connect(self.update_dashboard)
        time_filter_layout.addWidget(self.time_period_combo)
        time_filter_layout.addStretch(1)
        dashboard_layout.addLayout(time_filter_layout)
        
        # Transaction management buttons
        transaction_mgmt_layout = QHBoxLayout()
        
        # Clear Transactions button
        clear_button = QPushButton("Clear Transactions")
        clear_button.setStyleSheet("background-color: #f44336; color: white;")
        clear_button.clicked.connect(self.open_transaction_clearer)
        transaction_mgmt_layout.addWidget(clear_button)
        
        transaction_mgmt_layout.addStretch(1)
        
        # Add the transaction management layout to the dashboard
        dashboard_layout.addLayout(transaction_mgmt_layout)
        
        # Split dashboard into panels
        dashboard_splitter = QSplitter(Qt.Horizontal)
        dashboard_layout.addWidget(dashboard_splitter)
        
        # Left panel - Budget summary
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_layout = QVBoxLayout(left_panel)
        
        # Budget usage section
        budget_group = QGroupBox("Budget Usage")
        budget_layout = QVBoxLayout(budget_group)
        self.budget_table = QTableWidget(0, 4)
        self.budget_table.setHorizontalHeaderLabels(["Category", "Spent", "Budget", "Percentage"])
        self.budget_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Make table read-only
        self.budget_table.setEditTriggers(QTableWidget.NoEditTriggers)
        budget_layout.addWidget(self.budget_table)
        left_layout.addWidget(budget_group)
        
        # Right panel - Transactions
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_panel)
        
        # Recent transactions section
        transactions_group = QGroupBox("Recent Transactions")
        transactions_layout = QVBoxLayout(transactions_group)
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentIndexChanged.connect(self.update_transactions)
        filter_layout.addWidget(self.category_filter)
        filter_layout.addStretch(1)
        transactions_layout.addLayout(filter_layout)
        
        self.transactions_table = QTableWidget(0, 7)  # Added an extra column for edit/delete buttons
        self.transactions_table.setHorizontalHeaderLabels(["Date", "Category", "Amount", "Description", "Payment Method", "Edit", "Delete"])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Make transaction table read-only except for edit/delete buttons
        self.transactions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        transactions_layout.addWidget(self.transactions_table)
        right_layout.addWidget(transactions_group)
        
        # Add panels to splitter
        dashboard_splitter.addWidget(left_panel)
        dashboard_splitter.addWidget(right_panel)
        dashboard_splitter.setSizes([400, 600])
        
        # Transactions tab
        transactions_tab = QWidget()
        tabs.addTab(transactions_tab, "Transactions")
        transactions_layout = QVBoxLayout(transactions_tab)
        
        # Form for adding new transactions
        add_transaction_group = QGroupBox("Add New Transaction")
        form_layout = QFormLayout(add_transaction_group)
        
        # Date field
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_edit)
        
        # Amount field
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("Enter amount")
        form_layout.addRow("Amount:", self.amount_edit)
        
        # Category dropdown
        self.category_combo = QComboBox()
        form_layout.addRow("Category:", self.category_combo)
        
        # Description field
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Enter description")
        form_layout.addRow("Description:", self.description_edit)
        
        # Account type dropdown
        self.account_combo = QComboBox()
        self.account_combo.addItems(["Checking", "Savings", "Credit"])
        form_layout.addRow("Account Type:", self.account_combo)
        
        # Payment method dropdown
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash", "Debit Card", "Credit Card", "Bank Transfer", "Mobile Payment"])
        form_layout.addRow("Payment Method:", self.payment_combo)
        
        transactions_layout.addWidget(add_transaction_group)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add transaction button
        self.add_button = QPushButton("Add Transaction")
        self.add_button.clicked.connect(self.add_transaction)
        buttons_layout.addWidget(self.add_button)
        
        # Batch import button
        self.batch_import_button = QPushButton("Batch Import from CSV")
        self.batch_import_button.clicked.connect(self.open_batch_import)
        buttons_layout.addWidget(self.batch_import_button)
        
        # Multi-transaction button
        self.multi_transaction_button = QPushButton("Add Multiple Transactions")
        self.multi_transaction_button.clicked.connect(self.open_multi_transaction)
        buttons_layout.addWidget(self.multi_transaction_button)
        
        transactions_layout.addLayout(buttons_layout)
        transactions_layout.addStretch(1)
        
        # Visualizations tab
        visualizations_tab = QWidget()
        tabs.addTab(visualizations_tab, "Visualizations")
        viz_layout = QVBoxLayout(visualizations_tab)
        
        # Visualization type selector
        viz_selector_layout = QHBoxLayout()
        viz_selector_layout.addWidget(QLabel("Select Visualization:"))
        self.viz_type_combo = QComboBox()
        self.viz_type_combo.addItems([
            "Spending by Category", 
            "Monthly Spending Trend", 
            "Budget vs. Actual Spending"
        ])
        self.viz_type_combo.currentIndexChanged.connect(self.update_visualization)
        viz_selector_layout.addWidget(self.viz_type_combo)
        
        # Refresh visualization button
        refresh_viz_button = QPushButton("Refresh Visualization")
        refresh_viz_button.clicked.connect(self.refresh_visualization)
        viz_selector_layout.addWidget(refresh_viz_button)
        
        viz_selector_layout.addStretch(1)
        viz_layout.addLayout(viz_selector_layout)
        
        # Visualization container
        self.viz_stack = QStackedWidget()
        viz_layout.addWidget(self.viz_stack)
        
        # Add visualization widgets
        self.viz_stack.addWidget(self.data_visualizer.create_visualization_widget("spending_by_category"))
        self.viz_stack.addWidget(self.data_visualizer.create_visualization_widget("monthly_trend"))
        self.viz_stack.addWidget(self.data_visualizer.create_visualization_widget("budget_comparison"))
        
        # Load initial data
        self.load_categories()
        self.refresh_dashboard()
        
    def load_categories(self):
        """
        Load categories into the category dropdowns.
        """
        # Get categories from finance tracker
        categories = self.finance_tracker.get_category_names()
        
        # Update category combo box
        self.category_combo.clear()
        self.category_combo.addItems(categories)
        
        # Update category filter
        current_text = self.category_filter.currentText()
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(categories)
        
        # Try to restore previous selection
        index = self.category_filter.findText(current_text)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)
            
    def refresh_dashboard(self):
        """
        Refresh all dashboard elements.
        """
        self.update_dashboard()
        self.update_transactions()
        self.refresh_visualization()
        
    def refresh_visualization(self):
        """
        Refresh the current visualization to reflect updated data.
        """
        viz_type_index = self.viz_type_combo.currentIndex()
        
        # Create a new visualization widget based on the current selection
        viz_widget = None
        if viz_type_index == 0:
            viz_widget = self.data_visualizer.create_visualization_widget("spending_by_category")
        elif viz_type_index == 1:
            viz_widget = self.data_visualizer.create_visualization_widget("monthly_trend")
        elif viz_type_index == 2:
            viz_widget = self.data_visualizer.create_visualization_widget("budget_comparison")
            
        # Replace the current widget with the new one
        self.viz_stack.removeWidget(self.viz_stack.widget(viz_type_index))
        self.viz_stack.insertWidget(viz_type_index, viz_widget)
        self.viz_stack.setCurrentIndex(viz_type_index)
        
    def update_dashboard(self):
        """
        Update dashboard data based on selected time period.
        """
        # Get time period from combo box
        time_period_index = self.time_period_combo.currentIndex()
        if time_period_index == 0:
            time_period = "month"
        elif time_period_index == 1:
            time_period = "prev_month"
        elif time_period_index == 2:
            time_period = "year"
        else:
            time_period = "all"
            
        # Get budget usage data
        budget_data = self.finance_tracker.calculate_budget_usage(time_period)
            
        # Update budget table
        self.budget_table.setRowCount(len(budget_data))
        for row, (category, spent, budget, percentage) in enumerate(budget_data):
            # Category
            self.budget_table.setItem(row, 0, QTableWidgetItem(category))
            
            # Spent
            spent_item = QTableWidgetItem(f"${spent:.2f}")
            spent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.budget_table.setItem(row, 1, spent_item)
            
            # Budget
            budget_item = QTableWidgetItem(f"${budget:.2f}")
            budget_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.budget_table.setItem(row, 2, budget_item)
            
            # Percentage
            percentage_item = QTableWidgetItem(f"{percentage:.1f}%")
            percentage_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Highlight over-budget categories
            if percentage > 100:
                percentage_item.setBackground(QColor(255, 80, 80))  # red
            elif percentage > 80:
                percentage_item.setBackground(QColor(255, 255, 80))  # yellow
            else:
                percentage_item.setBackground(QColor(80, 200, 80))  # green
                
            self.budget_table.setItem(row, 3, percentage_item)
            
    def update_transactions(self):
        """
        Update transactions table based on category filter.
        """
        # Get selected category
        category = self.category_filter.currentText()
        
        # Get transactions
        if category == "All Categories":
            transactions = self.finance_tracker.get_recent_transactions(20)
        else:
            transactions = self.finance_tracker.get_transactions_by_category(category)
            
        # Update table
        self.transactions_table.setRowCount(len(transactions))
        
        for row, transaction in enumerate(transactions):
            # Parse transaction data
            # SQLite returns: transaction_id, date, amount, category, description, account_type, payment_method
            transaction_id = transaction[0]
            date = transaction[1]
            amount = transaction[2]
            category = transaction[3]
            description = transaction[4]
            payment_method = transaction[6]
            
            # Date
            self.transactions_table.setItem(row, 0, QTableWidgetItem(date))
            
            # Category
            self.transactions_table.setItem(row, 1, QTableWidgetItem(category))
            
            # Amount
            amount_item = QTableWidgetItem(f"${amount:.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.transactions_table.setItem(row, 2, amount_item)
            
            # Description
            self.transactions_table.setItem(row, 3, QTableWidgetItem(description))
            
            # Payment Method
            self.transactions_table.setItem(row, 4, QTableWidgetItem(payment_method))
            
            # Edit button
            edit_button = QPushButton("Edit")
            edit_button.setStyleSheet("background-color: #4caf50;")
            # Store the transaction_id as a property of the button
            edit_button.setProperty("transaction_id", transaction_id)
            edit_button.clicked.connect(self.edit_transaction)
            self.transactions_table.setCellWidget(row, 5, edit_button)
            
            # Delete button
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("background-color: #f44336;")
            # Store the transaction_id as a property of the button
            delete_button.setProperty("transaction_id", transaction_id)
            delete_button.clicked.connect(self.delete_transaction)
            self.transactions_table.setCellWidget(row, 6, delete_button)
    
    def update_visualization(self):
        """
        Update the visualization based on selected type.
        """
        # Get selected visualization type
        viz_type_index = self.viz_type_combo.currentIndex()
        
        # Update the stacked widget to show the selected visualization
        self.viz_stack.setCurrentIndex(viz_type_index)
        
        self.refresh_visualization()
        
    def add_transaction(self):
        """
        Add a new transaction from form data.
        """
        try:
            # Get values from form
            date = self.date_edit.date().toString("yyyy-MM-dd")
            
            # Validate amount
            try:
                amount = float(self.amount_edit.text())
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except ValueError:
                QMessageBox.warning(self, "Invalid Amount", "Please enter a valid positive number for the amount.")
                return
                
            category = self.category_combo.currentText()
            description = self.description_edit.text()
            account_type = self.account_combo.currentText()
            payment_method = self.payment_combo.currentText()
            
            # Add transaction
            result = self.finance_tracker.add_transaction(
                date, amount, category, description, account_type, payment_method
            )
            
            if result > 0:
                QMessageBox.information(self, "Success", "Transaction added successfully.")
                
                # Clear form
                self.amount_edit.clear()
                self.description_edit.clear()
                
                # Refresh dashboard
                self.refresh_dashboard()
            else:
                QMessageBox.warning(self, "Error", "Failed to add transaction. Please check your input.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def open_multi_transaction(self):
        """
        Open the multi-transaction dialog.
        """
        dialog = MultiTransactionDialog(self, self.finance_tracker)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh dashboard after successful import
            self.refresh_dashboard()
    
    def open_batch_import(self):
        """
        Open the batch import dialog.
        """
        dialog = BatchImportDialog(self, self.finance_tracker)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh dashboard after successful import
            self.refresh_dashboard()
            
    def open_transaction_clearer(self):
        """
        Open the transaction clearing dialog.
        """
        dialog = ClearTransactionsDialog(self, self.finance_tracker)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh dashboard after clearing transactions
            self.refresh_dashboard()
            
    def delete_transaction(self):
        """
        Deletes a transaction when the delete button is clicked.
        """
        # Gets the button that was clicked
        button = self.sender()
        if not button:
            return
            
        # Gets the transaction_id from the button's properties
        transaction_id = button.property("transaction_id")
        if not transaction_id:
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete this transaction?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Deletes the transaction
            success = self.finance_tracker.delete_transaction(transaction_id)
            
            if success:
                QMessageBox.information(self, "Success", "Transaction deleted successfully!")
                # Refreshes the dashboard
                self.refresh_dashboard()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete transaction!")
                
    def edit_transaction(self):
        """
        Opens an edit dialog for a transaction when the edit button is clicked.
        """
        # Gets the button that was clicked
        button = self.sender()
        if not button:
            return
            
        # Gets the transaction_id from the button's properties
        transaction_id = button.property("transaction_id")
        if not transaction_id:
            return
            
        # Gets the transaction data
        transaction = self.finance_tracker.get_transaction(transaction_id)
        if not transaction:
            QMessageBox.warning(self, "Error", "Transaction not found.")
            return
            
        # Opens the edit dialog
        dialog = EditTransactionDialog(self, transaction, self.finance_tracker)
        if dialog.exec_() == QDialog.Accepted:
            # Refreshes the dashboard
            self.refresh_dashboard()


class EditTransactionDialog(QDialog):
    """
    Dialog for editing an existing transaction.
    
    This dialog allows users to:
    - View and modify transaction details
    - Save changes to the database
    - Cancel and discard changes
    """
    
    def __init__(self, parent, transaction, finance_tracker):
        """
        Initialize the edit transaction dialog.
        
        Args:
            parent: Parent widget.
            transaction: Transaction data to edit.
            finance_tracker: FinanceTracker instance.
        """
        super().__init__(parent)
        
        self.transaction = transaction
        self.finance_tracker = finance_tracker
        
        self.init_ui()
        
    def init_ui(self):
        """
        Set up the dialog UI.
        """
        # Set dialog properties
        self.setWindowTitle("Edit Transaction")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create form layout
        form_layout = QFormLayout()
        layout.addLayout(form_layout)
        
        # Transaction ID (read-only)
        self.transaction_id = self.transaction[0]
        id_label = QLabel(f"Transaction ID: {self.transaction_id}")
        layout.addWidget(id_label)
        
        # Date field
        self.date_edit = QDateEdit()
        date = datetime.datetime.strptime(self.transaction[1], "%Y-%m-%d").date()
        self.date_edit.setDate(QDate(date.year, date.month, date.day))
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_edit)
        
        # Amount field
        self.amount_edit = QLineEdit()
        self.amount_edit.setText(str(self.transaction[2]))
        form_layout.addRow("Amount:", self.amount_edit)
        
        # Category dropdown
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.finance_tracker.get_category_names())
        current_category_index = self.category_combo.findText(self.transaction[3])
        if current_category_index >= 0:
            self.category_combo.setCurrentIndex(current_category_index)
        form_layout.addRow("Category:", self.category_combo)
        
        # Description field
        self.description_edit = QLineEdit()
        self.description_edit.setText(self.transaction[4])
        form_layout.addRow("Description:", self.description_edit)
        
        # Account type dropdown
        self.account_combo = QComboBox()
        self.account_combo.addItems(["Checking", "Savings", "Credit"])
        current_account_index = self.account_combo.findText(self.transaction[5])
        if current_account_index >= 0:
            self.account_combo.setCurrentIndex(current_account_index)
        form_layout.addRow("Account Type:", self.account_combo)
        
        # Payment method dropdown
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash", "Debit Card", "Credit Card", "Bank Transfer", "Mobile Payment"])
        current_payment_index = self.payment_combo.findText(self.transaction[6])
        if current_payment_index >= 0:
            self.payment_combo.setCurrentIndex(current_payment_index)
        form_layout.addRow("Payment Method:", self.payment_combo)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def save_changes(self):
        """
        Saves the changes to the transaction.
        """
        try:
            # Get values from form
            date = self.date_edit.date().toString("yyyy-MM-dd")
            
            # Validate amount
            try:
                amount = float(self.amount_edit.text())
                if amount <= 0:
                    raise ValueError("Amount must be positive!")
            except ValueError:
                QMessageBox.warning(self, "Invalid Amount", "Please enter a valid positive number for the amount!")
                return
                
            category = self.category_combo.currentText()
            description = self.description_edit.text()
            account_type = self.account_combo.currentText()
            payment_method = self.payment_combo.currentText()
            
            # Update transaction
            success = self.finance_tracker.update_transaction(
                self.transaction_id,
                date,
                amount,
                category,
                description,
                account_type,
                payment_method
            )
            
            if success:
                QMessageBox.information(self, "Success", "Transaction updated successfully!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to update transaction. Please check your input!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")