#Authors: Adnan Syed, Dhruvkumar Satishbhai Ahir, Kartik Rajeev Patil
#Date: May 02, 2025

#Enhanced Data Visualization Module for Personal Finance Tracker and Advisor.

#This module handles the creation of charts and graphs for visualizing financial data.
#It provides methods to generate various types of visualizations using matplotlib.

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import calendar
from datetime import datetime, timedelta
import numpy as np
from PyQt5.QtWidgets import (QVBoxLayout, QWidget, QLabel, QComboBox, 
                            QHBoxLayout, QDateEdit, QPushButton, QGroupBox, 
                            QFormLayout)
from PyQt5.QtCore import Qt, QDate

class FinanceDataVisualizer:
    """
    Data Visualization class that creates charts and graphs for financial analysis.
    
    This class provides methods for:
    - Creating spending by category pie charts for specific months
    - Generating monthly spending trend line charts with custom date ranges
    - Visualizing budget vs. actual spending bar charts per month
    - Creating interactive matplotlib figures for the PyQt GUI
    """
    
    def __init__(self, finance_tracker):
        """
        Initialize the data visualizer with a finance tracker.
        
        Args:
            finance_tracker: FinanceTracker instance for accessing financial data.
        """
        self.finance_tracker = finance_tracker
        self.current_month = datetime.now().strftime("%Y-%m")
        self.current_chart = None  # Store reference to the current chart
        
    def create_spending_by_category_chart(self, year_month=None):
        """
        Creates a pie chart showing spending distribution by category for a specific month.
        
        Args:
            year_month (str): Month to display in the format "YYYY-MM". Defaults to current month.
            
        Returns:
            FigureCanvas: A matplotlib figure canvas containing the pie chart.
        """
        if not year_month:
            year_month = self.current_month
            
        # Parse year and month
        year, month = map(int, year_month.split('-'))
        
        # Calculate start and end dates for the selected month
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day}"
        
        # Get spending data by category for the selected month
        spending_data = self.finance_tracker.db.get_spending_by_category(start_date, end_date)
        
        # Prepare data for pie chart
        categories = []
        amounts = []
        
        # Only include categories with non-zero spending
        for category, amount in spending_data:
            if amount > 0:
                categories.append(category)
                amounts.append(amount)
        
        # Create figure and plot
        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        
        # Generate pie chart
        if len(amounts) > 0:
            wedges, texts, autotexts = ax.pie(
                amounts, 
                labels=categories,
                autopct='%1.1f%%', 
                startangle=90,
                shadow=False,
                colors=plt.cm.tab10.colors[:len(categories)]  # Use a colorful palette
            )
            
            # Equal aspect ratio ensures pie chart is circular
            ax.axis('equal')
            
            # Set title with month name
            month_name = datetime(year, month, 1).strftime("%B %Y")
            ax.set_title(f'Spending by Category: {month_name}', fontsize=14)
            
            # Improve font size of percentage labels
            for autotext in autotexts:
                autotext.set_fontsize(9)
                autotext.set_weight('bold')
                
            # Improve text labels
            for text in texts:
                text.set_fontsize(10)
                
            # Add total spending text
            total_spending = sum(amounts)
            ax.text(0, -1.2, f'Total Spending: ${total_spending:.2f}', 
                   horizontalalignment='center', fontsize=12, fontweight='bold')
        else:
            ax.text(0.5, 0.5, f'No spending data available for {datetime(year, month, 1).strftime("%B %Y")}', 
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=12)
            ax.axis('off')
        
        # Create canvas
        canvas = FigureCanvas(fig)
        return canvas
    
    def create_monthly_trend_chart(self, start_date=None, end_date=None):
        """
        Creates a line chart showing spending trends over a custom date range.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format. Defaults to 6 months ago.
            end_date (str): End date in YYYY-MM-DD format. Defaults to current date.
            
        Returns:
            FigureCanvas: A matplotlib figure canvas containing the line chart.
        """
        # Default to past 6 months if no dates specified
        if not start_date or not end_date:
            end_date_obj = datetime.now()
            start_date_obj = end_date_obj - timedelta(days=180)  # Approximately 6 months
            
            start_date = start_date_obj.strftime("%Y-%m-%d")
            end_date = end_date_obj.strftime("%Y-%m-%d")
        else:
            # Parse the provided dates
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Calculate months between start and end dates
        months = []
        current_date = start_date_obj.replace(day=1)
        end_date_month = end_date_obj.replace(day=1)
        
        while current_date <= end_date_month:
            months.append(current_date.strftime("%b %Y"))
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Get spending for each month
        spending_amounts = []
        for month_str in months:
            month_obj = datetime.strptime(month_str, "%b %Y")
            month_start = month_obj.strftime("%Y-%m-01")
            month_end = month_obj.replace(day=calendar.monthrange(month_obj.year, month_obj.month)[1]).strftime("%Y-%m-%d")
            
            # Get spending for this month
            spending_data = self.finance_tracker.db.get_spending_by_category(month_start, month_end)
            total = sum(amount for _, amount in spending_data)
            spending_amounts.append(total)
        
        # Create figure and plot
        fig = Figure(figsize=(10, 5))
        ax = fig.add_subplot(111)
        
        if len(months) > 0 and any(amount > 0 for amount in spending_amounts):
            # Generate line chart
            ax.plot(months, spending_amounts, marker='o', linestyle='-', linewidth=2, markersize=8, color='#1f77b4')
            
            # Fill area under the line
            ax.fill_between(months, spending_amounts, alpha=0.3, color='#1f77b4')
            
            # Add labels and title
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Total Spending ($)', fontsize=12)
            
            date_range_text = f"{start_date_obj.strftime('%b %Y')} to {end_date_obj.strftime('%b %Y')}"
            ax.set_title(f'Monthly Spending Trend: {date_range_text}', fontsize=14)
            
            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Add grid lines for better readability
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Add data point labels
            for i, (month, amount) in enumerate(zip(months, spending_amounts)):
                ax.annotate(f'${amount:.2f}', 
                          (month, amount),
                          textcoords="offset points", 
                          xytext=(0, 10), 
                          ha='center',
                          fontweight='bold')
        else:
            ax.text(0.5, 0.5, f'No spending data available for selected date range', 
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=12)
            ax.axis('off')
        
        # Adjust layout to make room for rotated x-axis labels
        fig.tight_layout()
        
        # Create canvas
        canvas = FigureCanvas(fig)
        return canvas
    
    def create_budget_comparison_chart(self, year_month=None):
        """
        Creates a bar chart comparing budget vs. actual spending by category for a specific month.
        
        Args:
            year_month (str): Month to display in the format "YYYY-MM". Defaults to current month.
            
        Returns:
            FigureCanvas: A matplotlib figure canvas containing the bar chart.
        """
        if not year_month:
            year_month = self.current_month
            
        # Parse year and month
        year, month = map(int, year_month.split('-'))
        
        # Calculate start and end dates for the selected month
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day}"
        
        # Get spending data for the specified month
        spending_data = self.finance_tracker.db.get_spending_by_category(start_date, end_date)
        
        # Convert to dictionary for easier lookup
        spending_dict = {category: amount for category, amount in spending_data}
        
        # Get all categories and their budgets
        categories_data = self.finance_tracker.get_all_categories()
        
        # Prepare data for bar chart
        categories = []
        spent_amounts = []
        budget_amounts = []
        
        # Extract data for categories with budget or spending
        for category_data in categories_data:
            category_name = category_data[1]
            monthly_budget = category_data[2]
            
            # Get spending for this category (defaults to 0 if not found)
            spent = spending_dict.get(category_name, 0)
            
            # Only include categories with budget or spending
            if monthly_budget > 0 or spent > 0:
                categories.append(category_name)
                spent_amounts.append(spent)
                budget_amounts.append(monthly_budget)
        
        # Create figure and plot
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        if len(categories) > 0:
            # Set width of bars
            bar_width = 0.35
            
            # Set positions of bars on x-axis
            r1 = np.arange(len(categories))
            r2 = [x + bar_width for x in r1]
            
            # Create bars
            spent_bars = ax.bar(r1, spent_amounts, bar_width, label='Spent', color='#ff7f0e')
            budget_bars = ax.bar(r2, budget_amounts, bar_width, label='Budget', color='#2ca02c')
            
            # Add data labels above bars
            for bar in spent_bars:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'${height:.0f}',
                             xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3),  # 3 points vertical offset
                             textcoords="offset points",
                             ha='center', va='bottom',
                             fontsize=8)
                             
            for bar in budget_bars:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'${height:.0f}',
                             xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3),  # 3 points vertical offset
                             textcoords="offset points",
                             ha='center', va='bottom',
                             fontsize=8)
            
            # Add labels and title
            ax.set_xlabel('Categories', fontsize=12)
            ax.set_ylabel('Amount ($)', fontsize=12)
            
            # Set title with month name
            month_name = datetime(year, month, 1).strftime("%B %Y")
            ax.set_title(f'Budget vs. Actual Spending: {month_name}', fontsize=14)
            
            ax.set_xticks([r + bar_width/2 for r in range(len(categories))])
            ax.set_xticklabels(categories)
            
            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Add legend
            ax.legend()
            
            # Add grid lines for better readability
            ax.grid(True, linestyle='--', alpha=0.3, axis='y')
        else:
            ax.text(0.5, 0.5, f'No budget comparison data available for {datetime(year, month, 1).strftime("%B %Y")}', 
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=12)
            ax.axis('off')
        
        # Adjust layout to make room for rotated x-axis labels
        fig.tight_layout()
        
        # Create canvas
        canvas = FigureCanvas(fig)
        return canvas
    
    def create_visualization_widget(self, chart_type="spending_by_category"):
        """
        Creates a widget containing the specified visualization chart with controls for date selection.
        
        Args:
            chart_type (str): Type of chart to create. Options:
                - "spending_by_category": Pie chart of spending by category
                - "monthly_trend": Line chart of monthly spending trends
                - "budget_comparison": Bar chart of budget vs. actual spending
                
        Returns:
            QWidget: A widget containing the visualization chart and controls.
        """
        # Create a widget to hold the visualization and controls
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        
        # Create controls based on chart type
        if chart_type == "spending_by_category" or chart_type == "budget_comparison":
            # Month selector for pie chart and budget comparison
            controls_widget = QGroupBox("Select Month")
            controls_layout = QHBoxLayout(controls_widget)
            
            # Create a combo box with available months
            self.month_selector = QComboBox()
            self.populate_month_selector(self.month_selector)
            controls_layout.addWidget(QLabel("Month:"))
            controls_layout.addWidget(self.month_selector)
            
            # Apply button
            apply_button = QPushButton("Apply")
            controls_layout.addWidget(apply_button)
            controls_layout.addStretch(1)
            
            main_layout.addWidget(controls_widget)
            
            # Create the initial chart
            if chart_type == "spending_by_category":
                self.current_chart = self.create_spending_by_category_chart()
                
                # Connect the apply button to update the chart
                apply_button.clicked.connect(lambda: self.update_spending_chart(self.current_chart, main_layout))
            else:  # budget_comparison
                self.current_chart = self.create_budget_comparison_chart()
                
                # Connect the apply button to update the chart
                apply_button.clicked.connect(lambda: self.update_budget_chart(self.current_chart, main_layout))
        
        elif chart_type == "monthly_trend":
            # Date range selector for trend chart
            controls_widget = QGroupBox("Select Date Range")
            controls_layout = QFormLayout(controls_widget)
            
            # Start date picker
            self.start_date_edit = QDateEdit()
            self.start_date_edit.setDate(QDate.currentDate().addMonths(-6))  # Default to 6 months ago
            self.start_date_edit.setCalendarPopup(True)
            controls_layout.addRow("Start Date:", self.start_date_edit)
            
            # End date picker
            self.end_date_edit = QDateEdit()
            self.end_date_edit.setDate(QDate.currentDate())  # Default to today
            self.end_date_edit.setCalendarPopup(True)
            controls_layout.addRow("End Date:", self.end_date_edit)
            
            # Apply button
            button_layout = QHBoxLayout()
            apply_button = QPushButton("Apply")
            button_layout.addWidget(apply_button)
            button_layout.addStretch(1)
            controls_layout.addRow("", button_layout)
            
            main_layout.addWidget(controls_widget)
            
            # Create the initial chart
            self.current_chart = self.create_monthly_trend_chart()
            
            # Connect the apply button to update the chart
            apply_button.clicked.connect(lambda: self.update_trend_chart(self.current_chart, main_layout))
        else:
            # Default to spending by category if an invalid chart type is specified
            self.current_chart = self.create_spending_by_category_chart()
    
        # Add the chart to the widget
        main_layout.addWidget(self.current_chart)
    
        return widget
    
    def populate_month_selector(self, combo_box):
        """
        Populates a combo box with available months from the database.
        
        Args:
            combo_box: QComboBox to populate.
        """
        # Get transaction date range from database
        try:
            self.finance_tracker.db.cursor.execute("SELECT MIN(date), MAX(date) FROM transactions")
            date_range = self.finance_tracker.db.cursor.fetchone()
            
            if date_range and date_range[0] and date_range[1]:
                min_date = datetime.strptime(date_range[0], "%Y-%m-%d")
                max_date = datetime.strptime(date_range[1], "%Y-%m-%d")
                
                # Generate a list of months between min and max dates
                current_date = min_date.replace(day=1)
                end_date = max_date.replace(day=1)
                
                months = []
                while current_date <= end_date:
                    months.append((current_date.strftime("%Y-%m"), current_date.strftime("%B %Y")))
                    # Move to next month
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
                
                # Add months to combo box (most recent first)
                for year_month, display_name in reversed(months):
                    combo_box.addItem(display_name, year_month)
                
                # Set current month as default if available
                current_month = datetime.now().strftime("%B %Y")
                index = combo_box.findText(current_month)
                if index >= 0:
                    combo_box.setCurrentIndex(index)
            else:
                # No transaction data, add current month
                current_date = datetime.now()
                combo_box.addItem(current_date.strftime("%B %Y"), current_date.strftime("%Y-%m"))
                
        except Exception as e:
            print(f"Error populating month selector: {e}")
            # Add current month as fallback
            current_date = datetime.now()
            combo_box.addItem(current_date.strftime("%B %Y"), current_date.strftime("%Y-%m"))
    
    def update_spending_chart(self, old_chart_widget, layout):
        """
        Updates the spending by category chart based on selected month.
        
        Args:
            old_chart_widget: Current chart widget to replace.
            layout: Layout containing the chart widget.
        """
        # Get selected month
        selected_month = self.month_selector.currentData()
        
        # Create new chart
        new_chart = self.create_spending_by_category_chart(selected_month)
        
        # Remove old chart
        layout.removeWidget(old_chart_widget)
        old_chart_widget.setParent(None)
        
        # Add new chart to layout at same position (should be index 1)
        layout.addWidget(new_chart)
        
        # Store reference to the new chart for future updates
        self.current_chart = new_chart
    
    def update_budget_chart(self, old_chart_widget, layout):
        """
        Updates the budget comparison chart based on selected month.
        
        Args:
            old_chart_widget: Current chart widget to replace.
            layout: Layout containing the chart widget.
        """
        # Get selected month
        selected_month = self.month_selector.currentData()
        
        # Create new chart
        new_chart = self.create_budget_comparison_chart(selected_month)
        
        # Remove old chart
        layout.removeWidget(old_chart_widget)
        old_chart_widget.setParent(None)
        
        # Add new chart to layout at same position (should be index 1)
        layout.addWidget(new_chart)
        
        # Store reference to the new chart for future updates
        self.current_chart = new_chart
    
    def update_trend_chart(self, old_chart_widget, layout):
        """
        Updates the monthly trend chart based on selected date range.
        
        Args:
            old_chart_widget: Current chart widget to replace.
            layout: Layout containing the chart widget.
        """
        # Get selected date range
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        # Create new chart
        new_chart = self.create_monthly_trend_chart(start_date, end_date)
        
        # Remove old chart
        layout.removeWidget(old_chart_widget)
        old_chart_widget.setParent(None)
        
        # Add new chart to layout at same position (should be index 1)
        layout.addWidget(new_chart)
        
        # Store reference to the new chart for future updates
        self.current_chart = new_chart