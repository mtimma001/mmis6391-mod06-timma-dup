from flask import Blueprint, render_template
import plotly.express as px
import pandas as pd
from app.db_connect import get_db
from app.functions import calculate_total_sales_by_region, analyze_monthly_sales_trends, get_top_performing_region

visualization = Blueprint('visualization', __name__)

@visualization.route('/show_visualization')
def show_visualization():
    # Connect to the database and fetch data
    connection = get_db()
    query = """
        SELECT sd.sales_data_id, sd.monthly_amount, sd.date, r.region_name
        FROM sales_data sd
        JOIN regions r ON sd.region_id = r.region_id
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(result, columns=['sales_data_id', 'monthly_amount', 'date', 'region_name'])

    # Ensure the date column is in datetime format for trend analysis
    df['date'] = pd.to_datetime(df['date'])

    # Use the analysis functions from functions.py
    total_sales_by_region = calculate_total_sales_by_region(df)
    monthly_sales_trend = analyze_monthly_sales_trends(df)
    top_performing_region = get_top_performing_region(total_sales_by_region)

    # Convert Period objects to strings for JSON serialization
    monthly_sales_trend['Month'] = monthly_sales_trend['Month'].astype(str)

    # Generate Plotly visualizations
    total_sales_fig = px.bar(total_sales_by_region, x='Region', y='Total Sales', title='Total Sales by Region')
    total_sales_plot = total_sales_fig.to_html(full_html=False)

    monthly_sales_fig = px.line(monthly_sales_trend, x='Month', y='Total Sales', title='Monthly Sales Trend')
    monthly_sales_plot = monthly_sales_fig.to_html(full_html=False)

    return render_template(
        "visualization.html",
        total_sales_plot=total_sales_plot,
        monthly_sales_plot=monthly_sales_plot)