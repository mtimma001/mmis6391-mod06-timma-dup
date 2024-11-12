import pandas as pd

def calculate_total_sales_by_region(df):
    """
    Calculate total sales by region.
    """
    total_sales_by_region = df.groupby('region')['monthly_amount'].sum().reset_index()
    total_sales_by_region.columns = ['Region', 'Total Sales']
    return total_sales_by_region

def analyze_monthly_sales_trends(df):
    """
    Analyze monthly sales trends.
    """
    df['date'] = pd.to_datetime(df['date'])  # Ensure the date is in datetime format
    df['month'] = df['date'].dt.to_period('M')  # Extract the month for trend analysis
    monthly_sales_trend = df.groupby('month')['monthly_amount'].sum().reset_index()
    monthly_sales_trend.columns = ['Month', 'Total Monthly Sales']
    return monthly_sales_trend

def get_top_performing_region(total_sales_by_region):
    """
    Identify the top-performing region based on total sales.
    """
    top_region = total_sales_by_region.sort_values(by='Total Sales', ascending=False).iloc[0]
    return top_region

def get_bottom_performing_region(total_sales_by_region):
    """
    Identify the bottom-performing region based on total sales.
    """
    bottom_region = total_sales_by_region.sort_values(by='Total Sales').iloc[0]
    return bottom_region
