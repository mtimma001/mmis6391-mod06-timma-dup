import pandas as pd

def calculate_total_sales_by_region(df):
    # Group by region_name and sum the monthly_amount
    total_sales_by_region = df.groupby('region_name')['monthly_amount'].sum().reset_index()
    total_sales_by_region.columns = ['Region', 'Total Sales']
    return total_sales_by_region

def analyze_monthly_sales_trends(df):
    # Group by month and sum the monthly_amount
    df['month'] = df['date'].dt.to_period('M')
    monthly_sales_trend = df.groupby('month')['monthly_amount'].sum().reset_index()
    monthly_sales_trend.columns = ['Month', 'Total Sales']
    return monthly_sales_trend

def get_top_performing_region(total_sales_by_region):
    # Sort by Total Sales and get the top region
    if not total_sales_by_region.empty:
        top_performing_region = total_sales_by_region.sort_values(by='Total Sales', ascending=False).iloc[0]
        return top_performing_region
    else:
        return None