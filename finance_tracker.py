#Authors: Adnan Syed, Dhruvkumar Satishbhai Ahir, Kartik Rajeev Patil
#Date: May 02, 2025

#Finance Tracker Module for Personal Finance Tracker and Advisor.

#This module handles the business logic for tracking finances
#and provides methods for analyzing financial data.


from datetime import datetime, timedelta
import calendar

class FinanceTracker:
    """
    Finance Tracker class that manages financial data and analysis.
    
    This class provides methods for:
    - Adding and retrieving transactions
    - Calculating spending by category
    - Analyzing budget usage
    - Generating basic financial insights
    """
    
    def __init__(self, database):
        """
        Initializes the finance tracker with a database connection.
        
        Args:
            database: Database instance for data storage and retrieval.
        """
        self.db = database
        
    def add_transaction(self, date, amount, category, description, account_type, payment_method):
        """
        Adds a new transaction.
        
        Args:
            date (str): Transaction date in YYYY-MM-DD format.
            amount (float): Transaction amount.
            category (str): Transaction category.
            description (str): Transaction description.
            account_type (str): Account type.
            payment_method (str): Payment method.
            
        Returns:
            int: Transaction ID if successful, -1 otherwise.
        """
        return self.db.add_transaction(date, amount, category, description, account_type, payment_method)
        
    def get_recent_transactions(self, limit=10):
        """
        Gets the most recent transactions.
        
        Args:
            limit (int): Maximum number of transactions to return.
            
        Returns:
            list: List of transaction data.
        """
        return self.db.get_all_transactions(limit)
        
    def get_transactions_by_category(self, category):
        """
        Gets the transactions for a specific category.
        
        Args:
            category (str): Category name.
            
        Returns:
            list: List of transaction data.
        """
        return self.db.get_transactions_by_category(category)
        
    def get_all_categories(self):
        """
        Gets all the available categories from the database.
        
        Returns:
            list: List of category data.
        """
        return self.db.get_all_categories()
        
    def get_category_names(self):
        """
        Gets only the names of all categories.
        
        Returns:
            list: List of category names.
        """
        categories = self.db.get_all_categories()
        return [category[1] for category in categories]  # category_name is at index 1
        
    def get_spending_by_category(self, time_period="all"):
        """
        Gets the total spending by category for a specified time period.
        
        Args:
            time_period (str): Time period for analysis. Options:
                - "all": All time
                - "month": Current month
                - "prev_month": Previous month
                - "year": Current year
                
        Returns:
            list: List of (category, amount) tuples.
        """
        today = datetime.now()
        
        if time_period == "month":
            # Current month
            start_date = f"{today.year}-{today.month:02d}-01"
            # Last day of current month
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_date = f"{today.year}-{today.month:02d}-{last_day}"
            
        elif time_period == "prev_month":
            # Previous month
            prev_month_date = today.replace(day=1) - timedelta(days=1)
            start_date = f"{prev_month_date.year}-{prev_month_date.month:02d}-01"
            last_day = calendar.monthrange(prev_month_date.year, prev_month_date.month)[1]
            end_date = f"{prev_month_date.year}-{prev_month_date.month:02d}-{last_day}"
            
        elif time_period == "year":
            # Current year
            start_date = f"{today.year}-01-01"
            end_date = f"{today.year}-12-31"
            
        else:  # "all" or any invalid values
            # All time
            start_date = None
            end_date = None
            
        return self.db.get_spending_by_category(start_date, end_date)
        
    def calculate_budget_usage(self, time_period="month"):
        """
        Calculates the budget usage for each category.
        
        Args:
            time_period (str): Time period for analysis. Options:
                - "month": Current month (default)
                - "prev_month": Previous month
                - "year": Current year
                - "all": All time
                
        Returns:
            list: List of (category, spent, budget, percentage) tuples.
        """
        # Gets the spending by category for the specified time period
        spending = self.get_spending_by_category(time_period)
        
        # Gets all the categories and their budgets
        categories = self.db.get_all_categories()
        
        # Creates a dictionary of the category budgets for easy lookup
        budgets = {category[1]: category[2] for category in categories}  # category_name: monthly_budget
        
        # For year and all time, we need to adjust the budget calculation
        today = datetime.now()
        budget_multiplier = 1.0  # Default for month

        if time_period == "year":
            # For a full year, multiply by 12
            budget_multiplier = 12.0
        elif time_period == "all":
            # For all time, we need to find the range of dates in transactions
            try:
                self.db.cursor.execute("SELECT MIN(date), MAX(date) FROM transactions")
                date_range = self.db.cursor.fetchone()
                if date_range and date_range[0] and date_range[1]:
                    min_date = datetime.strptime(date_range[0], "%Y-%m-%d")
                    max_date = datetime.strptime(date_range[1], "%Y-%m-%d")
                    # Calculate number of months (including partial months)
                    month_diff = (max_date.year - min_date.year) * 12 + max_date.month - min_date.month
                    if month_diff < 1:
                        budget_multiplier = 1.0  # At least one month
                    else:
                        budget_multiplier = float(month_diff + 1)  # +1 to include partial months
            except:
                budget_multiplier = 1.0  # Default to 1 month if there's an error
        
        # Calculates the budget usage for each category
        budget_usage = []
        for category_data in categories:
            category_name = category_data[1]
            monthly_budget = category_data[2]
            
            # Calculate total budget based on time period
            total_budget = monthly_budget * budget_multiplier
            
            # Find the spending for this category
            spent = 0
            for spend_category, amount in spending:
                if spend_category == category_name:
                    spent = amount
                    break
                    
            # Calculates the percentage of the budget used
            percentage = (spent / total_budget * 100) if total_budget > 0 else 0
            
            budget_usage.append((category_name, spent, total_budget, percentage))
            
        # Sort by the percentage of budget used in descending order
        budget_usage.sort(key=lambda x: x[3], reverse=True)
        
        return budget_usage
        
    def get_over_budget_categories(self, time_period="month"):
        """
        Gets the categories that are over the budget for the specified time period.
        
        Args:
            time_period (str): Time period to check. Options:
                - "month": Current month (default)
                - "prev_month": Previous month
                - "year": Current year
                - "all": All time
                
        Returns:
            list: List of (category, spent, budget, percentage) tuples for over-budget categories.
        """
        budget_usage = self.calculate_budget_usage(time_period)
        return [category for category in budget_usage if category[3] > 100]
        
    def get_spending_trend(self, num_months=6):
        """
        Gets the monthly spending trend for the past several months.
        
        Args:
            num_months (int): Number of months to include.
            
        Returns:
            dict: Dictionary with months as keys and total spending as values.
        """
        today = datetime.now()
        spending_trend = {}
        
        for i in range(num_months):
            # Calculate month
            month_date = today.replace(day=1) - timedelta(days=i * 30)
            month_str = f"{month_date.year}-{month_date.month:02d}"
            month_name = month_date.strftime("%b %Y")
            
            # Calculate date range for the month
            start_date = f"{month_date.year}-{month_date.month:02d}-01"
            last_day = calendar.monthrange(month_date.year, month_date.month)[1]
            end_date = f"{month_date.year}-{month_date.month:02d}-{last_day}"
            
            # Get spending for the month
            spending = self.db.get_spending_by_category(start_date, end_date)
            total = sum(amount for _, amount in spending)
            
            spending_trend[month_name] = total
            
        return spending_trend
        
    def get_account_types(self):
        """
        Gets the unique account types from transactions.
        
        Returns:
            list: List of account types.
        """
        try:
            self.db.cursor.execute("SELECT DISTINCT account_type FROM transactions")
            results = self.db.cursor.fetchall()
            return [r[0] for r in results if r[0]]
        except Exception as e:
            print(f"Error getting account types: {e}")
            return []
            
    def get_payment_methods(self):
        """
        Gets the unique payment methods from the transactions.
        
        Returns:
            list: List of payment methods.
        """
        try:
            self.db.cursor.execute("SELECT DISTINCT payment_method FROM transactions")
            results = self.db.cursor.fetchall()
            return [r[0] for r in results if r[0]]
        except Exception as e:
            print(f"Error getting payment methods: {e}")
            return []
            
    def delete_transaction(self, transaction_id):
        """
        Deletes a transaction.
        
        Args:
            transaction_id (int): ID of the transaction to delete.
            
        Returns:
            bool: True if transaction was deleted successfully, False otherwise.
        """
        return self.db.delete_transaction(transaction_id)
        
    def update_transaction(self, transaction_id, date, amount, category, description, account_type, payment_method):
        """
        Updates an existing transaction.
        
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
        return self.db.update_transaction(transaction_id, date, amount, category, description, account_type, payment_method)
        
    def get_transaction(self, transaction_id):
        """
        Gets a specific transaction by its ID.
        
        Args:
            transaction_id (int): ID of the transaction to retrieve.
            
        Returns:
            tuple: Transaction data, or None if not found.
        """
        return self.db.get_transaction(transaction_id)

    def clear_transactions_by_date_range(self, start_date, end_date):
        """
        Clears all transactions between the specified start and end dates.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.
            
        Returns:
            int: Number of transactions deleted.
        """
        try:
            # Validate dates
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD format.")
                return 0
                
            # Get count of transactions to be deleted (for return value)
            self.db.cursor.execute(
                "SELECT COUNT(*) FROM transactions WHERE date >= ? AND date <= ?",
                (start_date, end_date)
            )
            count = self.db.cursor.fetchone()[0]
            
            # Delete transactions
            self.db.cursor.execute(
                "DELETE FROM transactions WHERE date >= ? AND date <= ?",
                (start_date, end_date)
            )
            
            self.db.conn.commit()
            return count
            
        except Exception as e:
            print(f"Error clearing transactions by date range: {e}")
            return 0
            
    def clear_all_transactions(self):
        """
        Clears all transactions from the database.
        
        Returns:
            int: Number of transactions deleted.
        """
        try:
            # Get count of transactions to be deleted (for return value)
            self.db.cursor.execute("SELECT COUNT(*) FROM transactions")
            count = self.db.cursor.fetchone()[0]
            
            # Delete all transactions
            self.db.cursor.execute("DELETE FROM transactions")
            
            self.db.conn.commit()
            return count
            
        except Exception as e:
            print(f"Error clearing all transactions: {e}")
            return 0