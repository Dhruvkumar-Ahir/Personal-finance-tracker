# Personal Finance Tracker and Advisor

A comprehensive financial management application that helps users track their spending, analyze expenses, and make better financial decisions.

## Authors
- Adnan Syed
- Dhruvkumar Satishbhai Ahir
- Kartik Rajeev Patil

## Date
May 02, 2025

## Features

- **Transaction Management**: Add, edit, delete, and view financial transactions
- **Budget Tracking**: Set and monitor monthly budgets for different spending categories
- **Multi-Transaction Import**: Batch import multiple transactions from CSV files
- **Data Visualization**: View spending patterns with interactive charts and graphs
- **Financial Insights**: See budget usage percentages and identify over-budget categories
- **User-Friendly Interface**: Intuitive GUI with color-coded budget indicators

## Installation Requirements

- Python 3.12 or later
- Required Python modules:
  - PyQt5 (for GUI)
  - Matplotlib (for data visualization)
  - SQLite3 (built into Python, for database operations)

To install the required modules, run:
```
pip install PyQt5 matplotlib
```

## Usage Instructions

### Starting the Application

1. Run the `main.py` file to start the application:
   ```
   python main.py
   ```

2. The application will open with the Dashboard tab selected.

### Dashboard Tab

- **Budget Usage Table**: Shows your spending for each category compared to your budget
  - Green: Under 80% of budget
  - Yellow: Between 80% and 100% of budget
  - Red: Over 100% of budget (exceeded budget)
  
- **Recent Transactions**: Displays your most recent transactions
  - Filter transactions by category using the dropdown menu
  - Edit or delete transactions using the buttons provided

- **Time Period Filter**: Select different time periods to view your financial data
  - Current Month (default)
  - Previous Month
  - Current Year
  - All Time

### Transactions Tab

- **Add Transaction**: Enter transaction details and click "Add Transaction"
  - Date: Select the transaction date
  - Amount: Enter the amount (must be a positive number)
  - Category: Select from predefined categories
  - Description: Enter a description or vendor name
  - Account Type: Select the account type
  - Payment Method: Select the payment method

- **Batch Import**: Import multiple transactions at once from a CSV file
  - Click "Batch Import from CSV"
  - Select a CSV file with the required format
  - Review and select transactions to import
  - Click "Import Selected"
  
  *CSV Format:* date,amount,category,description,account_type,payment_method

### Visualizations Tab

- **Visualization Types**: Select from different visualization types
  - Spending by Category: Pie chart showing the distribution of your spending
  - Monthly Spending Trend: Line chart showing your spending over time
  - Budget vs. Actual Spending: Bar chart comparing your budget to actual spending

## Data Files

The application looks for CSV files in the `data` directory:
- `categories.csv`: Contains budget categories and monthly budget allocations
- `transactions.csv`: Contains transaction records

If these files don't exist, the application will create a new database with default categories.

## Database

The application uses SQLite for data storage. The database file `finance_tracker.db` will be created in the application directory.

## Help and Support

If you have any questions or issues, please contact one of the authors or submit an issue on GitHub.

Happy budgeting!